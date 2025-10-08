# CLAUDE.md

100xFenok-Generator 프로젝트 가이드 - TerminalX 6개 금융 리포트 자동 생성 시스템

## 🎯 프로젝트 핵심

**목표**: TerminalX에서 Part1/Part2 리포트 자동 생성 (각 3개, 총 6개)
**현재 상태**: 🔄 구현 중 (2025-10-08)
**성공 이력**:
- ✅ 2025-08-20 (Part1/Part2 리포트 생성 성공)
- ✅ 2025-10-08 (일반 리포트 6개 생성 완료 - 참고용, Feno_Docs 프롬프트)
**현재 작업**: Part1/Part2 리포트 생성 (Archive 모니터링 방식)

**⚠️ 중요: 리포트 타입 구분**
1. **일반 리포트** (Feno_Docs/일반리포트/*.md)
   - URL: `/agent/enterprise`
   - 방식: 즉시 생성 (30초), Archive 불필요
   - 코드: `generate_simple_report(prompt, report, past_day)` in main_generator.py:272-360
   - **Past Day 설정**: 2025-10-08 구현 완료 (main_generator.py:300-333)

2. **Part1/Part2 리포트** (Feno_Docs/20250829 *.json)
   - URL: `/agent/enterprise/report/create`
   - 방식: Archive 큐 → 모니터링 (5-10분) → HTML 추출
   - 코드: `generate_report_html()` in main_generator.py:362-461
   - Archive: `ReportBatchManager.monitor_and_retry()` in report_manager.py:53-143
   - **올바른 실행 순서**:
     1. Part1/Part2 리포트 생성 요청 (Archive 큐 진입)
     2. 생성 중인 동안 일반 리포트 6개 생성 (시간 활용)
     3. Archive 모니터링 → Part1/Part2 완료 확인
     4. Part1/Part2 HTML 추출 및 저장

## 📂 작동하는 코드 위치

**절대 새 파일 만들지 마라. 아래 코드가 이미 작동한다:**

| 기능 | 파일 | 줄 | 상태 |
|------|------|---|------|
| 로그인 | `main_generator.py` | 45-78 | ✅ |
| 브라우저 설정 | `main_generator.py` | 25-43 | ✅ |
| 기본 리포트 생성 | `main_generator.py` | 272-324 | ✅ |
| Archive 확인 | `quick_archive_check.py` | 156-198 | ✅ (Part1/Part2용) |
| 전체 워크플로우 | `test_full_6reports.py` | 전체 | ✅ (2025-10-08) |

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
3. **Archive 확인 생략 금지**: Part1/Part2 리포트는 Archive 필수
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
- 기본 리포트 6개 즉시 생성 성공 (2분 57초)
- Archive 모니터링 불필요 (기본 리포트 특성)
- 코드 검증: test_full_6reports.py 작동 확인
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

### Archive 페이지 폴링 (Part1/Part2 리포트 전용!)
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
# 기본 리포트: supersearchx-body 클래스 포함
# Part1/Part2 리포트: markdown-body 클래스 포함
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
2. Archive 상태 확인 필수 (Part1/Part2 리포트)
3. 새 파일 만들지 말고 기존 코드 수정
4. 각 단계 승인 받고 진행

---

**마지막 업데이트**: 2025-10-08
**독립 Git 프로젝트** - workspace와 별개로 관리됨

## 📋 Part1/Part2 리포트 구조 (현재 목표)

**Part1 리포트** (Sections 1-6):
1. Executive Summary & Today's Thesis
2. Market Pulse: Intraday Volatility & Risk Factors
3. Performance Dashboard: Asset Classes, Sectors, Individual Stocks
4. Correlation Matrix: Asset Interactions
5. Wall Street Intelligence: Insights from Experts
6. Institutional Flows: Large Purchases, Short Selling, ETF Flows

**Part2 리포트** (Sections 7-11):
7. Sector Rotation & Theme Analysis
8. Tech Leadership Tracking
9. Trade Signals & Short-term Strategy
10. Tomorrow's Catalysts: Economic Indicators, Earnings, Event Calendar
11. Appendix

**템플릿 위치**:
- `Feno_Docs/20250829 100x Daily Wrap Part1.json` (612줄, 40KB)
- `Feno_Docs/20250829 100x Daily Wrap Part2.json` (635줄, 37KB)
- `Feno_Docs/part1/part1_01-03.json` (예제 3개)
- `Feno_Docs/part2/part2_01-03.json` (예제 3개)

**핵심 차이점**:
- 기본 리포트: `supersearchx-body` 클래스, Archive 불필요
- Part1/Part2: `markdown-body` 클래스, Archive 모니터링 필수

**핵심 파일**:
- `main_generator.py`: 리포트 생성 + HTML 추출
- `report_manager.py`: Archive 모니터링 + 재시도 로직

---

**마지막 업데이트**: 2025-10-08
**독립 Git 프로젝트** - workspace와 별개로 관리됨

## 📌 Claude Integration 워크플로우 (2025-10-08 추가)

**목적**: GEMINI 수동 워크플로우를 Claude Desktop 통합 워크플로우로 대체
**위치**: `Feno_Docs/Claude_Integration/`
**소요 시간**: ~40분 (기존 GEMINI 2시간 30분 → 70% 단축)

### 워크플로우 구조 (DL01-DL04)

**DL01: JSON 통합** (`/integrate-json`)
- 룰북: `Feno_Docs/Claude_Integration/integration_agent.md`
- 입력: Part1×3, Part2×3, 일반×6 파일
- 사용자 작업: 품질 선택 지시 (출처 지정 문서)
- Claude 작업: 오류 데이터 보정 + 인용 제거 + 표준화
- 출력: 섹션별 출처 요약 + 통합 JSON

**DL02: HTML 생성** (`/generate-html`)
- 룰북: `Feno_Docs/Claude_Integration/html_generator.md`
- 입력: 통합 JSON (DL01 결과물)
- Claude 작업: Section 1-11 매핑 + 한글 번역 + 키워드 강조
- 출력: 100x Daily Wrap HTML 파일

**DL03: 품질 검토** (`/review-html`)
- 룰북: `Feno_Docs/Claude_Integration/quality_reviewer.md`
- 입력: 1차 생성 HTML (DL02 결과물)
- Claude 작업: 5대 원칙 기반 검토 (데이터 무결성, 구조, 가독성, 시각, 스타일링)
- 출력: Before/After 코드 조각으로 개선안 제시

**DL04: 인덱스 업데이트** (`/update-index`)
- 룰북: `Feno_Docs/Claude_Integration/index_manager.md`
- 입력: 최종 완성 HTML (DL03 결과물)
- Claude 작업: 메타데이터 추출 + 인덱스 JSON 업데이트
- 출력: 신규 메타데이터 JSON + 업데이트된 인덱스 JSON

**전체 워크플로우** (`/full-workflow`)
- 명령: `.claude/commands/full-workflow.md`
- 실행: DL01 → DL02 → DL03 → DL04 순차 실행
- 사용자 게이트: DL01 완료 후 품질 선택 지시 필요
- 사용자 검토: DL03 개선안 검토 및 적용

### 파일 구조

```
Feno_Docs/Claude_Integration/
├── integration_agent.md      # DL01 룰북 (JSON 통합)
├── html_generator.md          # DL02 룰북 (HTML 생성)
├── quality_reviewer.md        # DL03 룰북 (품질 검토)
├── index_manager.md           # DL04 룰북 (인덱스 관리)
└── quality_selection_guide.md # 사용자 가이드 (품질 선택 기준)

.claude/commands/
├── integrate-json.md          # DL01 슬래시 커맨드
├── generate-html.md           # DL02 슬래시 커맨드
├── review-html.md             # DL03 슬래시 커맨드
├── update-index.md            # DL04 슬래시 커맨드
└── full-workflow.md           # 전체 워크플로우 커맨드
```

### 사용 방법

**Step 1: 품질 선택** (사용자 작업, ~30분)
- 가이드 참조: `Feno_Docs/Claude_Integration/quality_selection_guide.md`
- Part1×3, Part2×3, 일반×6 파일 읽기
- 섹션별로 최우수 답변 선택
- 출처 지정 문서 작성 (Markdown 형식)

**Step 2: 통합 워크플로우 실행** (자동, ~10분)
```bash
/full-workflow
```
또는 개별 단계 실행:
```bash
/integrate-json    # 사용자 출처 지정 문서 제공 필요
/generate-html
/review-html       # 개선안 검토 후 적용
/update-index
```

### 핵심 개선 사항

1. **시간 절감**: GEMINI 2시간 30분 → Claude 40분 (70% 단축)
2. **자동화**: 오류 보정, 인용 제거, 표준화 자동 처리
3. **품질 보장**: 5대 원칙 기반 체계적 검토
4. **구조화**: 단계별 룰북 + 슬래시 커맨드 시스템
5. **사용자 중심**: 품질 선택은 사용자, 나머지는 자동화

