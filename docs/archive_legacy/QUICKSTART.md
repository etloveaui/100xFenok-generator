# 100xFenok Generator - Quick Start Guide

**5분 안에 시작하는 실행 가이드**

---

## 1단계: 사전 확인 (1분)

### 필수 요구사항
```bash
# Chrome/Edge 브라우저 설치 확인
# Python 3.8+ 설치 확인
python --version

# 프로젝트 디렉토리 이동
cd C:\Users\etlov\agents-workspace\projects\100xFenok-generator
```

**예상 결과**: Python 버전이 3.8 이상으로 표시됨

**실패 시**: Python 설치 필요 → https://python.org

---

## 2단계: 의존성 설치 (2분)

```bash
# 필수 라이브러리 설치
pip install selenium beautifulsoup4 Jinja2 pyperclip

# 설치 확인
pip list | grep -E "selenium|beautifulsoup4"
```

**예상 결과**:
```
beautifulsoup4    4.12.0
selenium          4.15.0
```

**실패 시**: 관리자 권한으로 재실행 또는 `--user` 플래그 추가

**소요 시간**: 약 1-2분

---

## 3단계: 설정 확인 (30초)

### A. 자격 증명 확인
```bash
# TerminalX 로그인 정보 확인 (보안 주의!)
# 파일: secrets/my_sensitive_data.md
# 계정: meanstomakemewealthy@naver.com
# 비밀번호: !00baggers
```

**실패 시**: 자격 증명 파일이 없으면 생성 필요

### B. ChromeDriver 확인
```bash
# chromedriver.exe 존재 확인
ls -la chromedriver.exe

# 예상 출력: 약 19MB 크기의 실행 파일
```

**예상 결과**: `-rwxr-xr-x ... 19670528 ... chromedriver.exe`

**실패 시**: 프로젝트에 이미 포함되어 있음 (확인 필요)

---

## 4단계: 테스트 실행 (1분)

### 옵션 A: 단일 리포트 테스트 (추천)
```bash
# 개선된 HTML 추출 로직 테스트
python test_improved_extraction.py
```

**예상 결과**:
```
[Phase 1] TerminalX 로그인... ✅
[Phase 2] 리포트 생성 요청... ✅
[Phase 3] Archive 모니터링... ✅ GENERATED
[Phase 4] HTML 추출... ✅ 150KB
```

**소요 시간**: 약 5-8분 (리포트 생성 대기 포함)

### 옵션 B: 6개 리포트 전체 테스트
```bash
# 전체 자동화 실행 (권장하지 않음 - 처음 사용 시)
python test_full_6reports.py
```

**소요 시간**: 약 20-30분

---

## 5단계: 결과 확인 (30초)

### 생성된 파일 확인
```bash
# HTML 파일 목록 확인
ls -lh generated_html/

# 예상 출력:
# -rw-r--r-- 1 etlov 197609 150K ... 20251007_Crypto_Analysis.html
# -rw-r--r-- 1 etlov 197609 140K ... 20251007_AI_Technology_Report.html
```

**성공 기준**:
- 파일 크기 > 50KB
- markdown-body 또는 supersearchx-body 클래스 포함
- "No documents found" 문자열 없음

### 품질 검증
```bash
# HTML 내용 샘플 확인
head -50 generated_html/20251007_Crypto_Analysis.html
```

**예상 내용**:
- HTML 헤더
- 스타일시트
- markdown-body 또는 supersearchx-body div
- 실제 금융 데이터 (테이블, 차트 등)

**실패 시**: `TROUBLESHOOTING.md` 참조

---

## 빠른 문제 해결

### 로그인 실패
```
증상: "Login failed" 또는 타임아웃
해결: browser_controller.py 사용 (줄 45-78)
     자격 증명 확인: secrets/my_sensitive_data.md
```

### HTML 추출 실패
```
증상: "No documents found" 에러
해결: Archive 상태 확인 필수
     quick_archive_check.py 로직 사용 (줄 156-198)
```

### 브라우저 시작 실패
```
증상: ChromeDriver 실행 오류
해결: Chrome 브라우저와 ChromeDriver 버전 호환성 확인
     필요시 chromedriver.exe 업데이트
```

---

## 다음 단계

### 성공 시
1. `DAILY_USAGE.md` 참조 - 일상적인 사용법
2. `CHECKLIST.md` 참조 - 작업 검증 체크리스트
3. 프로덕션 환경 설정 고려

### 실패 시
1. `TROUBLESHOOTING.md` 참조 - 상세 문제 해결
2. 로그 파일 확인: `log/*.log`
3. 테스트 모드 실행: `--debug` 플래그 사용

---

## 핵심 포인트

### 작동하는 것 ✅
- 로그인 (browser_controller.py)
- 브라우저 제어 (main_generator.py:25-43)
- Past Day 설정 (free_explorer.py:317-335)
- Archive 상태 확인 (quick_archive_check.py:156-198)

### 중요 사항 ⚠️
- **Archive 확인 필수**: 리포트 완료 대기 없이 추출 시도하면 실패
- **타임아웃 설정**: 리포트 생성에 5-10분 소요
- **HTML 검증**: 크기와 클래스 확인 필수

### 예상 시간
- **초기 설정**: 3분
- **단일 테스트**: 5-8분
- **전체 실행**: 20-30분

---

**마지막 업데이트**: 2025-10-07
**다음 읽을 문서**: DAILY_USAGE.md
**문제 발생 시**: TROUBLESHOOTING.md
