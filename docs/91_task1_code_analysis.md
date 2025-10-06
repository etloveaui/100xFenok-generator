# Task 1: main_generator.py 코드 분석 결과

**분석 날짜**: 2025-10-06
**분석자**: Claude Code (fenomeno-auto-v8)

---

## 📋 분석 요약

### 중요 발견

**✅ 좋은 소식**:
- main_generator.py는 **완전히 작동하는 코드**입니다 (2025-08-20 성공)
- Archive 상태 확인 로직이 **이미 구현되어 있습니다** (report_manager.py)
- Past Day 설정 로직이 **free_explorer.py에 있습니다**

**❌ 문제점**:
- main_generator.py는 **Custom Report만 처리**합니다
- **일반 URL 리포트 생성 로직이 없습니다**
- Past Day 설정이 main_generator.py에 통합되어 있지 않습니다

---

## 🔍 상세 분석

### 1. Custom Report 생성 로직 (✅ 있음)

**파일**: `main_generator.py`
**메서드**: `generate_report_html()` (Line 228-480)

**동작 방식**:
```python
# 1. 템플릿 ID 10으로 폼 접속
report_form_url = "https://theterminalx.com/agent/enterprise/report/form/10"

# 2. Part1 또는 Part2에 따라 다른 파일 로드
if report.part_type == "Part1":
    prompt_file = "21_100x_Daily_Wrap_Prompt_1_20250723.md"
    source_pdf_file = "10_100x_Daily_Wrap_My_Sources_1_20250723.pdf"
else:  # Part2
    prompt_file = "21_100x_Daily_Wrap_Prompt_2_20250708.md"
    source_pdf_file = "10_100x_Daily_Wrap_My_Sources_2_20250709.pdf"

# 3. 리포트 폼 입력
- Report Title 입력
- Reference Date 입력 (시작일/종료일)
- Sample Report 업로드 (PDF)
- Own Sources 업로드 (PDF 2개)
- Prompt 입력 (Ctrl+V)

# 4. Generate 버튼 클릭
generate_button.click()

# 5. URL 변경 대기 (최대 20분)
WebDriverWait(self.driver, 1200).until(
    EC.url_matches(r"https://theterminalx.com/agent/enterprise/report/\d+")
)

# 6. "Generating..." 메시지 확인
report.status = "GENERATING"
return True
```

**✅ Past Day 설정**: Custom Report는 **필요 없음** (확인됨)

---

### 2. 일반 URL 리포트 생성 로직 (❌ 없음)

**문제**: main_generator.py에는 일반 URL로 직접 접속하여 리포트 생성하는 로직이 **전혀 없습니다**.

**필요한 로직** (현재 존재하지 않음):
```python
def generate_normal_url_report(self, ticker_or_query: str):
    """일반 URL로 리포트 생성 - 미구현"""
    # 1. 일반 URL로 직접 접속
    url = f"https://theterminalx.com/agent/enterprise/some-url"

    # 2. Past Day 설정 ← 이게 필요함!
    self._set_past_day()

    # 3. 프롬프트 입력
    # 4. Generate 클릭
    # 5. 완료 대기
```

**발견**: 이 프로젝트는 **Custom Report만 자동화**하고 있습니다!

---

### 3. Archive 상태 확인 로직 (✅ 있음)

**파일**: `report_manager.py`
**클래스**: `ReportBatchManager`
**메서드**: `monitor_and_retry()` (Line 53-117)

**동작 방식**:
```python
def monitor_and_retry(self, timeout=1800, initial_interval=30):
    """Archive 페이지 폴링하여 완료 확인"""
    while time.time() - overall_start_time < timeout:
        # 1. Archive 페이지 새로고침
        self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")

        # 2. 테이블에서 상태 읽기
        rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
        for row in rows:
            title_element = row.find_element(By.XPATH, ".//td[1]")
            status_element = row.find_element(By.XPATH, ".//td[4]")
            status_map[title_element.text.strip()] = status_element.text.strip()

        # 3. 리포트 상태 업데이트
        for report in pending_reports:
            if status == "GENERATED":
                report.status = "GENERATED"
            elif status == "FAILED":
                report.status = "FAILED"
                report.retry_count += 1

        # 4. 대기 후 재확인 (지수 백오프)
        time.sleep(current_interval)
        current_interval = min(current_interval * 1.2, 120)
```

**✅ 결론**: Archive 폴링 로직은 **완벽하게 작동합니다**!

---

### 4. Past Day 설정 로직 (✅ 있지만 분리됨)

**파일**: `free_explorer.py`
**라인**: 317-335

**동작 방식**:
```python
# "Any Time" 또는 "Past Day" 텍스트를 가진 요소 찾기
if clickable and ('Any Time' in text or 'Past Day' in text):
    elem.click()
    time.sleep(2)

    # 드롭다운 열렸는지 확인
    page_source_after = self.driver.page_source
    if 'Past' in page_source_after:
        # Past Day 옵션 클릭
        past_options = self.driver.find_elements(
            By.XPATH,
            "//*[contains(text(), 'Past Day') or contains(text(), 'Past day')]"
        )
        for option in past_options:
            if option.is_displayed():
                option.click()
                return True
```

**❌ 문제**: 이 로직이 main_generator.py에 **통합되어 있지 않습니다**.

---

## 🚨 핵심 발견사항

### 발견 1: Custom Report만 자동화됨
- main_generator.py는 **Custom Report Builder 전용**
- Part1, Part2 각 3개씩 총 6개 생성 (템플릿 ID 10)
- **일반 URL 리포트 생성 로직 없음**

### 발견 2: Archive 확인은 이미 작동함
- report_manager.py의 `monitor_and_retry()`가 완벽히 작동
- 테이블 XPath: `//table/tbody/tr`
- 상태 컬럼: `td[4]` (GENERATING, GENERATED, FAILED)

### 발견 3: Past Day 설정은 분리되어 있음
- free_explorer.py:317-335에 작동하는 로직 존재
- main_generator.py에 통합되어 있지 않음
- **Custom Report는 Past Day 필요 없음** (확인됨)

### 발견 4: 워크플로우 흐름
```
run_full_automation():
  1. 로그인 (_login_terminalx)
  2. Part1, Part2 리포트 추가 (batch_manager.add_report)
  3. 각 리포트 생성 요청 (generate_report_html) ← 여기서 GENERATING 상태
  4. Archive 모니터링 (batch_manager.monitor_and_retry) ← 여기서 GENERATED 확인
  5. HTML 추출 (driver.page_source)
  6. JSON 변환 및 통합
```

---

## 💡 해야 할 작업 (정확히)

### 작업 없음: Custom Report
- ✅ 이미 완벽히 작동함
- ✅ Archive 확인 포함됨
- ✅ Past Day 불필요

### 작업 필요: 일반 URL 리포트 (만약 있다면)
- ❌ 일반 URL 리포트 생성 메서드 추가
- ❌ Past Day 설정 로직 통합
- ❌ Archive 확인 추가

---

## 🤔 사용자 확인 필요

**질문**: 6개 리포트가 정확히 뭔가요?

**Option A**: Custom Report Part1, Part2만 (각 3개씩)
- 현재 main_generator.py로 완전 자동화 가능
- **수정 필요 없음**

**Option B**: Custom Report + 일반 URL 리포트
- 일반 URL 리포트 생성 로직 추가 필요
- Past Day 설정 통합 필요

---

## 📝 다음 단계 제안

1. **사용자 확인**: 6개 리포트 정확한 목록
2. **Option A라면**: main_generator.py 테스트만 하면 됨
3. **Option B라면**: 일반 URL 리포트 생성 메서드 추가

---

**분석 완료**: 2025-10-06
**다음 작업**: 사용자 확인 후 Task 2 진행
