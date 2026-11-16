# 12주차 GitHub Actions

- 기존 방명록에 린트 검사와 `/healthz`, 글 등록·조회 테스트를 추가했다. PR에서는 검사와 이미지 빌드까지 실행하고, main에서는 성공하면 GHCR에 게시한다. [첫 PR 검사](https://github.com/besin012/devops/actions/runs/43850101043)
- 문법 오류와 변수 오타는 린트에서 잡혔다. `/healthz`가 500을 반환했을 때는 린트를 통과하고 테스트에서 실패했다. [문법 오류](https://github.com/besin012/devops/actions/runs/43850185862) · [변수 오타](https://github.com/besin012/devops/actions/runs/43850256343) · [응답 코드 오류](https://github.com/besin012/devops/actions/runs/43850347116)
- main에는 PR과 `build` 통과를 필수로 설정했다. [검사 실패로 머지가 막힌 PR](https://github.com/besin012/devops/pull/6)에서 오류를 고친 뒤 다시 검사했다.
- 기존 GHCR 패키지에서 쓰기 권한 오류가 나서 `guestbook-week12`에 amd64·arm64 이미지를 게시했다. 태그는 `0d13b25`와 `latest`다. [게시 로그](https://github.com/besin012/devops/actions/runs/43850806568)
- 게시한 커밋 태그로 kind의 방명록 Deployment 이미지를 바꾸고, `rollout status`, `/healthz`, 페이지 제목을 확인하는 실습을 진행했다. [쿠버네티스 실행 로그](https://github.com/besin012/devops/actions/runs/43851042480)
