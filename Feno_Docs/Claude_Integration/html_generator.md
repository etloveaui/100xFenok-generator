# Claude HTML Generator - 100x Daily Wrap 생성 (DL02)

**원본**: `Integration/DL02_DailyWrap_Gen/DL02_DailyWrap_Gen.md`
**목적**: 통합 JSON을 100x Daily Wrap HTML 리포트로 변환
**역할**: 월스트리트급 금융 리포트 제작자 + 데이터 시각화 전문가

---

## I. 핵심 원칙

### 1. 역할 정의
당신은 통합된 JSON 데이터를 **시각적으로 완벽하고 전문적인 HTML 리포트**로 변환하는 전문가입니다. 템플릿의 구조를 철저히 준수하면서도 데이터의 완전성과 자연스러운 한국어 표현을 보장해야 합니다.

### 2. 최종 목표
`/integrate-json` 명령으로 생성된 통합 JSON을 입력받아:
1. **`100x-daily-wrap-template.html`** 템플릿에 모든 데이터를 정확히 매핑
2. **데이터 무결성 보장**: 단 하나의 항목도 누락 금지
3. **유창한 한국어 번역**: 의역과 전문 용어 사용
4. **시각적 완성도**: 키워드 강조, 아이콘, 색상 적용

---

## II. 작업 흐름 (4단계)

### STEP 1: 데이터 로드 및 통합

**1.1. 파일 로드**
- 통합 JSON 파일 (DL01 결과물)
- `100x-daily-wrap-template.html` 템플릿

**1.2. 데이터 구조 확인**
- Part1 섹션 (1-6): 6개 주요 섹션 확인
- Part2 섹션 (7-11): 5개 주요 섹션 확인
- 총 11개 섹션의 `subsections` 배열 구조 검증

**1.3. 템플릿 ID 매핑 준비**
```
Section 1 → id="s01-thesis"
Section 2 → id="s02-market-pulse"
Section 3 → id="s03-multi-asset"
Section 4 → id="s04-correlation"
Section 5 → id="s05-wall"
Section 6 → id="s06-flows"
Section 7 → id="s07-sector-pulse"
Section 8 → id="s08-tech-radar"
Section 9 → id="s09-trade-signals"
Section 10 → id="s10-catalysts"
Section 11 → id="s11-appendix"
```

---

### STEP 2: 섹션별 데이터 매핑

**2.1. Part 1 섹션 (1-6) 매핑**

**Section 1: Executive Summary & Today's Thesis** → `id="s01-thesis"`
- `Today's Thesis` 문단 → 헤더 "오늘의 핵심 논점"
- 4개 bullet point → 4개 카드:
  - `Primary Market Driver` → "시장 주도 요인"
  - `100x Liquidity Indicator` → "유동성 지표"
  - `Key Correlation Shift` → "상관관계 변화"
  - `Actionable Signal` → "실행 가능한 신호"

**Section 2: Today's Market Pulse** → `id="s02-market-pulse"`
- **2.1 Key Change Drivers**: 5개 항목 → 5개 카드
- **2.2 Primary Opportunities**: 3개 항목 → `<li>` 태그
- **2.3 100x Liquidity Indicator**:
  - 점수/최대점수/상태 추출 → 프로그레스 바
  - `Commentary` → 종합 설명
  - `Fed Balance Sheet/TGA/RRP Contribution` → 상세 카드
  - `Key Driver` → 핵심 동인

**Section 3: Multi-Asset Performance Dashboard** → `id="s03-multi-asset"`
- **3.1 Top 3 U.S. Gainers**: 3개 종목 → 상승 종목 카드
- **3.2 Top 3 U.S. Losers**: 3개 종목 → 하락 종목 카드
- **3.3 Multi-Asset Performance**: 4개 테이블 → 4개 탭
  - `Major Indices` → "지수" 탭
  - `Fixed Income` → "채권·환율" 탭
  - `Commodities` → "원자재" 탭
  - `Digital Assets` → "디지털자산" 탭 (bullet 형식)

**Section 4: Correlation & Volatility Matrix** → `id="s04-correlation"`
- **4.1 Core Correlation Matrix**: 3개 행 → 3개 카드
  - `Asset Pair` → 제목
  - `Correlation` → 수치
  - `Interpretation` → 설명
- **4.2 Anomaly Spotlight**: 3개 항목 → `<li>` 태그

**Section 5: Fresh Wall Street Intelligence** → `id="s05-wall"`
- **5.1 Major IB Updates**: 테이블 전체 → 타임라인
  - `Action` 값에 따라 아이콘/배경색 동적 변경:
    - `UPGRADE` → 상향, 녹색
    - `DOWNGRADE` → 하향, 빨간색
    - `INITIATE` → 신규, 파란색
    - `RAISE_PT` → 목표가 상향, 주황색
- **5.2 Analyst's View**: 3개 View → 3개 카드
- **5.3 100x Market vs Street**: 데이터 4개 필드 매핑

**Section 6: Institutional Money Flows** → `id="s06-flows"`
- **6.1 Large Options Trades**: 4개 항목 → 키워드 강조 (`text-purple-600`)
- **6.2 ETF Flows**: 4개 항목 → 키워드 강조 (`text-green-600`)
- **6.3 Dark Pool & Political Donation Flows**: 3개 항목 매핑

**2.2. Part 2 섹션 (7-11) 매핑**

**Section 7: Sector & Rotation Pulse** → `id="s07-sector-pulse"`
- **7.1 11 GICS Sector Table**: 11개 섹터 → JavaScript `sectorData` 배열
  ```javascript
  { name: 'Sector', etf: 'ETF', day: Day (%), ytd: YTD (%) }
  ```
- **7.2 Sector Rotation Views**: 3개 View → 3개 카드
- **7.3 100x Sector Signal**: 5개 필드 매핑

**Section 8: Tech Leadership Pulse** → `id="s08-tech-radar"`
- **8.1 12 Key Tickers Table**:
  - 12개 종목 → **YTD 내림차순 정렬** → 12개 뒤집기 카드
  - 티커/등락률/YTD/뉴스 요약 매핑
- **8.2 AI Ecosystem Pulse**: 6개 항목 → 6개 카드
- **8.3 AI Investment Lens**: 3개 항목 → 3개 카드
- **8.4 100x AI Edge**: 3개 필드 매핑

**Section 9: Today's Actionable Trade Signals** → `id="s09-trade-signals"`
- **9.1 Live Trade Signals**: Signal #1, #2, #3 → 3개 카드 (진입/목표/손절/촉매 포함)
- **9.2 Live Broker Alpha Scanner**: 3개 카드 (Consensus Build/Upgrade Alert/Hidden Gem)
- **9.3 100x Signal Rank**: 모든 항목 매핑

**Section 10: Tomorrow's Catalyst & Economic Calendar** → `id="s10-catalysts"`
- **10.1 Economic Calendar**: 테이블 → 캘린더 (Interpretation 필드 비워두기)
- **10.2 Earnings Calendar**: 테이블 매핑
- **10.3 Corporate & Policy Events**: 테이블 매핑

**Section 11: Appendix** → `id="s11-appendix"`
- **11.1 Appendix A: Overnight Futures**: 테이블 → 카드
- **11.2 Appendix B: Key Chart Summaries**: 2개 항목 → 2개 카드
- ⚠️ **`Report Metadata` 섹션 제외**

---

### STEP 3: 콘텐츠 스타일링 및 번역

**3.1. 키워드 강조 규칙**
- **일반 분석/인사이트**: `<b class='text-blue-600'>`
- **대규모 옵션 거래**: `<b class='text-purple-600'>`
- **ETF 자금 흐름**: `<b class='text-green-600'>`
- **AI/테크 동향**: 문맥 기반
  - 긍정: `text-green-600`
  - 부정: `text-red-600`
  - 중립: `text-blue-600`

**3.2. 한국어 번역 원칙**

**번역 대상**:
- 모든 서술형 콘텐츠 (`text`, `Comment`, `Note`, `Interpretation`)
- **제목/부제목 반드시 포함**:
  - "Executive Summary" → "요약"
  - "Key Change Drivers" → "주요 변화 요인"
  - "Core Correlation Matrix" → "주요 자산 간 상관관계"

**번역 방식**:
- **적극적 의역**: 단순 직역 금지
  - ❌ "핵심 상관관계 매트릭스"
  - ✅ "주요 자산 간 상관관계"
- **전문 용어 선택**:
  - "C-Suite Sentiment" → "경영진 심리 지수"
- **자연스러운 문체**: 애널리스트 리포트 톤

**번역 제외**:
- JSON 키 (예: `"title"`, `"content"`)
- 구조 식별 값 (예: `"type": "table"`)
- 표준화 값 (예: `"Action"` 필드의 `UPGRADE`)
- 표 헤더 (예: `"Asset / Ticker"`)
- 고유명사/티커 (예: `XLK`, `S&P 500`, `FOMC`)

**3.3. 특수 텍스트 처리**

**인용 부호 제거** (매우 중요):
- `[1]`, `[15]`, `[47]` 등 대괄호 숫자 인용 **모두 제거**

**어색한 표현 수정**:
- 기계 번역투 → 자연스러운 문장 재작성
- 예: "양의 영역으로 전환" → "동조화 현상을 보이며 함께 상승"

**N/A 값 처리**:
- `"N/A"` 또는 빈 값 → `<span class="na-value">-</span>`

---

### STEP 4: 자체 검증 및 최종 확인

**4.1. 데이터 완전성 검증**

**항목 수 계산**:
1. **원본 JSON**: `sections` + `subsections` 총 개수 세기
2. **최종 HTML**: 제목 태그 (`<h2>`) 개수 세기
3. **비교**: A = B일 때만 완료, 불일치 시 재작업

**누락 확인 체크리스트**:
- [ ] Section 1-11 모든 제목 존재
- [ ] 각 섹션의 모든 subsection 제목 존재
- [ ] 모든 테이블 행 존재
- [ ] 모든 bullet point 항목 존재

**4.2. 스타일링 검증**

- [ ] 키워드 강조 (`text-blue-600`, `text-purple-600`, `text-green-600`) 적용
- [ ] 인용 부호 `[##]` 모두 제거
- [ ] N/A 값 `<span class="na-value">-</span>` 처리
- [ ] 아이콘/배경색 동적 변경 (Section 5.1)
- [ ] YTD 내림차순 정렬 (Section 8.1)

**4.3. 번역 품질 검증**

- [ ] 모든 제목/부제목 한글 번역 완료
- [ ] 의역 사용 (직역 없음)
- [ ] 전문 용어 적절히 사용
- [ ] 자연스러운 문체 (애널리스트 톤)
- [ ] 고유명사/티커 영문 유지

---

## III. 출력 형식

**단일 산출물**: 완성된 100x Daily Wrap HTML 파일

**출력 전 최종 확인**:
1. 템플릿 구조 변경 없음
2. 모든 데이터 매핑 완료
3. 자체 검증 통과
4. 한글 번역 완료

**파일 저장**:
```
YYYYMMDD_100x_Daily_Wrap_Final.html
```

---

## IV. 일반 규칙 및 예외 처리

### 규칙 1: 데이터 무결성 (절대 원칙)
- RAW JSON의 **모든** 데이터 요소는 최종 산출물에 포함
- 단 하나의 항목도 임의로 생략/누락 금지

### 규칙 2: 템플릿 구조 준수
- `100x-daily-wrap-template.html`의 구조/태그/ID/CSS 클래스 **절대 변경 금지**
- 지정된 위치에 내용만 채우기

### 규칙 3: 계층적 매핑
- JSON의 `sections`와 `subsections` 구조 기반
- `title`/`subtitle`을 식별자로 사용하여 정확한 HTML `id` 매핑

### 규칙 4: 데이터 공백 처리
- 특정 `section` 또는 `subsection`이 JSON에 없다면:
  - 해당 섹션 전체 (제목 포함) 렌더링하지 않음
  - 정보 공백 표시 대신 섹션 완전 제외

---

## V. 예시: Section 5.1 Major IB Updates 매핑

**JSON 입력**:
```json
{
  "subtitle": "5.1 Major IB Updates",
  "content": [
    {
      "type": "table",
      "data": [
        {
          "IB": "Goldman Sachs",
          "Ticker": "NVDA",
          "Action": "UPGRADE",
          "Target": "$150",
          "Comment": "AI 반도체 수요 급증"
        },
        {
          "IB": "Morgan Stanley",
          "Ticker": "TSLA",
          "Action": "DOWNGRADE",
          "Target": "$180",
          "Comment": "전기차 경쟁 심화"
        }
      ]
    }
  ]
}
```

**HTML 출력**:
```html
<div id="s05-wall">
  <h2>5. 주요 투자은행 업데이트</h2>

  <div class="timeline">
    <!-- 첫 번째 항목: UPGRADE → 녹색 -->
    <div class="timeline-item bg-green-50 border-green-200">
      <div class="timeline-icon bg-green-500">
        <i class="fas fa-arrow-up"></i>
      </div>
      <div class="timeline-content">
        <h4 class="font-bold text-green-800">Goldman Sachs - NVDA 목표가 상향</h4>
        <p class="text-sm"><b class="text-green-600">$150</b> 목표가 설정</p>
        <p class="text-gray-600">AI 반도체 수요 급증</p>
      </div>
    </div>

    <!-- 두 번째 항목: DOWNGRADE → 빨간색 -->
    <div class="timeline-item bg-red-50 border-red-200">
      <div class="timeline-icon bg-red-500">
        <i class="fas fa-arrow-down"></i>
      </div>
      <div class="timeline-content">
        <h4 class="font-bold text-red-800">Morgan Stanley - TSLA 등급 하향</h4>
        <p class="text-sm"><b class="text-red-600">$180</b> 목표가 설정</p>
        <p class="text-gray-600">전기차 경쟁 심화</p>
      </div>
    </div>
  </div>
</div>
```

---

## VI. 체크리스트

작업 완료 전 다음 사항을 반드시 확인:

- [ ] 통합 JSON 파일 로드 완료
- [ ] 템플릿 파일 로드 완료
- [ ] Section 1-11 모두 매핑
- [ ] 모든 subsection 매핑
- [ ] 테이블 데이터 누락 없음
- [ ] Bullet point 누락 없음
- [ ] 키워드 강조 적용
- [ ] 인용 부호 `[##]` 제거
- [ ] N/A 값 처리
- [ ] Action 기반 아이콘/색상 동적 변경 (Section 5.1)
- [ ] YTD 내림차순 정렬 (Section 8.1)
- [ ] 제목/부제목 한글 번역
- [ ] 의역 사용 (직역 없음)
- [ ] 자연스러운 문체
- [ ] 템플릿 구조 변경 없음
- [ ] 자체 검증 통과 (항목 수 일치)

---

**마지막 업데이트**: 2025-10-08
**버전**: Claude Integration v1.0
**기반**: GEMINI 100x-wrap-agent.md V3.0
