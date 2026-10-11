#!/usr/bin/env python3
"""교안 순서로 실행. 기존 방명록 파일과 jiyun-guestbook 컨테이너는 유지."""
from pathlib import Path
import subprocess, shlex, tempfile, shutil, time, json
root=Path(__file__).resolve().parents[1]
app=root/'guestbook'
logs=root/'logs'
logs.mkdir(exist_ok=True)
docker=['/Users/leejiyun/.docker/bin/docker','--host','unix:///Users/leejiyun/.docker/run/docker.sock']
results=[]
def run(label,args,cwd=app,expected=False):
    cmd=docker+args if isinstance(args,list) else ['/bin/zsh','-c',args]
    display='docker '+shlex.join(args) if isinstance(args,list) else args
    print('\n['+label+'] $ '+display,flush=True)
    try:
        p=subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
        output=p.stdout; rc=p.returncode
    except subprocess.TimeoutExpired as e:
        output=str(e.stdout or '')+'\n240초 제한 초과'; rc=124
    text='$ '+display+'\n'+output+'\nExit code: '+str(rc)+'\n'
    (logs/(label+'.txt')).write_text(text)
    print(output[-4500:],flush=True)
    results.append({'step':label,'exit_code':rc,'expected_failure':expected})
    return rc==0

def ready(port):
    for _ in range(30):
        p=subprocess.run(['curl','-fsS',f'http://127.0.0.1:{port}/healthz'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if p.returncode==0:return
        time.sleep(0.5)

prefix='w06-1011-'
run('06-latest-tag',['pull','ghcr.io/makyraen/inhatc-devops-guestbook:latest'],expected=True)
public=run('17-pull',['pull','ghcr.io/makyraen/inhatc-devops-guestbook:v1'])
if public:
    if run('17-run',['run','-d','-p','127.0.0.1:18080:5000','--name',prefix+'demo','ghcr.io/makyraen/inhatc-devops-guestbook:v1']):
        ready(18080);run('17-health','curl -fsS http://127.0.0.1:18080/healthz')
        run('18-demo-remove',['rm','-f',prefix+'demo'])
    if run('18-env',['run','-d','-p','127.0.0.1:18080:5000','--name',prefix+'demo','-e','APP_TITLE=지윤의 방명록','-e','THEME_COLOR=#16a34a','ghcr.io/makyraen/inhatc-devops-guestbook:v1']):
        ready(18080); run('18-env-check',['exec',prefix+'demo','printenv','APP_TITLE','THEME_COLOR']);run('18-logs',['logs',prefix+'demo'])
run('19-files','ls -la')
run('20-local-python','python3 app.py',expected=True)
run('21-dockerfile','cat Dockerfile')
run('22-defaults',"rg 'APP_TITLE|THEME_COLOR' app.py")
run('23-build-v1',['build','--progress=plain','-t','guestbook:week06-v1','.'])
run('24-images',['image','ls','--filter','reference=*guestbook*'])
if run('24-run',['run','-d','-p','127.0.0.1:18084:5000','--name',prefix+'gb','guestbook:week06-v1']):
    ready(18084);run('24-post',"curl -fsS --data-urlencode 'name=지윤' --data-urlencode 'message=도커 이미지 실행 확인!' http://127.0.0.1:18084/add -o /dev/null; curl -fsS http://127.0.0.1:18084/api/entries")
run('25-rebuild-cached',['build','--progress=plain','-t','guestbook:week06-v1.1','.'])
# 실습 변경은 임시 빌드 컨텍스트에서만 수행하여 기존 방명록 디자인 보존
with tempfile.TemporaryDirectory(prefix='week06-cache-') as td:
    ctx=Path(td)/'guestbook';shutil.copytree(app,ctx)
    html=ctx/'templates/index.html';html.write_text(html.read_text()+'\n<!-- 캐시 비교 실습 -->\n')
    run('25-code-change',['build','--progress=plain','-t','guestbook:week06-v1.2','.'],ctx)
    (ctx/'Dockerfile.bad').write_text('FROM python:3.12-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD ["python", "app.py"]\n')
    run('26-bad-before',['build','--progress=plain','-f','Dockerfile.bad','-t','guestbook:week06-bad','.'],ctx)
    f=ctx/'app.py';f.write_text(f.read_text()+'\n# 캐시 비교 실습\n')
    run('26-bad-after',['build','--progress=plain','-f','Dockerfile.bad','-t','guestbook:week06-bad','.'],ctx)
run('27-remove-bad',['rmi','guestbook:week06-bad'])
run('30-existing-registry-tag',['image','inspect','ghcr.io/besin012/guestbook:v2','--format','{{json .RepoDigests}}'])
if public:
    if run('32-example-exchange',['run','-d','-p','127.0.0.1:19090:5000','--name',prefix+'friend','ghcr.io/makyraen/inhatc-devops-guestbook:v1']):
        ready(19090);run('32-example-health','curl -fsS http://127.0.0.1:19090/healthz')
run('34-architecture',['image','inspect','guestbook:v2','--format','{{.Architecture}}'])
registry=run('38-registry-pull',['pull','ghcr.io/besin012/guestbook:v2'])
if registry:
    if run('38-check-run',['run','-d','-p','127.0.0.1:18085:5000','--name',prefix+'check','ghcr.io/besin012/guestbook:v2']):
        ready(18085);run('38-app-files',['exec',prefix+'check','ls','/app']);run('38-check-remove',['rm','-f',prefix+'check'])
run('39-v2-build',['build','--progress=plain','-t','guestbook:v2','.'])
if run('39-v2-env',['run','-d','-p','127.0.0.1:18086:5000','--name',prefix+'gbv2','-e','THEME_COLOR=#C6A15B','guestbook:v2']):
    ready(18086);run('39-v2-env-check',['exec',prefix+'gbv2','printenv','THEME_COLOR'])
if public:
    custom=root/'Dockerfile.custom'
    custom.write_text('FROM ghcr.io/makyraen/inhatc-devops-guestbook:v1\nENV APP_TITLE="지윤의 방명록" \\\n    THEME_COLOR="#7C9A82"\n')
    run('40-custom-build',['build','--progress=plain','-f',str(custom),'-t','guestbook:week06-custom','.'])
    if run('40-custom-run',['run','-d','-p','127.0.0.1:18082:5000','--name',prefix+'custom','guestbook:week06-custom']):
        ready(18082);run('40-custom-env',['exec',prefix+'custom','printenv','APP_TITLE','THEME_COLOR'])
        run('41-history',['history','guestbook:week06-custom'])
        run('42-custom-remove',['rm','-f',prefix+'custom'])
    if run('42-override',['run','-d','-p','127.0.0.1:18083:5000','--name',prefix+'custom','-e','THEME_COLOR=#16a34a','guestbook:week06-custom']):
        ready(18083);run('42-override-env',['exec',prefix+'custom','printenv','THEME_COLOR'])
        run('47-before-restart',"curl -fsS --data-urlencode 'name=실습' --data-urlencode 'message=메모리 저장 확인' http://127.0.0.1:18083/add -o /dev/null; curl -fsS http://127.0.0.1:18083/api/entries")
        run('47-restart',['restart',prefix+'custom']);ready(18083)
        run('47-after-restart','curl -fsS http://127.0.0.1:18083/api/entries')
run('46-fat',['build','--progress=plain','-t','guestbook:week06-fat','.'])
run('46-slim',['build','--progress=plain','-f','Dockerfile.multistage','-t','guestbook:week06-slim','.'])
run('46-size',['image','ls','--filter','reference=guestbook:week06-*'])
(logs/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print('실습 완료. 캡처 후 임시 컨테이너를 정리합니다. 기존 jiyun-guestbook은 유지합니다.',flush=True)
