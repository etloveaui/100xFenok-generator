# 100xFenok-Generator Architecture Design

**문서 버전**: 1.0
**작성일**: 2025-10-07
**작성자**: System Architect Agent

---

## 🎯 Executive Summary

### 시스템 목적
TerminalX 플랫폼에서 **18개 금융 리포트**를 자동 생성하는 통합 시스템
- Custom Reports: 6개 (Part1: 3개, Part2: 3개)
- 일반 리포트: 12개 (Feno_Docs/일반리포트/*.md)

### 핵심 문제
- **현재 상태**: Custom 6개만 구현됨 (main_generator.py)
- **누락 기능**: 일반 리포트 12개 + Past Day 드롭다운 설정
- **아키텍처 복잡도**: 35개 파일, 85% 코드 중복 (Solution Multiplication Pattern)

### 설계 원칙
1. **기존 성공 코드 재사용**: main_generator.py (2025-08-20 검증완료)
2. **Archive 상태 확인 필수**: quick_archive_check.py 패턴 통합
3. **Past Day 설정**: free_explorer.py 로직 활용
4. **단일 통합 워크플로우**: 18개 리포트 일괄 처리

---

## 📊 Current State Analysis

### 1. 기존 파일 구조

```
100xFenok-generator/
├── main_generator.py           ✅ Custom 6개 생성 (Template ID 10)
│   ├── generate_report_html()  ✅ 폼 작성 + 생성 요청
│   ├── _wait_for_completion()  ⚠️  누락됨! (핵심 문제)
│   └── extract_and_validate_html() ✅ HTML 추출
│
├── free_explorer.py            ✅ Past Day 설정 로직
│   └── analyze_period_elements_detailed() (L290-343)
│
├── quick_archive_check.py      ✅ Archive 모니터링
│   ├── _find_generated_reports() (L183-215)
│   └── check_archive_immediately() (L123-181)
│
├── Feno_Docs/일반리포트/       📂 12개 리포트 정의 파일
│   ├── 3.1 3.2 Gain Lose.md
│   ├── 3.3 Fixed Income.md
│   ├── 5.1 Major IB Updates.md
│   ├── 6.3 Dark Pool & Political Donation Flows.md
│   ├── 7.1 11 GICS Sector Table.md
│   ├── 8.1 12 Key Tickers Table.md
│   └── ... (6개 더)
│
└── report_manager.py           ✅ Batch 관리 로직
    ├── Report (데이터 클래스)
    └── ReportBatchManager (모니터링)
```

### 2. 성공 패턴 (main_generator.py)

#### Phase 1: 리포트 생성 요청 (Fire-and-Forget)
```python
# main_generator.py:689-696
for report in batch_manager.reports:
    self.generate_report_html(report, report_date_str, ref_date_start, ref_date_end)
    # ✅ 폼 작성, PDF 업로드, Prompt 입력
    # ✅ Generate 버튼 클릭
    # ✅ URL 변경 대기 → report.url 저장
    # ✅ "Generating..." 메시지 확인
```

#### Phase 2: Archive 모니터링 (Monitor & Retry)
```python
# report_manager.py (ReportBatchManager)
def monitor_and_retry(self):
    # ✅ Archive 페이지 폴링
    # ✅ 상태 확인: GENERATING → GENERATED
    # ✅ 실패 시 재시도 (max_retries=3)
```

#### Phase 3: HTML 추출 및 검증
```python
# main_generator.py:720-787
def extract_and_validate_html(self, report, output_path):
    # ✅ supersearchx-body 클래스 대기 (폴링)
    # ✅ "No documents found" 에러 감지
    # ✅ HTML 크기 검증 (50KB 이상)
```

### 3. 누락된 기능

#### A. Past Day 드롭다운 설정 (일반 리포트용)
```python
# free_explorer.py:317-335 로직 필요
# 현재: main_generator.py에 없음
# 필요: "Any Time" 드롭다운 → "Past Day" 선택
```

#### B. 일반 리포트 Prompt 구성
```python
# 현재: Part1/Part2만 템플릿 파일 사용 (input_data/*.md)
# 필요: Feno_Docs/일반리포트/*.md 파일 읽어서 Prompt로 사용
```

#### C. 템플릿 ID 동적 선택
```python
# 현재: Template ID 10 고정 (L311)
# 필요: 일반 리포트는 다른 템플릿 ID 사용 가능성
#       (또는 같은 ID에서 Past Day만 다르게 설정)
```

---

## 🏗️ Proposed Architecture

### System Context Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   100xFenok-Generator                    │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐   ┌────────────┐│
│  │ main_        │───▶│ report_      │◀──│ Selenium   ││
│  │ generator.py │    │ manager.py   │   │ WebDriver  ││
│  └──────────────┘    └──────────────┘   └────────────┘│
│         │                    │                  │       │
│         ▼                    ▼                  ▼       │
│  ┌──────────────────────────────────────────────────┐  │
│  │         TerminalX Web Platform                    │  │
│  │  - Report Form (Template ID 10)                   │  │
│  │  - Archive Page (Status Monitoring)               │  │
│  │  - Generated Report Pages (HTML Extraction)       │  │
│  └──────────────────────────────────────────────────┘  │
│         │                    │                  │       │
│         ▼                    ▼                  ▼       │
│  ┌──────────────┐    ┌──────────────┐   ┌────────────┐│
│  │ input_data/  │    │ Feno_Docs/   │   │ generated_ ││
│  │ (Part1/2)    │    │ 일반리포트/   │   │ html/      ││
│  └──────────────┘    └──────────────┘   └────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  FenokReportGenerator                    │
├─────────────────────────────────────────────────────────┤
│ Configuration & Initialization                          │
│  - __init__(): 경로 설정, WebDriver 초기화              │
│  - _load_credentials(): TerminalX 로그인 정보           │
│  - _setup_webdriver(): Selenium Chrome 설정             │
├─────────────────────────────────────────────────────────┤
│ Authentication                                          │
│  - _login_terminalx(): Multi-fallback 로그인 전략       │
├─────────────────────────────────────────────────────────┤
│ Report Generation Core                                  │
│  - generate_report_html(): 폼 작성 + 생성 요청          │
│    ├─ _input_date_directly(): 날짜 입력                 │
│    ├─ _set_past_day_dropdown(): 🆕 Past Day 설정       │
│    └─ _submit_and_wait(): Generate 버튼 + URL 대기     │
├─────────────────────────────────────────────────────────┤
│ Archive Monitoring (ReportBatchManager 위임)           │
│  - monitor_and_retry(): 상태 폴링 + 재시도              │
│    └─ _check_status(): Archive 테이블 파싱             │
├─────────────────────────────────────────────────────────┤
│ HTML Extraction & Validation                            │
│  - extract_and_validate_html(): 폴링 기반 추출          │
│    ├─ supersearchx-body 클래스 대기                     │
│    └─ "No documents found" 에러 감지                    │
├─────────────────────────────────────────────────────────┤
│ Report Configuration Management 🆕                      │
│  - _load_report_configs(): 18개 리포트 정의 로드        │
│    ├─ Custom Reports (6개): input_data/*.md            │
│    └─ 일반 리포트 (12개): Feno_Docs/일반리포트/*.md    │
├─────────────────────────────────────────────────────────┤
│ Orchestration Workflow                                  │
│  - run_full_automation(): 전체 워크플로우 실행          │
│    ├─ Phase 1: Fire-and-Forget (18개 생성 요청)        │
│    ├─ Phase 2: Monitor & Retry (Archive 모니터링)      │
│    └─ Phase 3: Extract & Process (HTML 추출)           │
└─────────────────────────────────────────────────────────┘
```

### Data Model

```python
@dataclass
class ReportConfig:
    """리포트 설정 (통합 데이터 모델)"""
    report_id: str              # "custom_part1_1", "general_3.1"
    report_type: str            # "custom" | "general"
    part_type: str              # "Part1" | "Part2" | "General"
    title: str                  # "20250723 100x Daily Wrap Part1"

    # 공통 필드
    prompt_source: str          # 파일 경로: input_data/*.md 또는 Feno_Docs/*.md
    template_id: int            # TerminalX Template ID (기본: 10)

    # 일반 리포트 전용
    past_day: Optional[int]     # 90, 180, 270 등 (Custom은 None)
    keywords: Optional[str]     # 검색 키워드
    urls: Optional[List[str]]   # 특정 URL 리스트
    num_pages: int              # 검색 결과 페이지 수 (기본: 30)

    # PDF 업로드 (Custom 전용)
    source_pdf: Optional[str]   # Sample Report PDF
    prompt_pdf: Optional[str]   # Prompt PDF

@dataclass
class Report:
    """실행 중 상태 추적 (기존 유지)"""
    part_type: str
    title: str
    url: str = ""
    status: str = "PENDING"     # PENDING → GENERATING → GENERATED | FAILED
    retry_count: int = 0
```

### Sequence Diagram: 18-Report Generation

```
User → FenokReportGenerator: run_full_automation()

[Phase 1: Fire-and-Forget]
FenokReportGenerator → ConfigLoader: _load_report_configs()
ConfigLoader → Feno_Docs: Read *.md files (12개)
ConfigLoader → input_data: Read templates (6개)
ConfigLoader -->> FenokReportGenerator: 18 ReportConfig objects

loop for each ReportConfig
    FenokReportGenerator → TerminalX: navigate to form

    alt Custom Report (Part1/2)
        FenokReportGenerator → TerminalX: Upload PDFs
        FenokReportGenerator → TerminalX: Input prompt from .md
        FenokReportGenerator → TerminalX: Set date range
    else General Report
        FenokReportGenerator → TerminalX: Input prompt from .md
        FenokReportGenerator → TerminalX: Set Past Day dropdown
        FenokReportGenerator → TerminalX: Set keywords/urls
    end

    FenokReportGenerator → TerminalX: Click Generate
    TerminalX -->> FenokReportGenerator: report_url
    FenokReportGenerator → ReportBatchManager: Add to batch
end

[Phase 2: Monitor & Retry]
loop until all completed (timeout: 20분)
    ReportBatchManager → TerminalX: Navigate to Archive
    ReportBatchManager → TerminalX: Check status table

    alt Report GENERATED
        ReportBatchManager: Mark as GENERATED
    else Report FAILED
        ReportBatchManager: Increment retry_count
        alt retry_count < max_retries
            ReportBatchManager → FenokReportGenerator: Regenerate
        else
            ReportBatchManager: Mark as FAILED (permanent)
        end
    else Still GENERATING
        ReportBatchManager: Wait 30s, check again
    end
end

[Phase 3: Extract & Process]
loop for each GENERATED Report
    FenokReportGenerator → TerminalX: Navigate to report_url
    FenokReportGenerator → TerminalX: Poll for supersearchx-body
    TerminalX -->> FenokReportGenerator: HTML content
    FenokReportGenerator → Filesystem: Save to generated_html/
end

FenokReportGenerator -->> User: Success (18 HTML files)
```

---

## 🔧 Implementation Strategy

### Option A: Quick Integration (5시간) ⭐ **권장**

#### 목표
main_generator.py에 최소 변경으로 18개 리포트 생성

#### 변경 사항

**1. Report Configuration Loader 추가**
```python
# main_generator.py 상단에 추가
def _load_report_configs(self, report_date_str: str) -> List[ReportConfig]:
    """18개 리포트 설정 로드"""
    configs = []

    # Custom Reports (6개)
    for part_type in ["Part1", "Part2"]:
        for i in range(1, 4):  # 각 Part당 3개
            configs.append(ReportConfig(
                report_id=f"custom_{part_type.lower()}_{i}",
                report_type="custom",
                part_type=part_type,
                title=f"{report_date_str} 100x Daily Wrap {part_type}",
                prompt_source=self._get_custom_prompt_path(part_type),
                template_id=10,
                source_pdf=self._get_source_pdf_path(part_type),
                prompt_pdf=self._get_prompt_pdf_path(part_type)
            ))

    # 일반 리포트 (12개)
    general_report_dir = os.path.join(self.project_dir, 'Feno_Docs', '일반리포트')
    for md_file in os.listdir(general_report_dir):
        if md_file.endswith('.md'):
            report_name = md_file.replace('.md', '')
            configs.append(ReportConfig(
                report_id=f"general_{report_name}",
                report_type="general",
                part_type="General",
                title=f"{report_date_str} {report_name}",
                prompt_source=os.path.join(general_report_dir, md_file),
                template_id=10,  # 또는 다른 ID
                past_day=90,  # 기본값, 필요 시 조정
                num_pages=30
            ))

    return configs
```

**2. Past Day 설정 함수 추가**
```python
# free_explorer.py:317-335 로직 이식
def _set_past_day_dropdown(self, past_day: int):
    """Past Day 드롭다운 설정

    Args:
        past_day: 90, 180, 270 등
    """
    try:
        # 1. "Any Time" 드롭다운 클릭
        any_time_dropdown = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Any Time')]"))
        )
        any_time_dropdown.click()
        time.sleep(1)

        # 2. Past Day 옵션 선택
        past_day_option = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), 'Past {past_day} Day')]"))
        )
        past_day_option.click()
        time.sleep(1)

        print(f"  - Past {past_day} Day 설정 완료")
        return True

    except Exception as e:
        print(f"  - Past Day 설정 실패: {e}")
        return False
```

**3. generate_report_html() 확장**
```python
def generate_report_html(self, report: Report, config: ReportConfig,
                          report_date_str: str, ref_date_start_str: str, ref_date_end_str: str):
    """리포트 생성 (Custom + 일반 통합)"""

    # ... (기존 폼 접근 로직)

    # Report Title 입력
    report_title_input.send_keys(report.title)

    if config.report_type == "custom":
        # Custom Report 로직 (기존 유지)
        self._input_date_directly(ref_date_start_str, True)
        self._input_date_directly(ref_date_end_str, False)
        upload_sample_input.send_keys(config.source_pdf)
        add_sources_input.send_keys(f"{config.source_pdf}\n{config.prompt_pdf}")

    elif config.report_type == "general":
        # 일반 리포트 로직 (신규)
        self._set_past_day_dropdown(config.past_day)

        # Keywords 설정 (필요 시)
        if config.keywords:
            keywords_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Keywords']")
            keywords_input.send_keys(config.keywords)

        # URLs 설정 (필요 시)
        if config.urls:
            urls_textarea = self.driver.find_element(By.XPATH, "//textarea[@placeholder='URLs']")
            urls_textarea.send_keys("\n".join(config.urls))

    # Prompt 입력 (공통)
    with open(config.prompt_source, 'r', encoding='utf-8') as f:
        prompt_content = f.read()

    prompt_textarea = self.driver.find_element(By.XPATH, "//textarea[@placeholder='...')
    pyperclip.copy(prompt_content)
    ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

    # Generate 버튼 클릭 (공통)
    # ... (기존 로직 유지)
```

**4. run_full_automation() 수정**
```python
def run_full_automation(self):
    """18개 리포트 통합 자동화"""

    if not self._login_terminalx():
        return

    batch_manager = ReportBatchManager(self.driver)

    today = datetime.now()
    report_date_str = today.strftime('%Y%m%d')
    ref_date_start = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    ref_date_end = today.strftime('%Y-%m-%d')

    # 18개 리포트 설정 로드
    report_configs = self._load_report_configs(report_date_str)

    # Phase 1: Fire-and-Forget
    print(f"\n--- Phase 1: {len(report_configs)}개 리포트 생성 요청 ---")
    for config in report_configs:
        report = Report(part_type=config.part_type, title=config.title)
        batch_manager.add_report(report)
        self.generate_report_html(report, config, report_date_str, ref_date_start, ref_date_end)

    # Phase 2: Monitor & Retry (기존 로직 유지)
    print("\n--- Phase 2: Archive 모니터링 ---")
    success = batch_manager.monitor_and_retry()

    # Phase 3: Extract & Process (기존 로직 유지)
    print("\n--- Phase 3: HTML 추출 ---")
    # ... (기존 코드)
```

#### 파일 변경 요약
| 파일 | 변경 내용 | 라인 수 |
|------|----------|---------|
| `main_generator.py` | +3 함수 (_load_report_configs, _set_past_day_dropdown, generate_report_html 확장) | +150 |
| `report_manager.py` | ReportConfig 데이터 클래스 추가 | +30 |
| **총계** | **2개 파일** | **+180 라인** |

#### 장점
✅ 최소 변경으로 18개 리포트 지원
✅ 기존 성공 코드 재사용 (검증된 패턴)
✅ 5시간 내 구현 가능
✅ 테스트 시간 최소화

#### 단점
⚠️ 35개 파일 중복 문제 미해결 (추후 리팩토링 필요)
⚠️ 코드 가독성 저하 (main_generator.py 1000+ 라인)

---

### Option B: Complete Redesign (5일) 🔄

#### 목표
35개 파일을 12개로 재구성, 중복 85% 제거

#### 새로운 파일 구조
```
100xFenok-generator/
├── src/
│   ├── core/
│   │   ├── config.py           # 설정 관리 (경로, 자격증명)
│   │   ├── browser.py          # WebDriver 추상화
│   │   └── auth.py             # TerminalX 인증
│   ├── report/
│   │   ├── generator.py        # 리포트 생성 핵심 로직
│   │   ├── monitor.py          # Archive 모니터링
│   │   ├── extractor.py        # HTML 추출 및 검증
│   │   └── config_loader.py    # 18개 리포트 설정 로드
│   ├── utils/
│   │   ├── date_utils.py       # 날짜 입력 로직
│   │   ├── file_utils.py       # 파일 I/O 헬퍼
│   │   └── logger.py           # 통합 로깅
│   └── models/
│       ├── report_config.py    # ReportConfig 데이터 모델
│       └── report_status.py    # Report 실행 상태
├── main.py                      # 엔트리 포인트
├── Feno_Docs/                   # 리포트 정의 (기존 유지)
└── tests/                       # 단위 테스트
```

#### 장점
✅ 코드 중복 85% → 5% 감소
✅ 단위 테스트 가능
✅ 유지보수성 향상
✅ 확장성 우수

#### 단점
❌ 5일 소요 (Phase 1: 1일, Phase 2: 2일, Phase 3: 1일, Phase 4: 1일)
❌ 전체 코드 재작성
❌ 회귀 테스트 위험
❌ 즉시 사용 불가

---

## 🚀 Recommended Approach

### Phase 1: Quick Integration (Option A)
**목표**: 18개 리포트 생성 기능 5시간 내 완성

**작업 순서**:
1. `ReportConfig` 데이터 클래스 추가 (30분)
2. `_load_report_configs()` 구현 (1시간)
3. `_set_past_day_dropdown()` 이식 (30분)
4. `generate_report_html()` 확장 (2시간)
5. `run_full_automation()` 통합 (1시간)

**검증 방법**:
```bash
# 테스트 실행
python main_generator.py

# 기대 결과:
# - 18개 리포트 생성 요청 성공
# - Archive에서 18개 모두 GENERATED 확인
# - generated_html/ 디렉토리에 18개 HTML 파일 생성
```

### Phase 2: Incremental Refactoring (Optional)
**조건**: Phase 1 안정화 후, 시간 여유 시 진행

**우선순위**:
1. **P1**: 중복 함수 추출 (로그인, HTML 추출) → utils/
2. **P2**: ReportBatchManager 강화 (병렬 모니터링)
3. **P3**: 테스트 커버리지 추가 (핵심 함수만)

---

## 📋 Risk Assessment

| 리스크 | 확률 | 영향 | 완화 전략 |
|--------|------|------|-----------|
| Past Day 드롭다운 셀렉터 변경 | 중 | 높음 | Multi-fallback 셀렉터 배열 사용 (free_explorer.py 패턴) |
| Archive 상태 확인 타임아웃 | 중 | 중간 | Retry 로직 + 타임아웃 20분 (현재 검증됨) |
| Template ID 불일치 (일반 리포트) | 낮 | 중간 | 사전 수동 테스트로 ID 확인 |
| 18개 동시 생성 시 플랫폼 제한 | 낮 | 높음 | Batch 크기 조정 (6개씩 3 rounds) |
| HTML 추출 실패 (No documents found) | 중 | 높음 | extract_and_validate_html() 폴링 로직 (이미 구현됨) |

---

## 🧪 Testing Strategy

### Unit Tests (Phase 2 이후)
```python
# tests/test_config_loader.py
def test_load_report_configs():
    configs = load_report_configs("20250723")
    assert len(configs) == 18
    assert configs[0].report_type == "custom"
    assert configs[6].report_type == "general"

# tests/test_past_day_dropdown.py
def test_set_past_day_dropdown(mock_driver):
    generator = FenokReportGenerator()
    success = generator._set_past_day_dropdown(90)
    assert success == True
```

### Integration Tests
```python
# tests/test_full_workflow.py
def test_18_reports_generation():
    generator = FenokReportGenerator()
    generator.run_full_automation()

    # 검증
    html_files = os.listdir(generator.generated_html_dir)
    assert len(html_files) == 18
```

### Manual Tests (Phase 1 필수)
1. Custom Report 1개 생성 → HTML 추출 성공 확인
2. 일반 리포트 1개 생성 → Past Day 설정 확인
3. 18개 일괄 생성 → Archive 모니터링 동작 확인

---

## 📝 Implementation Checklist

### Phase 1: Quick Integration (5시간)
- [ ] `ReportConfig` 데이터 클래스 정의 (report_manager.py)
- [ ] `_load_report_configs()` 구현 (main_generator.py)
  - [ ] Custom Reports (6개) 설정 생성
  - [ ] 일반 리포트 (12개) Feno_Docs 파싱
- [ ] `_set_past_day_dropdown()` 함수 추가 (free_explorer.py 이식)
  - [ ] Multi-fallback 셀렉터 배열
  - [ ] 클릭 + 옵션 선택 로직
- [ ] `generate_report_html()` 확장
  - [ ] `if config.report_type == "custom"` 분기
  - [ ] `elif config.report_type == "general"` 분기
  - [ ] Prompt 파일 읽기 공통화
- [ ] `run_full_automation()` 수정
  - [ ] 18개 설정 로드
  - [ ] Batch Manager에 18개 등록
  - [ ] Phase 1/2/3 워크플로우 통합
- [ ] 수동 테스트
  - [ ] Custom 1개 + 일반 1개 생성 확인
  - [ ] 18개 일괄 생성 확인
  - [ ] HTML 추출 성공 확인

### Phase 2: Stabilization (Optional)
- [ ] 에러 핸들링 강화
  - [ ] 각 리포트별 독립 try-catch
  - [ ] 실패 리포트 로그 상세화
- [ ] Retry 로직 개선
  - [ ] 실패 원인별 Retry 전략 (폼 오류 vs 생성 실패)
- [ ] 로깅 체계 정비
  - [ ] 파일 로그 추가 (logs/*.log)
  - [ ] 진행률 표시 (18개 중 N개 완료)

---

## 🔍 Key Technical Decisions

### 1. Template ID 전략
**결정**: 일반 리포트도 Template ID 10 사용 시도
**근거**:
- Custom Reports는 ID 10으로 검증됨
- Past Day 드롭다운은 폼 내 옵션으로 설정 가능 (PDF 업로드와 독립적)
- 실패 시 다른 ID로 fallback (5, 1 등)

**검증 방법**:
```python
# main_generator.py:311-347 리다이렉션 우회 로직 재사용
if "archive" in current_url:
    # 다중 우회 시도 (이미 구현됨)
    alternative_urls = [
        f"https://theterminalx.com/agent/enterprise/report/form/{template_id}",
        "https://theterminalx.com/agent/enterprise/report/form/5",
        "https://theterminalx.com/agent/enterprise/report/form/1"
    ]
```

### 2. Past Day 값 설정
**결정**: 기본값 90일, 리포트별 커스터마이즈 가능
**근거**:
- Feno_Docs/*.md 파일에 Past Day 명시되지 않음
- 90일은 분기 분석에 적합한 기간
- 추후 각 리포트 특성에 맞춰 조정 (예: 일일 리포트는 1일)

**설정 예시**:
```python
# report_configs.py (나중에 분리 시)
PAST_DAY_CONFIG = {
    "3.1 3.2 Gain Lose.md": 1,      # 일일 데이터
    "7.1 11 GICS Sector Table.md": 90,  # 분기 데이터
    "default": 90
}
```

### 3. Archive 모니터링 타임아웃
**결정**: 20분 유지 (현재 설정)
**근거**:
- main_generator.py:491에서 1200초(20분) 검증됨
- 18개 리포트 동시 생성 시 더 오래 걸릴 수 있으나, Retry 로직으로 대응

**개선 방안** (Phase 2):
```python
# 생성 중인 리포트 개수에 따라 동적 타임아웃
timeout = base_timeout + (num_pending_reports * 60)  # 리포트당 +1분
```

### 4. Batch 크기 전략
**결정**: Phase 1에서는 18개 일괄, 문제 발생 시 6개씩 분할
**근거**:
- TerminalX 플랫폼의 동시 생성 제한 불명
- Fire-and-Forget 패턴은 개별 생성 요청만 처리 (플랫폼 측 큐잉)
- Archive 모니터링은 병렬 진행 상태 확인 가능

**Fallback 계획**:
```python
# 플랫폼 제한 발견 시
for batch_start in range(0, 18, 6):
    batch_configs = report_configs[batch_start:batch_start+6]
    # Phase 1/2/3 실행
```

---

## 📊 Success Metrics

### 기능 완성도
- [ ] 18개 리포트 모두 생성 요청 성공
- [ ] Archive에서 18개 모두 GENERATED 상태 도달
- [ ] 18개 HTML 파일 모두 추출 및 저장

### 성능
- [ ] 전체 워크플로우 실행 시간 < 30분
- [ ] HTML 추출 실패율 < 5% (18개 중 1개 이하)
- [ ] Retry 성공률 > 90%

### 코드 품질
- [ ] 신규 코드 라인 수 < 200 (Option A)
- [ ] 기존 성공 패턴 재사용률 > 80%
- [ ] 주석 커버리지 > 50%

---

## 🔗 Dependencies

### External
- **Selenium WebDriver**: 4.x (Chrome)
- **pyperclip**: 클립보드 복사 (Prompt 입력)
- **Python**: 3.8+

### Internal
- `main_generator.py`: 핵심 생성 로직
- `report_manager.py`: Batch 관리
- `free_explorer.py`: Past Day 설정 참조
- `quick_archive_check.py`: Archive 모니터링 참조

### Configuration Files
- `Feno_Docs/일반리포트/*.md`: 12개 리포트 정의
- `input_data/*_Prompt_*.md`: Custom Reports Prompt
- `input_data/*_Sources_*.pdf`: Custom Reports PDF

---

## 📚 References

### 내부 문서
- `MASTER_GUIDE.md`: 전체 프로젝트 가이드
- `docs/ANALYSIS_20251006.md`: As-Is 분석 결과
- `docs/TROUBLESHOOTING.md`: 과거 실패 사례
- `CLAUDE.md`: 프로젝트별 지침

### 외부 자료
- [Selenium Python Docs](https://selenium-python.readthedocs.io/)
- [TerminalX Platform](https://theterminalx.com/agent/enterprise)

---

## 🎓 Lessons Learned

### 성공 요인 (2025-08-20)
1. **Archive 상태 확인 필수**: 생성 완료 대기 없이 추출 시 "No documents found"
2. **Multi-fallback 전략**: 로그인, 폼 접근 시 다중 셀렉터 배열 사용
3. **Hybrid Date Input**: contenteditable 세그먼트 + 숨은 input 동기화

### 실패 요인 (2025-08-25)
1. **Past Day 설정 누락**: 기존 코드 무시하고 새로 작성
2. **Archive 모니터링 생략**: 생성 요청 후 바로 추출 시도
3. **사용자 요구 미반영**: "100번 지시했는데도" 기존 자료 찾지 않음

### 교훈
- ✅ **기존 성공 코드 우선**: 새 파일 만들기 전에 재사용 검토
- ✅ **단계별 승인**: 각 Phase마다 사용자 확인 후 진행
- ✅ **증분 개발**: 전체 재작성보다 최소 변경 우선

---

## 📅 Timeline

### Option A: Quick Integration (5시간)
```
Hour 0-1: Setup & Planning
  - ReportConfig 데이터 모델 설계
  - _load_report_configs() 뼈대 작성

Hour 1-2: Configuration Loading
  - Custom Reports (6개) 설정 생성
  - Feno_Docs 파싱 로직

Hour 2-3: Past Day Implementation
  - _set_past_day_dropdown() 함수 이식
  - 테스트 (일반 리포트 1개)

Hour 3-5: Integration & Testing
  - generate_report_html() 확장
  - run_full_automation() 통합
  - 18개 일괄 생성 테스트
```

### Option B: Complete Redesign (5일)
```
Day 1: Architecture & Models
  - 새 파일 구조 생성
  - 데이터 모델 정의
  - 의존성 정리

Day 2-3: Core Implementation
  - 리포트 생성 로직 재작성
  - Archive 모니터링 재구현
  - HTML 추출 모듈화

Day 4: Integration & Migration
  - 기존 워크플로우 통합
  - 설정 파일 마이그레이션

Day 5: Testing & Stabilization
  - 단위 테스트 작성
  - 통합 테스트 실행
  - 버그 수정
```

---

## ✅ Approval Gates

### Gate 1: Architecture Approval
**질문**: Option A (5시간) vs Option B (5일)?
**승인 기준**: 사용자 일정 및 우선순위
**다음 단계**: 선택된 옵션의 Phase 1 시작

### Gate 2: Implementation Review (Option A)
**질문**: _load_report_configs() + _set_past_day_dropdown() 구현 완료?
**승인 기준**: 1개 일반 리포트 생성 성공
**다음 단계**: generate_report_html() 확장

### Gate 3: Final Validation
**질문**: 18개 리포트 모두 생성 성공?
**승인 기준**: generated_html/ 디렉토리에 18개 HTML 파일
**다음 단계**: 프로덕션 배포 또는 Phase 2 리팩토링

---

## 🚨 Critical Notes

### ⚠️ 절대 금지
1. **새 파일 생성 금지**: 35개 존재, 더 만들지 마라
2. **기존 성공 코드 무시 금지**: main_generator.py 2025-08-20 검증됨
3. **Archive 확인 생략 금지**: Phase 2 필수
4. **임의 진행 금지**: 각 Gate마다 승인 받기

### ✅ 필수 확인
1. **로그인 성공**: _login_terminalx() multi-fallback
2. **폼 접근 성공**: Template ID 10 리다이렉션 우회
3. **Archive GENERATED**: monitor_and_retry() 상태 확인
4. **HTML 추출 성공**: supersearchx-body 존재 + 50KB 이상

---

**문서 종료**
**다음 단계**: Gate 1 - Architecture Approval
