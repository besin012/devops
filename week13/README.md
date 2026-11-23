# 13주차 GitOps

Argo CD가 Git의 YAML을 읽고 클러스터를 같은 상태로 맞추는 실습이다.

## 실행 방법

Argo CD가 설치된 클러스터에서 아래 순서로 실행한다.

```bash
kubectl create namespace week13
cp week13/k8s/secret.yaml.example week13/k8s/secret.yaml
# secret.yaml의 CHANGE_ME를 실습용 비밀번호로 변경
kubectl -n week13 apply -f week13/k8s/secret.yaml
kubectl apply -f argocd-application.yaml
kubectl -n week13 get pods
kubectl -n week13 port-forward svc/guestbook 8080:80
```

브라우저에서 http://localhost:8080 으로 확인한다. 배포 파일은 `week13/k8s`에 있고, Secret은 Git에서 제외했다.

## 실습 결과

- Git에서 replicas를 2개에서 4개로 바꾸니 Argo CD가 반영했다. 직접 10개로 늘린 값은 selfHeal로 다시 4개가 됐다.
- 스케일 변경 커밋을 revert하니 2개로 돌아왔다. hello ConfigMap을 Git에 추가하고 삭제해 prune 동작도 확인했다.
- 제목을 CI/CD로 바꾼 이미지를 Actions로 게시했다. 배포 YAML에는 latest 대신 커밋 태그 `8113efe`를 사용했다.

맥의 Docker가 연결되지 않아 GitHub 러너의 임시 kind 클러스터에서 실행했다. 변경 실험에는 `week13-gitops-demo-45151075425` 브랜치를 사용했고, 저장한 Application은 main을 읽도록 설정했다.

[실행 로그](https://github.com/besin012/devops/actions/runs/45151075425)
