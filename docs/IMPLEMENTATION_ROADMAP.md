# 100xFenok-Generator: Implementation Roadmap

**Date**: 2025-10-07
**Status**: Ready for Execution

---

## Quick Reference

```
Current State: ❌ 20% success rate (missing Archive completion check)
Target State:  ✅ 95% success rate (5-hour Quick Fix)
Long-term:     ✅ 99% success rate (5-day Full Refactor)

Critical Path: Archive Monitor Integration → 95% success
Timeline:      5 hours (Quick Fix) → 5 days (Full Refactor)
Risk:          🟢 Low (proven logic exists)
```

---

## Phase 1: Quick Fix (5 Hours)

### Hour 1-2: Extract and Integrate Archive Monitor

#### Task 1.1: Extract Archive Monitoring Logic
```python
# SOURCE: quick_archive_check.py:156-198
# DESTINATION: main_generator.py (new method)

def _wait_for_archive_completion(self, report_id: str, timeout: int = 300) -> bool:
    """
    Poll Archive page until report status is 'GENERATED' or 'FAILED'.

    Args:
        report_id: Report ID to monitor (extracted from URL)
        timeout: Maximum wait time in seconds (default 300 = 5 minutes)

    Returns:
        True if report generated successfully, False otherwise
    """
    start_time = time.time()

    while (time.time() - start_time) < timeout:
        # Navigate to Archive page
        self.driver.get('https://theterminalx.com/agent/enterprise/report/archive')

        # Wait for page load
        time.sleep(3)

        # Wait for JavaScript rendering (critical!)
        time.sleep(7)

        try:
            # Wait for table to appear
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//table/tbody"))
            )

            # Poll for table rows (max 5 attempts)
            rows = []
            for attempt in range(5):
                rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
                if len(rows) > 0:
                    break
                time.sleep(2)

            if len(rows) == 0:
                print(f"[Archive Monitor] No rows found, retrying...")
                time.sleep(5)
                continue

            # Find our report in the table
            for row in rows[:10]:  # Check recent 10 reports
                try:
                    # Column 1: Report title/ID
                    # Column 4: Status
                    title_elem = row.find_element(By.XPATH, ".//td[1]")
                    status_elem = row.find_element(By.XPATH, ".//td[4]")

                    # Check if this is our report (by ID in URL or title)
                    row_text = title_elem.text.strip()
                    if report_id in row_text or report_id in title_elem.get_attribute('innerHTML'):
                        status = status_elem.text.strip().upper()

                        if status == "GENERATED":
                            print(f"[Archive Monitor] Report {report_id} completed successfully!")
                            return True
                        elif status == "FAILED":
                            print(f"[Archive Monitor] Report {report_id} generation failed!")
                            return False
                        elif status == "GENERATING":
                            print(f"[Archive Monitor] Report {report_id} still generating...")
                            # Continue polling
                        else:
                            print(f"[Archive Monitor] Unknown status: {status}")

                except NoSuchElementException:
                    continue

        except TimeoutException:
            print(f"[Archive Monitor] Archive page load timeout, retrying...")

        # Wait before next poll
        time.sleep(5)

    print(f"[Archive Monitor] Timeout after {timeout} seconds")
    return False
```

**Deliverable**: New method in `main_generator.py` (lines ~1010-1080)

#### Task 1.2: Extract Report ID from URL
```python
def _extract_report_id_from_url(self, report_url: str) -> str:
    """
    Extract report ID from TerminalX report URL.

    Example: https://theterminalx.com/agent/enterprise/report/1234 → "1234"
    """
    import re
    match = re.search(r'/report/(\d+)', report_url)
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Could not extract report ID from URL: {report_url}")
```

**Deliverable**: New method in `main_generator.py` (lines ~1008-1015)

### Hour 3: Integrate into Main Workflow

#### Task 3.1: Modify generate_report_html()
```python
# LOCATION: main_generator.py:272-524
# MODIFICATION: Add after line 506 (after "Generating your report" message)

def generate_report_html(self, report: Report, report_date_str: str,
                        ref_date_start_str: str, ref_date_end_str: str):
    """
    TerminalX에서 보고서를 생성하고, 완료될 때까지 대기한 후 URL과 제목을 반환합니다.
    """
    # ... existing code (lines 272-505) ...

    # 2단계: "Generating..." 메시지 등장 대기 (리포트 생성 시작 확인)
    print("  - 'Generating your report' 메시지 등장 대기 중...")
    WebDriverWait(self.driver, 60).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Generating your report (it may take up to 5 minutes).')]"))
    )
    print("  - 'Generating your report' 메시지 등장 확인. 리포트 생성 시작됨.")

    report.url = generated_report_url
    report.status = "GENERATING"

    # ===== NEW CODE STARTS HERE =====
    # 3단계: Archive 페이지에서 완료 대기 (CRITICAL NEW STEP!)
    print("  - Archive 페이지에서 완료 상태 모니터링 시작...")
    try:
        report_id = self._extract_report_id_from_url(generated_report_url)
        print(f"  - Report ID 추출 완료: {report_id}")

        success = self._wait_for_archive_completion(report_id, timeout=300)

        if not success:
            print(f"  - [ERROR] Report {report_id} 완료 대기 실패 (타임아웃 또는 생성 실패)")
            report.status = "FAILED"
            return False

        print(f"  - [SUCCESS] Report {report_id} 생성 완료 확인!")
        report.status = "GENERATED"
        return True

    except Exception as e:
        print(f"  - [ERROR] Archive 모니터링 중 예외 발생: {e}")
        report.status = "FAILED"
        return False
    # ===== NEW CODE ENDS HERE =====
```

**Deliverable**: Modified `generate_report_html()` with Archive completion check

### Hour 4: Testing and Validation

#### Test Plan
```bash
# Test 1: Single Report Generation
cd C:\Users\etlov\agents-workspace\projects\100xFenok-generator
python -c "
from main_generator import FenokReportGenerator
import json

generator = FenokReportGenerator()
config = json.load(open('six_reports_config.json'))[0]
result = generator.generate_single_report(config)
print(f'Test 1 Result: {result}')
"

# Test 2: Archive Monitor Timeout
python -c "
from main_generator import FenokReportGenerator
generator = FenokReportGenerator()
# Test with non-existent report ID
result = generator._wait_for_archive_completion('9999999', timeout=30)
assert result == False, 'Timeout test failed'
print('Test 2 Passed: Timeout handled correctly')
"

# Test 3: Two Reports Sequential
python test_two_reports.py
```

#### Validation Checklist
```
✅ Archive monitor extracts report ID correctly
✅ Archive page loads and table renders
✅ Status polling works (every 5 seconds)
✅ "GENERATED" status detected correctly
✅ Timeout after 5 minutes if not completed
✅ HTML extraction only occurs AFTER completion
✅ supersearchx-body class present in extracted HTML
✅ No "No documents found" errors
```

### Hour 5: Documentation and Handoff

#### Update Documentation
```markdown
# File: EXECUTION_GUIDE.md (UPDATE)

## Running the Fixed Generator

### Quick Start
```bash
cd C:\Users\etlov\agents-workspace\projects\100xFenok-generator
python main_generator.py
```

### What Changed (2025-10-07 Fix)
- Added Archive completion monitoring (critical fix)
- Reports now wait for "GENERATED" status before extraction
- Eliminates "No documents found" errors
- Success rate improved from 20% to 95%+

### Expected Behavior
1. Login to TerminalX (30 seconds)
2. For each of 6 reports:
   - Submit report form (30 seconds)
   - Wait for "Generating..." message (10 seconds)
   - **NEW**: Poll Archive page until "GENERATED" (2-5 minutes)
   - Extract HTML with supersearchx-body (10 seconds)
   - Convert to JSON (5 seconds)
3. Total time: 18-36 minutes for all 6 reports

### Success Indicators
- Console shows: "[Archive Monitor] Report XXXX completed successfully!"
- HTML files contain supersearchx-body class
- JSON files have complete section data
- No "No documents found" errors
```

---

## Phase 2: Full Refactor (5 Days)

### Day 1: Core Infrastructure

#### Morning: Browser Session Management
```python
# NEW FILE: core/browser_session.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os

class BrowserSession:
    """Centralized browser lifecycle management"""

    def __init__(self, project_dir: str, headless: bool = False):
        self.project_dir = project_dir
        self.headless = headless
        self.driver = None

    def start(self):
        """Initialize ChromeDriver with standard settings"""
        chromedriver_path = os.path.join(self.project_dir, 'chromedriver.exe')
        service = Service(executable_path=chromedriver_path)
        options = webdriver.ChromeOptions()

        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_page_load_timeout(60)

        # Position on left FHD monitor
        self.driver.set_window_position(-1920, 0)
        self.driver.maximize_window()

        return self.driver

    def close(self):
        """Clean shutdown of browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

#### Afternoon: Authentication Module
```python
# NEW FILE: core/authentication.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TerminalXAuth:
    """TerminalX authentication handler"""

    def __init__(self, driver):
        self.driver = driver

    def login(self, username: str, password: str) -> bool:
        """
        Login to TerminalX with multi-fallback selector strategy.

        Returns:
            True if login successful, False otherwise
        """
        try:
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(5)

            # Step 1: Find login button (multiple selectors)
            login_btn = self._find_element_with_fallback([
                "//button[contains(text(), 'Log in')]",
                "//button[contains(., 'Log in')]",
                "//a[contains(text(), 'Log in')]",
                "//button[contains(@class, 'login')]",
            ])

            if not login_btn:
                return False

            login_btn.click()
            time.sleep(3)

            # Step 2: Find email input
            email_input = self._find_element_with_fallback([
                "//input[@placeholder='Enter your email']",
                "//input[@type='email']",
                "//input[@name='email']",
            ])

            if not email_input:
                return False

            # Step 3: Find password input
            password_input = self._find_element_with_fallback([
                "//input[@placeholder='Enter your password']",
                "//input[@type='password']",
                "//input[@name='password']",
            ])

            if not password_input:
                return False

            # Step 4: Enter credentials
            email_input.clear()
            email_input.send_keys(username)
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(2)

            # Step 5: Submit login
            login_submit = self._find_element_with_fallback([
                "//button[contains(text(), 'Continue')]",
                "//button[contains(text(), 'Log In')]",
                "//button[@type='submit']",
            ])

            if not login_submit:
                return False

            login_submit.click()

            # Step 6: Verify success
            success = self._verify_login_success()
            return success

        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def _find_element_with_fallback(self, selectors: list):
        """Try multiple selectors until one works"""
        for selector in selectors:
            try:
                element = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                return element
            except:
                continue
        return None

    def _verify_login_success(self) -> bool:
        """Verify login succeeded by checking for dashboard elements"""
        success_selectors = [
            "//button[contains(., 'Subscriptions')]",
            "//div[contains(@class, 'dashboard')]",
            "//button[contains(., 'Archive')]",
        ]

        for selector in success_selectors:
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                return True
            except:
                continue

        return False
```

**Deliverables**:
- ✅ `core/browser_session.py` (80 lines)
- ✅ `core/authentication.py` (120 lines)
- ✅ Unit tests for both modules

### Day 2: TerminalX Domain Logic

#### Morning: Report Generator
```python
# NEW FILE: terminalx/report_generator.py
from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class ReportConfig:
    """Report configuration from six_reports_config.json"""
    name: str
    keywords: str
    urls: list
    past_day: int
    prompt: str

class ReportGenerator:
    """Handles report submission workflow"""

    def __init__(self, driver):
        self.driver = driver

    def submit_report(self, config: ReportConfig,
                     ref_date_start: str,
                     ref_date_end: str) -> Optional[str]:
        """
        Submit report form to TerminalX.

        Returns:
            Report URL if successful, None otherwise
        """
        # Navigate to report form
        form_url = "https://theterminalx.com/agent/enterprise/report/form/10"
        self.driver.get(form_url)
        time.sleep(3)

        # Check for redirects
        if not self._handle_redirects(form_url):
            return None

        # Fill form fields
        if not self._fill_report_title(config.name):
            return None

        if not self._fill_date_range(ref_date_start, ref_date_end):
            return None

        if not self._upload_sample_report():
            return None

        if not self._fill_prompt(config.prompt):
            return None

        # Submit
        report_url = self._click_generate()
        return report_url

    def _handle_redirects(self, expected_url: str) -> bool:
        """Handle archive page redirects"""
        # Implementation from main_generator.py:322-427
        pass

    def _fill_report_title(self, title: str) -> bool:
        """Fill report title field"""
        # Implementation from main_generator.py:432-442
        pass

    def _fill_date_range(self, start: str, end: str) -> bool:
        """Fill date range using hybrid method"""
        # Implementation from main_generator.py:445-449
        pass

    def _upload_sample_report(self) -> bool:
        """Upload sample report PDF"""
        # Implementation from main_generator.py:451-463
        pass

    def _fill_prompt(self, prompt: str) -> bool:
        """Fill prompt textarea"""
        # Implementation from main_generator.py:465-471
        pass

    def _click_generate(self) -> Optional[str]:
        """Click generate button and capture URL"""
        # Implementation from main_generator.py:478-495
        pass
```

#### Afternoon: Archive Monitor (Clean Implementation)
```python
# NEW FILE: terminalx/archive_monitor.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

class ArchiveMonitor:
    """Monitors Archive page for report completion"""

    def __init__(self, driver):
        self.driver = driver
        self.archive_url = "https://theterminalx.com/agent/enterprise/report/archive"

    def wait_for_completion(self, report_id: str, timeout: int = 300) -> bool:
        """
        Poll Archive page until report is completed or failed.

        Args:
            report_id: Report ID to monitor
            timeout: Maximum wait time in seconds

        Returns:
            True if completed successfully, False if failed or timeout
        """
        start_time = time.time()
        poll_interval = 5

        while (time.time() - start_time) < timeout:
            status = self._check_status(report_id)

            if status == "GENERATED":
                return True
            elif status == "FAILED":
                return False
            elif status == "GENERATING":
                pass  # Continue polling
            else:
                pass  # Unknown status, continue polling

            time.sleep(poll_interval)

        return False  # Timeout

    def _check_status(self, report_id: str) -> str:
        """
        Check current status of report in Archive table.

        Returns:
            "GENERATED", "FAILED", "GENERATING", or "NOT_FOUND"
        """
        try:
            # Navigate to Archive
            self.driver.get(self.archive_url)

            # Wait for page load
            time.sleep(3)

            # Wait for JavaScript rendering
            time.sleep(7)

            # Wait for table
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//table/tbody"))
            )

            # Poll for rows
            rows = self._wait_for_table_rows()

            if not rows:
                return "NOT_FOUND"

            # Find our report
            for row in rows[:10]:
                try:
                    title_elem = row.find_element(By.XPATH, ".//td[1]")
                    status_elem = row.find_element(By.XPATH, ".//td[4]")

                    row_text = title_elem.text.strip()

                    if report_id in row_text or report_id in title_elem.get_attribute('innerHTML'):
                        return status_elem.text.strip().upper()

                except NoSuchElementException:
                    continue

            return "NOT_FOUND"

        except TimeoutException:
            return "NOT_FOUND"
        except Exception as e:
            print(f"Archive check error: {e}")
            return "NOT_FOUND"

    def _wait_for_table_rows(self, max_attempts: int = 5) -> list:
        """Wait for table rows to render"""
        for attempt in range(max_attempts):
            rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
            if len(rows) > 0:
                return rows
            time.sleep(2)
        return []
```

**Deliverables**:
- ✅ `terminalx/report_generator.py` (300 lines)
- ✅ `terminalx/archive_monitor.py` (150 lines)
- ✅ `terminalx/html_extractor.py` (100 lines)
- ✅ Integration tests

### Day 3: Generator Layer

#### Six Reports Generator
```python
# NEW FILE: generators/six_reports_generator.py
from core.browser_session import BrowserSession
from core.authentication import TerminalXAuth
from terminalx.report_generator import ReportGenerator
from terminalx.archive_monitor import ArchiveMonitor
from terminalx.html_extractor import HTMLExtractor
from data.html_to_json import HTMLToJSON
import json
import os

class SixReportsGenerator:
    """Main orchestrator for 6-report generation"""

    def __init__(self, project_dir: str, secrets_file: str):
        self.project_dir = project_dir
        self.secrets_file = secrets_file
        self.browser = None
        self.driver = None

    def generate_all(self) -> list:
        """Generate all 6 reports sequentially"""
        # Load config
        config_path = os.path.join(self.project_dir, 'six_reports_config.json')
        with open(config_path, 'r') as f:
            configs = json.load(f)

        # Load credentials
        credentials = self._load_credentials()

        # Start browser
        self.browser = BrowserSession(self.project_dir, headless=False)
        self.driver = self.browser.start()

        try:
            # Login
            auth = TerminalXAuth(self.driver)
            if not auth.login(credentials['username'], credentials['password']):
                raise Exception("Login failed")

            # Generate each report
            results = []
            for config in configs:
                result = self._generate_single_report(config)
                results.append(result)

            return results

        finally:
            self.browser.close()

    def _generate_single_report(self, config: dict) -> dict:
        """Generate single report"""
        # Initialize components
        generator = ReportGenerator(self.driver)
        monitor = ArchiveMonitor(self.driver)
        extractor = HTMLExtractor(self.driver)
        converter = HTMLToJSON()

        # Step 1: Submit report
        report_url = generator.submit_report(config, start_date, end_date)

        if not report_url:
            return {"status": "FAILED", "reason": "submission_failed"}

        # Step 2: Extract report ID
        report_id = self._extract_report_id(report_url)

        # Step 3: Wait for completion (CRITICAL)
        success = monitor.wait_for_completion(report_id, timeout=300)

        if not success:
            return {"status": "FAILED", "reason": "generation_timeout"}

        # Step 4: Extract HTML
        html_path = extractor.extract(report_url, output_dir)

        if not html_path:
            return {"status": "FAILED", "reason": "extraction_failed"}

        # Step 5: Convert to JSON
        json_path = converter.convert(html_path, output_dir)

        if not json_path:
            return {"status": "FAILED", "reason": "conversion_failed"}

        return {
            "status": "SUCCESS",
            "report_url": report_url,
            "html_path": html_path,
            "json_path": json_path
        }
```

**Deliverables**:
- ✅ `generators/six_reports_generator.py` (250 lines)
- ✅ `generators/base_generator.py` (100 lines)
- ✅ End-to-end tests

### Day 4: Testing Suite

#### Test Structure
```
tests/
├── unit/
│   ├── test_browser_session.py
│   ├── test_authentication.py
│   ├── test_report_generator.py
│   ├── test_archive_monitor.py      ← CRITICAL
│   └── test_html_extractor.py
├── integration/
│   ├── test_login_workflow.py
│   ├── test_report_submission.py
│   └── test_full_generation.py
└── e2e/
    └── test_six_reports.py
```

#### Critical Test: Archive Monitor
```python
# tests/unit/test_archive_monitor.py
import pytest
from unittest.mock import Mock, patch
from terminalx.archive_monitor import ArchiveMonitor

def test_completion_detection():
    """Test successful completion detection"""
    driver = Mock()
    monitor = ArchiveMonitor(driver)

    # Mock Archive page with GENERATED status
    with patch.object(monitor, '_check_status', return_value='GENERATED'):
        result = monitor.wait_for_completion('1234', timeout=10)

    assert result == True

def test_failure_detection():
    """Test failure detection"""
    driver = Mock()
    monitor = ArchiveMonitor(driver)

    with patch.object(monitor, '_check_status', return_value='FAILED'):
        result = monitor.wait_for_completion('1234', timeout=10)

    assert result == False

def test_timeout_handling():
    """Test timeout after 5 minutes"""
    driver = Mock()
    monitor = ArchiveMonitor(driver)

    with patch.object(monitor, '_check_status', return_value='GENERATING'):
        result = monitor.wait_for_completion('1234', timeout=10)

    assert result == False

@pytest.mark.integration
def test_real_archive_polling():
    """Integration test with real browser"""
    # This test requires actual TerminalX access
    pass
```

**Deliverables**:
- ✅ 30+ unit tests
- ✅ 10+ integration tests
- ✅ 3 E2E tests
- ✅ Test coverage > 85%

### Day 5: Documentation and CI/CD

#### Documentation Updates
```
docs/
├── ARCHITECTURE.md (UPDATE)
├── API_REFERENCE.md (NEW)
├── DEPLOYMENT_GUIDE.md (NEW)
└── TROUBLESHOOTING_V2.md (NEW)
```

#### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest tests/unit/
      - name: Run integration tests
        run: pytest tests/integration/
      - name: Generate coverage report
        run: pytest --cov=. --cov-report=html
```

**Deliverables**:
- ✅ Complete API documentation
- ✅ Deployment guide
- ✅ CI/CD pipeline
- ✅ Code coverage dashboard

---

## Success Metrics

### Phase 1 (Quick Fix)
```
Metric                    Target      Actual
─────────────────────────────────────────────
Success Rate             ≥ 95%       _____
Avg Time per Report      3-6 min     _____
"No documents" Errors    0           _____
Archive Timeouts         < 5%        _____
User Satisfaction        High        _____
```

### Phase 2 (Full Refactor)
```
Metric                    Target      Actual
─────────────────────────────────────────────
Code Files               12          _____
Code Duplication         < 15%       _____
Test Coverage            > 85%       _____
Build Success Rate       100%        _____
Documentation Complete   Yes         _____
```

---

## Risk Mitigation

### Quick Fix Risks
| Risk | Mitigation |
|------|------------|
| Integration breaks existing workflow | Copy existing file first, test thoroughly |
| Archive page rendering issues | Use proven logic from quick_archive_check.py |
| Timeout too short | Start with 5 minutes, adjust based on data |
| Report ID extraction fails | Multiple regex patterns with fallback |

### Full Refactor Risks
| Risk | Mitigation |
|------|------------|
| Breaking changes during refactor | Feature flag system, gradual rollout |
| Test coverage gaps | Minimum 85% coverage gate in CI/CD |
| Performance regression | Benchmark before/after |
| User confusion with new structure | Clear migration guide + compatibility layer |

---

## Next Steps

### Immediate (Today)
1. ✅ Read this roadmap
2. ✅ Review Quick Fix code samples
3. ⏳ Approve Phase 1 Quick Fix
4. ⏳ Execute Hour 1-2 tasks

### This Week
1. Complete Phase 1 Quick Fix (5 hours)
2. Production testing (2 days)
3. User acceptance testing (2 days)
4. Plan Phase 2 kickoff

### Next Week
1. Execute Phase 2 Full Refactor (5 days)
2. Comprehensive testing
3. Production deployment
4. Monitoring and iteration

---

**Document Status**: Ready for Approval
**Owner**: System Architect
**Approval Required**: User
**Next Review**: After Phase 1 Completion
