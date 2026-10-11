#!/usr/bin/env python3
from pathlib import Path
source=Path(__file__).with_name('run_lab.py').read_text()
exec(source.split("prefix='w06-1011-'")[0])
run('38-public-pull',['pull','ghcr.io/besin012/guestbook:v2'])
run('38-public-run',['run','-d','-p','127.0.0.1:18085:5000','--name','w06-1011-check','ghcr.io/besin012/guestbook:v2'])
ready(18085)
run('38-public-files',['exec','w06-1011-check','ls','/app'])
run('38-public-health','curl -fsS http://127.0.0.1:18085/healthz')
run('38-manifest',['manifest','inspect','ghcr.io/besin012/guestbook:v2'])
