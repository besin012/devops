# 11주차 쿠버네티스 설정과 상태 점검

- ConfigMap에 제목, 색상, Redis 주소를 넣고 Redis 비밀번호는 Secret으로 연결했다. Secret을 base64로 디코딩하면 원래 값으로 돌아와서 실제 비밀번호 파일은 Git에서 제외했다.
- 방명록 Pod를 2개에서 4개로 늘렸다. 같은 Redis를 쓰는 4개 Pod에서 테스트 글을 확인했다. ConfigMap의 제목과 색을 바꾸고 `rollout restart`를 해도 글은 남았다.
- Redis를 내리니 `/readyz`가 503을 반환했고 Pod는 재시작 없이 `0/1`이 됐다. Redis를 올리니 다시 `1/1`이 됐다.
- liveness 경로를 `/devops`로 바꾸니 404가 발생하고 컨테이너가 재시작됐다. `rollout undo`로 원래 경로를 복구했다.
- 문제가 생기면 `get pods`로 먼저 상태를 보고, `describe pod`로 Events를 확인한 뒤 `logs --previous`로 재시작 전 로그를 본다.

[실행 로그](https://github.com/besin012/devops/actions/runs/43852090821) · [실습 YAML](k8s/)
