# 지윤의 방명록

수업에서 받은 Flask 방명록을 바탕으로 제목, 파란색 테마, 안내 문구와 레이아웃을 수정했다.
이름과 메시지를 입력하면 글 목록에 표시된다.

## Compose로 실행

이 폴더에서 실행한다. .env가 없는 경우 .env.example을 복사해 비밀번호를 입력한다.

```bash
cp .env.example .env
docker compose config -q
docker compose up -d --build --scale web=3
```

http://localhost:8080 으로 접속한다. nginx, 웹 3개, Redis가 실행된다.
기존 .env는 덮어쓰지 않는다. .env는 Git에 올리지 않는다.

```bash
docker compose ps
docker compose logs web
docker compose down
```

`down`은 볼륨을 남긴다. `down -v`는 Redis 데이터도 지우므로 주의한다.

## 단독 실행

```bash
docker build -t guestbook:v2 .
docker run -d --name jiyun-guestbook \
  -p 127.0.0.1:8081:5000 guestbook:v2
```

Redis 설정이 없으면 메모리에 저장하며 재시작 시 글이 사라진다.
Redis를 사용하는 경우에도 데이터 유지 여부는 Redis 설정과 볼륨에 달려 있다.

이미지: `ghcr.io/besin012/guestbook:v2`

## 주요 파일

- app.py: 글 등록, 목록 조회, Redis 연결
- templates/index.html: 방명록 화면
- Dockerfile: 이미지 빌드
- compose.yaml: nginx, web, Redis 구성
- nginx.conf: 웹 요청 전달
- .env.example: 로컬 설정 양식

`/healthz`는 앱 응답을 확인하고, `/readyz`는 Redis 연결까지 확인한다.
현재 메인 화면에는 hostname이 표시되지 않아 `/healthz`로 확인한다.

실습 결과: [6주차](../README.md), [7주차](../../week07/README.md)
