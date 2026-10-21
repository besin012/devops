# 6주차 - Dockerfile

수업 방명록을 수정하고 Docker 이미지로 만들어 GHCR에 올렸다.
제목은 `지윤의 방명록`, 색은 파란색 `#0B5ED7`로 바꿨다.
안내 문구와 글 목록도 편지 형태로 수정했다.

![방명록 화면](images/guestbook-blue-complete.png)

## 빌드와 실행

[guestbook](guestbook/) 폴더에서 실행한다.

```bash
docker build -t guestbook:v2 .
docker run -d --name jiyun-guestbook \
  -p 127.0.0.1:8081:5000 guestbook:v2
curl http://localhost:8081/healthz
```

`status: ok` 응답을 확인했고, 브라우저에서 글 등록도 확인했다.
같은 이름의 컨테이너가 이미 있으면 `docker run`을 다시 실행할 수 없으므로 먼저 상태를 확인한다.

## Dockerfile 정리

| 명령 | 역할 |
|---|---|
| FROM | Python 기반 이미지 선택 |
| WORKDIR | 작업 폴더를 /app으로 지정 |
| COPY requirements.txt | 라이브러리 목록을 먼저 복사 |
| RUN pip install | 빌드할 때 라이브러리 설치 |
| COPY . . | 앱 코드와 HTML 복사 |
| RUN useradd / USER | 일반 사용자로 실행하도록 설정 |
| ENV | 제목과 색상 기본값 설정 |
| EXPOSE | 사용할 포트를 표시. 실제 연결은 -p 필요 |
| CMD | 컨테이너 시작 시 앱 실행 |

RUN은 빌드할 때, CMD는 컨테이너를 실행할 때 동작한다.
`--no-cache-dir`은 pip 캐시 옵션이고 Docker 레이어 캐시와는 다르다.

## 캐시 비교

```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

이 순서에서는 HTML만 수정했을 때 pip 설치 단계가 `CACHED`로 재사용됐다.
반대로 `COPY . .`을 먼저 하면 코드가 바뀔 때 pip도 다시 실행됐다.
비교용 수정은 임시 폴더에서 진행해 방명록 원본은 유지했다.

![캐시 확인](images/cache-log.png)

[좋은 순서 로그](logs/25-code-change.txt) / [나쁜 순서 로그](logs/26-bad-after.txt)

## GHCR 업로드

```bash
docker tag guestbook:v2 ghcr.io/besin012/guestbook:v2
docker push ghcr.io/besin012/guestbook:v2
```

이미지 주소: `ghcr.io/besin012/guestbook:v2`

[GitHub Packages](https://github.com/users/besin012/packages/container/package/guestbook)에서 v2를 확인했다.
10월 7일 업로드했고, 10월 11일 Public으로 바꾼 뒤 인증 없이 pull/run 되는지 확인했다.

![GHCR](images/registry-public.png)

[다운로드 결과](logs/38-public-pull.txt) / [실행 확인](logs/38-public-health.txt)

## 추가로 확인한 내용

- 설정 우선순위는 `코드 기본값 < Dockerfile ENV < docker run -e`이다.
- 교안 GHCR 예제는 manifest 오류가 나서 교안의 Docker Hub 예제로 대체했다. 친구 이미지 주소는 없어 실제 친구 이미지 교환은 하지 않았다.
- 게시한 이미지는 arm64용이다. 멀티 아키텍처 푸시는 하지 않았다.
- 멀티스테이지 비교에서는 일반 이미지 227MB, 멀티스테이지 이미지 224MB였다. [비교 로그](logs/46-size.txt)
- 메모리 모드에서 글을 등록하고 재시작하니 글이 사라졌다. 다음 주에 Redis를 연결해 비교했다.

나머지 실행 결과는 [logs](logs/), 캡처는 [images](images/)에 있다.
