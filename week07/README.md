# 7주차 실습 1: Docker Compose와 Redis

2026-10-12 교안 19–27쪽 실행 완료. 기존 파란색 방명록 소스와 디자인 유지.
Compose 파일: `../week06/guestbook/compose.yaml`. 프로젝트: week07-lab1.
웹 http://localhost:8080 . 기존 메모리 버전 8081도 유지.
Redis 비밀번호는 교안의 로컬 실습용 값이며 실제 서비스에 사용하지 않는다.

| 확인 작업 | 글 개수 |
|---|---|
| 테스트 글 등록 | 3 |
| restart web | 3 유지 |
| down 후 up -d | 3 유지 |
| down -v 후 up -d | 0으로 초기화 |

web 로그에서 Redis 연결 성공 확인. Redis는 서비스 이름으로 접근하며 외부 포트를 게시하지 않는다.
AOF와 named volume으로 데이터를 저장한다. down은 볼륨 보존, down -v는 볼륨까지 삭제.
삭제 실습은 이번에 새로 만든 week07-lab1_redis-data 테스트 볼륨에만 적용했다.
최종 web과 redis는 실행 중이고 방명록은 비어 있다. 실제 명령어/응답 기록은 logs/에 저장.
단순 depends_on은 Redis 준비 완료를 보장하지 않는다. healthcheck는 교안 실습 3에서 추가한다.

터미널 확인:

```bash
cd ~/Desktop/2학년2학기/DevOps/devops/week06/guestbook
docker compose ps
docker compose logs web
```

실습 1의 확인 결과이다. 실습 2·3 및 혼자 해보기 결과는 아래에 기록했다.

## 실습 2: 네트워크 격리 (교안 29–30쪽)

- 호스트 127.0.0.1:6379 접속: ConnectionRefusedError로 실패 (예상 결과).
- web 컨테이너 내부에서 redis 이름의 DNS 해석 성공.
- web → redis:6379 TCP 연결 성공.
- Redis에는 ports가 없어 호스트에 게시되지 않았지만, 같은 Compose 네트워크의 web은 서비스 이름으로 접근 가능하다.
- 결과 원문: logs/lab2-*.txt. 기존 서비스와 데이터는 변경하지 않았다.

## 실습 3: Compose 다듬기

### 완료한 확인

- 3-1: 비밀번호를 guestbook/.env로 분리. .env.example 작성, .gitignore의 .env 및 기존 .dockerignore 제외 확인. 실제 값은 Git에 올리지 않음.
- 3-2: Redis 및 web에 healthcheck 추가. Redis service_healthy 이후 web 시작. Redis와 web 모두 healthy.
- 3-3: 기존 고정 8080 포트로 web=3 실행 시 포트 충돌 재현. nginx만 8080 게시, web은 expose 5000으로 변경. nginx 1 + web 3 + Redis 1 실행 성공.
- 24회 /healthz 호출에서 서로 다른 hostname 3개 확인 (logs/lab3-11-distribution.json). web들의 방명록 글 개수가 같아 공유 Redis 사용 확인.
- web-2 수동 중지 후 응답 상태 확인, compose up -d --scale web=3으로 복구 완료.
- 3-4: compose config --quiet 성공. REDIS_PASSWORD를 빈 값으로 실행하면 필수 값 오류로 중단됨.
- develop.watch의 app.py 및 templates rebuild 설정 저장.

### 아직 확인하지 못한 단계

이 실행 환경의 macOS 파일 감시가 `failed to start eventstream`으로 종료되어 watch에 의한 자동 재빌드 실제 동작은 확인하지 못했다.
기본 잠금 디렉터리 쓰기 권한도 부여되지 않아 공식 XDG_RUNTIME_DIR 설정으로 작업 폴더를 사용했지만, 파일 감시 자체는 여전히 실패했다.
아래 명령어를 사용자 터미널에서 실행한 뒤 templates/index.html의 문구를 수정·저장하면 자동 재빌드를 확인할 수 있다.

```bash
cd ~/Desktop/2학년2학기/DevOps/devops/week06/guestbook
docker compose watch --no-up
```

Ctrl+C는 watch만 종료하며 실행 중인 서비스는 유지된다.
최종 nginx 1개 + healthy web 3개 + healthy Redis 1개 실행 중. 기존 파란색 디자인과 Redis 글 유지.
로그에는 비밀번호를 가렸다. 혼자 해보기에서 Git 커밋·푸시 및 week07 태그를 기록한다.

## 혼자 해보기 (교안 61쪽)

### 현재 Compose 상태

```text
$ docker compose ps
NAME                  IMAGE             COMMAND                  SERVICE   CREATED             STATUS                       PORTS
week07-lab1-nginx-1   nginx:alpine      "/docker-entrypoint.…"   nginx     About an hour ago   Up About an hour             127.0.0.1:8080->80/tcp
week07-lab1-redis-1   redis:7-alpine    "docker-entrypoint.s…"   redis     About an hour ago   Up About an hour (healthy)   6379/tcp
week07-lab1-web-1     week07-lab1-web   "python app.py"          web       50 minutes ago      Up 50 minutes (healthy)      5000/tcp
week07-lab1-web-2     week07-lab1-web   "python app.py"          web       50 minutes ago      Up 50 minutes (healthy)      5000/tcp
week07-lab1-web-3     week07-lab1-web   "python app.py"          web       50 minutes ago      Up 50 minutes (healthy)      5000/tcp
```

### scale 후 호스트명

24회 /healthz 요청에서 다음 3개의 서로 다른 웹 컨테이너 응답을 확인했다:

- `2a151a9c02b7`
- `380696d68b1e`
- `ff8eef99ba3f`

원문: logs/self-study-hostnames.json. 브라우저 자동화가 ERR_BLOCKED_BY_CLIENT로 차단되어 이번 호스트명 화면 캡처는 아직 저장하지 못했다. 아래 URL을 일반 브라우저에서 새로고침하여 서로 다른 hostname이 표시된 화면 2~3개를 캡처하고 week07/images/에 추가해야 한다.

http://localhost:8080/healthz

현재 커스텀 방명록 메인 화면은 hostname을 표시하지 않으므로 /healthz 응답으로 확인한다.

### down과 down -v 비교

| 명령 | 컨테이너/네트워크 | Redis 볼륨 | 테스트 글 |
|---|---|---|---|
| down → up -d | 삭제 후 재생성 | 유지 | 3개 유지 |
| down -v → up -d | 삭제 후 재생성 | 삭제 후 새로 생성 | 0개 |

실습 1의 실제 로그 08-down.txt, 12-after-down-up.json, 13-down-v.txt, 15-after-down-v-up.json에 결과를 저장했다. 기존 테스트 결과를 사용해 비교하며, 현재 사용자 글을 다시 삭제하지 않았다.

### .env를 Git에 올리지 않는 이유

.env에는 실제 Redis 비밀번호가 들어 있다. 공개 저장소에 커밋하면 다른 사람이 값을 볼 수 있고, 파일에서 지워도 과거 Git 이력에 남을 수 있다. compose.yaml은 환경변수 참조만 사용하고 .env.example은 값이 없는 작성 양식을 공유한다. .gitignore는 Git 커밋에서 제외하며 .dockerignore는 Docker 이미지로 복사되는 것을 막는다. 두 파일은 암호화 기능이 아니다.

### 자동 반영 상태

사용자 터미널에서 Watch enabled가 표시됐지만, 이후 수정한 문구는 실행 컨테이너에 반영되지 않았다. 수동 docker compose up -d --build --scale web=3으로 적용했다. 따라서 자동 재빌드 성공으로 기록하지 않았다.

### 저장소 기록

소스는 기존 week06/guestbook을 계속 사용한다. 중복 복사하지 않았다. Compose, nginx.conf, .env.example, 수정한 HTML, week07 기록 및 .gitignore를 커밋 대상으로 선택했다. .env와 이번 실습과 관계없는 week04 수정은 포함하지 않는다. main에 푸시하고 week07 태그를 생성한다.
