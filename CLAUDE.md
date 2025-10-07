# CLAUDE.md

100xFenok-Generator 프로젝트 가이드 - TerminalX 6개 금융 리포트 자동 생성 시스템

## 🎯 프로젝트 핵심

**목표**: TerminalX에서 6개 금융 리포트 자동 생성
**현재 상태**: ✅ 성공 (2025-10-08 - 6/6 리포트 100% 생성)
**성공 이력**:
- ✅ 2025-08-20 (main_generator.py로 6개 생성 성공)
- ✅ 2025-10-08 (Archive 모니터링 통합 완료 - 6/6 성공)
**해결된 문제**: ReportBatchManager.monitor_and_retry()로 Archive 폴링 완료

## 📂 작동하는 코드 위치

**절대 새 파일 만들지 마라. 아래 코드가 이미 작동한다:**

| 기능 | 파일 | 줄 | 상태 |
|------|------|---|------|
| 로그인 | `main_generator.py` | 45-78 | ✅ |
| 브라우저 설정 | `main_generator.py` | 25-43 | ✅ |
| Past Day 설정 | `free_explorer.py` | 317-335 | ✅ |
| Archive 확인 | `quick_archive_check.py` | 156-198 | ✅ |
| 전체 워크플로우 | `main_generator.py` | 228-480 | ✅ (2025-08-20) |

## 🔧 Quick Fix 솔루션 (5시간)

```python
# main_generator.py에 추가할 핵심 로직:
def generate_report_with_archive_check(self, ...):
    # 1. 리포트 생성 요청 (기존 코드 그대로)
    report_url = self._submit_report()
    report_id = self._extract_report_id(report_url)

    # 2. Archive 완료 대기 (← 이게 누락됨!)
    success = self._wait_for_completion(report_id, timeout=300)

    # 3. 완료된 경우에만 추출
    if success:
        html = self._extract_html()  # 이제 supersearchx-body 있음
        return html
    else:
        raise Exception("Report generation timeout")

def _wait_for_completion(self, report_id, timeout=300):
    """quick_archive_check.py:156-198 로직 사용"""
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

## 🚫 절대 금지 사항

1. **새 파일 생성 금지**: 35개 파일 존재, 더 만들지 마라
2. **기존 코드 무시 금지**: 2025-08-20 성공 코드가 있다
3. **Archive 확인 생략 금지**: 이게 핵심 실패 원인
4. **임의 진행 금지**: 각 단계마다 승인 받아라

## 📋 개발 접근 방식

### Phase 1: As-Is Analysis
**상태**: ✅ 완료
**산출물**: `docs/ANALYSIS_20251006.md`, `MASTER_GUIDE.md`
**결론**: Solution Multiplication Pattern (35개 파일, 85% 중복)

### Phase 2: To-Be Design
**상태**: ✅ 완료
**산출물**: `docs/ARCHITECTURE.md`
**결론**: Quick Fix (5시간) vs 전체 재설계 (5일)

### Phase 3: Master Plan
**상태**: ✅ 완료
**선택**: Option A (Quick Fix) 선택 및 완료

### Phase 4: Implementation
**상태**: ✅ 완료 (2025-10-08)
**성과**:
- Archive 모니터링 통합 완료
- 6개 리포트 100% 생성 성공 (8분 27초)
- 코드 클린업: 27 → 14 파일 (48% 감소)
- 테스트 프레임워크 검증 완료

## 🛠️ MCP/Mode 전략

**사용 완료**:
- `@root-cause-analyst`: Solution Multiplication Pattern 식별
- `@system-architect`: 35→12 파일 재설계안

**필요 시 사용**:
- `playwright` MCP: 브라우저 자동화 개선/디버깅
- `sequential-thinking` MCP: 복잡한 워크플로우 분석
- `@refactoring-expert`: 코드 중복 제거 시

## 🔍 핵심 기술 패턴

### Selenium 브라우저 자동화
```python
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

# 항상 WebDriverWait 사용, time.sleep(고정값) 피하기
```

### Archive 페이지 폴링 (필수!)
```python
# ❌ 잘못된 방법 (현재):
time.sleep(300)  # 5분 blind wait
html = extract_html()  # 아직 완료 안됐는데 추출

# ✅ 올바른 방법:
while not completed and time < timeout:
    status = check_archive_status(report_id)
    if status == 'Generated':
        break
    time.sleep(5)
html = extract_html()  # 완료 확인 후 추출
```

### HTML 추출 검증
```python
# 기대: supersearchx-body 클래스 포함
# 실패 신호: MuiTable + "No documents found"
if 'No documents found' in html:
    raise Exception("Report not ready yet")
```

## 📚 참조 문서

- `MASTER_GUIDE.md`: 전체 가이드
- `docs/TROUBLESHOOTING.md`: 과거 실패 사례
- `docs/ARCHITECTURE.md`: 시스템 구조 분석
- `README.md`: 프로젝트 개요

## ⚠️ 과거 실패에서 배운 교훈

**2025-08-25 실패 Git 커밋 메시지**:
```
"Past Day 설정 완전 실패 (사용자가 100번 말했는데도 안했음)"
"기존 자료 안찾고 새로 만들기만 함 (골백번 지시했는데도 무시)"
```

**교훈**:
1. 기존 성공 코드부터 먼저 확인
2. Archive 상태 확인 필수
3. 새 파일 만들지 말고 기존 코드 수정
4. 각 단계 승인 받고 진행

---

**마지막 업데이트**: 2025-10-06
**독립 Git 프로젝트** - workspace와 별개로 관리됨
## 🎉 프로젝트 완료 (2025-10-08)

**최종 성과**:
- ✅ 6개 리포트 100% 생성 성공
- ✅ Archive 모니터링 통합 완료
- ✅ 코드베이스 정리: 27 → 14 파일
- ✅ 실행 시간: 8분 27초

**핵심 파일**:
- `main_generator.py`: 리포트 생성 + HTML 추출
- `report_manager.py`: Archive 모니터링 (monitor_and_retry)
- `test_full_6reports.py`: 6개 리포트 배치 테스트
- `test_archive_simple.py`: 단일 리포트 검증 테스트

---

**마지막 업데이트**: 2025-10-08
**독립 Git 프로젝트** - workspace와 별개로 관리됨

