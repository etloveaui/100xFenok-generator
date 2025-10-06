# 문제 해결 가이드

**마지막 업데이트**: 2025-10-06

---

## 📋 목차

1. [과거 실패 사례](#과거-실패-사례)
2. [일반적인 문제](#일반적인-문제)
3. [작동하는 코드 위치](#작동하는-코드-위치)
4. [디버깅 방법](#디버깅-방법)

---

## 과거 실패 사례

### 2025-08-25 23:08: 완전 실패

**증상**:
```
❌ Past Day 설정 - 완전 실패
❌ Generate 버튼 - 실패 (Enter 키로만 시도)
❌ 실제 보고서 생성 - 실패 (5분 대기 후 타임아웃)
❌ 데이터 추출 - 실패 (MuiTable 에러만 추출)
```

**에러 메시지**:
```html
<table class="MuiTable-root">
  <tbody>
    <tr>
      <td colspan="4">No documents found in your private data room.</td>
    </tr>
  </tbody>
</table>
```

**기대했던 결과**:
```html
<div class="supersearchx-body ...">
  실제 주식 데이터와 분석 내용
  완전한 테이블 구조
</div>
```

**근본 원인**:
1. **리포트 완료 대기 로직 누락** - 5분 blind wait 후 바로 추출 시도
2. **Archive 상태 확인 안함** - 실제로 완료됐는지 검증 없음
3. **기존 성공 코드 무시** - 새 파일만 계속 생성

**Git 커밋 메시지에서**:
```
"Past Day 설정 완전 실패 (사용자가 100번 말했는데도 안했음)"
"Generate 버튼 못찾고 Enter로만 시도"
"기존 자료 안찾고 새로 만들기만 함 (골백번 지시했는데도 무시)"
```

**교훈**:
- ✅ 기존 성공 코드부터 먼저 확인
- ✅ Archive 페이지로 실제 상태 검증
- ✅ Blind wait 대신 active polling

---

### 2025-08-20 11:17: 성공 ✅

**결과**:
```
✅ 6개 리포트 생성 성공
✅ Report IDs: 1198, 1199, 1200, 1201, 1202, 1203
✅ 로그인 → Generate → URL 확인 모두 성공
```

**로그 파일**: `real_terminalx_20250820_111715.log`

**성공 요인**:
1. **Archive 페이지 모니터링** - 30분 동안 상태 폴링
2. **"GENERATED" 상태 확인** - 실제 완료 확인
3. **완료 후 데이터 추출** - 타이밍 정확함

**유일한 문제**:
```
⚠️ 아카이브에서 완료 대기 타임아웃
⚠️ 완료된 보고서를 찾을 수 없음
```

**이유**: 폴링 로직은 있었지만 타임아웃 너무 짧음

**교훈**:
- ✅ 기본 워크플로우는 완벽히 작동
- ✅ Archive 폴링이 핵심
- ✅ 타임아웃만 조정하면 됨

---

## 일반적인 문제

### 문제 1: 로그인 실패

**증상**:
```
❌ 로그인 타임아웃: 로그인 페이지 로드 또는 로그인 후 리다이렉트 실패
❌ 로그인 요소를 찾을 수 없습니다
```

**해결책**:
```python
# browser_controller.py:82-117 사용
def login_terminalx(self):
    self.driver.get("https://theterminalx.com/agent/enterprise")

    # 로그인 버튼 클릭
    login_button = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in')]"))
    )
    login_button.click()

    # 자격 증명 입력
    email_input = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter your email']"))
    )
    email_input.send_keys(self.username)
    password_input.send_keys(self.password)

    # 로그인 실행
    login_submit.click()

    # 성공 확인
    WebDriverWait(self.driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Subscriptions')]"))
    )
```

**확인 사항**:
1. 자격 증명: `../../secrets/my_sensitive_data.md`
2. ChromeDriver 버전 호환성
3. 네트워크 연결 상태

---

### 문제 2: Past Day 설정 실패

**증상**:
```
❌ Past Day 설정 요소를 찾지 못했습니다
❌ Custom Report Builder 버튼 없음
```

**해결책**:
```python
# free_explorer.py:317-335 정확한 로직
def set_past_day_properly(self):
    # 다양한 셀렉터로 시도
    period_selectors = [
        "//select[contains(@name, 'period')]",
        "//button[contains(text(), 'Past Day')]",
        "//div[contains(@class, 'date')]//select"
    ]

    for selector in period_selectors:
        elements = self.driver.find_elements(By.XPATH, selector)
        for elem in elements:
            if elem.is_displayed():
                # Any Time 클릭
                if 'Any Time' in elem.text or 'Past Day' in elem.text:
                    elem.click()
                    time.sleep(2)

                    # 드롭다운 열림 확인
                    if 'Past' in page_source_after:
                        # Past Day 옵션 찾아서 클릭
                        past_options = self.driver.find_elements(
                            By.XPATH, "//*[contains(text(), 'Past Day')]"
                        )
                        for option in past_options:
                            if option.is_displayed():
                                option.click()
                                return True
```

**코드 위치**: `free_explorer.py:317-335`

---

### 문제 3: Generate 버튼 못찾음

**증상**:
```
❌ Generate 버튼을 찾을 수 없습니다
⌨️ Enter 키로 제출 시도
```

**해결책**:
```python
# terminalx_6reports_fixed.py:264-300
def click_generate_properly(self):
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
        elements = self.driver.find_elements(By.XPATH, selector)
        for elem in elements:
            if elem.is_displayed() and elem.is_enabled():
                elem.click()
                return True

    # 최후의 수단: Enter 키
    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.RETURN)
```

---

### 문제 4: 리포트 완료 대기 실패 ← 핵심!

**증상**:
```
❌ 5분 대기 후 "No documents found"
❌ supersearchx-body 클래스 없음
❌ MuiTable 에러만 추출됨
```

**근본 원인**:
```python
# 잘못된 방법 (현재)
await page.wait_for_timeout(300000)  # 5분 blind wait
html = extract_html()  # 아직 완료 안됐는데 추출 시도
```

**올바른 해결책**:
```python
# quick_archive_check.py:156-198 사용
def wait_for_completion(report_id, timeout_seconds=300, poll_interval=5):
    """Archive 페이지를 폴링하여 'Generated' 상태 확인"""
    start_time = time.time()

    while (time.time() - start_time) < timeout_seconds:
        # Archive 페이지로 이동
        self.driver.get('https://terminalx.com/reports/archive')

        # 리포트 상태 확인
        row_selector = f'tr[data-report-id="{report_id}"]'
        status_element = self.driver.find_element(By.CSS_SELECTOR,
            f'{row_selector} td.status-column')
        status = status_element.text.strip()

        if status == 'Ready' or status == 'Generated':
            return True  # 완료!
        elif status == 'Failed':
            raise Exception(f"Report {report_id} failed")

        # 다시 확인
        time.sleep(poll_interval)

    return False  # 타임아웃
```

**사용 예시**:
```python
# 1. 리포트 생성 요청
report_id = submit_report_request()

# 2. 완료 대기 (핵심!)
success = wait_for_completion(report_id, timeout_seconds=300)

# 3. 완료된 경우에만 추출
if success:
    html = extract_html()  # 이제 supersearchx-body 있음
else:
    print("타임아웃: 리포트 생성 실패")
```

**코드 위치**: `quick_archive_check.py:156-198`

---

## 작동하는 코드 위치

### 핵심 기능별 코드

| 기능 | 파일 | 줄 번호 | 상태 |
|------|------|---------|------|
| **로그인** | `main_generator.py` | 45-78 | ✅ 작동 |
| **브라우저 설정** | `main_generator.py` | 25-43 | ✅ 작동 |
| **브라우저 제어** | `browser_controller.py` | 전체 | ✅ 작동 |
| **Past Day 설정** | `free_explorer.py` | 317-335 | ✅ 작동 |
| **Archive 상태 확인** | `quick_archive_check.py` | 156-198 | ✅ 작동 |
| **Archive 모니터링** | `report_manager.py` | 53-117 | ✅ 작동 |
| **전체 워크플로우** | `main_generator.py` | 228-480 | ✅ 2025-08-20 성공 |

### Quick Reference

```bash
# 로그인
cat main_generator.py | sed -n '45,78p'

# Past Day 설정
cat free_explorer.py | sed -n '317,335p'

# Archive 확인
cat quick_archive_check.py | sed -n '156,198p'

# 전체 워크플로우
cat main_generator.py | sed -n '228,480p'
```

---

## 디버깅 방법

### 방법 1: 디버깅 모드 실행

```bash
python main_generator.py --debug
```

**출력**:
```
=== 디버깅 테스트: 로그인 및 리다이렉션 확인 ===
로그인 성공. 폼 페이지 접근 테스트 시작...
폼 URL로 이동: https://theterminalx.com/agent/enterprise/report/form/10
도착한 URL: https://theterminalx.com/agent/enterprise/report/form/10
✅ 폼 페이지 접근 성공
✅ Report Title 필드 발견
```

**문제 발생 시**:
```
도착한 URL: https://theterminalx.com/agent/enterprise/report/archive
❌ 아카이브 페이지로 리다이렉션됨 - 문제 확인
```

### 방법 2: 로그 파일 확인

```bash
# 최근 로그 확인
cat browser_controller_20250825_230823.log

# 성공 로그 비교
cat real_terminalx_20250820_111715.log
```

**찾을 내용**:
- 로그인 성공/실패
- URL 리다이렉션
- 요소 찾기 성공/실패
- 타임아웃 발생

### 방법 3: 브라우저 실시간 확인

```python
# browser_controller.py 활용
from browser_controller import BrowserController

bc = BrowserController()
bc.start_browser()
bc.login_terminalx()

# 브라우저가 열린 상태로 수동 확인
input("Press Enter to continue...")
```

**확인 사항**:
1. 실제로 로그인 됐는가?
2. Past Day 설정 UI가 보이는가?
3. Generate 버튼이 존재하는가?
4. Archive 페이지에 리포트가 보이는가?

### 방법 4: UI 구조 분석

```bash
# TerminalX UI 구조 확인
cat terminalx_analysis/analysis_20250823_001656.json
```

**발견 가능한 정보**:
- 버튼 목록 (17개)
- 입력 필드 (textarea, file input)
- Custom Report Builder 버튼 존재 확인

---

## 빠른 체크리스트

### 실행 전 확인
- [ ] ChromeDriver 존재: `chromedriver.exe`
- [ ] 자격 증명 확인: `../../secrets/my_sensitive_data.md`
- [ ] 의존성 설치: `pip install selenium pyperclip beautifulsoup4`

### 실행 중 확인
- [ ] 로그인 성공 (Subscriptions 버튼 보임)
- [ ] Past Day 설정 성공 (드롭다운 변경 확인)
- [ ] Generate 버튼 클릭 성공
- [ ] Archive 페이지에서 "Generating..." 확인
- [ ] "Generated" 상태로 변경 확인
- [ ] supersearchx-body HTML 추출 확인

### 실행 후 확인
- [ ] 출력 파일 존재: `terminalx_6reports_output/*.html`
- [ ] 파일 크기 > 1KB (1,057 bytes가 아님)
- [ ] supersearchx-body 클래스 포함
- [ ] "No documents found" 없음

---

## 긴급 복구

### 완전히 막혔을 때

**Step 1: 성공 코드로 돌아가기**
```bash
# 2025-08-20 성공 버전 확인
git log --oneline | grep "2025-08-20"
git show [commit-hash]:main_generator.py > main_generator_20250820.py
```

**Step 2: 최소 테스트**
```bash
# 로그인만 테스트
python -c "
from browser_controller import BrowserController
bc = BrowserController()
bc.start_browser()
print('Success!' if bc.login_terminalx() else 'Failed!')
"
```

**Step 3: 단계별 테스트**
1. 로그인 성공?
2. 폼 페이지 접근?
3. Past Day 설정?
4. Generate 클릭?
5. Archive 확인?

---

**작성자**: Claude Code (fenomeno-auto-v8)
**참조**: `MASTER_GUIDE.md`, `docs/ARCHITECTURE.md`
**마지막 업데이트**: 2025-10-06
