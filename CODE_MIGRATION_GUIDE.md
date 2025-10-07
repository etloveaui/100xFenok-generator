# 환경 변수 기반 보안 시스템 마이그레이션 가이드

## 개요

하드코딩된 크레덴셜을 환경 변수 기반 시스템으로 마이그레이션하는 가이드입니다.

---

## 1. main_generator.py 마이그레이션

### 변경 전 (Line 23-67)
```python
# secrets 파일 경로: projects/100xFenok-generator/secret/
self.secrets_file = os.path.join(self.project_dir, 'secret', 'my_sensitive_data.md')

def _load_credentials(self):
    """secrets/my_sensitive_data.md에서 TerminalX 로그인 자격 증명을 로드합니다."""
    try:
        with open(self.secrets_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 정규 표현식 등을 사용하여 사용자 이름과 비밀번호를 파싱해야 합니다.
            if "The TerminalX Credentials" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "The TerminalX Credentials" in line:
                        self.terminalx_username = lines[i+1].split(':')[-1].strip().replace('`', '').replace('**', '')
                        self.terminalx_password = lines[i+2].split(':')[-1].strip().replace('`', '').replace('**', '')
                        break
        if not self.terminalx_username or not self.terminalx_password:
            raise ValueError("TerminalX 자격 증명을 찾을 수 없습니다.")
        print("TerminalX 자격 증명 로드 완료.")
    except FileNotFoundError:
        print(f"오류: {self.secrets_file} 파일을 찾을 수 없습니다.")
        exit()
    except Exception as e:
        print(f"자격 증명 로드 중 오류 발생: {e}")
        exit()
```

### 변경 후
```python
# secure_config 임포트 추가 (파일 상단에)
from secure_config import get_terminalx_credentials

class FenokReportGenerator:
    def __init__(self):
        # 1. 경로 표준화
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.abspath(os.path.join(self.project_dir, '..', '..'))

        # ❌ 제거: self.secrets_file 관련 모든 코드
        # self.secrets_file = os.path.join(self.project_dir, 'secret', 'my_sensitive_data.md')

        self.generated_html_dir = os.path.join(self.project_dir, 'generated_html')
        # ... 기타 경로들 ...

        self.driver = None
        self.terminalx_username = None
        self.terminalx_password = None

        self._load_credentials()
        self._setup_webdriver()
        self._create_directories()

    def _load_credentials(self):
        """환경 변수에서 TerminalX 로그인 자격 증명을 로드합니다."""
        try:
            self.terminalx_username, self.terminalx_password = get_terminalx_credentials()
            print("✅ TerminalX 자격 증명 로드 완료 (from environment variables).")
        except ValueError as e:
            print(f"❌ 오류: {e}")
            print("\n해결 방법:")
            print("1. .env.example을 .env로 복사")
            print("2. .env 파일에 TERMINALX_EMAIL과 TERMINALX_PASSWORD 설정")
            print("3. pip install python-dotenv 실행")
            exit(1)
        except Exception as e:
            print(f"❌ 자격 증명 로드 중 예상치 못한 오류 발생: {e}")
            exit(1)
```

---

## 2. 기타 스크립트 마이그레이션

### 패턴 1: 직접 하드코딩된 경우
```python
# 변경 전
email = "meanstomakemewealthy@naver.com"
password = "!00baggers"

# 변경 후
from secure_config import get_terminalx_credentials
email, password = get_terminalx_credentials()
```

### 패턴 2: API 키 사용
```python
# 변경 전
openai_api_key = "sk-xxxxxxxxxxxxx"

# 변경 후
from secure_config import get_config
config = get_config()
openai_api_key = config.openai_api_key
```

### 패턴 3: 선택적 API 키
```python
# 변경 후 (API 키가 없어도 괜찮은 경우)
from secure_config import get_api_key

api_key = get_api_key('openai')  # 없으면 빈 문자열 반환
if api_key:
    # API 사용
else:
    print("⚠️  OpenAI API 키가 설정되지 않았습니다.")
```

---

## 3. 마이그레이션 체크리스트

### 사전 준비
- [ ] `install_security_dependencies.bat` 실행 (python-dotenv 설치)
- [ ] `.env.example`을 `.env`로 복사
- [ ] `.env` 파일에 새로운 크레덴셜 입력
- [ ] `python secure_config.py` 실행하여 설정 테스트

### 코드 마이그레이션
- [ ] `main_generator.py` 수정
- [ ] 기타 `.py` 파일에서 하드코딩된 크레덴셜 검색
  ```bash
  findstr /s /i "meanstomakemewealthy" *.py
  findstr /s /i "!00baggers" *.py
  findstr /s /i "sk-" *.py
  ```
- [ ] 검색된 모든 파일 마이그레이션

### 테스트
- [ ] 각 스크립트 개별 테스트
- [ ] 전체 워크플로우 테스트
- [ ] 에러 핸들링 테스트 (.env 없을 때)

### 정리
- [ ] `secret/` 디렉토리 삭제
- [ ] `my_sensitive_data.md` 로컬 파일 삭제
- [ ] Git 히스토리 정리 (`emergency_security_cleanup.bat`)
- [ ] 원격 저장소 강제 푸시

---

## 4. 주의사항

### ✅ 해야 할 것
- 환경 변수 사용
- `.env` 파일을 `.gitignore`에 포함 (이미 완료)
- 새 크레덴셜로 교체 후 마이그레이션
- 에러 핸들링 추가

### ❌ 하지 말아야 할 것
- `.env` 파일을 Git에 커밋
- 하드코딩된 크레덴셜 남기기
- 구 크레덴셜 재사용 (이미 노출됨)
- `secret/` 디렉토리 재생성

---

## 5. 트러블슈팅

### 문제: "Required environment variable 'TERMINALX_EMAIL' not found"
```bash
# 해결:
# 1. .env 파일이 프로젝트 루트에 있는지 확인
# 2. .env 파일에 TERMINALX_EMAIL=... 줄이 있는지 확인
# 3. 줄 끝에 불필요한 공백이나 따옴표가 없는지 확인
```

### 문제: "ModuleNotFoundError: No module named 'dotenv'"
```bash
# 해결:
pip install python-dotenv
```

### 문제: secure_config.py에서 .env 파일을 찾지 못함
```bash
# 해결:
# .env 파일이 프로젝트 루트에 있는지 확인:
# C:\Users\etlov\agents-workspace\projects\100xFenok-generator\.env
```

---

## 6. 예시: 전체 워크플로우

```bash
# 1. 종속성 설치
install_security_dependencies.bat

# 2. 환경 변수 설정
copy .env.example .env
notepad .env  # 새 크레덴셜 입력

# 3. 설정 테스트
python secure_config.py

# 4. 코드 마이그레이션 (main_generator.py 수정)
# ... (위 가이드 참조)

# 5. 테스트
python main_generator.py

# 6. 정리
emergency_security_cleanup.bat

# 7. 원격 푸시
git push origin --force --all
```

---

**작성일**: 2025-10-07
**버전**: 1.0
