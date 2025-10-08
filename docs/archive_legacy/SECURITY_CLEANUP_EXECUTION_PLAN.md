# 🚨 보안 정리 실행 계획 - 즉시 실행 가이드

**긴급도**: 🔴 **CRITICAL**
**예상 소요 시간**: 1-2시간
**실행 위치**: `C:\Users\etlov\agents-workspace\projects\100xFenok-generator`

---

## 📋 실행 순서 (반드시 이 순서대로!)

### ✅ PHASE 0: 크레덴셜 무효화 (최우선!)

**⏱️ 소요 시간**: 30분
**❌ 이 단계를 건너뛰면 안 됩니다!**

#### Step 0.1: TerminalX 비밀번호 변경
```
1. https://terminalx.com 접속
2. 로그인: meanstomakemewealthy@naver.com / !00baggers
3. Settings → Security → Change Password
4. 새 비밀번호 설정 (강력한 비밀번호 사용!)
5. 새 비밀번호를 안전한 곳에 기록
```

#### Step 0.2: API 키 무효화
```
OpenAI (platform.openai.com):
1. API Keys 섹션
2. 기존 키 "Revoke" 클릭
3. "Create new secret key" 클릭
4. 새 키를 안전한 곳에 기록

Anthropic (console.anthropic.com):
1. API Keys 섹션
2. 기존 키 삭제
3. 새 키 생성
4. 새 키를 안전한 곳에 기록

Google Cloud (console.cloud.google.com):
1. APIs & Services → Credentials
2. 기존 API 키 삭제
3. "CREATE CREDENTIALS" → API Key
4. 새 키를 안전한 곳에 기록
```

#### Step 0.3: GitHub 리포지토리 보안 조치
```
1. https://github.com/etloveaui/100xFenok-generator 접속
2. Settings → General → Danger Zone
3. "Change repository visibility" → Private 선택
   OR
   "Delete this repository" 고려 (완전 삭제 후 재생성)
```

**🔴 체크포인트**: 위 모든 단계를 완료했습니까?
- [ ] TerminalX 비밀번호 변경 완료
- [ ] OpenAI API 키 회전 완료
- [ ] Anthropic API 키 회전 완료
- [ ] Google API 키 회전 완료
- [ ] GitHub 리포지토리 Private 변경 완료

---

### ✅ PHASE 1: 종속성 설치

**⏱️ 소요 시간**: 5분

```cmd
cd "C:\Users\etlov\agents-workspace\projects\100xFenok-generator"
install_security_dependencies.bat
```

**예상 출력**:
```
[1/2] python-dotenv 설치 중...
✅ python-dotenv 설치 완료

[2/2] (선택사항) git-filter-repo 설치 중...
✅ git-filter-repo 설치 완료 (또는 실패해도 괜찮음)
```

---

### ✅ PHASE 2: 환경 변수 설정

**⏱️ 소요 시간**: 5분

#### Step 2.1: .env 파일 생성
```cmd
copy .env.example .env
notepad .env
```

#### Step 2.2: .env 파일 편집 (메모장에서)
```env
# ============================================================
# Environment Variables
# ============================================================

# TerminalX Credentials (새 비밀번호 사용!)
TERMINALX_EMAIL=meanstomakemewealthy@naver.com
TERMINALX_PASSWORD=새로_변경한_비밀번호_입력

# OpenAI API (새 키 사용!)
OPENAI_API_KEY=sk-새로_발급받은_키_입력

# Anthropic API (새 키 사용!)
ANTHROPIC_API_KEY=sk-ant-새로_발급받은_키_입력

# Google API (새 키 사용!)
GOOGLE_API_KEY=새로_발급받은_키_입력
```

**저장**: Ctrl+S → 메모장 닫기

#### Step 2.3: 설정 테스트
```cmd
python secure_config.py
```

**예상 출력**:
```
✅ Loaded environment variables from: C:\Users\...\100xFenok-generator\.env
✅ Configuration loaded successfully

TerminalX Email: meant***@naver.com
TerminalX Password: ************
✅ Openai API Key: sk-xxx...xxxx
✅ Anthropic API Key: sk-ant...xxxx
✅ Google API Key: AIza...xxxx
```

**❌ 에러 발생 시**:
- `.env` 파일이 프로젝트 루트에 있는지 확인
- 환경 변수 이름이 정확한지 확인 (대소문자 구분)
- 줄 끝에 불필요한 공백 제거

---

### ✅ PHASE 3: Git 히스토리 정리

**⏱️ 소요 시간**: 10-20분 (리포지토리 크기에 따라)

#### Step 3.1: 정리 스크립트 실행
```cmd
emergency_security_cleanup.bat
```

**예상 출력**:
```
[1/6] 백업 생성 중...
✅ 백업 완료: backup_before_cleanup.bundle

[2/6] 민감한 파일 Git 히스토리에서 완전 제거 중...
✅ 히스토리 정리 완료

[3/6] 로컬 참조 정리 중...
✅ 로컬 정리 완료

[4/6] .gitignore 업데이트 중...
✅ .gitignore 업데이트 완료

[5/6] 로컬 민감 파일 삭제 중...
✅ 로컬 파일 정리 완료

[6/6] 변경사항 커밋 중...
✅ 커밋 완료

============================================================
✅ 로컬 정리 완료!
============================================================
```

**🔴 중요**: 이 시점에서 Git 히스토리가 재작성되었습니다!

#### Step 3.2: 백업 확인
```cmd
dir backup_before_cleanup.bundle
```

백업 파일이 존재하는지 확인하세요. 문제 발생 시 복구 가능합니다.

---

### ✅ PHASE 4: 원격 저장소 강제 푸시

**⏱️ 소요 시간**: 5분

**⚠️  WARNING**: 이 작업은 Git 히스토리를 영구적으로 변경합니다!

```cmd
git push origin --force --all
git push origin --force --tags
```

**예상 출력**:
```
Enumerating objects: ...
Counting objects: 100% (...), done.
...
+ d0ffb91...abc1234 main -> main (forced update)
```

**✅ 성공 신호**: "forced update" 메시지

---

### ✅ PHASE 5: 코드 마이그레이션

**⏱️ 소요 시간**: 15-30분

#### Step 5.1: 하드코딩된 크레덴셜 검색
```cmd
findstr /s /i "meanstomakemewealthy" *.py
findstr /s /i "!00baggers" *.py
findstr /s /i "secret/my_sensitive_data.md" *.py
```

검색 결과가 나온 파일들을 마이그레이션해야 합니다.

#### Step 5.2: main_generator.py 마이그레이션

`CODE_MIGRATION_GUIDE.md` 문서를 참조하여 수정:

**핵심 변경사항**:
1. 파일 상단에 `from secure_config import get_terminalx_credentials` 추가
2. `self.secrets_file` 관련 코드 제거
3. `_load_credentials()` 메서드 교체

#### Step 5.3: 기타 파일 마이그레이션

Step 5.1에서 검색된 다른 파일들도 동일하게 수정

#### Step 5.4: 테스트
```cmd
python main_generator.py
```

**예상 출력**:
```
✅ TerminalX 자격 증명 로드 완료 (from environment variables).
WebDriver 설정 완료 (좌측 FHD 모니터, 전체 화면).
...
```

---

### ✅ PHASE 6: 최종 정리 및 커밋

**⏱️ 소요 시간**: 5분

```cmd
git add .
git commit -m "🔒 security: Migrate to environment variable based credential system

- Replace hardcoded credentials with secure_config.py
- All API keys and passwords now loaded from .env file
- Remove dependency on secret/my_sensitive_data.md

Ref: SECURITY_INCIDENT_RESPONSE.md"

git push origin main
```

---

## 📊 최종 검증 체크리스트

### 보안 조치
- [ ] TerminalX 비밀번호 변경됨
- [ ] 모든 API 키 회전됨
- [ ] GitHub 리포지토리 Private
- [ ] Git 히스토리에서 민감 파일 제거됨
- [ ] 원격 저장소에 강제 푸시됨

### 시스템 구현
- [ ] python-dotenv 설치됨
- [ ] .env 파일 생성 및 설정됨
- [ ] secure_config.py 테스트 통과
- [ ] main_generator.py 마이그레이션 완료
- [ ] 기타 스크립트 마이그레이션 완료

### 정리 작업
- [ ] secret/ 디렉토리 삭제됨
- [ ] my_sensitive_data.md 파일 삭제됨
- [ ] .gitignore 업데이트됨
- [ ] backup_before_cleanup.bundle 백업 파일 존재

### 테스트
- [ ] secure_config.py 실행 성공
- [ ] main_generator.py 실행 성공
- [ ] 전체 워크플로우 테스트 성공

---

## 🔗 참조 문서

- **사고 대응 보고서**: `SECURITY_INCIDENT_RESPONSE.md`
- **코드 마이그레이션 가이드**: `CODE_MIGRATION_GUIDE.md`
- **보안 설정 모듈**: `secure_config.py`
- **환경 변수 템플릿**: `.env.example`

---

## ⚠️ 문제 발생 시 복구 방법

### 복구 옵션 1: Git 히스토리 복원
```cmd
git bundle verify backup_before_cleanup.bundle
git fetch backup_before_cleanup.bundle
git reset --hard FETCH_HEAD
```

### 복구 옵션 2: 환경 변수 문제
```cmd
# secure_config.py에서 에러 메시지 확인
python secure_config.py

# .env 파일 내용 확인
type .env

# 필요시 .env.example에서 다시 복사
copy /Y .env.example .env
notepad .env
```

---

## 📞 지원

**문서**: `SECURITY_INCIDENT_RESPONSE.md`, `CODE_MIGRATION_GUIDE.md`
**백업**: `backup_before_cleanup.bundle`

---

**작성일**: 2025-10-07
**버전**: 1.0
**상태**: 실행 준비 완료

**🔴 지금 시작하세요! PHASE 0부터 순서대로 실행하세요.**
