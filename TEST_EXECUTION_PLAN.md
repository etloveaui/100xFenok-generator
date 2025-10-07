# 테스트 실행 계획

**날짜**: 2025-10-07
**목적**: 100xFenok-Generator 전체 기능 검증
**예상 소요**: 2-3시간

---

## 테스트 항목별 실행 방법

### Test 1: 로그인 및 기본 접근 테스트 (5분)

**목적**: TerminalX 로그인 및 리다이렉션 처리 검증

**실행 명령**:
```bash
cd C:\Users\etlov\agents-workspace\projects\100xFenok-generator
python main_generator.py --debug
```

**예상 출력**:
```
=== 디버깅 테스트: 로그인 및 리다이렉션 확인 ===
TerminalX 로그인 시도...
페이지 로드 완료, 5초 대기...
로그인 버튼 찾음: //button[contains(text(), 'Log in')]
로그인 버튼 클릭 완료
이메일 입력 필드 찾음
비밀번호 입력 필드 찾음
이메일 입력: meanstomakemewealthy@naver.com
비밀번호 입력 완료
로그인 제출 버튼 찾음
로그인 제출 버튼 클릭
로그인 성공 확인: //button[contains(., 'Archive')]
TerminalX 로그인 성공
로그인 성공. 폼 페이지 접근 테스트 시작...
폼 URL로 이동: https://theterminalx.com/agent/enterprise/report/form/10
도착한 URL: https://theterminalx.com/agent/enterprise/report/form/10
[SUCCESS] 폼 페이지 접근 성공
[SUCCESS] Report Title 필드 발견
```

**성공 기준**:
- 로그인 성공 메시지
- 폼 페이지 접근 성공
- Report Title 필드 발견

**실패 시 조치**:
1. 자격 증명 확인: `secret/my_sensitive_data.md`
2. TerminalX 웹사이트 접근 가능 여부 확인
3. Chromedriver 버전 확인: `update_chromedriver.py` 실행

---

### Test 2: Part1, Part2 생성 테스트 (15-20분)

**목적**: 기본 Daily Wrap 리포트 생성 검증

**실행 명령**:
```bash
cd C:\Users\etlov\agents-workspace\projects\100xFenok-generator
python main_generator.py
```

**예상 출력 (주요 단계)**:
```
--- 100xFenok Report Generation Automation Start ---
TerminalX 로그인 시도...
TerminalX 로그인 성공

--- Phase 1: 리포트 생성 요청 시작 ---
[Batch Manager] Part1 (20251007 100x Daily Wrap Part1) 리포트가 배치에 추가되었습니다.
[Batch Manager] Part2 (20251007 100x Daily Wrap Part2) 리포트가 배치에 추가되었습니다.

--- Part1 보고서 생성 요청 시작 ---
Report: 20251007 100x Daily Wrap Part1
Date: 20251007, Range: 2025-10-06 ~ 2025-10-07
파일 존재 확인:
  - Prompt 파일: input_data/21_100x_Daily_Wrap_Prompt_1_20250723.md (존재)
  - Source PDF: input_data/10_100x_Daily_Wrap_My_Sources_1_20250723.pdf (존재)
  - Prompt PDF: input_data/21_100x_Daily_Wrap_Prompt_1_20250723.pdf (존재)
Prompt 파일 로드 성공 (길이: XXXXX자)
  - 리포트 폼 URL로 이동 시도: https://theterminalx.com/agent/enterprise/report/form/10
  - 실제 도착한 URL: https://theterminalx.com/agent/enterprise/report/form/10
  - Report Title 입력 필드 발견됨!
  - Report Title 입력 중: '20251007 100x Daily Wrap Part1'
  - Report Title 입력 완료!
  - Reference Date 입력 중: 2025-10-06 ~ 2025-10-07
  - Report Reference Date 입력 완료!
  - Sample Report 업로드 중: input_data/10_100x_Daily_Wrap_My_Sources_1_20250723.pdf
  - Sample Report 업로드 완료!
  - Own Sources 업로드 중: ...
  - Own Sources 업로드 완료!
  - Prompt 입력 중... (길이: XXXXX자)
  - Prompt 입력 완료!
  - Generate 버튼 활성화 대기 중...
  - Generate 버튼 활성화 확인!
  - Generate 버튼 클릭! 보고서 생성 시작 대기 중...
  - 산출물 URL 변경 대기 중 (최대 20분)...
  - 보고서 URL 확인 완료: https://theterminalx.com/agent/enterprise/report/XXXX
  - 'Generating your report' 메시지 등장 대기 중...
  - 'Generating your report' 메시지 등장 확인. 리포트 생성 시작됨.

(Part2 반복)

--- Phase 2: 아카이브 페이지에서 상태 모니터링 시작 ---
[Batch Manager] 아카이브 페이지 새로고침. 남은 리포트: 2
[Batch Manager] Archive 페이지 로딩 대기중...
[Batch Manager] JavaScript 렌더링 대기중...
[Batch Manager] 테이블 행 렌더링 대기중...
[Batch Manager] 테이블 행 10개 발견
[Batch Manager] 대기: '20251007 100x Daily Wrap Part1' -> GENERATING
[Batch Manager] 대기: '20251007 100x Daily Wrap Part2' -> GENERATING
(30초 대기, 반복)
[Batch Manager] 성공: '20251007 100x Daily Wrap Part1' -> GENERATED
[Batch Manager] 성공: '20251007 100x Daily Wrap Part2' -> GENERATED
[Batch Manager] 모든 리포트가 성공적으로 생성되었습니다.

--- Phase 3: 데이터 추출 및 처리 시작 ---
  - '20251007 100x Daily Wrap Part1' HTML 추출 시작...
  - 페이지 렌더링 대기 (최대 120초)...
  - 렌더링 대기중... (5초, 현재 크기: 32547 bytes)
  - 렌더링 완료! HTML 크기: 149557 bytes
  - HTML 저장 완료: generated_html/20251007_part1.html
  - markdown-body 클래스 확인
  - supersearchx-body 클래스 확인

(Part2 반복)

--- 자동화 완료 ---
```

**성공 기준**:
- Phase 1: 2개 리포트 생성 요청 성공
- Phase 2: Archive 모니터링으로 "GENERATED" 상태 확인
- Phase 3: 2개 HTML 파일 생성 (각 100KB 이상)

**확인 명령**:
```bash
ls -lh generated_html/20251007_part*.html
```

**실패 시 조치**:
1. Archive 상태 확인: TerminalX 웹사이트에서 수동 확인
2. 타임아웃 연장: `report_manager.py:53` timeout 증가
3. 로그 분석: 어느 Phase에서 실패했는지 확인

---

### Test 3: 6개 리포트 전체 생성 테스트 (30-40분)

**목적**: 6개 리포트 동시 생성 및 Archive 모니터링 검증

**실행 명령**:
```bash
cd C:\Users\etlov\agents-workspace\projects\100xFenok-generator
python test_full_6reports.py
```

**예상 출력 (축약)**:
```
================================================================================
 100xFenok Generator - 6개 리포트 전체 테스트
 개선된 폴링 방식 HTML 추출 적용
================================================================================

[Phase 1] TerminalX 로그인...
✅ 로그인 성공

[Phase 2] 6개 리포트 생성 요청...
------------------------------------------------------------

[1/6] Crypto Analysis 생성 요청...
  ✅ 생성 요청 성공 - Report ID: 1234

[2/6] AI Technology Report 생성 요청...
  ✅ 생성 요청 성공 - Report ID: 1235

[3/6] Stock Market Analysis 생성 요청...
  ✅ 생성 요청 성공 - Report ID: 1236

[4/6] Tech Innovation Report 생성 요청...
  ✅ 생성 요청 성공 - Report ID: 1237

[5/6] Economic Indicators 생성 요청...
  ✅ 생성 요청 성공 - Report ID: 1238

[6/6] Energy Market Report 생성 요청...
  ✅ 생성 요청 성공 - Report ID: 1239

요청 완료: 6/6 리포트

[Phase 3] Archive 모니터링 (최대 20분)...
------------------------------------------------------------
[Batch Manager] 아카이브 페이지 새로고침. 남은 리포트: 6
(여러 번 반복)
[Batch Manager] 성공: 'Crypto Analysis' -> GENERATED
[Batch Manager] 성공: 'AI Technology Report' -> GENERATED
[Batch Manager] 성공: 'Stock Market Analysis' -> GENERATED
[Batch Manager] 성공: 'Tech Innovation Report' -> GENERATED
[Batch Manager] 성공: 'Economic Indicators' -> GENERATED
[Batch Manager] 성공: 'Energy Market Report' -> GENERATED
[Batch Manager] 모든 리포트가 성공적으로 생성되었습니다.

생성 완료: 6/6 리포트

[Phase 4] HTML 추출 (개선된 폴링 방식)...
------------------------------------------------------------

[추출] Crypto Analysis
  - 'Crypto Analysis' HTML 추출 시작...
  - 페이지 렌더링 대기 (최대 120초)...
  - 렌더링 완료! HTML 크기: 123456 bytes
  - HTML 저장 완료: generated_html/20251007_Crypto_Analysis.html
  ✅ 추출 성공
     - 파일: generated_html/20251007_Crypto_Analysis.html
     - 크기: 123,456 bytes
     - markdown-body: ✅
     - supersearchx-body: ✅

(나머지 5개 반복)

================================================================================
 테스트 결과 요약
================================================================================

📊 전체 통계:
  - 총 리포트: 6개
  - 생성 성공: 6개 (100.0%)
  - 추출 성공: 6개 (100.0%)
  - 실패: 0개

📑 개별 리포트 상태:
  ✅ Crypto Analysis: EXTRACTED
     └─ 123,456 bytes
  ✅ AI Technology Report: EXTRACTED
     └─ 134,567 bytes
  ✅ Stock Market Analysis: EXTRACTED
     └─ 145,678 bytes
  ✅ Tech Innovation Report: EXTRACTED
     └─ 156,789 bytes
  ✅ Economic Indicators: EXTRACTED
     └─ 167,890 bytes
  ✅ Energy Market Report: EXTRACTED
     └─ 178,901 bytes

🎉 테스트 성공!
성공률: 100.0%

결과 저장: test_results_20251007.json
```

**성공 기준**:
- 6개 리포트 모두 생성 요청 성공
- Archive 모니터링으로 6개 모두 "GENERATED" 상태 확인
- 6개 HTML 파일 생성 (각 100KB 이상)
- 성공률 80% 이상

**확인 명령**:
```bash
ls -lh generated_html/20251007_*.html
cat test_results_20251007.json
```

**실패 시 조치**:
1. 부분 성공 (4-5개): Archive 타임아웃 연장
2. 전체 실패 (0-2개): Test 2부터 재실행
3. HTML 추출 실패: `extract_and_validate_html()` 타임아웃 연장

---

### Test 4: Past Day 설정 변경 검증 (수동)

**목적**: 다양한 날짜 범위로 리포트 생성 검증

**실행 방법**:
1. `six_reports_config.json` 수정:
   ```json
   {
     "name": "Test Report",
     "past_day": 7,  // 1주일 → 30, 60, 90 테스트
     ...
   }
   ```

2. 단일 리포트 생성:
   ```bash
   python test_full_6reports.py
   ```

3. TerminalX 웹사이트에서 수동 확인:
   - Archive 페이지 방문
   - "Test Report" 클릭
   - Reference Date 확인: 올바른 날짜 범위인지 검증

**성공 기준**:
- Past Day 30: 최근 1개월 데이터
- Past Day 60: 최근 2개월 데이터
- Past Day 90: 최근 3개월 데이터

---

### Test 5: Archive 모니터링 스트레스 테스트 (고급)

**목적**: 긴 대기 시간 및 재시도 로직 검증

**실행 방법**:
1. `report_manager.py:53` 수정:
   ```python
   def monitor_and_retry(self, timeout: int = 3600, ...):  # 1시간으로 연장
   ```

2. 많은 리포트 동시 생성:
   - `six_reports_config.json`에 리포트 12개 추가
   - `test_full_6reports.py` 실행

**성공 기준**:
- 모든 리포트 GENERATED 상태 도달
- 재시도 로직 작동 (일부 실패 시)
- 지수 백오프 정상 작동

---

## 테스트 체크리스트

### Pre-Test 확인
- [ ] Chromedriver 설치됨: `chromedriver.exe` 존재
- [ ] 자격 증명 존재: `secret/my_sensitive_data.md`
- [ ] Python 의존성 설치: `pip install -r requirements.txt`
- [ ] 네트워크 연결: TerminalX 웹사이트 접근 가능

### Test 1: 로그인 (5분)
- [ ] 로그인 성공
- [ ] 폼 페이지 접근
- [ ] Report Title 필드 발견

### Test 2: Part1, Part2 (20분)
- [ ] Part1 생성 요청 성공
- [ ] Part2 생성 요청 성공
- [ ] Archive 모니터링 완료
- [ ] 2개 HTML 파일 생성
- [ ] 파일 크기 검증 (>100KB)

### Test 3: 6개 리포트 (40분)
- [ ] 6개 리포트 생성 요청 성공
- [ ] Archive 모니터링 완료 (6개 모두)
- [ ] 6개 HTML 파일 생성
- [ ] 성공률 80% 이상

### Test 4: Past Day 변경 (수동)
- [ ] Past Day 30 검증
- [ ] Past Day 60 검증
- [ ] Past Day 90 검증

### Test 5: 스트레스 테스트 (옵션)
- [ ] 12개 리포트 동시 생성
- [ ] 재시도 로직 작동
- [ ] 지수 백오프 확인

---

## 문제 해결 가이드

### 문제 1: 로그인 실패

**증상**:
```
로그인 실패: Timeout
```

**해결 방법**:
1. 자격 증명 확인:
   ```bash
   cat secret/my_sensitive_data.md
   ```
2. TerminalX 웹사이트 수동 접속 테스트
3. 셀렉터 업데이트 필요 여부 확인

### 문제 2: Archive 모니터링 타임아웃

**증상**:
```
[Batch Manager] 오류: 전체 작업 시간 초과.
```

**해결 방법**:
1. `report_manager.py:53` timeout 증가:
   ```python
   def monitor_and_retry(self, timeout: int = 3600, ...):  # 30분 → 1시간
   ```
2. Archive 페이지 수동 확인
3. TerminalX 서버 상태 확인

### 문제 3: HTML 추출 "No documents found"

**증상**:
```
  - 오류: 'No documents found' 감지 - 리포트 생성 실패
```

**해결 방법**:
1. Archive에서 상태 재확인
2. 리포트 URL 수동 접속
3. `extract_and_validate_html()` 타임아웃 증가:
   ```python
   max_wait = 300  # 120초 → 300초
   ```

### 문제 4: HTML 크기 너무 작음

**증상**:
```
  - 렌더링 대기중... (120초, 현재 크기: 5678 bytes)
```

**해결 방법**:
1. 크기 임계값 조정:
   ```python
   if html_size > 10000:  # 50KB → 10KB
   ```
2. "No documents found" 처리 개선 (계속 대기)
3. Archive 페이지에서 상태 재확인

### 문제 5: Chromedriver 버전 불일치

**증상**:
```
WebDriver 설정 중 오류 발생: ...
```

**해결 방법**:
```bash
python update_chromedriver.py
```

---

## 테스트 결과 보고 양식

### Test Execution Report

**날짜**: YYYY-MM-DD
**실행자**:
**환경**: Windows 10/11, Python 3.x, Chrome 버전

**Test 1: 로그인**
- [ ] PASS / [ ] FAIL
- 실행 시간: ___ 분
- 비고:

**Test 2: Part1, Part2**
- [ ] PASS / [ ] FAIL
- 실행 시간: ___ 분
- 생성된 파일:
  - Part1: ___ KB
  - Part2: ___ KB
- 비고:

**Test 3: 6개 리포트**
- [ ] PASS / [ ] FAIL
- 실행 시간: ___ 분
- 성공률: ___ %
- 생성된 파일:
  1. Crypto Analysis: ___ KB
  2. AI Technology Report: ___ KB
  3. Stock Market Analysis: ___ KB
  4. Tech Innovation Report: ___ KB
  5. Economic Indicators: ___ KB
  6. Energy Market Report: ___ KB
- 비고:

**Test 4: Past Day 변경**
- [ ] PASS / [ ] FAIL
- 테스트한 설정: Past Day ___, ___, ___
- 비고:

**Test 5: 스트레스 테스트**
- [ ] PASS / [ ] FAIL / [ ] SKIPPED
- 리포트 수: ___
- 성공률: ___ %
- 비고:

**전체 평가**:
- 총 실행 시간: ___ 시간
- 전체 성공률: ___ %
- 주요 문제점:
- 개선 제안:

---

**작성자**: Quality Engineer (Claude Code)
**버전**: 1.0
**최종 업데이트**: 2025-10-07
