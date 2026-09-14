# Week03 셸 스크립팅

## 실습 내용
- 셸 스크립트 작성과 실행 권한 설정
- export로 환경 변수 전달
- 웹 서버 포트를 8080으로 변경
- 조건문으로 Python3 설치 여부 확인

## 주요 명령어
- chmod u+x start.sh: 실행 권한 부여
- export WEB_PORT="8080": 포트 번호 설정
- command -v python3: Python3 명령어 확인

## 실행 방법
qwen-web 폴더에서 다음 명령을 실행한다.

    ./start_with_export_2.sh

브라우저에서 http://localhost:8080으로 접속한다.
종료하려면 Ctrl+C를 누른다.

## 배운 점
실행 권한이 없으면 permission denied 오류가 발생한다.
환경 변수는 export를 사용해 실행할 프로그램에 전달한다.
if 조건문으로 프로그램 실행 전에 필요한 조건을 검사할 수 있다.
