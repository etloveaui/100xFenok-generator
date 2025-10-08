# 100x Daily Wrap 품질 선택 가이드

**목적**: 사용자가 Part1×3, Part2×3, 일반×6 파일 중에서 섹션별 최우수 답변을 선택하는 가이드
**대상**: 100xFenok-generator 프로젝트 사용자
**소요 시간**: ~30분

---

## I. 개요

TerminalX는 동일한 프롬프트에 대해 **여러 버전의 리포트**를 생성합니다. 각 버전의 품질이 다르므로, **사용자가 직접 품질을 평가하고 섹션별로 최우수 답변을 선택**해야 합니다.

**생성되는 파일**:
- **Part1 리포트**: 3개 (Part1_01.json, Part1_02.json, Part1_03.json)
- **Part2 리포트**: 3개 (Part2_01.json, Part2_02.json, Part2_03.json)
- **일반 리포트**: 6개 (선택 사항, HTML 형식)

**Claude의 역할**:
사용자가 선택한 파일들을 기반으로 자동으로 통합, 검토, 인덱싱을 수행합니다.

---

## II. 품질 선택 기준

### 기준 1: 정보의 깊이 (Depth)
- 데이터가 구체적이고 상세한가?
- 표면적 설명에 그치지 않고 근거와 맥락을 제공하는가?

**예시**:
- ❌ 낮은 품질: "엔비디아 상승"
- ✅ 높은 품질: "엔비디아는 AI 반도체 수요 급증으로 +5.2% 상승, 신고가 경신"

---

### 기준 2: 논리의 명확성 (Clarity)
- 인과관계가 명확한가?
- 독자가 쉽게 이해할 수 있는 구조인가?

**예시**:
- ❌ 낮은 품질: "연준 정책 불확실성으로 시장 변동성"
- ✅ 높은 품질: "연준의 금리 인하 지연 가능성 → 투자자 심리 위축 → 변동성 확대"

---

### 기준 3: 통찰력 (Insight)
- 단순 사실 나열을 넘어 **의미 있는 해석**을 제공하는가?
- 시장 흐름의 **숨은 패턴**을 발견했는가?

**예시**:
- ❌ 낮은 품질: "테크 섹터 강세"
- ✅ 높은 품질: "테크 섹터 강세는 AI 투자 재개 신호이며, 반도체 공급망 정상화가 주요 동인"

---

### 기준 4: 데이터 정확성 (Accuracy)
- 수치, 티커, 날짜가 정확한가?
- 명백한 오류나 모순이 없는가?

**예시**:
- ❌ 낮은 품질: "2년물과 10년물 금리가 모두 3.5%"
- ✅ 높은 품질: "2년물 3.917%, 10년물 4.388%"

---

## III. 품질 선택 프로세스

### STEP 0: 파일 저장 (표준 디렉토리)

**중요**: 모든 파일을 다음 표준 디렉토리에 저장하세요:

```
Feno_Docs/daily_reports/latest/
├── part1_01.json
├── part1_02.json
├── part1_03.json
├── part2_01.json
├── part2_02.json
├── part2_03.json
└── general/
    ├── 3.1_3.2_Gain_Lose.html
    ├── 3.3_Fixed_Income.html
    ├── 5.1_Major_IB_Updates.html
    ├── 6.3_Dark_Pool.html
    ├── 7.1_11_GICS_Sector.html
    └── 8.1_12_Key_Tickers.html
```

- **Part1/Part2 JSON**: `latest/` 디렉토리에 직접 저장
- **일반 리포트 HTML**: `latest/general/` 하위 디렉토리에 저장

---

### STEP 1: 파일 읽기

**Part1 리포트 3개 읽기** (`latest/` 디렉토리):
1. `part1_01.json`을 열어 Section 1-6 내용 확인
2. `part1_02.json`을 열어 Section 1-6 내용 확인
3. `part1_03.json`을 열어 Section 1-6 내용 확인

**Part2 리포트 3개 읽기** (`latest/` 디렉토리):
1. `part2_01.json`을 열어 Section 7-11 내용 확인
2. `part2_02.json`을 열어 Section 7-11 내용 확인
3. `part2_03.json`을 열어 Section 7-11 내용 확인

**일반 리포트 6개 읽기** (`latest/general/` 디렉토리, 선택 사항):
- `3.1_3.2_Gain_Lose.html`: Section 3.1-3.2 보충
- `3.3_Fixed_Income.html`: Section 3.3 보충
- `5.1_Major_IB_Updates.html`: Section 5.1 보충
- `6.3_Dark_Pool.html`: Section 6.3 보충
- `7.1_11_GICS_Sector.html`: Section 7.1 보충
- `8.1_12_Key_Tickers.html`: Section 8.1 보충

---

### STEP 2: 섹션별 비교 및 선택

**각 섹션마다 3개 버전 비교**:

**Section 1 예시**:
- Part1_01: 요약이 간결하나 통찰력 부족
- Part1_02: 데이터 풍부하나 논리 흐름 약함
- Part1_03: ✅ **데이터 + 논리 + 통찰력 모두 우수** → **선택**

**섹션별로 반복**:
- Section 1: Part1_02 선택
- Section 2.1-2.3: Part1_01 선택
- Section 3.1-3.2: general_3.1_3.2_Gain_Lose.html 선택 (보충 자료 우수)
- Section 3.3: Part1_03 + general_3.3_Fixed_Income.html **조합** (데이터 오류 보정 필요)
- ...

---

### STEP 3: 출처 지정 문서 작성

선택이 완료되면 다음 형식으로 **출처 지정 문서**를 작성합니다.

**중요**: 파일명만 입력하세요. 전체 경로는 Claude가 자동으로 구성합니다.

```markdown
# 출처 지정

## Part1

- 섹션 1: part1_02.json
- 섹션 2.1-2.3: part1_01.json
- 섹션 3.1-3.2: 3.1_3.2_Gain_Lose.html
- 섹션 3.3: part1_03.json + 3.3_Fixed_Income.html (파일 조합)
- 섹션 4.1-4.2: part1_02.json
- 섹션 5.1: general_5.1_Major_IB_Updates.html
- 섹션 5.2-5.3: part1_01.json
- 섹션 6.1-6.3: part1_02.json

## Part2

- 섹션 7.1: 7.1_11_GICS_Sector.html
- 섹션 7.2-7.3: part2_01.json
- 섹션 8.1: 8.1_12_Key_Tickers.html
- 섹션 8.2-8.4: part2_02.json
- 섹션 9.1-9.3: part2_03.json
- 섹션 10.1-10.3: part2_01.json
- 섹션 11.1-11.2: part2_02.json
```

---

## IV. 특수 상황 처리

### 상황 1: 파일 조합 (오류 보정)

**발생 조건**:
- JSON 파일에 명백한 오류가 있고, HTML 파일에 정확한 데이터가 있는 경우

**예시**:
- **Section 3.3**: Part1_03.json의 "2년물과 10년물 금리가 모두 3.5%"는 오류
- 3.3_Fixed_Income.html에 정확한 데이터: "2년물 3.917%, 10년물 4.388%"

**출처 지정**:
```markdown
- 섹션 3.3: part1_03.json + 3.3_Fixed_Income.html (파일 조합)
```

**Claude의 처리**:
- Part1_03.json의 오류 데이터를 HTML 데이터로 **수정**
- HTML의 나머지 서술 내용을 **보강**
- 기존 JSON 구조는 **절대 삭제 금지**

---

### 상황 2: 단일 파일 선택

**발생 조건**:
- 특정 파일이 모든 측면에서 우수한 경우

**출처 지정**:
```markdown
- 섹션 1: part1_02.json
```

**Claude의 처리**:
- 해당 파일의 내용을 그대로 사용

---

### 상황 3: HTML 전체 교체

**발생 조건**:
- HTML 파일이 특정 섹션 전체를 대체할 만큼 우수한 경우

**예시**:
- Section 5.1: 5.1_Major_IB_Updates.html이 JSON보다 월등히 우수

**출처 지정**:
```markdown
- 섹션 5.1: 5.1_Major_IB_Updates.html
```

**Claude의 처리**:
- HTML 내용을 JSON 구조로 변환 후 해당 섹션 **전체 대체**

---

## V. 실전 예시

### 예시 1: Part1 Section 3.3 품질 선택

**Part1_01.json**:
```json
{
  "subtitle": "3.3 Multi-Asset Performance",
  "content": [
    {
      "type": "table",
      "data": [
        { "Asset": "2Y Treasury", "Yield": "3.5%" },
        { "Asset": "10Y Treasury", "Yield": "3.5%" }
      ]
    }
  ]
}
```
→ ❌ **오류 발견**: 2년물과 10년물 금리가 동일 (비현실적)

**Part1_02.json**:
```json
{
  "subtitle": "3.3 Multi-Asset Performance",
  "content": [
    {
      "type": "table",
      "data": [
        { "Asset": "2Y Treasury", "Yield": "N/A" },
        { "Asset": "10Y Treasury", "Yield": "N/A" }
      ]
    }
  ]
}
```
→ ❌ **데이터 부족**: 수치 없음

**Part1_03.json**:
```json
{
  "subtitle": "3.3 Multi-Asset Performance",
  "content": [
    {
      "type": "table",
      "data": [
        { "Asset": "2Y Treasury", "Yield": "3.5%" },
        { "Asset": "10Y Treasury", "Yield": "3.5%" },
        { "Asset": "주요 지수", "Day (%)": "..." },
        { "Asset": "원자재", "Day (%)": "..." }
      ]
    }
  ]
}
```
→ ⚠️ **구조 우수하나 오류 포함**: 금리 데이터 오류

**general_3.3_Fixed_Income.html**:
```html
<h3>미국 국채 시장</h3>
<table>
  <tr><td>2Y Treasury</td><td>3.917%</td></tr>
  <tr><td>10Y Treasury</td><td>4.388%</td></tr>
</table>
<p>
시장은 9월 금리 인하 기대감을 반영하고 있으나, 공급 부담이 상승 압력으로 작용합니다.
</p>
```
→ ✅ **정확한 데이터 + 상세 설명**

**결정**:
- **Part1_03.json** (구조 우수)
- **general_3.3_Fixed_Income.html** (정확한 데이터 + 보강 내용)
- **조합 사용** (오류 보정 + 내용 보강)

**출처 지정**:
```markdown
- 섹션 3.3: part1_03.json + general_3.3_Fixed_Income.html (파일 조합)
```

---

### 예시 2: Part2 Section 7.1 품질 선택

**Part2_01.json**:
```json
{
  "subtitle": "7.1 11 GICS Sector Table",
  "content": [
    {
      "type": "table",
      "data": [
        { "Sector": "Technology", "ETF": "XLK", "Day (%)": "+1.2%", "YTD (%)": "+15.3%" },
        ...
      ]
    }
  ]
}
```
→ ✅ **데이터 정확, 구조 우수**

**Part2_02.json**:
```json
{
  "subtitle": "7.1 11 GICS Sector Table",
  "content": [
    {
      "type": "table",
      "data": [
        { "Sector": "Technology", "ETF": "XLK", "Day (%)": "+1.1%", "YTD (%)": "N/A" }
        ...
      ]
    }
  ]
}
```
→ ❌ **YTD 데이터 부족**

**Part2_03.json**:
```json
{
  "subtitle": "7.1 11 GICS Sector Table",
  "content": [
    {
      "type": "table",
      "data": [
        { "Sector": "Technology", "ETF": "XLK", "Day (%)": "+1.2%", "YTD (%)": "+15.5%" },
        ...
      ]
    }
  ]
}
```
→ ✅ **데이터 정확, YTD 포함**

**general_7.1_11_GICS_Sector.html**:
```html
<h3>11 GICS 섹터 성과</h3>
<table>
  <tr><th>Sector</th><th>ETF</th><th>Day (%)</th><th>YTD (%)</th></tr>
  <tr><td>Technology</td><td>XLK</td><td>+1.2%</td><td>+15.3%</td></tr>
  ...
</table>
<p>
테크 섹터는 AI 투자 재개 신호로 강세를 보이고 있으며, 반도체 공급망 정상화가 주요 동인입니다.
</p>
```
→ ✅ **데이터 정확 + 통찰력 높은 설명**

**결정**:
- **general_7.1_11_GICS_Sector.html** (데이터 정확 + 통찰력)

**출처 지정**:
```markdown
- 섹션 7.1: general_7.1_11_GICS_Sector.html
```

---

## VI. 체크리스트

품질 선택 완료 전 확인:

**전체 파일 확인**:
- [ ] Part1 JSON 3개 모두 읽음
- [ ] Part2 JSON 3개 모두 읽음
- [ ] 일반 HTML 6개 모두 읽음 (선택 사항)

**섹션별 선택 완료**:
- [ ] Part1 Section 1 선택 완료
- [ ] Part1 Section 2.1-2.3 선택 완료
- [ ] Part1 Section 3.1-3.2 선택 완료
- [ ] Part1 Section 3.3 선택 완료 (오류 확인)
- [ ] Part1 Section 4.1-4.2 선택 완료
- [ ] Part1 Section 5.1-5.3 선택 완료
- [ ] Part1 Section 6.1-6.3 선택 완료
- [ ] Part2 Section 7.1-7.3 선택 완료
- [ ] Part2 Section 8.1-8.4 선택 완료
- [ ] Part2 Section 9.1-9.3 선택 완료
- [ ] Part2 Section 10.1-10.3 선택 완료
- [ ] Part2 Section 11.1-11.2 선택 완료

**출처 지정 문서 작성**:
- [ ] Markdown 형식 사용
- [ ] Part1 모든 섹션 명시
- [ ] Part2 모든 섹션 명시
- [ ] "파일 조합" 표기 (해당 시)

---

## VII. Claude에게 전달

출처 지정 문서 작성 완료 후:

```
/integrate-json
```

명령을 실행하고, 출처 지정 문서를 첨부합니다.

Claude는 자동으로:
1. 지정된 파일들을 로드
2. 섹션별로 최우수 답변 통합
3. 오류 데이터 보정 (파일 조합 시)
4. 인용 제거 + 표준화
5. 통합 JSON 생성

---

**마지막 업데이트**: 2025-10-08
**버전**: Claude Integration v1.0
