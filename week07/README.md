# 7주차 - Docker Compose

6주차 방명록에 Redis를 연결하고 nginx를 앞에 두어 웹 컨테이너를 3개로 늘렸다.
소스는 [week06/guestbook](../week06/guestbook/)을 그대로 사용했다.
실습일은 2026년 10월 12일이다.

## 실행

```bash
cd week06/guestbook
cp .env.example .env
# .env에 사용할 Redis 비밀번호 입력
docker compose config -q
docker compose up -d --build --scale web=3
docker compose ps
```

저장소 루트에서 실행하는 명령이다. 기존 .env가 있다면 복사해서 덮어쓰지 않는다.
접속 주소는 http://localhost:8080 이다.

## 실습 1 - Redis와 볼륨

메모리에 저장하던 글을 Redis에 저장하도록 바꿨다.
웹에서 `REDIS_HOST=redis`를 사용해 Redis에 연결한다.

| 작업 | 글 개수 |
|---|---|
| 테스트 글 등록 | 3 |
| web 재시작 | 3개 유지 |
| down 후 up | 3개 유지 |
| down -v 후 up | 0개 |

`down`은 컨테이너와 네트워크를 지우지만 볼륨은 남긴다.
`down -v`는 볼륨까지 지워서 데이터도 사라진다. 이 비교는 실습용 볼륨으로 진행했다.

[down 후 결과](logs/12-after-down-up.json) / [down -v 후 결과](logs/15-after-down-v-up.json)

## 실습 2 - 네트워크

- Mac에서 `127.0.0.1:6379`에 연결하면 Connection refused가 나왔다.
- web 안에서는 `redis` 이름으로 IP를 찾고 TCP 연결에 성공했다.

Redis에 ports를 지정하지 않아 외부에서는 접근할 수 없지만, 같은 Compose 네트워크 안에서는 서비스 이름으로 연결할 수 있다.

[호스트 연결 결과](logs/lab2-02-host.txt) / [컨테이너 내부 연결 결과](logs/lab2-04-tcp.txt)

## 실습 3 - 설정 정리와 웹 확장

### .env

비밀번호를 compose.yaml에서 .env로 옮겼다.
.env는 실제 값이 들어가므로 Git에 올리지 않고, .env.example에는 작성 양식만 넣었다.
.gitignore는 Git에서 제외하고, .dockerignore는 이미지 안에 복사되지 않게 한다. 암호화하는 기능은 아니다.

### healthcheck

Redis와 web에 상태 확인을 추가했다.
단순 depends_on은 시작 순서만 정하므로, Redis가 healthy가 된 뒤 web을 시작하도록 바꿨다.
web은 `/readyz`로 Redis 연결 상태까지 확인한다.

### nginx와 scale

처음에는 web 3개가 모두 8080 포트를 쓰려고 해서 충돌했다.
nginx만 8080을 사용하고 web은 내부 5000 포트로 연결하도록 바꿨다.

```text
브라우저 :8080 → nginx → web 3개 → Redis 1개
```

세 웹은 같은 Redis를 사용해서 어느 웹으로 연결되어도 글 목록이 같았다.
web 하나를 직접 중지했을 때 자동으로 다시 켜지지는 않았다.
`docker compose up -d --scale web=3`으로 다시 3개를 실행했다.

### config와 watch

`docker compose config -q`로 설정 검사를 했다.
비밀번호를 빈 값으로 실행하면 필수 값 오류로 중단되는 것도 확인했다.

watch 설정은 app.py와 templates 변경 시 rebuild하도록 작성했다.
다만 Watch enabled가 표시된 뒤에도 문구 변경이 반영되지 않아 수동으로 다시 빌드했다.
자동 반영은 아직 성공 확인을 못 했다.

```bash
docker compose watch --no-up
```

## 실행 결과

10월 12일 기록이다. nginx 1개, web 3개, Redis 1개가 실행됐고 web과 Redis는 healthy였다.

```text
week07-lab1-nginx-1   Up       127.0.0.1:8080->80/tcp
week07-lab1-redis-1   healthy  6379/tcp
week07-lab1-web-1     healthy  5000/tcp
week07-lab1-web-2     healthy  5000/tcp
week07-lab1-web-3     healthy  5000/tcp
```

[원본 compose ps 출력](logs/self-study-ps.txt)

`/healthz`를 24번 요청했을 때 확인한 hostname은 아래와 같다.

- `2a151a9c02b7`
- `380696d68b1e`
- `ff8eef99ba3f`

[응답 기록](logs/self-study-hostnames.json)

호스트명 화면 캡처는 아직 추가하지 못했다.
메인 화면에는 hostname이 없으므로 http://localhost:8080/healthz 에서 확인할 수 있다.
나머지 명령어와 결과는 [logs](logs/)에 저장했다.
