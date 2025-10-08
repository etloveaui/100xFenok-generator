# 100xFenok-Generator 전체 자동화 설계 문서

**문서 생성일**: 2025-10-07
**설계 목표**: TerminalX → HTML 추출 → JSON 변환 → Gemini 통합 → 최종 100x Daily Wrap 생성까지 완전 자동화

---

## 1. 전체 아키텍처 개요

### 1.1 현재 워크플로우 (수동)
```
[사용자 수동 작업]
├─ Step 1: TerminalX 18개 리포트 생성
│   ├─ 6개 Part1 Custom (Template ID 10)
│   ├─ 6개 Part2 Custom (Template ID 10)
│   └─ 6개 일반 리포트 (Feno_Docs/일반리포트/*.md)
│
├─ Step 2: HTML → JSON 변환 (json_converter.py 사용?)
│
├─ Step 3: Gemini 웹사이트에 수동 복붙
│   ├─ 18개 HTML 파일 업로드
│   ├─ Instruction_Html.md 프롬프트 입력
│   └─ Gemini가 최우수 콘텐츠 선택 + 한국어 번역
│
└─ Step 4: 최종 100x Daily Wrap HTML 저장
```

### 1.2 목표 워크플로우 (자동화)
```
[완전 자동화 시스템]
├─ Phase 1: TerminalX 자동화 (main_generator.py 개선)
│   ├─ 로그인
│   ├─ 18개 리포트 생성 요청
│   ├─ Archive 완료 대기 (폴링) ← 핵심 누락 기능
│   └─ HTML 추출
│
├─ Phase 2: 데이터 변환 (json_converter.py)
│   ├─ HTML → JSON 변환
│   └─ 파일 정리 및 저장
│
├─ Phase 3: Gemini 자동 통합 (신규 개발 필요)
│   ├─ Gemini API 호출 OR 웹 자동화
│   ├─ Instruction_Html.md 프롬프트 전달
│   ├─ 18개 HTML 파일 입력
│   └─ 최종 100x Daily Wrap HTML 생성
│
└─ Phase 4: 결과 저장 및 알림
    ├─ 완성된 한국어 리포트 저장
    └─ 사용자에게 완료 알림
```

---

## 2. 데이터 플로우 다이어그램

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       Phase 1: TerminalX 자동화                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  [main_generator.py]                                                     │
│  ↓                                                                        │
│  1. 로그인 (verify_system.py 검증된 multi-fallback 전략)                 │
│  ↓                                                                        │
│  2. 18개 리포트 생성 요청                                                 │
│     ├─ Part1 Custom × 3 (Feno_Docs/part1/*.md 프롬프트)                 │
│     ├─ Part2 Custom × 3 (Feno_Docs/part2/*.md 프롬프트)                 │
│     └─ 일반 리포트 × 6 (Feno_Docs/일반리포트/*.md 프롬프트)             │
│         + Past Day 설정 (free_explorer.py 로직)                          │
│  ↓                                                                        │
│  3. Archive 완료 대기 (quick_archive_check.py 로직 통합) ← NEW!         │
│     - 폴링 주기: 5초 간격                                                 │
│     - 타임아웃: 300초 (5분)                                              │
│     - 상태 확인: "Generated" or "Ready" 확인                             │
│  ↓                                                                        │
│  4. HTML 추출 (supersearchx-body 클래스 검증)                            │
│     - 성공: supersearchx-body 포함 HTML                                  │
│     - 실패: "No documents found" → 에러                                  │
│  ↓                                                                        │
│  [Output: 18개 HTML 파일]                                                │
│  - generated_html/part1_01.html ~ part1_03.html                         │
│  - generated_html/part2_01.html ~ part2_03.html                         │
│  - generated_html/general_01.html ~ general_06.html                     │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                     Phase 2: 데이터 변환                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  [json_converter.py - TerminalXJSONConverter]                            │
│  ↓                                                                        │
│  1. HTML 파일 읽기 (BeautifulSoup 파싱)                                  │
│  ↓                                                                        │
│  2. 구조화된 JSON 변환                                                    │
│     - 섹션 (h2, h3) 추출                                                  │
│     - 테이블 파싱 (금융 데이터 특별 처리)                                 │
│     - 리스트, 텍스트 콘텐츠 파싱                                          │
│  ↓                                                                        │
│  3. 금융 데이터 정제                                                      │
│     - 통화 기호 처리 ($150.25 → {"value": 150.25, "unit": "$"})         │
│     - 퍼센트 처리 (3.85% → {"value": 3.85, "unit": "%"})                │
│     - 테이블 타입 자동 감지 (stock_data, interest_rates, etc.)          │
│  ↓                                                                        │
│  [Output: 18개 JSON 파일]                                                │
│  - generated_json/part1_01.json ~ part1_03.json                         │
│  - generated_json/part2_01.json ~ part2_03.json                         │
│  - generated_json/general_01.json ~ general_06.json                     │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                   Phase 3: Gemini 자동 통합 (NEW)                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  [Option A: Gemini API 연동] OR [Option B: 웹 자동화]                    │
│  ↓                                                                        │
│  1. Instruction_Html.md 프롬프트 로드                                     │
│     - 역할: 리포트 자동화 생성 에이전트                                   │
│     - 작업: 최우수 콘텐츠 선택 + 한국어 번역 + 템플릿 삽입               │
│  ↓                                                                        │
│  2. 18개 HTML 파일 입력                                                   │
│     - Gemini API: multimodal input (text + HTML)                         │
│     - 웹 자동화: Playwright/Selenium 파일 업로드                         │
│  ↓                                                                        │
│  3. Gemini 처리 (Instruction_Html.md 규칙)                               │
│     - 데이터 정제 (인용 부호 [##] 제거, 메타데이터 제거)                 │
│     - 최우수 콘텐츠 선택 (정보 깊이, 논리 명확성, 통찰력)                │
│     - 특별 규칙: 7.1, 8.1 테이블 완전성 검증 + 외부 데이터 보완          │
│     - 한국어 번역 (전문 금융 표현, 티커/고유명사 영문 유지)              │
│     - 템플릿 삽입 (id 기반 매핑, placeholder 교체)                        │
│  ↓                                                                        │
│  4. 최종 HTML 생성                                                        │
│     - 100x Daily Wrap 한국어 금융 리포트                                 │
│  ↓                                                                        │
│  [Output: 1개 완성된 HTML 파일]                                          │
│  - output/100x-daily-wrap-YYYYMMDD.html                                 │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                     Phase 4: 최종 결과 저장                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  [final_output_handler.py]                                               │
│  ↓                                                                        │
│  1. 완성된 HTML 저장                                                      │
│     - 경로: projects/100xFenok/100x/daily-wrap/                          │
│     - 파일명: 100x-daily-wrap-YYYYMMDD.html                              │
│  ↓                                                                        │
│  2. version.js 업데이트 (선택 사항)                                       │
│  ↓                                                                        │
│  3. 사용자 알림                                                           │
│     - 로그 출력: "100x Daily Wrap 생성 완료!"                            │
│     - 파일 경로 출력                                                      │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Phase별 상세 작업

### Phase 1: TerminalX 자동화 (main_generator.py 개선)

#### 현재 문제점
- **Archive 완료 대기 로직 누락**: 리포트 생성 요청 후 바로 추출 시도
- **결과**: "No documents found" 에러 (supersearchx-body 없음)
- **증거**: `quick_archive_check.py`에는 폴링 로직 존재하지만 `main_generator.py`에 통합 안됨

#### 해결 방안
```python
# main_generator.py 개선안

def generate_report_with_archive_check(self, report: Report):
    """리포트 생성 + Archive 완료 대기 통합 로직"""

    # 1. 리포트 생성 요청 (기존 코드)
    success = self._submit_report_request(report)
    if not success:
        return False

    # 2. Archive 완료 대기 (NEW - quick_archive_check.py 로직 통합)
    print(f"[Archive Monitor] {report.title} 완료 대기 중...")
    completed = self._wait_for_archive_completion(report, timeout=300)

    if not completed:
        print(f"[Archive Monitor] 타임아웃: {report.title}")
        report.status = "FAILED"
        return False

    # 3. HTML 추출 (완료 확인 후 실행)
    html_content = self._extract_html(report)
    if not html_content or 'No documents found' in html_content:
        print(f"[HTML Extractor] 추출 실패: {report.title}")
        report.status = "FAILED"
        return False

    # 4. HTML 저장
    html_path = self._save_html(html_content, report)
    report.html_path = html_path
    report.status = "GENERATED"
    return True

def _wait_for_archive_completion(self, report: Report, timeout: int = 300):
    """
    Archive 페이지를 폴링하여 리포트 완료 대기
    quick_archive_check.py:183-209 로직 기반
    """
    start_time = time.time()
    check_interval = 5  # 5초 간격

    while (time.time() - start_time) < timeout:
        # Archive 페이지로 이동
        self.driver.get('https://theterminalx.com/agent/enterprise/report/archive')
        time.sleep(3)  # 페이지 로딩 대기

        # JavaScript 렌더링 대기
        time.sleep(7)

        # 리포트 상태 확인
        status = self._check_report_status_in_archive(report.title)

        if status == "GENERATED" or status == "READY":
            print(f"[Archive Monitor] {report.title} 완료!")
            return True
        elif status == "FAILED":
            print(f"[Archive Monitor] {report.title} 생성 실패")
            return False

        # 다음 확인까지 대기
        print(f"[Archive Monitor] {report.title} 생성 중... ({int(time.time() - start_time)}초 경과)")
        time.sleep(check_interval)

    return False

def _check_report_status_in_archive(self, report_title: str):
    """Archive 페이지에서 특정 리포트의 상태 확인"""
    try:
        # 테이블 행 찾기
        rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")

        for row in rows:
            title_element = row.find_element(By.XPATH, ".//td[1]")
            current_title = title_element.text.strip()

            if report_title in current_title:
                # 상태 열 추출 (4번째 td)
                status_element = row.find_element(By.XPATH, ".//td[4]")
                status_text = status_element.text.strip().upper()

                return status_text

        # 해당 리포트를 찾지 못한 경우
        return "GENERATING"

    except Exception as e:
        print(f"[Archive Monitor] 상태 확인 실패: {e}")
        return "GENERATING"
```

#### Part1/Part2 프롬프트 확인 필요
- **현재 상태**: `Feno_Docs/part1/` 및 `Feno_Docs/part2/` 폴더에 HTML/JSON 예시 존재
- **질문**: Part1/Part2 리포트의 실제 프롬프트는 어디에 있나?
- **추정**: 별도 `.md` 파일 또는 `main_generator.py`에 하드코딩되어 있을 가능성

#### 일반 리포트 구현
```python
# Feno_Docs/일반리포트/*.md 기반 6개 리포트 생성

GENERAL_REPORTS = [
    "3.1 3.2 Gain Lose.md",
    "3.3 Fixed Income.md",
    "5.1 Major IB Updates.md",
    "6.3 Dark Pool & Political Donation Flows.md",
    "7.1 11 GICS Sector Table.md",
    "8.1 12 Key Tickers Table.md"
]

def generate_general_reports(self):
    """일반 리포트 6개 생성 (Past Day 설정 포함)"""
    for report_md in GENERAL_REPORTS:
        prompt_path = os.path.join(self.project_dir, 'Feno_Docs', '일반리포트', report_md)

        # 프롬프트 로드
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_text = f.read()

        # 리포트 생성 (Past Day 설정 적용)
        report = Report(part_type="GENERAL", title=report_md.replace('.md', ''))

        # Past Day 설정 (free_explorer.py:317-335 로직)
        self._set_past_day_filter()

        # 리포트 생성 요청 + Archive 대기
        success = self.generate_report_with_archive_check(report)

        if success:
            print(f"[General Report] {report.title} 생성 완료")
        else:
            print(f"[General Report] {report.title} 생성 실패")
```

---

### Phase 2: 데이터 변환 (json_converter.py)

#### 현재 상태
- **파일 존재**: `json_converter.py` (512줄)
- **기능**: TerminalX HTML → JSON 변환 (금융 데이터 특별 처리 포함)
- **작동 여부**: 미확인 (테스트 필요)

#### 검증 필요 사항
1. **금융 테이블 파싱 정확도**: 섹션 7.1, 8.1 테이블 완전성
2. **데이터 정제 품질**: 통화/퍼센트 파싱 정확도
3. **대량 변환 안정성**: 18개 파일 일괄 변환 성공률

#### 개선 제안
```python
# json_converter.py 개선안

def batch_convert_with_validation(self, html_files, output_dir):
    """18개 HTML → JSON 변환 + 검증"""
    results = {
        "success": [],
        "failed": [],
        "validation_errors": []
    }

    for html_file in html_files:
        try:
            # JSON 변환
            json_path = self.convert_html_file(html_file, output_dir)

            # 변환 결과 검증
            if self._validate_json_output(json_path):
                results["success"].append(json_path)
            else:
                results["validation_errors"].append(json_path)

        except Exception as e:
            results["failed"].append({"file": html_file, "error": str(e)})

    return results

def _validate_json_output(self, json_path):
    """JSON 변환 결과 검증"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 필수 필드 존재 확인
    if "sections" not in data:
        return False

    # 섹션별 콘텐츠 검증
    for section in data["sections"]:
        if not section.get("content"):
            return False

    return True
```

---

### Phase 3: Gemini 자동 통합 (신규 개발)

#### Option A: Gemini API 연동 (권장)

**장점**:
- 안정적인 자동화
- 브라우저 자동화 불필요
- 에러 처리 명확

**단점**:
- API Key 필요
- API 비용 발생 가능
- Multimodal 지원 확인 필요

**구현 예시**:
```python
# gemini_integrator.py (NEW)

import google.generativeai as genai
import os

class GeminiAutoIntegrator:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')  # 또는 gemini-2.5-pro

    def generate_daily_wrap(self, html_files, instruction_path):
        """
        18개 HTML 파일 + Instruction_Html.md → 최종 100x Daily Wrap 생성
        """
        # 1. Instruction 로드
        with open(instruction_path, 'r', encoding='utf-8') as f:
            instruction = f.read()

        # 2. HTML 파일들 로드
        html_contents = []
        for html_file in html_files:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_contents.append({
                    "filename": os.path.basename(html_file),
                    "content": f.read()
                })

        # 3. 프롬프트 구성
        prompt = self._build_prompt(instruction, html_contents)

        # 4. Gemini API 호출
        response = self.model.generate_content(prompt)

        # 5. 최종 HTML 추출
        final_html = self._extract_html_from_response(response.text)

        return final_html

    def _build_prompt(self, instruction, html_contents):
        """Gemini API용 프롬프트 구성"""
        prompt_parts = [instruction]

        for html_data in html_contents:
            prompt_parts.append(f"\n## {html_data['filename']}\n")
            prompt_parts.append(html_data['content'])

        return "\n".join(prompt_parts)

    def _extract_html_from_response(self, response_text):
        """
        Gemini 응답에서 ```html ... ``` 코드 블록 추출
        """
        import re

        # ```html ... ``` 패턴 찾기
        pattern = r'```html\s*(.*?)\s*```'
        matches = re.findall(pattern, response_text, re.DOTALL)

        if matches:
            return matches[0]
        else:
            # 코드 블록이 없으면 전체 응답 반환
            return response_text
```

#### Option B: 웹 자동화 (Playwright/Selenium)

**장점**:
- API Key 불필요
- Gemini 웹사이트 UI 직접 사용

**단점**:
- 불안정 (UI 변경 시 깨짐)
- 복잡한 에러 처리
- 파일 업로드 동작 구현 필요

**구현 예시**:
```python
# gemini_web_automation.py (NEW)

from playwright.sync_api import sync_playwright

class GeminiWebAutomation:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def generate_daily_wrap(self, html_files, instruction_path):
        """Playwright로 Gemini 웹사이트 자동화"""

        # 1. Gemini 접속
        self.page.goto('https://gemini.google.com')

        # 2. 로그인 (필요 시)
        # self._login()

        # 3. 새 대화 시작
        self.page.click('button:has-text("New chat")')

        # 4. Instruction 입력
        with open(instruction_path, 'r', encoding='utf-8') as f:
            instruction = f.read()

        self.page.fill('textarea[placeholder*="Message"]', instruction)

        # 5. HTML 파일들 업로드
        for html_file in html_files:
            self.page.set_input_files('input[type="file"]', html_file)

        # 6. 전송
        self.page.click('button[type="submit"]')

        # 7. 응답 대기
        self.page.wait_for_selector('.response-container', timeout=120000)

        # 8. 최종 HTML 추출
        response_text = self.page.inner_text('.response-container')
        final_html = self._extract_html_from_markdown(response_text)

        return final_html
```

#### 권장 사항: Option A (Gemini API)
- **이유**: 안정성, 에러 처리 명확성, 유지보수 용이성
- **필요 확인**: Gemini API Key 보유 여부

---

### Phase 4: 최종 결과 저장

```python
# final_output_handler.py (NEW)

import os
from datetime import datetime

class FinalOutputHandler:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.base_dir = os.path.abspath(os.path.join(project_dir, '..', '..'))
        self.output_dir = os.path.join(self.base_dir, 'projects', '100xFenok', '100x', 'daily-wrap')

    def save_final_output(self, final_html):
        """최종 100x Daily Wrap HTML 저장"""

        # 1. 파일명 생성 (YYYYMMDD 형식)
        today = datetime.now().strftime('%Y%m%d')
        filename = f"100x-daily-wrap-{today}.html"
        filepath = os.path.join(self.output_dir, filename)

        # 2. 디렉터리 생성 (필요 시)
        os.makedirs(self.output_dir, exist_ok=True)

        # 3. HTML 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_html)

        print(f"[Final Output] 100x Daily Wrap 저장 완료!")
        print(f"[Final Output] 경로: {filepath}")

        return filepath

    def update_version_js(self, filepath):
        """version.js 업데이트 (선택 사항)"""
        version_js_path = os.path.join(self.base_dir, 'projects', '100xFenok', 'version.js')

        # version.js 업데이트 로직 (필요 시 구현)
        pass
```

---

## 4. 에러 처리 전략

### 4.1 Phase 1 에러 처리 (TerminalX)

| 에러 상황 | 감지 방법 | 처리 방안 |
|----------|----------|----------|
| 로그인 실패 | 로그인 버튼 미확인 | multi-fallback 전략 (verify_system.py) |
| 리포트 생성 타임아웃 | Archive 300초 대기 후 미완료 | 재시도 (최대 2회) |
| HTML 추출 실패 | "No documents found" 검출 | Archive 상태 재확인 → 재추출 |
| Past Day 설정 실패 | 설정 UI 미확인 | 경고 로그 + 수동 확인 요청 |

### 4.2 Phase 2 에러 처리 (JSON 변환)

| 에러 상황 | 감지 방법 | 처리 방안 |
|----------|----------|----------|
| HTML 파싱 실패 | BeautifulSoup 예외 | 로그 기록 + 건너뛰기 |
| 테이블 추출 실패 | 테이블 헤더 없음 | raw_html 포함 + 경고 |
| 금융 데이터 정제 실패 | 숫자 변환 예외 | 원본 문자열 유지 |

### 4.3 Phase 3 에러 처리 (Gemini)

| 에러 상황 | 감지 방법 | 처리 방안 |
|----------|----------|----------|
| API 인증 실패 | 401/403 응답 | API Key 검증 요청 |
| API 요청 타임아웃 | 120초 대기 후 미응답 | 재시도 (최대 3회) |
| 응답 형식 오류 | ```html 블록 없음 | 원본 응답 저장 + 알림 |
| 토큰 제한 초과 | 413/429 응답 | 파일 분할 처리 |

### 4.4 전체 시스템 에러 처리

```python
# main_automation_pipeline.py (NEW)

class AutomationPipeline:
    def run_full_automation(self):
        """전체 자동화 파이프라인 실행"""
        try:
            # Phase 1: TerminalX
            html_files = self.phase1_terminalx()
            if not html_files:
                raise Exception("Phase 1 실패: HTML 파일 생성 실패")

            # Phase 2: JSON 변환
            json_results = self.phase2_json_conversion(html_files)
            if json_results["failed"]:
                print(f"경고: {len(json_results['failed'])}개 파일 변환 실패")

            # Phase 3: Gemini 통합
            final_html = self.phase3_gemini_integration(html_files)
            if not final_html:
                raise Exception("Phase 3 실패: Gemini 통합 실패")

            # Phase 4: 결과 저장
            output_path = self.phase4_save_output(final_html)

            print(f"전체 자동화 완료! 결과: {output_path}")
            return output_path

        except Exception as e:
            print(f"전체 자동화 실패: {e}")
            self._save_error_log(e)
            return None

    def _save_error_log(self, error):
        """에러 로그 저장"""
        log_dir = os.path.join(self.project_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f"error_{timestamp}.log")

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Error: {error}\n")
            f.write(f"Timestamp: {timestamp}\n")
```

---

## 5. 성공 기준

### 5.1 Phase 1 성공 기준
- ✅ 18개 리포트 모두 "Generated" 상태 확인
- ✅ 모든 HTML 파일에 `supersearchx-body` 클래스 존재
- ✅ "No documents found" 에러 0건

### 5.2 Phase 2 성공 기준
- ✅ 18개 JSON 파일 모두 생성 완료
- ✅ 모든 JSON 파일에 `sections` 필드 존재
- ✅ 섹션 7.1, 8.1 테이블 데이터 완전성 검증 통과

### 5.3 Phase 3 성공 기준
- ✅ Gemini API/웹 자동화 정상 실행
- ✅ 최종 HTML에 모든 섹션 데이터 삽입 완료
- ✅ 한국어 번역 품질 검증 (샘플 검토)

### 5.4 Phase 4 성공 기준
- ✅ 최종 HTML 파일 저장 성공
- ✅ 파일 크기 > 100KB (콘텐츠 충분성)
- ✅ HTML 문법 검증 통과

---

## 6. 다음 단계

이 설계 문서를 기반으로 다음 문서 작성:
1. **IMPLEMENTATION_PLAN.md**: 구체적인 구현 계획 및 우선순위
2. **QUESTIONS_FOR_USER.md**: 사용자 확인 필요 질문 리스트

**사용자 승인 필요**: 이 설계안이 요구사항을 충족하는지 확인 후 다음 단계 진행
