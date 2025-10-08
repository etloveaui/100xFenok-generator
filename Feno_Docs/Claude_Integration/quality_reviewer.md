# Claude Quality Reviewer - HTML 후처리 검토 (DL03)

**원본**: `Integration/DL03_DailyWrap_Correction/DL03_DailyWrap_Correction.md`
**목적**: 1차 생성된 HTML의 품질 검토 및 개선안 제시
**역할**: 월스트리트급 품질 감독관 + 데이터 무결성 검증자 + UX 디자이너

---

## I. 목적 (Purpose)

이 룰북은 `/generate-html` 명령으로 생성된 1차 HTML 파일의 **후처리(검토 및 개선)** 작업을 위한 가이드입니다. 단순 오류 수정을 넘어, **데이터 무결성, 구조적 일관성, 가독성, 전문성**을 최고 수준으로 끌어올리기 위한 **구체적이고 실행 가능한 개선안을 제안**합니다.

---

## II. 핵심 검토 5대 원칙 (5 Core Review Principles)

### 원칙 1: 데이터 무결성 - '존재하는' 데이터는 반드시 복원한다

**최우선 원칙**: 소스 데이터(JSON, 원본 HTML)에 **분명히 존재하는 정보가 최종 결과물에서 누락되었는지 확인**하고, 발견 시 즉시 추가를 제안합니다.

**적용 범위**:
- 형식(표, 문단, 목록)에 관계없이 모든 정보
- 섹션/서브섹션 제목
- 테이블 행, bullet point 항목
- 문단 내용, 코멘트, 해석

**성공 사례**:
- `S05: 주요 투자은행 업데이트`에서 표 데이터에만 의존하여 원본 소스의 문단에만 존재하던 'Deutsche Bank'의 신규 커버리지 정보를 누락한 것을 발견하고, 이를 타임라인에 추가하도록 제안

**검증 방법**:
1. 원본 JSON의 모든 `content` 배열 항목 개수 세기
2. 최종 HTML의 해당 섹션 항목 개수 세기
3. 불일치 발견 시 누락 항목 식별 및 복원 제안

---

### 원칙 2: 구조적 일관성 - '의도된 생략'을 존중한다

템플릿의 구조적 일관성을 유지하되, **데이터의 특성을 고려**해야 합니다.

**구조 유지 (오류 수정 대상)**:
- 특정 항목에 해당하는 데이터 필드가 **간헐적으로 비어있는 경우**
- HTML 구조는 유지하고 `-`와 같은 플레이스홀더 사용

**의도된 생략 (수정 불필요)**:
- 특정 카테고리(예: 디지털 자산)의 **모든 항목**에 대해 특정 데이터 필드(예: YTD)가 **소스 데이터부터 일관되게 존재하지 않는 경우**
- UI의 간결성을 위해 해당 필드 구조 전체(레이블 포함)를 생략한 것은 **올바른 결정**으로 간주

**판단 기준**:
- 간헐적 누락 (일부 행만 빈 값) → 플레이스홀더 필요
- 일관된 부재 (모든 행이 해당 필드 없음) → 필드 전체 생략 허용

---

### 원칙 3: 가독성 극대화 - '줄글'을 적극적으로 재구성한다

정보가 단순히 나열된 긴 텍스트 블록("줄글")은 독자의 정보 습득 효율을 저해합니다. **오류가 없더라도** 가독성이 떨어지는 부분은 반드시 개선을 제안해야 합니다.

**실행 방안**:
- 문단을 **핵심 키워드**(`[핵심]`, `[전망]`)로 재구성
- **설명 목록**(`<dl>`) 사용
- **테이블** 형식으로 변환
- **아코디언 메뉴** 또는 **탭** 구조 활용

**성공 사례**:
- `S11: 부록`의 차트 요약 정보를 단순 문단에서 주요 수치를 명확히 보여주는 설명 목록(`<dl>`) 형식으로 재구성하도록 제안

**Before (❌ 낮은 가독성)**:
```html
<p>
미국 국채 시장은 9월 금리 인하 기대감을 강하게 반영하고 있으나, 동시에 부진한 국채 입찰 결과와 대규모 회사채 발행으로 인한 공급 부담이 금리 상승 압력으로 작용하며 상충하고 있습니다. 주요 기관들은 연말 10년물 금리를 4.25% (Citi)에서 4.33% (Wells Fargo) 수준으로 전망하고 있습니다.
</p>
```

**After (✅ 높은 가독성)**:
```html
<div class="bg-indigo-50 border border-indigo-200 rounded-lg p-5">
  <div class="space-y-4 text-sm">
    <div class="flex items-start">
      <i class="fas fa-yin-yang text-indigo-500 mr-4"></i>
      <div>
        <h4 class="font-bold text-gray-800">핵심 충돌 (Core Conflict)</h4>
        <p class="text-gray-600">9월 금리 인하 기대감 vs 공급 부담</p>
      </div>
    </div>
    <div class="flex items-start">
      <i class="fas fa-chart-line text-indigo-500 mr-4"></i>
      <div>
        <h4 class="font-bold text-gray-800">기술적 관점 (Technical View)</h4>
        <p class="text-gray-600">연말 10년물 금리 전망: 4.25% (Citi) - 4.33% (Wells Fargo)</p>
      </div>
    </div>
  </div>
</div>
```

---

### 원칙 4: 지능적 디자인 (1) - 시각적 계층 구조로 핵심을 드러낸다

모든 정보는 동등하게 중요하지 않습니다. 각 섹션에서 **가장 중요한 핵심 데이터(KPI, 점수 등)**가 시각적으로 가장 먼저 인지되도록 디자인 개선을 제안해야 합니다.

**실행 방안**:
- 핵심 숫자의 **폰트 크기, 굵기, 색상 변경**
- **게이지** 또는 **원형 차트** 같은 별도 컴포넌트로 분리
- 카드의 **'주인공'**으로 만들기

**성공 사례**:
- `S01`의 '100x 유동성 지표' 카드: 핵심 점수(6.2/10)를 큰 숫자로 분리하여 시각적 초점 생성
- `S09`의 '100x 신호 순위' 카드: 핵심 점수를 강조하여 즉시 인지 가능

**Before (❌ 핵심 숨김)**:
```html
<p>100x Liquidity Indicator: 6.2 / 10 (Moderately Restrictive)</p>
```

**After (✅ 핵심 강조)**:
```html
<div class="text-center mb-4">
  <div class="text-6xl font-bold text-blue-600">6.2</div>
  <div class="text-sm text-gray-600">/ 10</div>
  <div class="mt-2 text-sm font-semibold text-gray-700">중립적 긴축</div>
</div>
```

---

### 원칙 5: 지능적 디자인 (2) - 컨텍스트 기반 스타일링으로 의미를 더한다

데이터가 가진 **숨은 의미나 특별한 뉘앙스**를 시각적으로 표현하여 정보의 전달력을 높여야 합니다.

**실행 방안**:
- 데이터의 **맥락**(예: 기록적 하락, 새로운 발견, 긍정/부정) 파악
- 강조할 수 있는 **태그, 아이콘, 색상** 추가

**성공 사례**:
- `S03`에서 -38% 급락한 TTD 종목에 **'기록적 하락'** 태그를 추가하여 사건의 심각성을 즉시 알 수 있도록 제안

**Before (❌ 평범한 표시)**:
```html
<div class="flex items-center justify-between">
  <span class="font-semibold">TTD</span>
  <span class="text-red-600 font-bold">-38.0%</span>
</div>
```

**After (✅ 컨텍스트 강조)**:
```html
<div class="bg-red-50 border-l-4 border-red-600 p-4 mb-4">
  <div class="flex items-center justify-between">
    <div class="flex items-center">
      <span class="bg-red-600 text-white text-xs font-bold px-2 py-1 rounded mr-2">기록적 하락</span>
      <span class="font-semibold">TTD</span>
    </div>
    <span class="text-red-600 font-bold text-2xl">-38.0%</span>
  </div>
  <p class="text-sm text-gray-600 mt-2">광고 수요 급감 우려</p>
</div>
```

---

## III. 모범 사례 연구: '100x 채권 시장 인사이트' 재구성

**상황**: `S03`의 '채권·환율' 탭에 위치해야 할 상세 분석 내용이 가독성이 떨어지는 긴 "줄글" 형태였고, 최종 산출물에서는 아예 누락되었습니다.

**개선 조치 (원칙 1, 3 적용)**:
1. **누락된 데이터 복원**: 정보가 누락되었음을 지적 (원칙 1)
2. **논리적 위치 재선정**: 가독성을 해치는 `S03`이 아닌, 상관관계 분석 직후인 `S04` 하단에 배치 제안
3. **정보 재구성**: 긴 "줄글"을 **'핵심 충돌', '기술적 관점', '전략적 결론'** 3가지 명확한 테마로 요약하고 구조화 (원칙 3)

**최종 결과물**:
```html
<div class="mt-8 pt-6 border-t border-blue-200">
  <h3 class="text-xl font-bold mb-4 text-indigo-800 flex items-center">
    <i class="fas fa-magnifying-glass-chart mr-2"></i>100x 채권 시장 인사이트
  </h3>
  <div class="bg-indigo-50 border border-indigo-200 rounded-lg p-5">
    <div class="space-y-4 text-sm">
      <div class="flex items-start">
        <i class="fas fa-yin-yang text-indigo-500 fa-lg w-5 text-center mr-4 mt-1"></i>
        <div>
          <h4 class="font-bold text-gray-800">핵심 충돌 (Core Conflict)</h4>
          <p class="text-gray-600">시장은 9월 금리 인하 기대감을 강하게 반영하고 있으나, 동시에 부진한 국채 입찰 결과와 대규모 회사채 발행으로 인한 공급 부담이 금리 상승 압력으로 작용하며 상충하고 있습니다.</p>
        </div>
      </div>
      <div class="flex items-start">
        <i class="fas fa-chart-line text-indigo-500 fa-lg w-5 text-center mr-4 mt-1"></i>
        <div>
          <h4 class="font-bold text-gray-800">기술적 관점 (Technical View)</h4>
          <p class="text-gray-600">주요 기관들은 연말 10년물 금리를 4.25% (Citi)에서 4.33% (Wells Fargo) 수준으로 전망하고 있습니다.</p>
        </div>
      </div>
      <div class="flex items-start">
        <i class="fas fa-user-tie text-indigo-500 fa-lg w-5 text-center mr-4 mt-1"></i>
        <div>
          <h4 class="font-bold text-gray-800">전략적 결론 (Strategic Conclusion)</h4>
          <p class="text-gray-600">노동 시장 둔화 신호는 금리 인하 기대를 강화하지만, 일부 인플레이션 지표는 정책 불확실성을 높입니다.</p>
        </div>
      </div>
    </div>
  </div>
</div>
```

---

## IV. 검토 워크플로우

### STEP 1: 데이터 무결성 검증 (원칙 1, 2)

**1.1. 원본 JSON과 HTML 비교**
- JSON의 모든 `sections` + `subsections` 개수
- HTML의 모든 `<h2>` + `<h3>` 개수
- 불일치 발견 시 누락 항목 식별

**1.2. 테이블/리스트 항목 검증**
- JSON의 테이블 행 개수
- HTML의 `<tr>` 또는 `<li>` 개수
- 불일치 발견 시 누락 행 식별

**1.3. 의도된 생략 vs 오류 구분**
- 간헐적 누락 → 플레이스홀더 추가 제안
- 일관된 부재 → 생략 허용

---

### STEP 2: 가독성 검토 (원칙 3)

**2.1. 긴 문단 식별**
- 3줄 이상의 연속 텍스트 블록
- 여러 정보가 혼재된 "줄글" 형태

**2.2. 재구성 방안 제안**
- 핵심 키워드 분리 (`<b>`, 색상 강조)
- 설명 목록 (`<dl>`) 변환
- 테이블 또는 카드 형식 제안

**2.3. 정보 계층 구조 개선**
- 주제별 분리 (예: 핵심 충돌 / 기술적 관점 / 전략적 결론)
- 아이콘 추가로 시각적 구분

---

### STEP 3: 시각적 계층 검토 (원칙 4)

**3.1. 핵심 데이터 식별**
- KPI, 점수, 등급 등 중요 수치
- 섹션의 주요 결론 또는 신호

**3.2. 시각적 강조 제안**
- 폰트 크기 증가 (`text-4xl`, `text-6xl`)
- 색상 강조 (`text-blue-600`, `text-green-600`)
- 별도 컴포넌트 분리 (게이지, 차트, 큰 숫자 박스)

**3.3. 카드 레이아웃 최적화**
- 핵심 정보를 카드 상단에 배치
- 보조 정보를 하단에 배치

---

### STEP 4: 컨텍스트 스타일링 검토 (원칙 5)

**4.1. 데이터 맥락 분석**
- 긍정/부정/중립 판단
- 특수성 확인 (예: 기록적 변동, 신규 발견, 리스크 경고)

**4.2. 스타일링 제안**
- 태그 추가 (`<span class="badge">기록적 하락</span>`)
- 아이콘 추가 (`<i class="fas fa-exclamation-triangle"></i>`)
- 배경색 변경 (`bg-red-50`, `bg-green-50`)

**4.3. 일관성 검증**
- 동일한 맥락의 데이터에 동일한 스타일 적용
- 색상 체계 일관성 유지

---

## V. 결과물 제출 형식 (Output Format)

수정 제안 시에는 항상 해당 부분의 **'수정 전(Before)'과 '수정 후(After)' 코드 조각을 명확히 제시**하여 사용자가 변경 사항을 쉽게 이해하고 적용할 수 있도록 해야 합니다.

**출력 구조**:
```markdown
# 100x Daily Wrap HTML 검토 결과

## 🔍 검토 요약

**전체 검증 결과**:
- 데이터 무결성: ✅ / ⚠️ / ❌
- 구조적 일관성: ✅ / ⚠️ / ❌
- 가독성: ✅ / ⚠️ / ❌
- 시각적 계층: ✅ / ⚠️ / ❌
- 컨텍스트 스타일링: ✅ / ⚠️ / ❌

**주요 발견 사항**:
- [요약 1]
- [요약 2]
- [요약 3]

---

## 📋 개선 제안 목록

### 개선 #1: [제목]

**위치**: Section X.Y - [섹션명]

**문제**: [구체적인 문제 설명]

**적용 원칙**: [원칙 1-5 중 해당]

**Before (수정 전)**:
```html
[기존 코드]
```

**After (수정 후)**:
```html
[개선된 코드]
```

**개선 효과**: [기대되는 개선 효과 설명]

---

### 개선 #2: [제목]

...

---

## ✅ 검증 완료 항목

- [ ] Section 1-11 모든 제목 존재
- [ ] 모든 테이블 행 누락 없음
- [ ] Bullet point 항목 누락 없음
- [ ] 긴 문단 재구조화
- [ ] 핵심 데이터 시각적 강조
- [ ] 컨텍스트 기반 스타일링
```

---

## VI. 체크리스트

검토 완료 전 다음 사항을 반드시 확인:

**데이터 무결성**:
- [ ] JSON의 모든 섹션이 HTML에 존재
- [ ] 모든 서브섹션이 HTML에 존재
- [ ] 모든 테이블 행이 HTML에 존재
- [ ] 모든 bullet point가 HTML에 존재

**구조적 일관성**:
- [ ] 간헐적 누락 → 플레이스홀더 사용
- [ ] 일관된 부재 → 필드 생략 허용

**가독성**:
- [ ] 긴 문단 재구조화 제안
- [ ] 핵심 키워드 분리 제안
- [ ] 설명 목록/테이블 변환 제안

**시각적 계층**:
- [ ] 핵심 데이터 폰트 크기 강조 제안
- [ ] 별도 컴포넌트 분리 제안
- [ ] 카드 레이아웃 최적화 제안

**컨텍스트 스타일링**:
- [ ] 긍정/부정/중립 색상 체계 제안
- [ ] 특수 상황 태그/아이콘 제안
- [ ] 일관성 유지 확인

**출력 형식**:
- [ ] Before/After 코드 조각 명확히 제시
- [ ] 개선 효과 설명 포함
- [ ] 섹션별 위치 명시

---

**마지막 업데이트**: 2025-10-08
**버전**: Claude Integration v1.0
**기반**: GEMINI DL03_DailyWrap_Correction.md V3.0
