# 100xFenok-Generator 전체 자동화 구현 계획

**문서 생성일**: 2025-10-07
**목표**: TerminalX → HTML → JSON → Gemini → 최종 100x Daily Wrap까지 완전 자동화

**참고**: 이 문서는 기존 `IMPLEMENTATION_PLAN.md`를 확장하여 18개 리포트 전체 자동화를 다룹니다.

---

## 1. 구현 전략 비교

### Option A: Quick Fix (권장 - 1단계)

**목표**: 최소 변경으로 기존 시스템 작동 복구
**시간**: 5시간
**리스크**: 낮음 (기존 작동 코드 활용)

**변경 범위**:
- `main_generator.py`: Archive 대기 로직 추가 (100줄)
- `json_converter.py`: 검증 로직 추가 (50줄)
- 신규 파일: `gemini_integrator.py` (200줄)
- 신규 파일: `main_automation_pipeline.py` (150줄)

**산출물**:
- 6개 리포트 자동 생성 복구 (Phase 1)
- JSON 변환 자동화 (Phase 2)
- Gemini 수동 단계 유지 (Phase 3는 반자동)

---

### Option B: 완전 재설계 (2단계 - 선택 사항)

**목표**: 35개 파일을 12개로 통합, 완전 자동화
**시간**: 5일 (40시간)
**리스크**: 중간 (전체 구조 변경)

**변경 범위**:
- 전체 아키텍처 재설계
- 35개 파일 → 12개 파일 통합
- 완전 자동화 (Gemini API 통합 포함)

**산출물**:
- 18개 리포트 완전 자동 생성 (Part1 × 6 + Part2 × 6 + 일반 × 6)
- Gemini API 완전 통합 (사용자 개입 0)

---

## 2. 권장 접근: 단계별 구현

### Stage 1: Quick Fix (5시간) - 즉시 실행 가능
**목표**: 기존 6개 리포트 생성 복구

### Stage 2: 18개 확장 (10시간) - Quick Fix 성공 후
**목표**: Part1/Part2/일반 리포트 모두 자동화

### Stage 3: Gemini 통합 (15시간) - 사용자 결정 필요
**목표**: Gemini API 완전 자동화

### Stage 4: 전체 재설계 (40시간) - 선택 사항
**목표**: 코드 중복 제거, 유지보수성 향상

---

## 3. Task 리스트 (우선순위별)

### 🔴 CRITICAL (Stage 1: Quick Fix)

#### Task 1.1: HTML 추출 로직 개선 (기존 IMPLEMENTATION_PLAN 반영)
**파일**: `main_generator.py` (720-761줄)
**예상 시간**: 1시간
**의존성**: 없음

**문제 분석**:
- **기존 가정 (틀림)**: `supersearchx-body` 클래스만 사용
- **실제 발견**: `markdown-body` 클래스도 사용 (Feno_Docs 샘플 분석)
- **핵심 문제**: HTML 렌더링 완료 대기 부족 (10초 고정 → 부족)

**해결 방안**:
```python
# main_generator.py: extract_and_validate_html() 수정

def extract_and_validate_html(self, report, output_html_path):
    """HTML 추출 및 검증 - 폴링 방식으로 개선"""

    # 1. 리포트 페이지 이동
    self.driver.get(report.url)

    # 2. 렌더링 완료까지 폴링 (최대 2분)
    max_wait = 120
    poll_interval = 5
    elapsed = 0

    while elapsed < max_wait:
        try:
            # markdown-body 또는 supersearchx-body 찾기 (두 가지 모두 지원!)
            elements = self.driver.find_elements(
                By.XPATH,
                "//div[contains(@class, 'markdown-body') or contains(@class, 'supersearchx-body')]"
            )

            if elements:
                # HTML 추출
                html_content = self.driver.page_source

                # "No documents found" 체크
                if "No documents found" not in html_content:
                    # 크기 검증 (50KB 이상 = 콘텐츠 충분)
                    if len(html_content) > 50000:
                        # 저장
                        with open(output_html_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        print(f"  ✅ HTML 저장 완료: {output_html_path}")
                        return True
                    else:
                        print(f"  ⏳ 콘텐츠 크기 부족 ({len(html_content)} bytes), 대기 중...")

            time.sleep(poll_interval)
            elapsed += poll_interval

        except Exception as e:
            print(f"  ⏳ 렌더링 대기 중... ({elapsed}초 경과)")
            time.sleep(poll_interval)
            elapsed += poll_interval

    print(f"  ❌ HTML 추출 타임아웃 ({max_wait}초)")
    return False
```

**검증 방법**:
1. 단일 리포트 테스트 → HTML 추출 성공
2. `markdown-body` 또는 `supersearchx-body` 둘 다 작동 확인
3. 크기 검증 통과 (> 50KB)
4. "No documents found" 체크 통과

---

#### Task 1.2: Archive 완료 대기 통합 확인
**파일**: `report_manager.py`, `main_generator.py`
**예상 시간**: 30분
**의존성**: 없음

**현재 상태 확인**:
- ✅ `report_manager.py`: Archive 모니터링 이미 구현됨 (53-130줄)
- ✅ `main_generator.py`: `run_full_automation()`에서 호출됨

**작업 내용**:
1. Archive 모니터링 로직 정상 작동 확인
2. 폴링 주기 최적화 (현재: 30초 → 제안: 10초)
3. 타임아웃 설정 확인 (현재: 1800초 = 30분)

**개선 제안**:
```python
# report_manager.py: monitor_and_retry() 수정

def monitor_and_retry(self, timeout: int = 1800, initial_interval: int = 10):  # 30→10초
    """모든 리포트가 완료될 때까지 Archive 모니터링"""
    overall_start_time = time.time()
    current_interval = initial_interval

    while time.time() - overall_start_time < timeout:
        pending_reports = self.get_pending_reports()
        if not pending_reports:
            print("[Batch Manager] ✅ 모든 리포트가 성공적으로 생성되었습니다.")
            return True

        print(f"[Batch Manager] 🔄 Archive 페이지 새로고침. 남은 리포트: {len(pending_reports)}")
        # ... (기존 로직 유지)
```

**검증 방법**:
1. 2개 리포트 동시 생성 → Archive 모니터링 로그 확인
2. 모든 리포트 "GENERATED" 상태 확인
3. 타임아웃 없이 정상 완료

---

#### Task 1.3: 6개 리포트 설정 확인
**파일**: `main_generator.py`
**예상 시간**: 1시간
**의존성**: Task 1.1, 1.2 완료

**현재 상태**:
- ✅ Part1, Part2 리포트 이미 작동 (2025-08-20 성공 이력)
- ❓ 나머지 4개 리포트 설정 확인 필요

**작업 내용**:
1. 기존 성공 로그 (2025-08-20) 분석하여 6개 리포트 확인
2. `run_full_automation()` 로직에서 리포트 정의 확인
3. 프롬프트 파일 경로 검증

**확인 사항**:
```python
# main_generator.py에서 6개 리포트 정의 확인
REPORT_DEFINITIONS = [
    # Part1 3개?
    # Part2 3개?
    # 또는 다른 조합?
]
```

**검증 방법**:
1. 6개 리포트 정의 명확히 파악
2. 각 리포트의 프롬프트 파일 존재 확인
3. 테스트 실행 → 6개 모두 생성 성공

---

#### Task 1.4: 전체 워크플로우 통합 테스트
**파일**: `main_generator.py`
**예상 시간**: 2시간
**의존성**: Task 1.1, 1.2, 1.3 완료

**테스트 시나리오**:
1. **로그인 성공** → 타임아웃 없이 Dashboard 진입
2. **6개 리포트 생성 요청** → 모든 요청 성공
3. **Archive 모니터링** → 6개 모두 "GENERATED" 상태 확인
4. **HTML 추출** → 6개 HTML 파일 모두 저장 (`generated_html/`)
5. **검증** → 각 파일 크기 > 50KB, 클래스 확인

**성공 기준**:
- ✅ 6개 리포트 생성 성공률 > 95%
- ✅ Archive 폴링 정상 작동 (타임아웃 0건)
- ✅ HTML 추출 검증 통과 (markdown-body 또는 supersearchx-body 100%)

---

### 🟡 HIGH (Stage 2: 18개 확장)

#### Task 2.1: Part1/Part2 프롬프트 조사 및 구현
**파일**: `main_generator.py`
**예상 시간**: 3시간
**의존성**: Task 1.4 완료

**조사 대상**:
1. `Feno_Docs/part1/` 폴더 내용 확인
   - 현재: `part1_01.html/json` ~ `part1_03.html/json` (예시 파일)
   - 필요: 프롬프트 `.md` 파일 또는 정의 확인

2. `Feno_Docs/part2/` 폴더 내용 확인
   - 현재: `part2_01.html/json` ~ `part2_03.html/json` (예시 파일)
   - 필요: 프롬프트 `.md` 파일 또는 정의 확인

3. 2025-08-20 성공 로그 분석
   - 실제로 어떤 리포트가 생성되었는지 확인

**구현 계획**:
```python
# main_generator.py에 추가

PART1_REPORTS = [
    # 조사 후 확정 (예시)
    {"title": "Executive Summary", "prompt_file": "part1/01_executive_summary.md"},
    {"title": "Market Pulse", "prompt_file": "part1/02_market_pulse.md"},
    {"title": "Multi-Asset Dashboard", "prompt_file": "part1/03_multi_asset.md"},
    # ... (총 6개)
]

PART2_REPORTS = [
    # 조사 후 확정
    {"title": "Sector Analysis", "prompt_file": "part2/01_sector.md"},
    {"title": "Key Tickers", "prompt_file": "part2/02_tickers.md"},
    # ... (총 6개)
]

def generate_part1_reports(self):
    """Part1 Custom 리포트 6개 생성"""
    for report_def in PART1_REPORTS:
        prompt_path = os.path.join(
            self.project_dir, 'Feno_Docs', report_def['prompt_file']
        )

        # 프롬프트 로드
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt = f.read()

        # 리포트 생성
        report = Report(part_type="PART1", title=report_def['title'])
        success = self._generate_single_report(report, prompt)

        if success:
            print(f"[Part1] ✅ {report.title} 생성 완료")
        else:
            print(f"[Part1] ❌ {report.title} 생성 실패")
```

**검증 방법**:
1. Part1 6개 + Part2 6개 = 12개 리포트 생성 성공
2. 각 리포트 프롬프트가 올바르게 적용되었는지 HTML 내용 확인

---

#### Task 2.2: 일반 리포트 6개 구현
**파일**: `main_generator.py`
**예상 시간**: 3시간
**의존성**: Task 2.1 완료

**일반 리포트 정의**:
```python
GENERAL_REPORTS = [
    "3.1 3.2 Gain Lose.md",
    "3.3 Fixed Income.md",
    "5.1 Major IB Updates.md",
    "6.3 Dark Pool & Political Donation Flows.md",
    "7.1 11 GICS Sector Table.md",
    "8.1 12 Key Tickers Table.md"
]
```

**구현 내용**:
```python
def generate_general_reports(self):
    """일반 리포트 6개 생성 (Past Day 설정 포함)"""
    for report_md in GENERAL_REPORTS:
        # 1. Past Day 설정 적용 (free_explorer.py:317-335 로직)
        self._set_past_day_filter()

        # 2. 프롬프트 로드
        prompt_path = os.path.join(
            self.project_dir, 'Feno_Docs', '일반리포트', report_md
        )

        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt = f.read()

        # 3. 리포트 생성
        report = Report(part_type="GENERAL", title=report_md.replace('.md', ''))
        success = self._generate_single_report(report, prompt)

        if success:
            print(f"[General] ✅ {report.title} 생성 완료")

def _set_past_day_filter(self):
    """
    Past Day 설정 적용 (free_explorer.py:317-335 로직 사용)
    """
    try:
        # 1. Time Range 클릭
        time_range_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Time Range')]"))
        )
        time_range_button.click()
        time.sleep(1)

        # 2. Past Day 선택
        past_day_option = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'Past Day')]"))
        )
        past_day_option.click()
        time.sleep(2)

        print("[Past Day] ✅ Past Day 설정 완료")
        return True

    except Exception as e:
        print(f"[Past Day] ❌ Past Day 설정 실패: {e}")
        return False
```

**검증 방법**:
1. 일반 리포트 6개 생성 성공
2. Past Day 설정 정상 적용 확인 (Time Range UI 확인)
3. 섹션 7.1, 8.1 테이블 데이터 존재 확인

---

#### Task 2.3: 18개 통합 테스트
**파일**: `main_generator.py`
**예상 시간**: 2시간
**의존성**: Task 2.1, 2.2 완료

**테스트 시나리오**:
1. Part1 × 6개 생성 요청
2. Part2 × 6개 생성 요청
3. 일반 × 6개 생성 요청 (Past Day 적용)
4. Archive 모니터링 → 18개 모두 "GENERATED" 확인
5. HTML 추출 → 18개 파일 모두 저장

**성공 기준**:
- ✅ 18개 리포트 생성 성공률 > 90%
- ✅ Archive 폴링 타임아웃 0건
- ✅ HTML 파일 크기 검증 통과 (각 > 50KB)
- ✅ 전체 실행 시간 < 60분 (리포트당 평균 3분)

---

#### Task 2.4: JSON 변환 자동화
**파일**: `json_converter.py`, `main_generator.py`
**예상 시간**: 2시간
**의존성**: Task 2.3 완료

**작업 내용**:
```python
# main_generator.py에 추가

def convert_all_html_to_json(self):
    """18개 HTML → JSON 자동 변환"""
    print("\n=== [Phase 2] JSON 변환 시작 ===")

    converter = TerminalXJSONConverter()

    html_dir = self.generated_html_dir
    json_dir = self.generated_json_dir

    # 배치 변환 실행
    results = converter.batch_convert_directory(html_dir, json_dir)

    print(f"[JSON Converter] ✅ 변환 완료: {len(results)}개 파일")
    print(f"[JSON Converter] 결과: {json_dir}")

    return results

# run_full_automation()에 통합
def run_full_automation(self):
    # ... (기존 로직)

    # Phase 1: HTML 생성
    html_files = self.generate_all_18_reports()

    # Phase 2: JSON 변환 (NEW)
    json_files = self.convert_all_html_to_json()

    print(f"\n✅ 전체 자동화 완료!")
    print(f"  - HTML: {len(html_files)}개")
    print(f"  - JSON: {len(json_files)}개")
```

**검증 방법**:
1. 18개 HTML → 18개 JSON 변환 성공
2. 각 JSON 파일 구조 검증 (sections 필드 존재)
3. 섹션 7.1, 8.1 테이블 데이터 완전성 확인
4. 금융 데이터 파싱 정확도 샘플 검토 (통화/퍼센트)

---

### 🟢 MEDIUM (Stage 3: Gemini 통합)

#### Task 3.1: Gemini API Key 확인 및 설정
**파일**: 없음 (조사 작업)
**예상 시간**: 30분
**의존성**: 없음 (병렬 진행 가능)

**확인 사항**:
1. ✅ Gemini API Key 보유 여부
2. ✅ Gemini API 사용 가능 모델 확인
   - `gemini-2.0-flash-exp` (빠른 속도, 낮은 비용)
   - `gemini-2.5-pro` (높은 품질, 복잡한 작업)
3. ✅ API 비용 구조 확인
4. ✅ Multimodal 입력 지원 확인 (HTML 파일 입력 가능 여부)

**API Key 설정**:
```bash
# .env 파일 또는 환경 변수 설정
GEMINI_API_KEY=your_api_key_here
```

**결과에 따른 결정**:
- **API Key 있음** → Task 3.2 진행 (Gemini API 연동)
- **API Key 없음** → Task 3.3 진행 (웹 자동화) 또는 수동 단계 유지

---

#### Task 3.2: Gemini API 연동 구현 (Option A - 권장)
**파일**: `gemini_integrator.py` (신규)
**예상 시간**: 5시간
**의존성**: Task 3.1 완료 (API Key 확보)

**구현 내용**:
```python
# gemini_integrator.py (NEW)

import google.generativeai as genai
import os
import re
from pathlib import Path

class GeminiAutoIntegrator:
    """Gemini API를 사용한 자동 리포트 생성"""

    def __init__(self, api_key=None):
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')

        if not api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

        genai.configure(api_key=api_key)

        # 모델 선택 (빠른 속도 vs 높은 품질)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        # self.model = genai.GenerativeModel('gemini-2.5-pro')  # 더 높은 품질

    def generate_daily_wrap(self, html_files, instruction_path, template_path):
        """
        18개 HTML + Instruction + Template → 최종 100x Daily Wrap
        """
        print("\n=== [Phase 3] Gemini 통합 시작 ===")

        # 1. Instruction 로드
        with open(instruction_path, 'r', encoding='utf-8') as f:
            instruction = f.read()

        print(f"[Gemini] ✅ Instruction 로드: {instruction_path}")

        # 2. Template 로드
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        print(f"[Gemini] ✅ Template 로드: {template_path}")

        # 3. HTML 파일들 로드
        html_contents = []
        for html_file in html_files:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_contents.append({
                    "filename": os.path.basename(html_file),
                    "content": f.read()
                })

        print(f"[Gemini] ✅ HTML 파일 {len(html_contents)}개 로드")

        # 4. 프롬프트 구성
        prompt = self._build_prompt(instruction, html_contents, template)

        print(f"[Gemini] 📝 프롬프트 크기: {len(prompt)} 문자")

        # 5. Gemini API 호출
        print(f"[Gemini] 🤖 API 호출 중... (최대 2-3분 소요)")

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,  # 낮은 창의성 (일관성 중시)
                    "max_output_tokens": 8192  # 긴 HTML 출력 지원
                }
            )

            print(f"[Gemini] ✅ API 응답 수신")

        except Exception as e:
            print(f"[Gemini] ❌ API 호출 실패: {e}")
            return None

        # 6. HTML 추출
        final_html = self._extract_html_from_response(response.text)

        if final_html:
            print(f"[Gemini] ✅ 최종 HTML 생성 완료 ({len(final_html)} 문자)")
            return final_html
        else:
            print(f"[Gemini] ❌ HTML 추출 실패")
            return None

    def _build_prompt(self, instruction, html_contents, template):
        """Gemini API용 프롬프트 구성"""
        prompt_parts = [
            "# 입력 파일들\n",
            "## 1. Instruction (지침)\n",
            instruction,
            "\n## 2. 소스 HTML 파일들 (18개)\n"
        ]

        for i, html_data in enumerate(html_contents, 1):
            prompt_parts.append(f"\n### {i}. {html_data['filename']}\n")
            prompt_parts.append("```html\n")
            prompt_parts.append(html_data['content'])
            prompt_parts.append("\n```\n")

        prompt_parts.append("\n## 3. 마스터 템플릿 HTML\n")
        prompt_parts.append("```html\n")
        prompt_parts.append(template)
        prompt_parts.append("\n```\n")

        prompt_parts.append("\n# 작업 요청\n")
        prompt_parts.append("위 Instruction 지침에 따라 18개 소스 HTML과 마스터 템플릿을 처리하여 ")
        prompt_parts.append("최종 100x Daily Wrap HTML을 생성하세요.\n")

        return "".join(prompt_parts)

    def _extract_html_from_response(self, response_text):
        """
        Gemini 응답에서 ```html ... ``` 코드 블록 추출
        """
        # 정규표현식: ```html ... ``` 패턴
        pattern = r'```html\s*(.*?)\s*```'
        matches = re.findall(pattern, response_text, re.DOTALL)

        if matches:
            # 가장 긴 매치 선택 (최종 HTML일 가능성 높음)
            return max(matches, key=len)
        else:
            # 코드 블록이 없으면 전체 응답 반환 (Fallback)
            print("[Gemini] ⚠️ 코드 블록 없음, 전체 응답 반환")
            return response_text
```

**검증 방법**:
1. 테스트 입력 (18개 HTML) → Gemini API 호출 성공
2. 최종 HTML 출력 확인 (크기 > 100KB)
3. HTML 구조 검증 (섹션 ID 매핑 확인)
4. 한국어 번역 품질 샘플 검토
5. 템플릿 삽입 정확도 확인

---

#### Task 3.3: 전체 파이프라인 통합
**파일**: `main_automation_pipeline.py` (신규)
**예상 시간**: 2시간
**의존성**: Task 2.4, Task 3.2 완료

**구현 내용**:
```python
# main_automation_pipeline.py (NEW)

import os
from datetime import datetime
from main_generator import FenokReportGenerator
from json_converter import TerminalXJSONConverter
from gemini_integrator import GeminiAutoIntegrator

class FullAutomationPipeline:
    """100xFenok-Generator 전체 자동화 파이프라인"""

    def __init__(self):
        self.terminalx = FenokReportGenerator()
        self.converter = TerminalXJSONConverter()
        self.gemini = GeminiAutoIntegrator()
        self.project_dir = self.terminalx.project_dir

    def run(self):
        """전체 자동화 실행"""
        print("\n" + "="*80)
        print("  100xFenok-Generator 전체 자동화 시작")
        print("="*80 + "\n")

        start_time = datetime.now()

        try:
            # Phase 1: TerminalX 18개 리포트 생성
            print("\n[Phase 1] TerminalX 리포트 생성 중...")
            html_files = self._phase1_terminalx()

            if not html_files or len(html_files) < 18:
                raise Exception(f"Phase 1 실패: {len(html_files)}/18개 HTML 생성")

            print(f"[Phase 1] ✅ 완료: {len(html_files)}개 HTML 생성")

            # Phase 2: JSON 변환
            print("\n[Phase 2] JSON 변환 중...")
            json_results = self._phase2_json_conversion(html_files)

            print(f"[Phase 2] ✅ 완료: {len(json_results)}개 JSON 생성")

            # Phase 3: Gemini 통합
            print("\n[Phase 3] Gemini 통합 중...")
            final_html = self._phase3_gemini_integration(html_files)

            if not final_html:
                raise Exception("Phase 3 실패: Gemini 통합 실패")

            print("[Phase 3] ✅ 완료: 최종 HTML 생성")

            # Phase 4: 결과 저장
            print("\n[Phase 4] 결과 저장 중...")
            output_path = self._phase4_save_output(final_html)

            print(f"[Phase 4] ✅ 완료: {output_path}")

            # 실행 시간 계산
            elapsed = datetime.now() - start_time
            minutes = int(elapsed.total_seconds() / 60)
            seconds = int(elapsed.total_seconds() % 60)

            print("\n" + "="*80)
            print(f"  전체 자동화 성공!")
            print(f"  실행 시간: {minutes}분 {seconds}초")
            print(f"  결과 파일: {output_path}")
            print("="*80 + "\n")

            return output_path

        except Exception as e:
            print(f"\n❌ 전체 자동화 실패: {e}")
            self._save_error_log(e)
            return None

    def _phase1_terminalx(self):
        """Phase 1: TerminalX 리포트 생성"""
        # main_generator.py의 run_full_automation() 호출
        self.terminalx.run_full_automation()

        # 생성된 HTML 파일 목록 반환
        html_dir = self.terminalx.generated_html_dir
        html_files = [
            os.path.join(html_dir, f)
            for f in os.listdir(html_dir)
            if f.endswith('.html')
        ]

        return html_files

    def _phase2_json_conversion(self, html_files):
        """Phase 2: JSON 변환"""
        results = self.converter.batch_convert_directory(
            self.terminalx.generated_html_dir,
            self.terminalx.generated_json_dir
        )

        return results

    def _phase3_gemini_integration(self, html_files):
        """Phase 3: Gemini 통합"""
        instruction_path = os.path.join(
            self.project_dir, 'Feno_Docs', '기타', 'Instruction_Html.md'
        )

        template_path = self.terminalx.template_html_path

        final_html = self.gemini.generate_daily_wrap(
            html_files=html_files,
            instruction_path=instruction_path,
            template_path=template_path
        )

        return final_html

    def _phase4_save_output(self, final_html):
        """Phase 4: 결과 저장"""
        # 파일명 생성 (YYYYMMDD 형식)
        today = datetime.now().strftime('%Y%m%d')
        filename = f"100x-daily-wrap-{today}.html"

        # 출력 디렉터리
        output_dir = self.terminalx.output_daily_wrap_dir
        os.makedirs(output_dir, exist_ok=True)

        # 파일 저장
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_html)

        return filepath

    def _save_error_log(self, error):
        """에러 로그 저장"""
        log_dir = os.path.join(self.project_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f"error_{timestamp}.log")

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Error: {error}\n")
            f.write(f"Timestamp: {timestamp}\n")

# 메인 실행
if __name__ == "__main__":
    pipeline = FullAutomationPipeline()
    pipeline.run()
```

**실행 방법**:
```bash
cd C:\Users\etlov\agents-workspace\projects\100xFenok-generator
python main_automation_pipeline.py
```

**검증 방법**:
1. 전체 파이프라인 1회 완전 실행 성공
2. 최종 100x Daily Wrap HTML 저장 확인
3. 실행 시간 < 90분
4. 파일 크기 > 100KB
5. HTML 구조 검증 (섹션 모두 채워짐)

---

## 4. 의존성 그래프

```
[Stage 1: Quick Fix - 5시간]
Task 1.1 (HTML 추출 개선) ──┐
                            ├─→ Task 1.3 (6개 설정 확인)
Task 1.2 (Archive 확인)  ───┘         ↓
                                 Task 1.4 (통합 테스트)
                                      ↓
[Stage 2: 18개 확장 - 10시간]         ↓
Task 2.1 (Part1/2 조사) ──┐           ↓
                          ├─→ Task 2.3 (18개 테스트)
Task 2.2 (일반 6개)  ─────┘         ↓
                                Task 2.4 (JSON 변환)
                                     ↓
[Stage 3: Gemini 통합 - 15시간]      ↓
Task 3.1 (API Key 확인) ──┐          ↓
                          ├─→ Task 3.2 (API 연동)
                          │         ↓
                          └─→ Task 3.3 (파이프라인 통합)
```

---

## 5. 실행 일정 예시

### 1주차 (Stage 1: Quick Fix)
- **월요일**: Task 1.1 (1시간) + Task 1.2 (0.5시간)
- **화요일**: Task 1.3 (1시간) + Task 1.4 (2시간)
- **수요일**: 버그 수정 및 추가 테스트
- **목표**: 기존 6개 리포트 생성 복구

### 2주차 (Stage 2: 18개 확장)
- **월요일**: Task 2.1 (3시간) - Part1/2 조사 및 구현
- **화요일**: Task 2.2 (3시간) - 일반 리포트 6개
- **수요일**: Task 2.3 (2시간) - 18개 통합 테스트
- **목요일**: Task 2.4 (2시간) - JSON 변환 자동화
- **목표**: 18개 리포트 완전 자동화

### 3주차 (Stage 3: Gemini 통합) - 사용자 결정 필요
- **월요일**: Task 3.1 (0.5시간) - API Key 확인
- **화요일-목요일**: Task 3.2 (5시간) - Gemini API 연동
- **금요일**: Task 3.3 (2시간) - 파이프라인 통합
- **목표**: 완전 자동화 (사용자 개입 0)

---

## 6. 리스크 관리

### 높은 리스크

| 리스크 | 확률 | 영향 | 완화 방안 |
|--------|------|------|----------|
| HTML 렌더링 타임아웃 | 중 | 높음 | 폴링 방식 + 120초 대기 |
| Gemini API Key 없음 | 중 | 중간 | 수동 단계 유지 또는 웹 자동화 |
| Part1/2 프롬프트 미발견 | 낮 | 높음 | 2025-08-20 성공 로그 분석 |

### 중간 리스크

| 리스크 | 확률 | 영향 | 완화 방안 |
|--------|------|------|----------|
| JSON 변환 품질 저하 | 중 | 중간 | 검증 로직 강화 + 샘플 검토 |
| Gemini 응답 형식 변경 | 낮 | 중간 | 정규표현식 파싱 견고화 |
| Archive 모니터링 간헐적 실패 | 낮 | 낮음 | 재시도 로직 + 상세 로그 |

---

## 7. 성공 기준 (전체)

### Stage 1 성공 기준 (Quick Fix)
- ✅ 6개 리포트 생성 성공률 > 95%
- ✅ HTML 추출 검증 통과 (markdown-body 또는 supersearchx-body)
- ✅ Archive 폴링 정상 작동

### Stage 2 성공 기준 (18개 확장)
- ✅ 18개 리포트 생성 성공률 > 90%
- ✅ JSON 변환 성공률 > 95%
- ✅ 섹션 7.1, 8.1 데이터 완전성 > 90%

### Stage 3 성공 기준 (Gemini 통합)
- ✅ Gemini API 정상 작동
- ✅ 최종 HTML 품질 검증 통과 (크기 > 100KB, 섹션 완전성)
- ✅ 전체 실행 시간 < 90분

---

## 8. 다음 단계

1. **사용자 승인 대기**: `QUESTIONS_FOR_USER.md` 검토 후 결정
2. **Stage 선택**: Quick Fix (Stage 1) 우선 vs 완전 자동화 (Stage 1+2+3) 동시 진행
3. **Task 1.1 시작**: HTML 추출 로직 개선

**권장 접근**:
- **Phase 1**: Stage 1 (Quick Fix) 먼저 완료 → 작동 검증
- **Phase 2**: Stage 2 (18개 확장) 추가
- **Phase 3**: Gemini 통합 여부 사용자 결정
