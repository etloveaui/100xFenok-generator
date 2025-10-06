# Task 3 Phase 3: Master Plan - report_manager.py 수정

**작성일**: 2025-10-07 01:35
**Context**: verify_system.py 검증 로직을 report_manager.py에 적용

## 📋 Master Plan 개요

**목표**: report_manager.py의 Archive 모니터링 로직에 JavaScript 렌더링 대기 추가
**파일**: `report_manager.py`
**수정 라인**: Lines 65-90
**예상 소요**: 15분

## ✅ Task Checklist

### Task 3.1: Archive 페이지 대기 로직 추가
**대상**: `report_manager.py` Lines 65-77
**예상 시간**: 5분
**작업 내용**:
- Line 65 이후: 초기 로딩 대기 추가 (`time.sleep(3)`)
- Line 66 이후: JavaScript 렌더링 대기 (`time.sleep(7)`)
- Line 68: WebDriverWait 타임아웃 20초 → 15초 조정
- Line 69-77: 테이블 행 폴링 로직 추가 (5회 × 2초)

**상세 단계**:
```python
# Step 1: Archive 페이지 이동 후 대기
self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")
print("[Batch Manager] Archive 페이지 로딩 대기중...")
time.sleep(3)  # 초기 로딩

# Step 2: JavaScript 렌더링 대기
print("[Batch Manager] JavaScript 렌더링 대기중...")
time.sleep(7)

# Step 3: tbody 존재 확인
try:
    WebDriverWait(self.driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//table/tbody"))
    )

    # Step 4: 테이블 행 폴링
    print("[Batch Manager] 테이블 행 렌더링 대기중...")
    rows = []
    for attempt in range(5):
        rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
        if len(rows) > 0:
            print(f"[Batch Manager] 테이블 행 {len(rows)}개 발견")
            break
        print(f"[Batch Manager] 시도 {attempt+1}/5: 행 없음, 2초 대기...")
        time.sleep(2)

    # Step 5: 행 0개 체크
    if len(rows) == 0:
        print("[Batch Manager] 경고: 테이블 행이 렌더링되지 않음. 다음 폴링까지 대기.")
        time.sleep(current_interval)
        continue

    # Step 6: 기존 로직 (status_map 생성)
    status_map = {}
    for row in rows:
        ...
```

**검증 방법**:
- [ ] 코드 문법 오류 없음
- [ ] 들여쓰기 올바름
- [ ] 기존 로직과 연결 자연스러움

---

### Task 3.2: 에러 로깅 추가
**대상**: `report_manager.py` Lines 103-106
**예상 시간**: 3분
**작업 내용**:
- 각 대기 단계 로그 추가
- 행 개수 로그 추가
- 경고 메시지 개선

**상세 단계**:
```python
# 기존 except 블록 유지
except TimeoutException:
    print("[Batch Manager] 아카이브 페이지 로드 타임아웃. 새로고침.")
    print(f"[Batch Manager] 현재 URL: {self.driver.current_url}")  # 추가
except Exception as e:
    print(f"[Batch Manager] 상태 확인 중 예외 발생: {e}. 새로고침.")
    import traceback
    traceback.print_exc()  # 상세 에러 추가
```

**검증 방법**:
- [ ] 로그 출력 확인
- [ ] 에러 메시지 명확성

---

### Task 3.3: 코드 리뷰 및 정리
**대상**: `report_manager.py` 전체
**예상 시간**: 2분
**작업 내용**:
- 주석 정리
- 불필요한 공백 제거
- 변수명 일관성 확인

**검증 방법**:
- [ ] 코드 가독성 양호
- [ ] 주석 명확
- [ ] 스타일 일관성

---

### Task 3.4: Git 커밋 (선택)
**대상**: 수정된 `report_manager.py`
**예상 시간**: 2분
**작업 내용**:
- 변경사항 검토
- 의미있는 커밋 메시지 작성
- 커밋 실행

**커밋 메시지 예시**:
```
Fix: Archive 페이지 JavaScript 렌더링 대기 추가

- verify_system.py 검증 로직을 report_manager.py에 적용
- 초기 로딩(3초) + JS 렌더링(7초) + 폴링(5회×2초) 추가
- 테이블 행 0개 문제 해결
- Lines 65-90 수정

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

**검증 방법**:
- [ ] git status 확인
- [ ] git diff 검토
- [ ] 커밋 메시지 명확

---

### Task 3.5: 단위 테스트 (1개 리포트)
**대상**: 전체 시스템
**예상 시간**: 10분 (대기 시간 포함)
**작업 내용**:
- Part1 리포트 1개 생성 테스트
- Archive 모니터링 로그 확인
- "Generated" 상태 도달 검증
- HTML 추출 성공 확인

**테스트 스크립트**:
```python
# test_single_report.py
from main_generator import FenokReportGenerator
from datetime import datetime, timedelta

gen = FenokReportGenerator()
gen._login_terminalx()

from report_manager import ReportBatchManager
batch_manager = ReportBatchManager(gen.driver)

today = datetime.now()
report_date_str = today.strftime('%Y%m%d')
ref_date_start = (today - timedelta(days=1)).strftime('%Y-%m-%d')
ref_date_end = today.strftime('%Y-%m-%d')

# 1개 리포트만 생성
batch_manager.add_report("Part1", f"{report_date_str} Test Report Part1")
report = batch_manager.reports[0]
gen.generate_report_html(report, report_date_str, ref_date_start, ref_date_end)

# 모니터링
print("\n=== 모니터링 시작 ===")
success = batch_manager.monitor_and_retry()

print(f"\n=== 결과 ===")
print(f"성공 여부: {success}")
print(f"리포트 상태: {report.status}")
print(f"리포트 URL: {report.url}")
```

**검증 방법**:
- [ ] 로그인 성공
- [ ] 리포트 생성 요청 성공
- [ ] Archive 페이지에서 572개 행 발견
- [ ] "Generated" 상태 감지
- [ ] 모니터링 종료

---

### Task 3.6: 통합 테스트 (6개 리포트) - 선택
**대상**: 전체 워크플로우
**예상 시간**: 30분 (6개 리포트 생성 시간)
**작업 내용**:
- `main_generator.py` 실행
- 6개 리포트 (Part1 × 3, Part2 × 3) 생성
- 전체 프로세스 완료 확인

**실행 명령**:
```bash
cd /c/Users/etlov/agents-workspace/projects/100xFenok-generator
python main_generator.py
```

**검증 방법**:
- [ ] 6개 리포트 모두 생성 요청 성공
- [ ] Archive 모니터링 정상 작동
- [ ] 6개 리포트 모두 "Generated" 도달
- [ ] HTML 추출 6개 완료
- [ ] "No documents found" 에러 없음

---

## 📊 예상 시간표

| Task | 작업 | 예상 시간 | 누적 시간 |
|------|------|-----------|-----------|
| 3.1 | Archive 대기 로직 | 5분 | 5분 |
| 3.2 | 에러 로깅 | 3분 | 8분 |
| 3.3 | 코드 리뷰 | 2분 | 10분 |
| 3.4 | Git 커밋 (선택) | 2분 | 12분 |
| 3.5 | 단위 테스트 | 10분 | 22분 |
| 3.6 | 통합 테스트 (선택) | 30분 | 52분 |

**최소 완료**: Task 3.1-3.5 (22분)
**전체 완료**: Task 3.1-3.6 (52분)

## 🎯 성공 기준

### 필수 (Task 3.1-3.5)
- ✅ report_manager.py 수정 완료
- ✅ 문법 오류 없음
- ✅ 단위 테스트 (1개 리포트) 성공
- ✅ "Generated" 상태 정확히 감지
- ✅ 로그 출력 명확

### 추가 (Task 3.6)
- ✅ 6개 리포트 전체 생성 성공
- ✅ "No documents found" 에러 제거
- ✅ HTML 추출 6개 완료
- ✅ 전체 프로세스 30분 내 완료

## 🚨 리스크 및 대응

### 리스크 1: 대기 시간 부족
**증상**: 여전히 rows = [] 발생
**대응**: `time.sleep(7)` → `time.sleep(10)` 증가

### 리스크 2: 폴링 실패
**증상**: 5회 시도 모두 실패
**대응**: 폴링 횟수 5회 → 10회 증가

### 리스크 3: 기존 로직 파괴
**증상**: 기존 기능 작동 안함
**대응**: Git revert, Phase 2 재검토

## 📝 다음 단계

### Phase 4 준비
1. Master Plan 승인 받기 (사용자 확인)
2. Task 3.1-3.5 순차 실행
3. 각 Task 완료 후 체크리스트 확인
4. 문제 발생 시 리스크 대응 절차 적용

### 완료 후
1. 결과 문서 작성 (`docs/08_task3_phase4_results.md`)
2. CHECKPOINT.md 업데이트
3. 사용자에게 완료 보고

## 💡 핵심 원칙

**"한 번에 하나씩"**:
- Task 3.1 완료 → 검증 → Task 3.2
- 순차 진행으로 문제 조기 발견
- 각 단계 명확한 체크포인트

**"검증된 로직 재사용"**:
- verify_system.py 성공 → report_manager.py 적용
- 동일한 문제 → 동일한 해결책
- 위험 최소화, 성공 확률 극대화
