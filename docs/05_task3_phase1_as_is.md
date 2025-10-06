# Task 3 Phase 1: As-Is 분석 - Archive 대기 로직 통합

**작성일**: 2025-10-07 01:30
**Context**: verify_system.py 검증 완료 후 main_generator.py 통합

## 📋 분석 대상

### 주요 파일
1. **main_generator.py** (785줄) - 메인 자동화 스크립트
2. **report_manager.py** (117줄) - Archive 모니터링 로직

### 핵심 워크플로우

```python
# main_generator.py:628-719
def run_full_automation():
    # Phase 1: 리포트 생성 요청 (Fire-and-Forget)
    for report in batch_manager.reports:
        generate_report_html(report, ...)  # → status = "GENERATING"

    # Phase 2: Archive 모니터링 (Monitor & Retry)
    batch_manager.monitor_and_retry()     # ← report_manager.py

    # Phase 3: HTML 추출 및 처리
    if report.status == "GENERATED":
        driver.get(report.url)
        html = driver.page_source
```

## 🔴 문제점 식별

### 문제 1: report_manager.py Lines 68-77

**현재 코드**:
```python
def monitor_and_retry(self, timeout: int = 1800, initial_interval: int = 30):
    # ...
    WebDriverWait(self.driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//table/tbody"))
    )
    rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
    status_map = {}
    for row in rows:
        title_element = row.find_element(By.XPATH, ".//td[1]")
        status_element = row.find_element(By.XPATH, ".//td[4]")
        status_map[title_element.text.strip()] = status_element.text.strip()
```

**문제**:
1. `<tbody>` 태그 존재만 확인 (20초)
2. **JavaScript 렌더링 대기 없음**
3. `rows = []` 가능성 (verify_system.py와 동일)
4. `len(rows) == 0` → `status_map = {}` → 모든 리포트 "NOT_FOUND"

**증거**: verify_system.py에서 동일 문제 발생 및 해결 완료

### 문제 2: 에러 처리 부족

**Lines 103-106**:
```python
except TimeoutException:
    print("[Batch Manager] 아카이브 페이지 로드 타임아웃. 새로고침.")
except Exception as e:
    print(f"[Batch Manager] 상태 확인 중 예외 발생: {e}. 새로고침.")
```

**문제**:
- `rows = []`일 때 예외 발생 없음
- `status_map = {}`로 빈 딕셔너리 생성
- 모든 리포트가 "NOT_FOUND" 상태로 계속 대기

### 문제 3: 폴링 간격 증가

**Lines 113-114**:
```python
time.sleep(current_interval)
current_interval = min(current_interval * 1.2, 120)  # 지수 백오프
```

**문제**:
- 초기 30초 → 점차 증가 → 최대 120초
- 테이블 행 0개 문제 발견 지연
- 전체 타임아웃 1800초(30분) 안에 해결 못할 가능성

## ✅ verify_system.py 해결 방법

**성공한 수정 (Lines 254-296)**:
```python
# 초기 페이지 로딩 대기
time.sleep(3)

# JavaScript 렌더링 대기
time.sleep(7)

# 테이블 행 렌더링 폴링
for attempt in range(5):
    rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
    if len(rows) > 0:
        break
    time.sleep(2)

# 결과: 572개 리포트 발견!
```

**핵심**:
- 고정 대기 시간 (3 + 7초)
- 명시적 폴링 (5회 × 2초)
- 총 20초 동안 동적 렌더링 완료 보장

## 📊 현재 시스템 동작 분석

### 정상 시나리오
1. `generate_report_html()` → `status = "GENERATING"`
2. `monitor_and_retry()` → Archive 페이지 이동 (30초 간격)
3. `<tbody>` 존재 확인 (20초 대기)
4. `rows` 추출 → td[1] Title, td[4] Status
5. `status_map = {title: "Generated"}` 생성
6. `report.status = "GENERATED"` 업데이트
7. HTML 추출 진행

### 실패 시나리오 (현재)
1. `monitor_and_retry()` → Archive 페이지 이동
2. `<tbody>` 태그만 존재 (JavaScript 렌더링 전)
3. `rows = []` (빈 리스트)
4. `status_map = {}` (빈 딕셔너리)
5. `current_status_from_archive = "NOT_FOUND"`
6. "아카이브에서 찾을 수 없음. 계속 대기."
7. 30초 후 재시도 → 동일 문제 반복
8. 30분 타임아웃 → 전체 실패

## 🎯 수정 필요 위치

### report_manager.py
**Lines 65-77**: `monitor_and_retry()` 메서드 내 테이블 추출 로직

**수정 사항**:
1. Archive 페이지 이동 후 JavaScript 렌더링 대기 (10초)
2. 테이블 행 렌더링 폴링 (5회 × 2초)
3. `len(rows) == 0` 체크 및 경고 로그

### 추가 개선 (선택)
**Lines 113-114**: 폴링 간격 조정
- 초기 간격: 30초 → 10초 (더 빠른 감지)
- 최대 간격: 120초 → 60초 (불필요한 대기 감소)

## 📈 예상 효과

### 수정 전
- Archive 행 0개 → "NOT_FOUND" 반복
- 30분 타임아웃 → 실패
- "No documents found" 에러

### 수정 후
- JavaScript 렌더링 완료까지 대기
- 572개 리포트 정상 발견
- "Generated" 상태 정확히 감지
- HTML 추출 성공

## 🔧 다음 단계

### Phase 2: To-Be 설계
1. verify_system.py 로직을 report_manager.py에 적용
2. 동적 렌더링 대기 시간 설계
3. 에러 처리 강화
4. 로깅 개선

### Phase 3: Master Plan
1. report_manager.py 수정 체크리스트
2. 시간 예측
3. 검증 방법

### Phase 4: 구현 및 테스트
1. 코드 수정
2. 단일 리포트 테스트
3. 6개 리포트 통합 테스트

## 📝 핵심 교훈

**동일한 문제의 재발견**:
- verify_system.py: 테이블 행 0개 문제 해결
- report_manager.py: 동일 문제 존재 확인
- 해결 방법: 검증된 로직 재사용

**JavaScript 렌더링 페이지의 특징**:
- `WebDriverWait` + `EC.presence_of_element_located`는 태그 존재만 확인
- 동적 내용물(행) 렌더링은 별도 대기 필요
- 명시적 `time.sleep()` + 폴링이 더 안정적

## 🎯 성공 기준

**수정 후 검증**:
- ✅ Archive 페이지에서 572개 리포트 발견
- ✅ "Generated" 상태 정확히 추출
- ✅ 6개 리포트 전체 생성 성공
- ✅ "No documents found" 에러 제거
