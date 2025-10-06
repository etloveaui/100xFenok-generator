# Task 3 Phase 2: To-Be 설계 - Archive 동적 렌더링 대기 로직

**작성일**: 2025-10-07 01:32
**Context**: verify_system.py 검증 로직을 report_manager.py에 적용

## 🎯 설계 목표

**핵심**: JavaScript 동적 렌더링 완료까지 대기 후 테이블 행 추출

**검증 완료**: verify_system.py에서 572개 리포트 발견 성공

## 📐 설계 원칙

### 1. 검증된 로직 재사용
- verify_system.py Lines 254-296 패턴 적용
- 고정 대기 (3 + 7초) + 폴링 (5회 × 2초)
- 총 최대 20초 대기

### 2. 최소 침습적 수정
- report_manager.py의 기존 구조 유지
- `monitor_and_retry()` 메서드만 수정
- 다른 메서드/클래스 변경 없음

### 3. 하위 호환성
- 기존 호출 인터페이스 동일
- main_generator.py 수정 불필요
- 동작 검증 후 적용

## 🔧 설계 상세

### 수정 대상: report_manager.py Lines 65-77

**BEFORE** (현재):
```python
def monitor_and_retry(self, timeout: int = 1800, initial_interval: int = 30):
    while time.time() - overall_start_time < timeout:
        # ...
        self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")

        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//table/tbody"))
            )
            rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
            status_map = {}
            for row in rows:
                # ...
```

**AFTER** (설계):
```python
def monitor_and_retry(self, timeout: int = 1800, initial_interval: int = 30):
    while time.time() - overall_start_time < timeout:
        # ...
        self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")

        # === 추가: JavaScript 렌더링 대기 ===
        print("[Batch Manager] Archive 페이지 로딩 대기중...")
        time.sleep(3)  # 초기 페이지 로딩

        print("[Batch Manager] JavaScript 렌더링 대기중...")
        time.sleep(7)  # JavaScript 실행 및 테이블 렌더링

        try:
            # tbody 태그 존재 확인
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//table/tbody"))
            )

            # === 추가: 테이블 행 렌더링 폴링 ===
            print("[Batch Manager] 테이블 행 렌더링 대기중...")
            rows = []
            for attempt in range(5):
                rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
                if len(rows) > 0:
                    print(f"[Batch Manager] 테이블 행 {len(rows)}개 발견")
                    break
                print(f"[Batch Manager] 시도 {attempt+1}/5: 행 없음, 2초 대기...")
                time.sleep(2)

            # === 추가: 행 0개 경고 ===
            if len(rows) == 0:
                print("[Batch Manager] 경고: 테이블 행이 렌더링되지 않음. 다음 폴링까지 대기.")
                time.sleep(current_interval)
                continue  # 다음 모니터링 주기로 스킵

            # 기존 로직: status_map 생성
            status_map = {}
            for row in rows:
                # ... (기존 코드 그대로)
```

### 대기 시간 분석

**총 대기 시간 구성**:
```
1. 페이지 이동 (driver.get): ~2초
2. 초기 로딩 (time.sleep): 3초
3. JavaScript 렌더링: 7초
4. tbody 확인 (WebDriverWait): 최대 15초 (보통 즉시)
5. 행 폴링 (5회 × 2초): 최대 10초 (렌더링되면 즉시 중단)
----------------------------------------------
총합: 최소 12초, 최대 37초 (정상: ~15초)
```

**verify_system.py 대비 차이**:
- verify_system.py: 고정 20초
- report_manager.py: 15-37초 (동적 조정)
- 이유: 모니터링은 반복 호출되므로 초기 안정성 우선

### 폴링 간격 최적화 (선택적)

**현재**:
```python
time.sleep(current_interval)  # 초기 30초 → 최대 120초
current_interval = min(current_interval * 1.2, 120)
```

**제안** (선택 적용):
```python
time.sleep(current_interval)  # 초기 15초 → 최대 60초
current_interval = min(current_interval * 1.2, 60)
```

**근거**:
- JavaScript 렌더링 대기로 각 체크가 ~15초 소요
- 초기 간격 30초 → 15초로 감소 (더 빠른 감지)
- 최대 간격 120초 → 60초 (불필요한 대기 감소)

**유지** (권장):
- 기존 값 유지로 안정성 우선
- 렌더링 대기 추가만으로 충분한 개선

## 📊 예상 동작 시나리오

### 시나리오 1: 정상 생성 중
```
T=0s:   Archive 페이지 이동
T=2s:   초기 로딩 대기 시작 (3초)
T=5s:   JavaScript 렌더링 대기 시작 (7초)
T=12s:  tbody 확인 (즉시)
T=12s:  행 폴링 시작
T=12s:  572개 행 발견! (폴링 1회에 성공)
T=13s:  status_map 생성 → "GENERATING" 상태 확인
T=13s:  30초 대기 후 다음 체크
```

### 시나리오 2: 리포트 완료
```
T=0s:   Archive 페이지 이동
T=12s:  테이블 행 발견
T=13s:  status_map → "Generated" 발견
T=13s:  report.status = "GENERATED" 업데이트
T=13s:  모니터링 종료, Phase 3(HTML 추출)로 진행
```

### 시나리오 3: 렌더링 지연 (예외)
```
T=0s:   Archive 페이지 이동
T=12s:  행 폴링 시작
T=12s:  시도 1/5: 행 없음, 2초 대기
T=14s:  시도 2/5: 행 없음, 2초 대기
T=16s:  시도 3/5: 572개 행 발견!
T=17s:  status_map 생성 및 상태 업데이트
```

### 시나리오 4: 심각한 문제 (폴링 실패)
```
T=0s:   Archive 페이지 이동
T=12s:  행 폴링 시작
T=22s:  5회 시도 모두 실패, len(rows) = 0
T=22s:  경고 로그: "테이블 행이 렌더링되지 않음"
T=22s:  continue → 30초 대기
T=52s:  다음 모니터링 주기 시작
```

## 🔍 에러 처리 강화

### 추가 검증 로직

**행 개수 로깅**:
```python
if len(rows) > 0:
    print(f"[Batch Manager] 테이블 행 {len(rows)}개 발견")
else:
    print("[Batch Manager] 경고: 테이블 행 0개")
```

**status_map 검증**:
```python
if not status_map:
    print("[Batch Manager] 경고: status_map이 비어있음. Archive에 리포트 없거나 렌더링 실패.")
```

**pending_reports vs status_map 비교**:
```python
for report in pending_reports:
    if report.title not in status_map:
        print(f"[Batch Manager] 경고: '{report.title}' Archive에서 찾을 수 없음")
```

## 🎯 성공 기준

### 기능 검증
- ✅ Archive 페이지에서 572개 리포트 발견
- ✅ "Generated" 상태 정확히 감지
- ✅ "GENERATING" 상태 계속 모니터링
- ✅ "FAILED" 상태 재시도 관리

### 성능 검증
- ✅ 정상 케이스: ~15초/체크
- ✅ 지연 케이스: ~25초/체크 (폴링 성공)
- ✅ 실패 케이스: ~37초/체크 (폴링 실패 후 스킵)

### 안정성 검증
- ✅ 30분 타임아웃 내 6개 리포트 완료
- ✅ "No documents found" 에러 제거
- ✅ 재시도 로직 정상 작동

## 📝 구현 고려사항

### 1. import 추가 필요 없음
- 기존 `time` 모듈 사용
- 새 라이브러리 불필요

### 2. 기존 로직 보존
- `status_map` 생성 로직 동일
- `update_report_status()` 호출 방식 동일
- 재시도 메커니즘 변경 없음

### 3. 로깅 수준
- 디버깅: 각 대기 단계 로그
- 정상 운영: 행 발견 시만 로그
- 경고: 행 0개, status_map 비어있음

## 🔄 Phase 3 준비

### 다음 단계: Master Plan
1. **수정 위치**: report_manager.py Lines 65-90
2. **예상 시간**: 10분 코드 수정 + 5분 검토
3. **검증 방법**: 단일 리포트 생성 테스트
4. **통합 테스트**: 6개 리포트 자동 생성

### 완료 체크리스트
- [ ] Lines 65-90 수정
- [ ] 로깅 추가
- [ ] 행 0개 처리 로직
- [ ] 단위 테스트 (1개 리포트)
- [ ] 통합 테스트 (6개 리포트)

## 💡 핵심 아이디어

**"검증된 로직의 재사용"**:
- verify_system.py: 문제 발견 + 해결
- report_manager.py: 동일 로직 적용
- 성공 확률: 매우 높음 (이미 검증됨)

**"최소 변경의 원칙"**:
- 1개 메서드만 수정
- 기존 구조 유지
- 하위 호환성 보장
