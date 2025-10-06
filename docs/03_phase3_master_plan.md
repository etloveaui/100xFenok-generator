# Phase 3: Master Plan - 검증 스크립트 개선 실행 계획

**작성일**: 2025-10-07
**기반**: Phase 1 분석 + Phase 2 설계

## 🎯 Master Plan 개요

**목표**: verify_system.py를 개선하여 Archive 상태 확인 로직 검증

**소요 시간 예상**: 1-2시간

**작업 범위**:
1. verify_system.py 개선 (브라우저 위치 + Archive 상태 확인)
2. Past Day 드롭다운 검증 (선택적)
3. 검증 실행 및 결과 문서화

## 📋 작업 체크리스트

### Task 3.1: verify_system.py 브라우저 위치 제어 추가
**예상 시간**: 10분
**파일**: `verify_system.py`
**변경 위치**: `setup_browser()` 메서드

**변경 내용**:
```python
def setup_browser(self):
    """브라우저 설정"""
    print("브라우저 설정 중...")
    try:
        service = Service(executable_path=self.chromedriver_path)
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_page_load_timeout(60)

        # ✅ 추가: Primary monitor 좌상단 위치
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(1920, 1080)

        print("[OK] 브라우저 설정 완료 (primary monitor)")
        return True
    except Exception as e:
        print(f"[ERROR] 브라우저 설정 실패: {e}")
        return False
```

**검증 방법**:
- 스크립트 실행 시 브라우저가 primary monitor 좌상단에 표시되는지 확인

---

### Task 3.2: Archive 상태 확인 메서드 추가
**예상 시간**: 20분
**파일**: `verify_system.py`
**추가 위치**: `verify_archive_page()` 메서드 다음

**추가 메서드 1: check_report_status()**
```python
def check_report_status(self, report_title):
    """특정 리포트의 상태 확인

    Args:
        report_title: 리포트 제목 (식별용)

    Returns:
        str: 'GENERATING', 'GENERATED', 'FAILED', 'NOT_FOUND', 'ERROR'
    """
    try:
        print(f"[INFO] '{report_title}' 상태 확인 중...")

        # Archive 페이지 이동
        self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")
        time.sleep(3)

        # 테이블 존재 확인
        tbody = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//table/tbody"))
        )

        # 최상단 리포트 확인
        rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
        if len(rows) == 0:
            print("[WARNING] 리포트 없음")
            return 'NOT_FOUND'

        first_row = rows[0]

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
        if 'GENERAT' in status_text:
            if 'ING' in status_text:
                return 'GENERATING'
            elif 'ED' in status_text:
                return 'GENERATED'
        elif 'FAIL' in status_text:
            return 'FAILED'
        elif 'PEND' in status_text:
            return 'PENDING'
        else:
            print(f"[WARNING] 알 수 없는 상태: '{status_text}'")
            return status_text

    except Exception as e:
        print(f"[ERROR] 상태 확인 실패: {e}")
        return 'ERROR'
```

**추가 메서드 2: wait_for_report_completion()**
```python
def wait_for_report_completion(self, report_title, timeout=300):
    """리포트 완료 대기 (폴링)

    Args:
        report_title: 리포트 제목
        timeout: 최대 대기 시간 (초)

    Returns:
        bool: 성공 여부
    """
    print(f"\n=== '{report_title}' 완료 대기 ===")
    print(f"[INFO] Timeout: {timeout}초")

    start_time = time.time()
    check_count = 0

    while (time.time() - start_time) < timeout:
        check_count += 1
        elapsed = int(time.time() - start_time)

        print(f"\n[CHECK #{check_count}] 경과: {elapsed}초")

        status = self.check_report_status(report_title)

        if status == 'GENERATED':
            print(f"[SUCCESS] '{report_title}' 생성 완료! (총 {elapsed}초)")
            return True
        elif status == 'FAILED':
            print(f"[ERROR] '{report_title}' 생성 실패!")
            return False
        elif status == 'GENERATING':
            print(f"[INFO] 생성 중... (5초 후 재확인)")
            time.sleep(5)
        elif status == 'PENDING':
            print(f"[INFO] 대기 중... (5초 후 재확인)")
            time.sleep(5)
        else:
            print(f"[WARNING] 예상치 못한 상태: '{status}' (5초 후 재확인)")
            time.sleep(5)

    print(f"[TIMEOUT] {timeout}초 초과, 완료 대기 실패")
    return False
```

**검증 방법**:
- 테스트 리포트 제목으로 상태 확인 실행
- 로그 출력으로 Status 텍스트 확인

---

### Task 3.3: verify_archive_page() 메서드 개선
**예상 시간**: 15분
**파일**: `verify_system.py`
**변경 위치**: `verify_archive_page()` 메서드

**현재 문제점**:
- 리포트 없을 때만 확인 (테이블 행 0개)
- 실제 Status 텍스트 검증 안함

**개선 사항**:
```python
def verify_archive_page(self):
    """Archive 페이지 HTML 구조 및 Status 텍스트 검증"""
    print("\n=== Archive 페이지 검증 ===")
    try:
        self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")
        time.sleep(3)

        # 스크린샷 저장
        screenshot_path = os.path.join(self.output_dir, 'archive_page.png')
        self.driver.save_screenshot(screenshot_path)
        print(f"[SCREENSHOT] 스크린샷 저장: {screenshot_path}")

        # HTML 저장
        html_path = os.path.join(self.output_dir, 'archive_page.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
        print(f"[HTML] HTML 저장: {html_path}")

        # 테이블 구조 분석
        print("\n테이블 구조 분석 중...")

        try:
            tbody = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table/tbody"))
            )
            print("[OK] //table/tbody 찾음")

            rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
            print(f"[OK] 테이블 행 개수: {len(rows)}")

            if len(rows) > 0:
                # ✅ 추가: 모든 행의 Status 텍스트 수집
                status_texts = []

                for i, row in enumerate(rows[:5], 1):  # 최대 5개만 확인
                    try:
                        title_cell = row.find_element(By.XPATH, ".//td[1]")
                        status_cell = row.find_element(By.XPATH, ".//td[4]")

                        title_text = title_cell.text.strip()
                        status_text = status_cell.text.strip()

                        status_texts.append(status_text.upper())

                        print(f"\n[행 {i}]")
                        print(f"   Title: '{title_text[:50]}'")
                        print(f"   Status: '{status_text}'")
                    except Exception as e:
                        print(f"[WARNING] 행 {i} 분석 실패: {e}")

                # ✅ 추가: Status 텍스트 패턴 검증
                print(f"\n[SUMMARY] 발견된 Status 텍스트: {set(status_texts)}")

                # 예상 패턴과 비교
                expected_patterns = ['GENERATING', 'GENERATED', 'FAILED', 'PENDING']
                found_patterns = []

                for status in status_texts:
                    for pattern in expected_patterns:
                        if pattern in status:
                            found_patterns.append(pattern)
                            break

                print(f"[MATCH] 매칭된 패턴: {set(found_patterns)}")

                self.results['tests']['archive_structure'] = {
                    'status': 'SUCCESS',
                    'row_count': len(rows),
                    'status_texts': list(set(status_texts)),
                    'matched_patterns': list(set(found_patterns))
                }
            else:
                print("[WARNING] 테이블에 행이 없습니다 (리포트 없음)")
                self.results['tests']['archive_structure'] = {
                    'status': 'WARNING',
                    'message': '테이블 행 없음'
                }

            return True

        except TimeoutException:
            print("[ERROR] //table/tbody 찾기 실패")
            self.results['tests']['archive_structure'] = {
                'status': 'FAILED',
                'error': '//table/tbody 없음'
            }
            return False

    except Exception as e:
        print(f"[ERROR] Archive 페이지 검증 실패: {e}")
        self.results['tests']['archive_structure'] = {
            'status': 'FAILED',
            'error': str(e)
        }
        return False
```

**검증 방법**:
- Archive 페이지에 리포트 있을 때 실행
- Status 텍스트가 올바르게 추출되는지 확인
- "GENERATING", "GENERATED" 등 패턴 매칭 확인

---

### Task 3.4: 검증 스크립트 실행 및 결과 분석
**예상 시간**: 15분

**실행 순서**:
1. verify_system.py 실행
2. 브라우저 위치 확인 (primary monitor)
3. Archive 페이지 Status 텍스트 수집
4. verification_results.json 확인

**예상 출력**:
```json
{
  "timestamp": "2025-10-07T...",
  "tests": {
    "login": {
      "status": "SUCCESS",
      "message": "로그인 성공"
    },
    "archive_structure": {
      "status": "SUCCESS",
      "row_count": 10,
      "status_texts": ["GENERATED", "FAILED", "PENDING"],
      "matched_patterns": ["GENERATED", "FAILED", "PENDING"]
    }
  }
}
```

---

### Task 3.5: Past Day 드롭다운 검증 (선택적)
**예상 시간**: 30분
**우선순위**: 낮음 (Task 3.1-3.4 완료 후 결정)

**작업 내용**:
1. free_explorer.py:317-335 코드 확인
2. 드롭다운 XPath 검증
3. 선택 후 페이지 변화 확인

**결정 기준**:
- Archive 상태 확인 검증 성공 시 진행
- 시간 부족 시 Phase 4에서 처리

---

## 📊 Phase 4 준비 사항

### Phase 4에서 할 작업
1. 개선된 verify_system.py 실행
2. 실제 리포트 생성 후 완료 대기 테스트
3. main_generator.py에 Archive 대기 로직 추가

### Phase 4 전제조건
- ✅ verify_system.py 개선 완료
- ✅ Archive Status 텍스트 확인
- ✅ 폴링 로직 검증

---

## 🔍 예상 결과

### 성공 시
1. 브라우저가 primary monitor에 표시
2. Archive Status 텍스트 정확히 추출
3. "GENERATING", "GENERATED", "FAILED" 패턴 확인
4. 폴링 로직 검증 준비 완료

### 실패 시
1. Status 텍스트 불일치 → 매칭 규칙 조정
2. XPath 셀렉터 오류 → HTML 구조 재분석
3. 타이밍 이슈 → 대기 시간 조정

---

## 📝 문서화 계획

**Phase 4 완료 후 생성**:
- `04_phase4_implementation_results.md` - 구현 결과
- `05_final_verification_report.md` - 최종 검증 보고서

**업데이트**:
- `CLAUDE.md` - Quick Fix 솔루션 업데이트
- `99_TROUBLESHOOTING.md` - 발견된 이슈 추가

---

## ✅ 사용자 승인 대기

이 Master Plan으로 Phase 4 (구현) 진행해도 될까요?

**작업 순서**:
1. Task 3.1: 브라우저 위치 제어 추가 (10분)
2. Task 3.2: Archive 상태 확인 메서드 추가 (20분)
3. Task 3.3: verify_archive_page() 개선 (15분)
4. Task 3.4: 검증 실행 및 결과 분석 (15분)
5. (선택) Task 3.5: Past Day 드롭다운 검증 (30분)

**총 예상 시간**: 1-1.5시간
