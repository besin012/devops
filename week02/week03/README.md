# Week03

> 학습 목표: 반복하는 실행 명령을 스크립트로 만들고, 경로·권한·환경 변수·조건문으로 실행 과정을 자동화한다.

## 1. 실습 서비스의 전체 구조

```text
웹 브라우저
    ↓ 질문 전송
Python 웹 앱(chat.py) — 포트 8000 또는 8080
    ↓ API 요청
Ollama 서버 — 포트 11434
    ↓ 모델 실행
Qwen 모델
    ↓ 생성한 답변이 웹 앱을 거쳐 브라우저에 표시됨
```

| 구성 요소 | 역할 |
| --- | --- |
| Qwen | 질문에 대한 답변을 생성하는 AI 모델 |
| Ollama | 로컬에서 모델을 관리하고 실행하는 도구와 서버 |
| chat.py | 브라우저에서 받은 질문을 Ollama에 전달하는 Python 웹 앱 |
| start.sh | 경로와 실행 조건을 확인하고 웹 앱을 시작하는 스크립트 |

- `localhost`는 현재 사용하는 내 컴퓨터를 가리킨다.
- 포트 번호는 같은 컴퓨터에서 서로 다른 서비스를 구분한다.
- 웹 앱의 포트를 `8080`으로 바꿔도 Ollama의 포트 `11434`는 그대로다.
- 웹 앱 실행 중 `Ctrl+C`를 누르면 웹 앱이 종료된다. 별도로 실행된 Ollama 서버까지 종료되는 것은 아니다.
- 모델 파일은 Ollama가 별도로 관리하므로 GitHub에 올릴 필요가 없다.

## 2. 왜 셸 스크립트를 사용하는가?

셸 스크립트는 터미널에서 실행할 명령을 파일에 순서대로 적은 것이다.

매번 폴더 이동, 환경 설정, 프로그램 실행을 직접 입력하면 누락이나 오타가 생길 수 있다. 스크립트로 묶으면 같은 절차를 반복하기 쉽다.

```bash
./start.sh
```

이 한 줄로 스크립트에 작성한 준비 작업과 프로그램 실행을 수행한다.

## 3. 기본 start.sh 해석

```bash
#!/bin/bash
cd "$(dirname "$0")" || exit 1
exec python3 chat.py
```

### ① `#!/bin/bash` — 실행할 인터프리터 지정

첫 줄의 `#!`를 shebang(셔뱅)이라고 한다.

`#!/bin/bash`는 이 파일을 Bash로 해석하라는 뜻이다. Mac 터미널에서 zsh를 사용하더라도 `./start.sh`로 실행하면 이 셔뱅에 따라 Bash가 사용된다.

파일 확장자만으로 실행 언어가 결정되는 것은 아니다. 수업의 `run_py.sh`처럼 `.sh` 파일에도 Python 셔뱅과 Python 코드를 넣을 수 있다.

```python
#!/usr/bin/env python3
print("Hello, DevOps!")
```

`/usr/bin/env python3`는 `PATH`에서 Python3를 찾아 실행한다.

### ② `cd "$(dirname "$0")" || exit 1` — 작업 위치 고정

| 문법 | 의미 |
| --- | --- |
| `$0` | 실행한 스크립트의 이름 또는 경로 |
| `dirname "$0"` | 그 경로에서 디렉터리 부분 추출 |
| `$(명령어)` | 명령어의 표준 출력을 해당 자리에 넣는 명령어 치환 |
| `"..."` | 경로에 공백이 있어도 하나의 인자로 전달 |
| `cd` | 해당 디렉터리로 이동 |
| `A || B` | A가 실패했을 때 B 실행 |
| `exit 1` | 실패 상태로 스크립트 종료 |

전체 의미:

> 스크립트가 있는 폴더로 이동하고, 이동하지 못하면 실행을 중단한다.

이 처리가 있어야 다른 폴더에서 스크립트를 실행하더라도 같은 폴더에 있는 `chat.py`를 찾을 수 있다.

### ③ `exec python3 chat.py` — Python으로 프로세스 교체

`exec`는 현재 스크립트를 실행 중인 셸 프로세스를 Python 프로세스로 교체한다.

```bash
exec python3 chat.py
echo "End"
```

`exec`가 성공하면 아래의 `echo "End"`는 실행되지 않는다. Python이 끝난 뒤 돌아와서 나머지 줄을 실행할 셸이 없기 때문이다.

## 4. 실행 권한과 경로

```bash
chmod u+x start.sh
./start.sh
```

| 표현 | 의미 |
| --- | --- |
| `chmod` | 파일 권한 변경 |
| `u` | 파일 소유자 |
| `+x` | 실행 권한 추가 |
| `./` | 현재 디렉터리 |
| `ls -l` | 파일별 권한과 상세 정보 확인 |

실행 권한은 파일마다 따로 설정한다. `run_py.sh`에 권한을 줬다고 `start.sh`에도 적용되는 것은 아니다.

`start.sh`만 입력하면 셸은 보통 `PATH`에 등록된 폴더에서 명령어를 찾는다. 현재 폴더의 파일을 실행하려면 `./start.sh`처럼 경로를 지정한다.

## 5. 환경 변수로 실행 설정 전달하기

```bash
export MODEL="qwen3:0.6b"
```

`export`는 변수를 이후 실행할 프로그램이 물려받을 수 있도록 환경 변수로 설정한다.

- `MODEL`: 사용할 모델을 지정하는 설정
- `WEB_PORT`: 웹 앱의 포트를 지정하는 설정
- 변수 대입 시 `=` 양옆에 공백을 넣지 않는다.
- 환경 변수가 실제로 작동하려면 프로그램이 해당 변수를 읽도록 작성되어 있어야 한다.

### 모델을 지정하는 start_with_export.sh

```bash
#!/bin/bash
cd "$(dirname "$0")" || exit 1

export MODEL="qwen3:0.6b"
exec ./start.sh
```

환경 변수는 다음 실행 흐름으로 전달된다.

```text
start_with_export.sh
    → start.sh
    → python3 chat.py
```

`./start_with_export.sh`로 실행한 스크립트 안의 설정이 원래 터미널의 환경 변수까지 바꾸지는 않는다.

### 포트를 변경하는 start_with_export_2.sh — 46페이지

```bash
#!/bin/bash
cd "$(dirname "$0")" || exit 1

export WEB_PORT="8080"
exec ./start.sh
```

실행:

```bash
chmod u+x start.sh start_with_export_2.sh
./start_with_export_2.sh
```

브라우저 접속 주소:

```text
http://localhost:8080
```

이 파일은 포트만 지정한다. 모델도 함께 고정하려면 `exec` 위에 다음 줄을 추가한다.

```bash
export MODEL="qwen3:0.6b"
```

## 6. heredoc으로 여러 줄을 파일에 저장하기

터미널에서 다음 전체를 입력하면 파일이 만들어진다.

```bash
cat > start_with_export_2.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")" || exit 1
export WEB_PORT="8080"
exec ./start.sh
EOF
```

| 문법 | 의미 |
| --- | --- |
| `cat` | 입력받은 내용을 출력 |
| `> 파일명` | 출력을 파일에 저장. 기존 내용이 있으면 덮어씀 |
| `<< 'EOF'` | 종료 표시가 나올 때까지 여러 줄을 입력받음 |
| 마지막 `EOF` | 입력 종료 표시. 파일 내용에는 포함되지 않음 |

### `'EOF'`에 따옴표를 쓰는 이유

따옴표를 쓰면 파일을 만드는 순간에 `$MODEL`, `$0`, `$(...)` 등이 해석되지 않고 그대로 저장된다. 저장된 스크립트를 실행할 때 해석되도록 하기 위해서다.

마지막 `EOF`는 앞뒤 공백 없이 단독 줄에 입력한다. 끝 표시를 입력하지 않으면 셸은 계속 다음 입력을 기다린다.

교재의 줄 앞에 있는 `$`, `%`, `>`는 프롬프트 표시이므로 그대로 입력하지 않는다.

## 7. Python3를 확인하는 조건문 — 48페이지

최종 `start.sh`:

```bash
#!/bin/bash
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python3를 먼저 설치하세요." >&2
    exit 1
fi

exec python3 chat.py
```

실행 흐름:

```text
스크립트 폴더로 이동
    ↓
Python3 명령어를 찾을 수 있는가?
    ├─ 예 → chat.py 실행
    └─ 아니요 → 설치 안내 출력 → 실패 상태로 종료
```

### 조건문 문법

```bash
if 명령어; then
    명령어가 성공했을 때 실행할 내용
fi
```

셸의 `if`는 명령어의 종료 상태를 기준으로 판단한다.

| 종료 상태 | 의미 |
| --- | --- |
| `0` | 성공 |
| `0 이외` | 실패 |

`!`는 결과를 반대로 바꾼다.

```bash
if ! command -v python3; then
```

따라서 위 조건은 “Python3 명령어를 찾을 수 없다면”이라는 의미다. Python3가 있으면 설치 안내 없이 웹 앱을 실행하는 것이 정상이다.

## 8. 표준 출력, 표준 오류, 종료 상태

| 번호 | 이름 | 용도 |
| --- | --- | --- |
| `0` | 표준 입력, stdin | 프로그램이 받는 입력 |
| `1` | 표준 출력, stdout | 일반적인 실행 결과 |
| `2` | 표준 오류, stderr | 오류나 진단 메시지 |

### `>/dev/null 2>&1`

1. `>/dev/null`: 표준 출력을 버린다.
2. `2>&1`: 표준 오류도 표준 출력과 같은 곳으로 보낸다.

검사 결과의 성공·실패만 필요하므로 출력은 숨기는 것이다. 출력을 숨겨도 종료 상태는 확인할 수 있다.

리다이렉션은 왼쪽부터 적용하므로 순서가 중요하다. `2>&1 >/dev/null`은 같은 의미가 아니다.

### `echo "..." >&2`와 `exit 1`의 차이

```bash
echo "Python3를 먼저 설치하세요." >&2
exit 1
```

- `>&2`: 메시지를 표준 오류로 출력한다.
- `exit 1`: 스크립트를 실패 상태로 종료한다.

오류 메시지를 출력하는 것만으로 스크립트가 자동으로 실패 종료되지는 않는다.

## 9. 특수 변수 복습

다음과 같이 실행했다고 가정한다.

```bash
./command.sh qwen3:0.6b 8000
```

| 변수 | 값 또는 의미 |
| --- | --- |
| `$0` | `./command.sh` |
| `$1` | `qwen3:0.6b` |
| `$2` | `8000` |
| `$#` | 전달받은 인자 개수, 여기서는 `2` |
| `"$@"` | 전달받은 모든 인자를 각각 유지하여 전달 |
| `$?` | 직전 명령어의 종료 상태 |

종료 상태 확인:

```bash
command -v python3
echo $?
```

`$?`는 직전 명령의 결과이므로 확인하고 싶은 명령 바로 다음에 출력한다.

## 10. 다시 실행할 때의 순서

저장소의 `devops` 폴더에서 시작한다.

```bash
cd week03/qwen-web

# 현재 위치와 파일 확인
pwd
ls

# Ollama 응답과 설치된 모델 확인
curl -fsS http://127.0.0.1:11434/api/tags
ollama list

# 실행 권한 설정
chmod u+x start.sh start_with_export.sh start_with_export_2.sh

# 8080 포트로 실행
./start_with_export_2.sh
```

Ollama가 응답하지 않으면 Mac에서 Ollama 앱을 실행한다.

```bash
open -a Ollama
```

사용할 모델이 없다면 다운로드한다.

```bash
ollama pull qwen3:0.6b
```

웹 앱 실행 후 브라우저에서 `http://localhost:8080`으로 접속한다. 종료는 서버가 실행 중인 터미널에서 `Ctrl+C`를 누른다.

## 11. 실습 중 겪은 오류와 해결

| 증상 | 원인 및 해결 |
| --- | --- |
| `permission denied: ./start.sh` | 실행 권한 확인 후 `chmod u+x start.sh` 실행 |
| `command not found: start.sh` | 현재 폴더의 파일이라면 `./start.sh`로 실행 |
| `command not found: cd..` | `cd ..`처럼 명령어와 인자 사이에 공백 필요 |
| heredoc 입력이 끝나지 않음 | 종료 표시 `EOF`를 단독 줄에 입력 |
| 8080으로 변경했는데 접속되지 않음 | 터미널의 실행 오류와 안내 주소를 확인하고 8080으로 접속 |
| 모델 설정이 예상과 다름 | 실행한 스크립트에 `export MODEL=...`이 있는지 확인 |
| `not a git repository` | 현재 폴더 또는 상위 폴더에 Git 저장소 설정이 없음 |

### GitHub에 복습 글 수정 사항 올리기

기존 저장소 이력 연결을 완료한 후, `devops` 폴더에서 실행한다.

```bash
git status
git add week03/README.md
git diff --cached --stat
git commit -m "week03 셸 스크립팅 복습 정리"
git push
```

`git add`는 올릴 변경을 선택하고, `git commit`은 로컬 이력에 저장하며, `git push`는 GitHub로 전송한다.

이번 저장소의 기본 브랜치 이름은 `hi`다. `main`이 흔하지만 브랜치 이름이 반드시 `main`이어야 하는 것은 아니다.

## 12. 스스로 설명해 볼 복습 문제

1. `start.sh` 대신 `./start.sh`로 실행하는 이유는?
2. `chmod u+x`에서 `u`와 `x`는 각각 무엇인가?
3. `cd "$(dirname "$0")"`가 없으면 어떤 문제가 생길 수 있는가?
4. `|| exit 1`은 언제 실행되는가?
5. `exec`가 성공한 뒤 다음 줄이 실행되지 않는 이유는?
6. `export WEB_PORT="8080"`은 어떤 프로그램에 전달되는가?
7. heredoc의 `'EOF'`에 따옴표를 붙이는 이유는?
8. `if ! command -v python3`는 어떤 조건을 검사하는가?
9. 오류 출력과 실패 종료는 어떻게 다른가?
10. 웹 앱을 `Ctrl+C`로 종료하면 Ollama 서버도 종료되는가?

<details>
<summary>정답 확인</summary>

1. 현재 폴더의 파일을 경로로 직접 지정하기 위해서다.
2. `u`는 소유자, `x`는 실행 권한이다.
3. 실행 위치에 따라 상대 경로의 `chat.py`를 찾지 못할 수 있다.
4. 앞의 `cd` 명령이 실패했을 때 실행된다.
5. 셸 프로세스가 실행한 프로그램으로 교체되기 때문이다.
6. 해당 환경을 물려받는 `start.sh`와 그 안에서 실행하는 Python 앱에 전달된다.
7. 파일 생성 시 변수와 명령어 치환을 막고 코드를 그대로 저장하기 위해서다.
8. Python3 명령어를 찾을 수 없는지를 검사한다.
9. `>&2`는 출력 대상 지정이고, `exit 1`은 실패 상태로 실행을 종료하는 것이다.
10. 아니다. 별도로 실행 중인 Ollama 서버는 계속 동작한다.

</details>
