# Phase 2: To-Be 설계 - Archive 상태 확인 로직

**작성일**: 2025-10-07
**기반**: Phase 1 분석 결과 + 기존 코드 (quick_archive_check.py, CLAUDE.md)

## 🎯 설계 목표

**핵심 요구사항**:
1. Archive 페이지에서 리포트 상태를 실시간 확인
2. GENERATING → GENERATED 전환 감지
3. 최신 리포트 (tr[1]) 식별 및 상태 추적
4. 브라우저 창 위치 제어 (primary monitor)

## 📋 기존 코드 분석

### quick_archive_check.py (lines 183-200)
```python
def _find_generated_reports(self):
    """Generated 상태인 보고서들 찾기"""
    generated_reports = []

    # 보고서 행들 찾기
    report_rows = self.driver.find_elements(By.XPATH, "//tr | //div[contains(@class, 'report')]")

    for row in report_rows:
        row_text = row.text.lower()

        # Generated 상태 확인
        if "generated" in row_text:
            links = row.find_elements(By.XPATH, ".//a[contains(@href, '/report/')]")
            if links:
                report_url = links[0].get_attribute('href')
                generated_reports.append(report_url)

    return generated_reports
```

**문제점**:
- "generated" 문자열 포함 확인만 함 (소문자 변환 후)
- 사용자 피드백: "ting", "ted" 텍스트 (GENERATING, GENERATED?)
- td[4] 위치 확인 안함

### CLAUDE.md 제안 (lines 43-54)
```python
def _wait_for_completion(self, report_id, timeout=300):
    """Archive 완료 대기"""
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        self.driver.get('https://terminalx.com/reports/archive')
        status = self._check_status(report_id)
        if status == 'Ready' or status == 'Generated':
            return True
        elif status == 'Failed':
            return False
        time.sleep(5)
    return False
```

**개선점**:
- 폴링 로직 (5초마다 확인)
- timeout 설정 (300초 = 5분)
- report_id 기반 추적

## 🏗️ To-Be 아키텍처

### 1. 브라우저 창 위치 제어

```python
def setup_browser(self):
    """브라우저 설정 - primary monitor 고정"""
    service = Service(executable_path=self.chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    self.driver = webdriver.Chrome(service=service, options=options)
    self.driver.set_page_load_timeout(60)

    # Primary monitor 좌상단 위치
    self.driver.set_window_position(0, 0)
    self.driver.set_window_size(1920, 1080)

    print("[OK] 브라우저 설정 완료 (primary monitor)")
```

### 2. Archive 상태 확인 로직

**핵심 원리**:
- 최신 리포트 = `//table/tbody/tr[1]` (최상단)
- 리포트 제목으로 식별
- td[4]에서 Status 추출

```python
def check_report_status(self, report_title):
    """특정 리포트의 상태 확인

    Args:
        report_title: 리포트 제목 (식별용)

    Returns:
        str: 'GENERATING', 'GENERATED', 'FAILED', 'NOT_FOUND'
    """
    try:
        # Archive 페이지 이동
        self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")
        time.sleep(3)

        # 최상단 리포트 확인
        first_row = self.driver.find_element(By.XPATH, "//table/tbody/tr[1]")

        # 제목 확인 (td[1])
        title_cell = first_row.find_element(By.XPATH, ".//td[1]")
        title_text = title_cell.text.strip()

        # 상태 확인 (td[4])
        status_cell = first_row.find_element(By.XPATH, ".//td[4]")
        status_text = status_cell.text.strip().upper()

        print(f"[DEBUG] Title: '{title_text}', Status: '{status_text}'")

        # 제목 일치 확인
        if report_title not in title_text:
            print(f"[WARNING] 최상단 리포트가 '{report_title}'이 아님")
            return 'NOT_FOUND'

        # 상태 매칭
        if 'GENERAT' in status_text and 'ING' in status_text:
            return 'GENERATING'
        elif 'GENERAT' in status_text and 'ED' in status_text:
            return 'GENERATED'
        elif 'FAIL' in status_text:
            return 'FAILED'
        else:
            print(f"[WARNING] 알 수 없는 상태: '{status_text}'")
            return status_text

    except Exception as e:
        print(f"[ERROR] 상태 확인 실패: {e}")
        return 'ERROR'
```

### 3. 폴링 로직 (완료 대기)

```python
def wait_for_report_completion(self, report_title, timeout=300):
    """리포트 완료 대기 (폴링)

    Args:
        report_title: 리포트 제목
        timeout: 최대 대기 시간 (초)

    Returns:
        bool: 성공 여부
    """
    print(f"[INFO] '{report_title}' 완료 대기 시작 (timeout: {timeout}초)")

    start_time = time.time()
    check_count = 0

    while (time.time() - start_time) < timeout:
        check_count += 1
        elapsed = int(time.time() - start_time)

        print(f"[CHECK #{check_count}] 경과: {elapsed}초")

        status = self.check_report_status(report_title)

        if status == 'GENERATED':
            print(f"[SUCCESS] '{report_title}' 생성 완료!")
            return True
        elif status == 'FAILED':
            print(f"[ERROR] '{report_title}' 생성 실패!")
            return False
        elif status == 'GENERATING':
            print(f"[INFO] 생성 중... (5초 후 재확인)")
            time.sleep(5)
        else:
            print(f"[WARNING] 예상치 못한 상태: '{status}'")
            time.sleep(5)

    print(f"[TIMEOUT] {timeout}초 초과, 완료 대기 실패")
    return False
```

### 4. 전체 워크플로우

```python
def verify_report_generation_flow(self):
    """리포트 생성 → 대기 → 완료 확인 전체 플로우"""
    try:
        # 1. 로그인
        if not self.login():
            return False

        # 2. 리포트 생성 요청 (예시 - 실제는 다를 수 있음)
        print("\n=== 리포트 생성 요청 ===")
        report_title = "Test Report " + datetime.now().strftime("%Y%m%d_%H%M%S")

        # 여기서 실제 리포트 생성 로직 실행
        # self._submit_report(report_title)

        # 3. Archive 완료 대기
        print("\n=== Archive 완료 대기 ===")
        success = self.wait_for_report_completion(report_title, timeout=300)

        if success:
            # 4. 완료된 리포트 HTML 추출
            print("\n=== 리포트 HTML 추출 ===")
            html = self._extract_report_html(report_title)

            # 5. HTML 검증
            if 'supersearchx-body' in html:
                print("[OK] HTML 추출 성공 (supersearchx-body 포함)")
                return True
            else:
                print("[ERROR] HTML 추출 실패 (supersearchx-body 없음)")
                return False
        else:
            print("[ERROR] 리포트 생성 실패 또는 타임아웃")
            return False

    except Exception as e:
        print(f"[ERROR] 전체 플로우 실패: {e}")
        return False
```

## 📊 Status 텍스트 매칭 규칙

**사용자 피드백 기반**:
- "ting" → GENERATING
- "ted" → GENERATED

**예상 전체 텍스트**:
- "Generating" 또는 "GENERATING"
- "Generated" 또는 "GENERATED"
- "Failed" 또는 "FAILED"
- "Pending" 또는 "PENDING"

**매칭 전략**:
1. `.upper()` 로 대문자 변환
2. `'GENERAT' in status_text` 로 포함 확인
3. `'ING' in status_text` vs `'ED' in status_text` 로 구분

## 🔍 Past Day 드롭다운 검증

**free_explorer.py:317-335 로직 확인 필요**:
```python
# 예상 로직
def set_past_day(self, days):
    """Past Day 드롭다운 설정"""
    # 드롭다운 열기
    dropdown = self.driver.find_element(By.XPATH, "//select[@id='past-day'] | //div[@role='combobox']")
    dropdown.click()

    # 옵션 선택
    option = self.driver.find_element(By.XPATH, f"//option[contains(., '{days}')] | //div[contains(., '{days} days')]")
    option.click()

    # 적용 확인
    time.sleep(2)
```

**검증 방법**:
1. 드롭다운 요소 XPath 확인
2. 선택 후 실제 적용 확인 (페이지 변화 또는 쿼리 파라미터)

## 📈 개선 사항

### 기존 코드 대비
1. ✅ 브라우저 창 위치 제어 (primary monitor)
2. ✅ 최신 리포트 추적 (tr[1])
3. ✅ 정확한 Status 매칭 (td[4])
4. ✅ 폴링 로직 (5초 간격, timeout)
5. ✅ 디버그 로깅 (경과 시간, 체크 횟수)

### 추가 필요 사항
- ⏸️ Past Day 드롭다운 검증
- ⏸️ 리포트 HTML 추출 로직
- ⏸️ supersearchx-body 검증

## 🚀 다음 단계 (Phase 3: Master Plan)

**Master Plan 생성 항목**:
1. verify_system.py 개선
   - 브라우저 창 위치 추가
   - Archive 상태 확인 로직 추가
   - 폴링 로직 추가

2. Past Day 검증 스크립트
   - free_explorer.py:317-335 확인
   - 드롭다운 XPath 검증
   - 실제 적용 확인

3. 전체 플로우 테스트
   - 로그인 → 리포트 생성 요청 → 대기 → HTML 추출

## 사용자 승인 대기

이 설계안으로 Phase 3 (Master Plan) 작성해도 될까요?
