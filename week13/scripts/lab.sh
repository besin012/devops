#!/usr/bin/env bash
set -euo pipefail
mkdir -p evidence
exec > >(tee evidence/lab.log) 2>&1
if ! command -v kind >/dev/null; then
  curl -fsSLo "$RUNNER_TEMP/kind" https://kind.sigs.k8s.io/dl/v0.33.0/kind-linux-amd64
  chmod +x "$RUNNER_TEMP/kind"
  export PATH="$RUNNER_TEMP:$PATH"
fi
kind create cluster --name week13 --wait 120s
kubectl create namespace week13
kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl -n argocd rollout status deployment/argocd-repo-server --timeout=240s
kubectl -n argocd rollout status statefulset/argocd-application-controller --timeout=240s
password=$(openssl rand -hex 24)
echo "::add-mask::$password"
kubectl -n week13 create secret generic guestbook-secret --from-literal=REDIS_PASSWORD="$password"
git config user.name "$(git log -1 --format=%an)"
git config user.email "$(git log -1 --format=%ae)"
demo_branch="week13-gitops-demo-$GITHUB_RUN_ID"
git switch -c "$demo_branch"
git push origin "$demo_branch"
export DEMO_BRANCH="$demo_branch"
python3 - <<'PY'
from pathlib import Path
import os
p=Path('argocd-application.yaml')
p.write_text(p.read_text().replace('targetRevision: main','targetRevision: '+os.environ['DEMO_BRANCH']))
PY
kubectl apply -f argocd-application.yaml
wait_sync() {
  desired=$(git rev-parse HEAD)
  for i in {1..100}; do
    kubectl -n argocd annotate application guestbook argocd.argoproj.io/refresh=hard --overwrite >/dev/null
    status=$(kubectl -n argocd get application guestbook -o json)
    if jq -e --arg rev "$desired" '.status.sync.revision == $rev and .status.sync.status == "Synced" and .status.health.status == "Healthy"' <<< "$status" >/dev/null; then
      jq '{sync:.status.sync,health:.status.health}' <<< "$status"
      return 0
    fi
    if ((i % 6 == 0)); then
      jq '{sync:.status.sync,health:.status.health,conditions:.status.conditions,operation:.status.operationState.message}' <<< "$status"
      kubectl -n week13 get pods
    fi
    sleep 5
  done
  kubectl -n argocd get application guestbook -o yaml
  return 1
}
commit_push() {
  git add week13/k8s
  git commit -m "$1"
  git push origin "$demo_branch"
  wait_sync
}
wait_sync
kubectl -n week13 get pods
kubectl -n week13 logs -l app=guestbook | grep 'Redis 연결 성공'
# Change the desired state in Git.
sed -i 's/replicas: 2/replicas: 4/' week13/k8s/deployment.yaml
commit_push 'week13 : Pod 4개'
scale_commit=$(git rev-parse HEAD)
kubectl -n week13 get pods
# Change the live state and observe Argo CD self-healing.
kubectl -n week13 scale deployment guestbook --replicas=10
kubectl -n week13 get deployment guestbook
for i in {1..40}; do
  count=$(kubectl -n week13 get deployment guestbook -o jsonpath='{.spec.replicas}')
  if [ "$count" = 4 ]; then break; fi
  sleep 2
done
test "$count" = 4
echo 'selfHeal restored replicas=4'
wait_sync
git revert "$scale_commit" --no-edit
git push origin "$demo_branch"
wait_sync
test "$(kubectl -n week13 get deployment guestbook -o jsonpath='{.spec.replicas}')" = 2
kubectl -n week13 get pods
cat > week13/k8s/hello.yaml <<'YAML'
apiVersion: v1
kind: ConfigMap
metadata:
  name: hello
data:
  MESSAGE: "GitOps"
YAML
commit_push 'week13 : hello 추가'
kubectl -n week13 get configmap hello
git rm week13/k8s/hello.yaml
commit_push 'week13 : hello 삭제'
if kubectl -n week13 get configmap hello; then exit 1; fi
echo 'prune removed hello ConfigMap'
sed -i "s/guestbook-week12:0d13b25/guestbook-week12:$IMAGE_TAG/" week13/k8s/deployment.yaml
commit_push 'week13 : 새 이미지 배포'
kubectl -n week13 rollout status deployment/guestbook --timeout=120s
kubectl -n week13 get deployment guestbook -o jsonpath='{.spec.template.spec.containers[0].image}'
echo
kubectl -n week13 port-forward service/guestbook 18093:80 > /tmp/week13-forward.log 2>&1 &
forward_pid=$!
trap 'kill "$forward_pid" 2>/dev/null || true' EXIT
curl --retry 15 --retry-all-errors --retry-delay 1 -fsS http://localhost:18093/healthz
curl -fsS http://localhost:18093/ > evidence/guestbook.html
grep -o '<title>.*</title>' evidence/guestbook.html | grep 'CI/CD'
# Metrics API in the temporary kind cluster.
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl -n kube-system patch deployment metrics-server --type json -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
kubectl -n kube-system rollout status deployment/metrics-server --timeout=180s
for i in {1..30}; do
  if kubectl -n week13 top pods > evidence/top-before.txt; then break; fi
  sleep 5
done
cat evidence/top-before.txt
kubectl top nodes
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace --set-string grafana.adminPassword="$password" --set prometheus.prometheusSpec.retention=1h --wait --timeout 5m
kubectl -n monitoring get pods
kubectl -n monitoring port-forward svc/monitoring-grafana 13000:80 > /tmp/week13-grafana.log 2>&1 &
grafana_pid=$!
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 19090:9090 > /tmp/week13-prometheus.log 2>&1 &
prom_pid=$!
trap 'kill "$forward_pid" "$grafana_pid" "$prom_pid" 2>/dev/null || true' EXIT
curl --retry 15 --retry-all-errors --retry-delay 1 -fsS http://localhost:13000/api/health
curl -fsS -u "admin:$password" 'http://localhost:13000/api/search?query=Kubernetes' | jq '[.[]|{title,url}]' > evidence/grafana-dashboards.json
cat evidence/grafana-dashboards.json
kubectl -n week13 run load --image=busybox:1.37 --restart=Never -- sh -c 'while true; do wget -q -O /dev/null http://guestbook/; done'
kubectl -n week13 wait --for=condition=Ready=true pod/load --timeout=90s
sleep 60
kubectl -n week13 top pods | tee evidence/top-load.txt
curl -fsSG http://localhost:19090/api/v1/query --data-urlencode 'query=sum by(pod) (rate(container_cpu_usage_seconds_total{namespace="week13",container="web"}[1m]))' | jq . > evidence/prometheus-cpu.json
cat evidence/prometheus-cpu.json
kubectl -n week13 delete pod load
kubectl -n week13 logs -l app=guestbook --tail=5 --prefix
git log -6 --oneline
kubectl -n argocd get application guestbook
