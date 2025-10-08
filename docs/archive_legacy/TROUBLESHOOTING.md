# 100xFenok Generator - Troubleshooting Guide

**문제 해결 및 복구 가이드**

---

## 목차

1. [일반적인 문제](#일반적인-문제)
2. [단계별 문제 해결](#단계별-문제-해결)
3. [긴급 복구 절차](#긴급-복구-절차)
4. [디버깅 도구](#디버깅-도구)
5. [과거 실패 사례](#과거-실패-사례)

---

## 일반적인 문제

### 문제 1: 로그인 실패

**증상**:
```
❌ 로그인 타임아웃
❌ Login failed
❌ 로그인 요소를 찾을 수 없습니다
```

**원인 분석**:
1. 네트워크 연결 불안정
2. TerminalX 서버 응답 지연
3. 자격 증명 불일치
4. 브라우저/ChromeDriver 버전 호환성

**해결 방법**:

#### A. 자격 증명 확인
```bash
# 자격 증명 파일 확인
cat secrets/my_sensitive_data.md

# 예상 내용:
# 계정: meanstomakemewealthy@naver.com
# 비밀번호: !00baggers
```

#### B. 수동 로그인 테스트
```python
from browser_controller import BrowserController

bc = BrowserController()
bc.start_browser()

# 수동으로 브라우저에서 로그인 테스트
input("Press Enter after manual login test...")
```

#### C. 타임아웃 증가
```python
# browser_controller.py 수정
WebDriverWait(self.driver, 15).until(...)  # 10 → 15초로 증가
```

**예상 소요 시간**: 5-10분

**성공 확인**:
- 브라우저에 "Subscriptions" 버튼 표시
- Enterprise 페이지로 리다이렉트됨

---

### 문제 2: Past Day 설정 실패

**증상**:
```
❌ Past Day 설정 요소를 찾지 못했습니다
❌ 드롭다운 메뉴가 표시되지 않음
⚠️ "Any Time"이 "Past Day"로 변경되지 않음
```

**원인 분석**:
1. UI 요소 셀렉터 변경
2. JavaScript 렌더링 지연
3. 드롭다운 요소 찾기 실패

**해결 방법**:

#### A. 작동하는 코드 사용
```python
# free_explorer.py:317-335의 정확한 로직 사용
def set_past_day_properly(self):
    # 다양한 셀렉터로 시도
    period_selectors = [
        "//select[contains(@name, 'period')]",
        "//button[contains(text(), 'Past Day')]",
        "//div[contains(@class, 'date')]//select",
        "//div[contains(@class, 'time-range')]//button"
    ]

    for selector in period_selectors:
        elements = self.driver.find_elements(By.XPATH, selector)
        for elem in elements:
            if elem.is_displayed():
                # "Any Time" 클릭
                if 'Any Time' in elem.text or 'Past Day' in elem.text:
                    elem.click()
                    time.sleep(2)

                    # 드롭다운 열림 확인
                    page_source = self.driver.page_source
                    if 'Past' in page_source:
                        # Past Day 옵션 클릭
                        past_options = self.driver.find_elements(
                            By.XPATH, "//*[contains(text(), 'Past Day')]"
                        )
                        for option in past_options:
                            if option.is_displayed():
                                option.click()
                                print("✅ Past Day 설정 완료")
                                return True
    return False
```

**코드 위치**: `free_explorer.py:317-335`

#### B. 수동 확인 및 디버깅
```python
# 브라우저 개발자 도구로 확인
# 1. Custom Report Builder 페이지 접근
# 2. F12 개발자 도구 열기
# 3. Elements 탭에서 Past Day 드롭다운 찾기
# 4. XPath 또는 CSS 셀렉터 확인
```

#### C. 대기 시간 증가
```python
# JavaScript 렌더링 대기
time.sleep(5)  # 2초 → 5초로 증가
```

**예상 소요 시간**: 10-15분

**성공 확인**:
- 드롭다운에 "Past Day" 표시됨
- 페이지 소스에 "Past Day" 텍스트 포함

---

### 문제 3: Generate 버튼 찾기 실패

**증상**:
```
❌ Generate 버튼을 찾을 수 없습니다
⌨️ Enter 키로 제출 시도 중...
❌ 리포트 생성 요청 실패
```

**원인 분석**:
1. Generate 버튼 셀렉터 변경
2. 버튼이 disabled 상태
3. JavaScript로 동적 생성된 버튼

**해결 방법**:

#### A. 다중 셀렉터 전략
```python
# 7가지 셀렉터로 시도
generate_selectors = [
    "//button[contains(text(), 'Generate')]",
    "//button[contains(text(), 'Submit')]",
    "//button[contains(text(), 'Send')]",
    "//button[contains(text(), 'Create')]",
    "//button[@type='submit']",
    "//button[contains(@class, 'submit')]",
    "//button[contains(@class, 'generate')]"
]

for selector in generate_selectors:
    try:
        elements = self.driver.find_elements(By.XPATH, selector)
        for elem in elements:
            if elem.is_displayed() and elem.is_enabled():
                elem.click()
                print(f"✅ Generate 버튼 클릭 성공: {selector}")
                return True
    except Exception as e:
        continue

# 최후의 수단: Enter 키
self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.RETURN)
```

#### B. 버튼 상태 확인
```python
# 버튼이 활성화될 때까지 대기
WebDriverWait(self.driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate')]"))
)
```

#### C. JavaScript 직접 실행
```python
# Selenium으로 클릭이 안될 때
generate_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Generate')]")
self.driver.execute_script("arguments[0].click();", generate_button)
```

**예상 소요 시간**: 5-10분

**성공 확인**:
- 페이지 URL이 `/reports/archive`로 변경됨
- 또는 리포트 생성 확인 메시지 표시

---

### 문제 4: 리포트 완료 대기 실패 ⚠️ 핵심 문제!

**증상**:
```
❌ 5분 대기 후 "No documents found" 에러
❌ supersearchx-body 클래스 없음
❌ MuiTable 에러만 추출됨 (1,057 bytes)
```

**예상 HTML (실패)**:
```html
<table class="MuiTable-root">
  <tbody>
    <tr>
      <td colspan="4">No documents found in your private data room.</td>
    </tr>
  </tbody>
</table>
```

**기대 HTML (성공)**:
```html
<div class="supersearchx-body markdown-body">
  <div class="s01-thesis">
    실제 금융 데이터...
  </div>
</div>
```

**원인 분석**:
1. **Archive 상태 확인 없음** - 완료 여부 미검증
2. **Blind wait 사용** - 고정 시간 대기만 함
3. **렌더링 완료 미확인** - JavaScript 완료 체크 없음

**해결 방법** (가장 중요!):

#### A. Archive 폴링 로직 구현
```python
def wait_for_completion(self, report_id, timeout_seconds=600, poll_interval=10):
    """
    Archive 페이지에서 리포트 완료 상태 확인

    Args:
        report_id: 리포트 ID
        timeout_seconds: 최대 대기 시간 (기본 10분)
        poll_interval: 확인 간격 (기본 10초)

    Returns:
        True: 완료 성공
        False: 타임아웃
    """
    start_time = time.time()
    check_count = 0

    while (time.time() - start_time) < timeout_seconds:
        check_count += 1
        elapsed = int(time.time() - start_time)
        print(f"\n[체크 #{check_count}] Archive 상태 확인... (경과: {elapsed}초)")

        # Archive 페이지 접근
        self.driver.get('https://theterminalx.com/agent/enterprise/report/archive')
        time.sleep(10)  # JavaScript 렌더링 대기

        # 리포트 상태 확인
        try:
            # 테이블 파싱
            rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")

            for row in rows:
                try:
                    # 리포트 ID 확인
                    id_elem = row.find_element(By.XPATH, ".//td[1]")
                    status_elem = row.find_element(By.XPATH, ".//td[4]")

                    if report_id in id_elem.text:
                        status = status_elem.text.strip().upper()

                        if status == "GENERATED" or status == "READY":
                            print(f"✅ 리포트 {report_id} 완료됨!")
                            return True
                        elif status == "GENERATING":
                            print(f"🔄 리포트 {report_id} 생성 중... ({status})")
                        elif status == "PENDING":
                            print(f"⏳ 리포트 {report_id} 대기 중... ({status})")
                        elif status == "FAILED":
                            print(f"❌ 리포트 {report_id} 실패!")
                            return False
                except Exception as e:
                    continue
        except Exception as e:
            print(f"⚠️ Archive 페이지 파싱 오류: {e}")

        # 다음 확인까지 대기
        time.sleep(poll_interval)

    print(f"⏱️ 타임아웃: {timeout_seconds}초 초과")
    return False
```

**코드 위치**: `quick_archive_check.py:156-198` 참조

#### B. 통합 사용 예시
```python
def generate_report_with_archive_check(self, ...):
    """리포트 생성 + Archive 검증"""

    # 1. 리포트 생성 요청
    self._submit_report()
    report_url = self.driver.current_url
    report_id = report_url.split('/')[-1]

    print(f"📋 리포트 ID: {report_id}")

    # 2. Archive 완료 대기 (핵심!)
    print("[Phase 3] Archive 모니터링 시작...")
    success = self.wait_for_completion(
        report_id=report_id,
        timeout_seconds=600,  # 10분
        poll_interval=15      # 15초마다 확인
    )

    if not success:
        raise Exception(f"리포트 {report_id} 생성 타임아웃")

    # 3. 완료 확인 후 HTML 추출
    print("[Phase 4] HTML 추출 시작...")
    html_content = self._extract_html_with_polling()

    return html_content
```

#### C. HTML 추출 폴링
```python
def _extract_html_with_polling(self, max_wait=120, poll_interval=5):
    """HTML 렌더링 완료까지 폴링"""

    elapsed = 0
    while elapsed < max_wait:
        try:
            # markdown-body 또는 supersearchx-body 찾기
            elements = self.driver.find_elements(
                By.XPATH,
                "//div[contains(@class, 'markdown-body') or contains(@class, 'supersearchx-body')]"
            )

            if elements:
                html_content = self.driver.page_source

                # 검증
                if "No documents found" not in html_content:
                    if len(html_content) > 50000:  # 50KB 이상
                        print(f"✅ HTML 추출 완료 ({len(html_content)} bytes)")
                        return html_content

            print(f"  렌더링 대기중... ({elapsed}초)")
            time.sleep(poll_interval)
            elapsed += poll_interval

        except Exception as e:
            print(f"  렌더링 확인 중... ({elapsed}초)")
            time.sleep(poll_interval)
            elapsed += poll_interval

    raise Exception("HTML 렌더링 타임아웃")
```

**예상 소요 시간**: 10-15분 (리포트 생성 시간 포함)

**성공 확인**:
- Archive 페이지에서 "GENERATED" 상태 표시
- HTML에 markdown-body 또는 supersearchx-body 클래스 포함
- 파일 크기 > 50KB

---

### 문제 5: HTML 추출 후 크기 부족

**증상**:
```
⚠️ HTML 파일 크기: 1,057 bytes (50KB 미만)
❌ "No documents found" 문자열 포함
❌ markdown-body 클래스 없음
```

**원인 분석**:
1. 리포트가 실제로 완료되지 않음
2. JavaScript 렌더링 미완료
3. 잘못된 페이지에서 추출

**해결 방법**:

#### A. 크기 및 콘텐츠 검증
```python
def validate_html_content(html_content):
    """HTML 콘텐츠 검증"""

    # 크기 확인
    if len(html_content) < 50000:
        raise Exception(f"HTML 크기 부족: {len(html_content)} bytes")

    # "No documents found" 체크
    if "No documents found" in html_content:
        raise Exception("에러 페이지 감지: No documents found")

    # markdown-body 또는 supersearchx-body 확인
    if "markdown-body" not in html_content and "supersearchx-body" not in html_content:
        raise Exception("유효한 콘텐츠 클래스 없음")

    print("✅ HTML 콘텐츠 검증 완료")
    return True
```

#### B. 재시도 로직
```python
def extract_html_with_retry(self, max_retries=3):
    """재시도를 포함한 HTML 추출"""

    for attempt in range(max_retries):
        try:
            html_content = self._extract_html_with_polling()

            # 검증
            if self.validate_html_content(html_content):
                return html_content

        except Exception as e:
            print(f"⚠️ 시도 #{attempt + 1} 실패: {e}")
            if attempt < max_retries - 1:
                print("  10초 후 재시도...")
                time.sleep(10)
            else:
                raise

    raise Exception("HTML 추출 최종 실패")
```

**예상 소요 시간**: 2-5분

**성공 확인**:
- HTML 크기 > 50KB
- markdown-body 클래스 포함
- 실제 금융 데이터 포함

---

## 단계별 문제 해결

### Phase 1: 로그인 문제

**디버깅 체크리스트**:
1. [ ] ChromeDriver 실행 가능한가?
2. [ ] 브라우저 창이 열리는가?
3. [ ] TerminalX 로그인 페이지가 로드되는가?
4. [ ] 자격 증명이 입력되는가?
5. [ ] 로그인 버튼이 클릭되는가?
6. [ ] 로그인 후 리다이렉트되는가?

**디버깅 명령**:
```python
from browser_controller import BrowserController

bc = BrowserController()
bc.start_browser()
print("✅ 브라우저 시작됨")

success = bc.login_terminalx()
print(f"로그인 결과: {'성공' if success else '실패'}")

input("Press Enter to close...")
bc.driver.quit()
```

---

### Phase 2: 리포트 생성 문제

**디버깅 체크리스트**:
1. [ ] Custom Report 페이지에 접근했는가?
2. [ ] 리포트 제목이 입력되는가?
3. [ ] 프롬프트가 입력되는가?
4. [ ] Past Day가 설정되는가?
5. [ ] Generate 버튼을 찾을 수 있는가?
6. [ ] Generate 버튼이 클릭되는가?

**디버깅 명령**:
```bash
# 단일 리포트 테스트
python test_improved_extraction.py
```

---

### Phase 3: Archive 모니터링 문제

**디버깅 체크리스트**:
1. [ ] Archive 페이지에 접근 가능한가?
2. [ ] 리포트 목록이 표시되는가?
3. [ ] 리포트 ID를 찾을 수 있는가?
4. [ ] 상태 컬럼이 파싱되는가?
5. [ ] 상태 변경이 감지되는가?
6. [ ] "GENERATED" 상태를 확인할 수 있는가?

**수동 확인**:
1. 브라우저에서 Archive 페이지 접근
2. 리포트 목록 확인
3. 상태 컬럼 위치 확인
4. 개발자 도구로 테이블 구조 분석

---

### Phase 4: HTML 추출 문제

**디버깅 체크리스트**:
1. [ ] 리포트 페이지에 접근 가능한가?
2. [ ] JavaScript가 렌더링되는가?
3. [ ] markdown-body 또는 supersearchx-body가 있는가?
4. [ ] HTML 크기가 충분한가? (> 50KB)
5. [ ] "No documents found"가 없는가?

**수동 확인**:
```bash
# HTML 콘텐츠 샘플 확인
head -100 generated_html/20251007_Crypto_Analysis.html

# 크기 확인
ls -lh generated_html/*.html

# 클래스 확인
grep -c "markdown-body" generated_html/*.html
```

---

## 긴급 복구 절차

### 상황 1: 완전히 작동하지 않음

**복구 단계**:

#### 1. 기본 환경 확인 (5분)
```bash
# Python 확인
python --version

# 의존성 확인
pip list | grep -E "selenium|beautifulsoup4"

# ChromeDriver 확인
ls -la chromedriver.exe
```

#### 2. 성공 코드로 롤백 (10분)
```bash
# 2025-08-20 성공 버전 확인
git log --oneline --since="2025-08-20" --until="2025-08-21"

# 성공 버전 체크아웃 (선택사항)
git checkout [commit-hash]
```

#### 3. 최소 테스트 실행 (5분)
```bash
# 로그인만 테스트
python -c "
from browser_controller import BrowserController
bc = BrowserController()
bc.start_browser()
result = bc.login_terminalx()
print('✅ 로그인 성공' if result else '❌ 로그인 실패')
"
```

**예상 소요 시간**: 20분

---

### 상황 2: 간헐적 실패

**복구 단계**:

#### 1. 타임아웃 증가 (5분)
```python
# 모든 타임아웃 값 2배로 증가
WebDriverWait(self.driver, 20).until(...)  # 10 → 20초
time.sleep(10)  # 5 → 10초
timeout_seconds = 1200  # 600 → 1200초
```

#### 2. 재시도 로직 추가 (10분)
```python
def with_retry(func, max_retries=3):
    """재시도 래퍼 함수"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ 시도 #{attempt + 1} 실패, 재시도...")
                time.sleep(10)
            else:
                raise
```

#### 3. 로그 분석 (5분)
```bash
# 최근 로그 확인
tail -100 log/main_generator_*.log | grep -E "ERROR|WARNING|FAILED"
```

**예상 소요 시간**: 20분

---

### 상황 3: 특정 리포트만 실패

**복구 단계**:

#### 1. 실패 리포트 식별 (2분)
```bash
# 생성된 파일 확인
ls -lh generated_html/

# 크기가 작은 파일 찾기
find generated_html/ -type f -size -50k
```

#### 2. 개별 재실행 (10분)
```python
# 실패한 리포트만 재실행
failed_reports = ["Crypto_Analysis"]  # 실패한 리포트 이름

for report_name in failed_reports:
    print(f"\n재실행: {report_name}")
    # 개별 실행 로직
```

**예상 소요 시간**: 15분

---

## 디버깅 도구

### 도구 1: 브라우저 개발자 도구

**사용 방법**:
1. 브라우저 창에서 F12 키
2. Elements 탭: DOM 구조 확인
3. Console 탭: JavaScript 에러 확인
4. Network 탭: API 요청 확인

**확인 사항**:
- UI 요소 셀렉터
- JavaScript 에러
- API 응답 상태

---

### 도구 2: Selenium 스크린샷

**사용 방법**:
```python
# 각 단계마다 스크린샷 저장
def save_screenshot(driver, name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"debug_screenshots/{name}_{timestamp}.png"
    driver.save_screenshot(filename)
    print(f"📸 스크린샷 저장: {filename}")

# 사용 예시
save_screenshot(self.driver, "after_login")
save_screenshot(self.driver, "before_generate")
save_screenshot(self.driver, "archive_page")
```

---

### 도구 3: 로그 분석 스크립트

**사용 방법**:
```bash
# 에러 패턴 추출
grep -E "ERROR|FAILED|Exception" log/*.log | sort | uniq -c

# 성공/실패 통계
grep -c "✅" log/main_generator_*.log
grep -c "❌" log/main_generator_*.log
```

---

## 과거 실패 사례

### 2025-08-25: 완전 실패

**Git 커밋 메시지**:
```
"Past Day 설정 완전 실패 (사용자가 100번 말했는데도 안했음)"
"Generate 버튼 못찾고 Enter로만 시도"
"기존 자료 안찾고 새로 만들기만 함 (골백번 지시했는데도 무시)"
```

**교훈**:
1. ✅ 기존 성공 코드 재사용 필수
2. ✅ Archive 상태 확인 로직 필수
3. ✅ Blind wait 사용 금지
4. ✅ 단계별 검증 필수

---

### 2025-08-20: 성공 사례

**성공 요인**:
1. Archive 페이지 폴링 사용
2. "GENERATED" 상태 확인
3. 완료 후 데이터 추출

**참조 파일**:
- `main_generator.py` (2025-08-20 버전)
- `real_terminalx_20250820_111715.log`

---

## 빠른 참조

### 작동하는 코드 위치

| 기능 | 파일 | 줄 번호 |
|------|------|---------|
| 로그인 | main_generator.py | 45-78 |
| Past Day 설정 | free_explorer.py | 317-335 |
| Archive 확인 | quick_archive_check.py | 156-198 |
| HTML 추출 | main_generator.py | 720-787 |

### 긴급 연락처

**문서 참조 순서**:
1. QUICKSTART.md - 빠른 시작
2. CHECKLIST.md - 검증 체크리스트
3. TROUBLESHOOTING.md - 이 문서
4. MASTER_GUIDE.md - 완전한 가이드

---

**마지막 업데이트**: 2025-10-07
**작성자**: Claude Code Technical Writer
**다음 읽을 문서**: DAILY_USAGE.md
