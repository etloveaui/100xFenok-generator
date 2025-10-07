# 100xFenok-Generator System Diagrams

## 1. High-Level System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    100xFenok-Generator System                   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    main_generator.py                      │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │  Configuration Layer                                │  │ │
│  │  │  - Load credentials                                 │  │ │
│  │  │  - Setup WebDriver                                  │  │ │
│  │  │  - Initialize paths                                 │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │  Authentication Layer                               │  │ │
│  │  │  - Multi-fallback login                            │  │ │
│  │  │  - Session management                               │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │  Report Generation Layer                            │  │ │
│  │  │  - Load 18 report configs                          │  │ │
│  │  │  - Custom reports (6): Template + PDF              │  │ │
│  │  │  - General reports (12): Prompt + Past Day         │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │  Orchestration Layer                                │  │ │
│  │  │  Phase 1: Fire-and-Forget (18 requests)            │  │ │
│  │  │  Phase 2: Monitor & Retry (Archive polling)        │  │ │
│  │  │  Phase 3: Extract & Process (HTML extraction)      │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                  report_manager.py                        │ │
│  │  - ReportBatchManager: Archive monitoring                │ │
│  │  - Report status tracking: PENDING → GENERATING →        │ │
│  │    GENERATED | FAILED                                    │ │
│  │  - Retry logic: max 3 attempts per report                │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                   Selenium WebDriver                      │ │
│  │  - Chrome browser automation                              │ │
│  │  - Element interaction (click, type, upload)             │ │
│  │  - Page navigation and URL tracking                      │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                  TerminalX Web Platform                         │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐│
│  │  Login Page      │  │  Report Form     │  │  Archive     ││
│  │  /agent/         │→ │  /report/form/10 │→ │  /archive    ││
│  │  enterprise      │  │                  │  │              ││
│  └──────────────────┘  └──────────────────┘  └──────────────┘│
│                              │                      │          │
│                              ▼                      ▼          │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │               Report Generation Engine                    │ │
│  │  - Process uploaded PDFs (Custom)                        │ │
│  │  - Execute search queries (General)                      │ │
│  │  - Generate HTML reports                                 │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Generated Report Pages                       │ │
│  │  /agent/enterprise/report/[ID]                           │ │
│  │  - Contains supersearchx-body class                      │ │
│  │  - Rendered HTML content                                 │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                      Local Filesystem                           │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐│
│  │  Input Data      │  │  Feno_Docs       │  │  Output      ││
│  │                  │  │                  │  │              ││
│  │  Part1 Template  │  │  일반리포트/     │  │  generated_  ││
│  │  Part2 Template  │  │  - 3.1 3.2 Gain  │  │  html/       ││
│  │  Source PDFs     │  │  - 3.3 Fixed     │  │  (18 files)  ││
│  │  Prompt PDFs     │  │  - 5.1 Major IB  │  │              ││
│  │                  │  │  - ... (12 total)│  │              ││
│  └──────────────────┘  └──────────────────┘  └──────────────┘│
└────────────────────────────────────────────────────────────────┘
```

---

## 2. Report Generation Workflow (18 Reports)

```
┌─────────────────────────────────────────────────────────────┐
│                  Phase 1: Fire-and-Forget                    │
│                   (리포트 생성 요청)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  _load_report_configs()                 │
        │  Load 18 report configurations          │
        └─────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
    ┌─────────────────────┐   ┌─────────────────────┐
    │  Custom Reports (6) │   │  General Reports    │
    │  - Part1: 3개       │   │  (12)               │
    │  - Part2: 3개       │   │  - Feno_Docs/*.md   │
    │  - Template ID 10   │   │  - Past Day: 90     │
    │  - Upload PDFs      │   │  - Template ID 10   │
    └─────────────────────┘   └─────────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Loop: for each ReportConfig            │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Navigate to Report Form                │
        │  https://terminalx.com/.../form/10      │
        └─────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
    ┌─────────────────────┐   ┌─────────────────────┐
    │  Custom Flow:       │   │  General Flow:      │
    │  1. Upload PDFs     │   │  1. Set Past Day    │
    │  2. Set date range  │   │  2. Input keywords  │
    │  3. Input prompt    │   │  3. Input prompt    │
    └─────────────────────┘   └─────────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Click Generate Button                  │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Wait for URL change                    │
        │  /report/form → /report/[ID]            │
        │  Store report.url                       │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Confirm "Generating..." message        │
        │  report.status = "GENERATING"           │
        └─────────────────────────────────────────┘
                              │
                              ▼
                      (Repeat for 18 reports)

┌─────────────────────────────────────────────────────────────┐
│                  Phase 2: Monitor & Retry                    │
│                   (상태 모니터링)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Navigate to Archive Page               │
        │  https://terminalx.com/.../archive      │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Poll Archive Table (every 30s)         │
        │  Check status of 18 reports             │
        └─────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    ┌──────────┐      ┌──────────────┐    ┌──────────┐
    │ GENERATED│      │  GENERATING  │    │  FAILED  │
    └──────────┘      └──────────────┘    └──────────┘
          │                   │                   │
          │                   │                   ▼
          │                   │         ┌──────────────────┐
          │                   │         │ retry_count < 3? │
          │                   │         └──────────────────┘
          │                   │                │          │
          │                   │              Yes         No
          │                   │                │          │
          │                   │                ▼          ▼
          │                   │         ┌──────────┐  ┌──────┐
          │                   │         │ Regenerate│  │Mark  │
          │                   │         │  Report   │  │FAILED│
          │                   │         └──────────┘  └──────┘
          │                   │                │
          │                   │                ▼
          │                   └────────────▶ Wait 30s
          │                                    │
          │◀───────────────────────────────────┘
          │
          ▼
    (Continue when all 18 are GENERATED or max retries)

┌─────────────────────────────────────────────────────────────┐
│                Phase 3: Extract & Process                    │
│                    (HTML 추출)                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Loop: for each GENERATED report        │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Navigate to report.url                 │
        │  /agent/enterprise/report/[ID]          │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Poll for supersearchx-body class       │
        │  (max 120s)                             │
        └─────────────────────────────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          │                                       │
          ▼                                       ▼
    ┌──────────────┐                    ┌──────────────┐
    │ Class Found? │──Yes──▶            │ Check Size   │
    └──────────────┘                    │  > 50KB?     │
          │                             └──────────────┘
          No                                    │
          │                          ┌─────────┴─────────┐
          ▼                          │                   │
    ┌──────────────┐              Yes                   No
    │ Wait 5s      │                │                   │
    │ (max 120s)   │                ▼                   ▼
    └──────────────┘         ┌──────────────┐    ┌──────────┐
          │                  │ Extract HTML │    │  Retry   │
          └─────────────────▶│ Save to file │    └──────────┘
                             └──────────────┘
                                    │
                                    ▼
                        ┌─────────────────────┐
                        │  generated_html/    │
                        │  report_[N].html    │
                        └─────────────────────┘
                                    │
                                    ▼
                            (Repeat for 18 reports)
                                    │
                                    ▼
                        ┌─────────────────────┐
                        │  SUCCESS            │
                        │  18 HTML files      │
                        └─────────────────────┘
```

---

## 3. Data Flow Diagram

```
┌────────────────────────────────────────────────────────────┐
│                        Input Data                           │
└────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌──────────────────┐                      ┌──────────────────┐
│  Custom Reports  │                      │ General Reports  │
│                  │                      │                  │
│  input_data/     │                      │ Feno_Docs/       │
│  - Prompt_1.md   │                      │ 일반리포트/       │
│  - Prompt_2.md   │                      │ - 3.1 3.2.md     │
│  - Sources_1.pdf │                      │ - 3.3.md         │
│  - Sources_2.pdf │                      │ - 5.1.md         │
│                  │                      │ - ... (12 files) │
└──────────────────┘                      └──────────────────┘
        │                                           │
        └─────────────────────┬─────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  _load_report_configs()                 │
        │  Parse files, create ReportConfig       │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  List[ReportConfig] (18 items)          │
        │  ┌─────────────────────────────────┐   │
        │  │ ReportConfig                    │   │
        │  │ - report_id: str                │   │
        │  │ - report_type: custom|general   │   │
        │  │ - title: str                    │   │
        │  │ - prompt_source: path           │   │
        │  │ - past_day: Optional[int]       │   │
        │  │ - source_pdf: Optional[path]    │   │
        │  └─────────────────────────────────┘   │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  generate_report_html()                 │
        │  Fill form based on ReportConfig        │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  TerminalX Platform Processing          │
        │  (5-20 minutes per report)              │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Archive Status Monitoring              │
        │  Report.status: GENERATING → GENERATED  │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  extract_and_validate_html()            │
        │  Download rendered HTML                 │
        └─────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                       Output Data                           │
│                                                             │
│  generated_html/                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │ Custom Reports (6):                               │     │
│  │ - 20250723_part1_1.html                          │     │
│  │ - 20250723_part1_2.html                          │     │
│  │ - 20250723_part1_3.html                          │     │
│  │ - 20250723_part2_1.html                          │     │
│  │ - 20250723_part2_2.html                          │     │
│  │ - 20250723_part2_3.html                          │     │
│  │                                                   │     │
│  │ General Reports (12):                             │     │
│  │ - 20250723_3.1_3.2_gain_lose.html                │     │
│  │ - 20250723_3.3_fixed_income.html                 │     │
│  │ - 20250723_5.1_major_ib_updates.html             │     │
│  │ - 20250723_6.3_dark_pool.html                    │     │
│  │ - 20250723_7.1_11_gics_sector.html               │     │
│  │ - 20250723_8.1_12_key_tickers.html               │     │
│  │ - ... (6 more)                                    │     │
│  └──────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────┘
```

---

## 4. Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  main_generator.py                           │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  __init__()                                         │    │
│  │  - Load credentials                                 │    │
│  │  - Setup WebDriver                                  │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  _login_terminalx()                                 │    │
│  │  Multi-fallback: 6 login button selectors           │    │
│  │                  4 email input selectors             │    │
│  │                  3 password selectors                │    │
│  │                  7 submit button selectors           │    │
│  │                  6 success indicators                │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  run_full_automation()                              │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │ Phase 1: Fire-and-Forget                     │  │    │
│  │  │ for config in report_configs:                │  │    │
│  │  │   generate_report_html(config)               │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │           │                                         │    │
│  │           ▼                                         │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │ Phase 2: Monitor & Retry                     │  │    │
│  │  │ batch_manager.monitor_and_retry()            │◀─┼────┼──┐
│  │  └──────────────────────────────────────────────┘  │    │  │
│  │           │                                         │    │  │
│  │           ▼                                         │    │  │
│  │  ┌──────────────────────────────────────────────┐  │    │  │
│  │  │ Phase 3: Extract & Process                   │  │    │  │
│  │  │ for report in GENERATED:                     │  │    │  │
│  │  │   extract_and_validate_html(report)          │  │    │  │
│  │  └──────────────────────────────────────────────┘  │    │  │
│  └────────────────────────────────────────────────────┘    │  │
│                                                             │  │
└─────────────────────────────────────────────────────────────┘  │
                                                                  │
┌─────────────────────────────────────────────────────────────┐  │
│                  report_manager.py                           │  │
│                                                              │  │
│  ┌────────────────────────────────────────────────────┐    │  │
│  │  ReportBatchManager                                 │    │  │
│  │  - reports: List[Report]                            │    │  │
│  │  - max_retries_per_report: 3                        │    │  │
│  │  - archive_check_interval: 30s                      │    │  │
│  └────────────────────────────────────────────────────┘    │  │
│                           │                                  │  │
│                           ▼                                  │  │
│  ┌────────────────────────────────────────────────────┐    │  │
│  │  monitor_and_retry()                                │◀───┼──┘
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │ Loop (max 20 minutes):                       │  │    │
│  │  │   Navigate to Archive                        │  │    │
│  │  │   Check status table                         │  │    │
│  │  │   Parse report rows                          │  │    │
│  │  │   Update Report.status                       │  │    │
│  │  │   If FAILED & retry_count < 3:               │  │    │
│  │  │     Trigger regeneration                     │──┼────┼──┐
│  │  │   Sleep 30s                                  │  │    │  │
│  │  └──────────────────────────────────────────────┘  │    │  │
│  └────────────────────────────────────────────────────┘    │  │
│                                                             │  │
└─────────────────────────────────────────────────────────────┘  │
                                                                  │
┌─────────────────────────────────────────────────────────────┐  │
│                  Selenium WebDriver                          │  │
│                                                              │  │
│  ┌────────────────────────────────────────────────────┐    │  │
│  │  Chrome Browser Instance                            │    │  │
│  │  - Window position: -1920, 0 (Left FHD monitor)    │    │  │
│  │  - Maximize window                                  │    │  │
│  │  - Page load timeout: 60s                           │    │  │
│  └────────────────────────────────────────────────────┘    │  │
│                           │                                  │  │
│                           ▼                                  │  │
│  ┌────────────────────────────────────────────────────┐    │  │
│  │  Element Interaction Methods                        │    │  │
│  │  - find_element(By.XPATH, selector)                 │    │  │
│  │  - WebDriverWait(driver, timeout)                   │    │  │
│  │  - element.click()                                  │    │  │
│  │  - element.send_keys(text)                          │    │  │
│  │  - execute_script(js_code)                          │    │  │
│  └────────────────────────────────────────────────────┘    │  │
│                           │                                  │  │
│                           ▼                                  │  │
│  ┌────────────────────────────────────────────────────┐    │  │
│  │  Page State Management                              │    │  │
│  │  - driver.get(url)                                  │    │  │
│  │  - driver.current_url                               │    │  │
│  │  - driver.page_source                               │    │  │
│  └────────────────────────────────────────────────────┘    │  │
└─────────────────────────────────────────────────────────────┘  │
                           │                                      │
                           ▼                                      │
┌─────────────────────────────────────────────────────────────┐  │
│                  TerminalX Platform                          │  │
│                                                              │  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │  │
│  │ Login   │→ │ Form    │→ │ Report  │→ │ Archive │       │  │
│  │ Page    │  │ Page    │  │ Page    │  │ Page    │       │  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │  │
│                    │             │             │            │  │
│                    └──────┬──────┴──────┬──────┘            │  │
│                           │             │                   │  │
│                           ▼             ▼                   │  │
│              ┌─────────────────────────────────┐            │  │
│              │  Report Generation Queue        │            │  │
│              │  (Server-side processing)       │            │  │
│              └─────────────────────────────────┘            │  │
└─────────────────────────────────────────────────────────────┘  │
                                                                  │
                           Retry Loop ◀──────────────────────────┘
```

---

## 5. Error Handling & Recovery Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Error Handling Strategy                   │
└─────────────────────────────────────────────────────────────┘

Phase 1: Report Generation Errors
─────────────────────────────────
    │
    ▼
┌──────────────────┐
│ Archive Redirect │  ← 가장 흔한 에러
│ Detected?        │
└──────────────────┘
    │
    Yes
    │
    ▼
┌─────────────────────────────────────────┐
│ Multi-level Bypass Strategy:            │
│ 1. Direct retry (wait 5s)                │
│ 2. Alternative template IDs (10→5→1)    │
│ 3. Archive "New Report" button          │
│ 4. JavaScript forced navigation          │
└─────────────────────────────────────────┘
    │
    ▼
┌──────────────────┐
│ Success?         │
└──────────────────┘
    │          │
   Yes         No
    │          │
    │          ▼
    │    ┌──────────────────┐
    │    │ Mark FAILED      │
    │    │ Report to user   │
    │    └──────────────────┘
    ▼
┌──────────────────┐
│ Continue to      │
│ next report      │
└──────────────────┘

Phase 2: Archive Monitoring Errors
───────────────────────────────────
    │
    ▼
┌──────────────────┐
│ Report Status?   │
└──────────────────┘
    │
    ├─ GENERATING ──▶ Continue polling (max 20 min)
    │
    ├─ GENERATED ───▶ Proceed to extraction
    │
    └─ FAILED ──────▶ Retry logic
                        │
                        ▼
                  ┌──────────────────┐
                  │ retry_count < 3? │
                  └──────────────────┘
                        │          │
                       Yes         No
                        │          │
                        ▼          ▼
                  ┌──────────┐  ┌──────────┐
                  │ Increment│  │ Mark     │
                  │ counter  │  │ FAILED   │
                  │ Regenerate│  │ (final)  │
                  └──────────┘  └──────────┘

Phase 3: HTML Extraction Errors
────────────────────────────────
    │
    ▼
┌──────────────────────────────┐
│ supersearchx-body found?     │
└──────────────────────────────┘
    │          │
   Yes         No
    │          │
    │          ▼
    │    ┌──────────────────────┐
    │    │ "No documents found"? │
    │    └──────────────────────┘
    │          │          │
    │         Yes         No
    │          │          │
    │          ▼          ▼
    │    ┌──────────┐  ┌─────────┐
    │    │ Report   │  │ Wait 5s │
    │    │ not ready│  │ Retry   │
    │    │ (fail)   │  │ (120s   │
    │    └──────────┘  │ max)    │
    │                  └─────────┘
    ▼
┌──────────────────┐
│ HTML size > 50KB?│
└──────────────────┘
    │          │
   Yes         No
    │          │
    ▼          ▼
┌──────────┐  ┌─────────┐
│ Save     │  │ Too     │
│ file     │  │ small,  │
│ SUCCESS  │  │ retry   │
└──────────┘  └─────────┘
```

---

## 6. State Transition Diagram (Report Lifecycle)

```
┌─────────────────────────────────────────────────────────────┐
│                   Report Status Lifecycle                    │
└─────────────────────────────────────────────────────────────┘

       ┌─────────────┐
       │   PENDING   │  ← Initial state when Report object created
       └─────────────┘
             │
             │ generate_report_html() called
             │ Form submission successful
             │
             ▼
       ┌─────────────┐
       │ GENERATING  │  ← "Generating..." message confirmed
       └─────────────┘    report.url stored
             │
             │ Archive monitoring detects status
             │
       ┌─────┴──────────────────┐
       │                        │
       ▼                        ▼
 ┌──────────┐            ┌──────────┐
 │ GENERATED│            │  FAILED  │
 └──────────┘            └──────────┘
       │                        │
       │                        │ retry_count < max_retries?
       │                        │
       │                  ┌─────┴─────┐
       │                 Yes           No
       │                  │             │
       │                  ▼             ▼
       │          ┌──────────────┐  ┌──────────────┐
       │          │ retry_count++│  │ FAILED       │
       │          │ → PENDING    │  │ (permanent)  │
       │          └──────────────┘  └──────────────┘
       │                  │
       │                  └─────────────┐
       │                                │
       │◀───────────────────────────────┘
       │
       │ extract_and_validate_html() called
       │
       ▼
 ┌──────────────┐
 │ HTML_EXTRACTED│  ← Final success state
 └──────────────┘    HTML file saved to disk


Legend:
─────────
PENDING:        Report created, not yet submitted
GENERATING:     Form submitted, TerminalX processing
GENERATED:      TerminalX completed, ready for extraction
FAILED:         Generation failed (network/platform error)
HTML_EXTRACTED: HTML successfully saved to disk
```

---

**문서 종료**
**다음 참조**: ARCHITECTURE_DESIGN.md (상세 설명)
