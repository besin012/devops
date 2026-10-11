#!/usr/bin/env python3
from pathlib import Path
source=Path(__file__).with_name('run_lab.py').read_text()
exec(source.split("prefix='w06-1011-'")[0])
prefix='w06-1011-'
image='nearykam/inhatc-devops-guestbook:v1'
run('17-fallback-pull',['pull',image])
run('17-fallback-run',['run','-d','-p','127.0.0.1:18080:5000','--name',prefix+'demo',image]);ready(18080)
run('17-fallback-health','curl -fsS http://127.0.0.1:18080/healthz')
run('18-demo-remove',['rm','-f',prefix+'demo'])
run('18-env',['run','-d','-p','127.0.0.1:18080:5000','--name',prefix+'demo','-e','APP_TITLE=지윤의 방명록','-e','THEME_COLOR=#16a34a',image]);ready(18080)
run('18-env-check',['exec',prefix+'demo','printenv','APP_TITLE','THEME_COLOR']);run('18-logs',['logs',prefix+'demo'])
run('32-example-exchange',['run','-d','-p','127.0.0.1:19090:5000','--name',prefix+'friend',image]);ready(19090)
run('32-example-health','curl -fsS http://127.0.0.1:19090/healthz')
custom=root/'Dockerfile.custom'
custom.write_text('FROM nearykam/inhatc-devops-guestbook:v1\nENV APP_TITLE="지윤의 방명록" \\\n    THEME_COLOR="#7C9A82"\n')
run('40-custom-build',['build','--progress=plain','-f',str(custom),'-t','guestbook:week06-custom','.'])
run('40-custom-run',['run','-d','-p','127.0.0.1:18082:5000','--name',prefix+'custom','guestbook:week06-custom']);ready(18082)
run('40-custom-env',['exec',prefix+'custom','printenv','APP_TITLE','THEME_COLOR'])
run('41-history',['history','guestbook:week06-custom'])
run('42-custom-remove',['rm','-f',prefix+'custom'])
run('42-override',['run','-d','-p','127.0.0.1:18083:5000','--name',prefix+'custom','-e','THEME_COLOR=#16a34a','guestbook:week06-custom']);ready(18083)
run('42-override-env',['exec',prefix+'custom','printenv','THEME_COLOR'])
run('47-before-restart',"curl -fsS --data-urlencode 'name=실습' --data-urlencode 'message=메모리 저장 확인' http://127.0.0.1:18083/add -o /dev/null; curl -fsS http://127.0.0.1:18083/api/entries")
run('47-restart',['restart',prefix+'custom']);ready(18083)
run('47-after-restart','curl -fsS http://127.0.0.1:18083/api/entries')
(logs/'supplement-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
