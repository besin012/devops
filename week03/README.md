# 3주차 - 셸 스크립트

실행할 때마다 입력하던 명령어를 스크립트로 묶는 내용을 정리했다.
실습 코드는 [qwen-web](qwen-web/)에 있다.

## 앱 구조

브라우저 → chat.py → Ollama → Qwen 순서로 요청이 전달된다.
웹 앱의 포트와 Ollama의 포트는 다르다. 웹 포트를 8080으로 바꿔도 Ollama는 11434를 사용한다.

## start.sh

```bash
#!/bin/bash
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python3를 먼저 설치하세요." >&2
    exit 1
fi

exec python3 chat.py
```

- `#!/bin/bash`: Bash로 실행한다.
- `cd "$(dirname "$0")"`: 스크립트가 있는 폴더로 이동한다. 다른 위치에서 실행해도 chat.py를 찾을 수 있다.
- `|| exit 1`: 폴더 이동에 실패하면 종료한다.
- `command -v python3`: Python3 명령어가 있는지 확인한다. 앞의 `!`는 조건을 반대로 바꾼다.
- `>/dev/null 2>&1`: 검사 결과 출력은 숨기고 성공 여부만 사용한다.
- `exec`: 셸을 Python 프로세스로 바꾼다. 성공하면 뒤에 적힌 셸 명령은 실행되지 않는다.

## 실행 권한

```bash
chmod u+x start.sh
./start.sh
```

`u+x`는 파일 소유자에게 실행 권한을 주는 뜻이다.
현재 폴더에 있는 파일은 `start.sh`가 아니라 `./start.sh`처럼 경로를 적어 실행한다.

## 환경 변수

```bash
export MODEL="qwen3:0.6b"
export WEB_PORT="8080"
```

`export`로 설정하면 이후 실행하는 프로그램에 값이 전달된다.
변수 대입은 `=` 양옆에 공백을 넣지 않는다. 앱에서도 해당 환경 변수를 읽어야 적용된다.
스크립트 안에서 설정한 값이 원래 터미널의 설정까지 바꾸지는 않는다.

```bash
cd qwen-web
chmod u+x start.sh start_with_export_2.sh
./start_with_export_2.sh
```

## 헷갈렸던 문법

| 문법 | 뜻 |
|---|---|
| `$0` | 실행한 스크립트 경로 |
| `$1`, `$2` | 첫 번째, 두 번째 인자 |
| `$#` | 인자 개수 |
| `"$@"` | 모든 인자를 각각 유지해서 전달 |
| `$?` | 직전 명령의 종료 상태. 0이면 성공 |
| `>&2` | 표준 오류로 출력 |
| `exit 1` | 실패 상태로 종료 |

`echo ... >&2`는 오류 메시지를 출력하는 것이고, 실행을 끝내려면 `exit`가 따로 필요하다.

여러 줄을 파일에 넣을 때는 heredoc을 사용한다.

```bash
cat > example.sh << 'EOF_SCRIPT'
#!/bin/bash
echo "$1"
EOF_SCRIPT
```

끝 표시를 따옴표로 감싸면 파일을 만드는 시점에 `$1`이 바뀌지 않고 그대로 저장된다.
끝 표시는 공백 없이 단독 줄에 적는다.

## 오류 확인

- permission denied: 실행 권한 확인 후 `chmod u+x`.
- command not found: 현재 파일이면 `./`를 붙였는지 확인.
- `cd..`: `cd ..`처럼 공백이 필요하다.
- Ollama 연결 실패: Ollama 실행 상태와 `ollama list` 확인.
- 웹 앱에서 Ctrl+C: 웹 앱은 종료되지만 별도로 실행한 Ollama 서버까지 종료되지는 않는다.
