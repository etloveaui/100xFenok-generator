# 100xFenok-Generator: 완전한 요구사항 분석

**분석 날짜**: 2025-10-07
**분석자**: Requirements Analyst Persona
**상태**: 요구사항 명확화 완료

---

## 1. 실제 사용자 요구사항 (Ground Truth)

### 1.1 사용자가 언급한 내용
```
"일반 보고서 DAY 변경하는거"
"제대로 동작되는지 확인"
"체크리스트"
"plan 디자인"
```

### 1.2 요구사항 해석

#### 불명확한 표현 분석
| 사용자 언급 | 모호성 | 추정되는 의미 | 검증 필요 사항 |
|------------|--------|--------------|---------------|
| "일반 보고서 DAY 변경" | 🔴 높음 | Past Day 설정 변경? | 어떤 보고서? 몇 일로? |
| "제대로 동작되는지 확인" | 🟡 중간 | 전체 시스템 검증? | 검증 범위? 기준? |
| "체크리스트" | 🔴 높음 | 작업 항목 목록? | 어떤 작업들? |
| "plan 디자인" | 🟡 중간 | 실행 계획 수립? | Quick Fix? 전체 재설계? |

---

## 2. 프로젝트 현황 분석

### 2.1 문서화된 목표 (CLAUDE.md & MASTER_GUIDE.md 기준)

**명확한 프로젝트 목표**:
```
TerminalX에서 6개 금융 리포트 자동 생성
1. Crypto Analysis (Past 30 days)
2. AI Technology Report (Past 30 days)
3. Stock Market Analysis (Past 30 days)
4. Tech Innovation Report (Past 30 days)
5. Economic Indicators (Past 30 days)
6. Energy Market Report (Past 30 days)
```

### 2.2 현재 상태 평가

| 영역 | 상태 | 증거 |
|-----|------|------|
| **전체 성공률** | ❌ 20% | 2025-08-25 실패, 2025-08-20 성공 |
| **핵심 문제** | ✅ 식별됨 | Archive 완료 대기 로직 누락 |
| **해결 방법** | ✅ 제시됨 | Quick Fix (5시간) / Full Refactor (5일) |
| **Past Day 설정** | ✅ 작동 | `free_explorer.py:317-335` |
| **Archive 확인** | ✅ 작동 | `quick_archive_check.py:156-198` |
| **통합 상태** | ❌ 미완료 | main_generator.py에 미통합 |

### 2.3 최근 작업 이력 (Git Commits)

```bash
9dbb99f (2025-10-07) "작업 및 클린업"
d0ffb91 (2025-10-07) "진행중"
ddc97ad "업데이트"
bc77f6e "feat: TerminalX 6개 보고서 자동화 작업 - 완전 실패 기록"
```

**해석**: 최근 클린업 작업이 진행되었으나 핵심 기능 통합은 미완료

---

## 3. 요구사항 우선순위 도출

### 3.1 추정 우선순위 (증거 기반)

#### P0 (긴급, 시스템 차단 요소)
```
요구사항: Archive 완료 대기 로직 통합
근거:
- CLAUDE.md:8 "핵심 문제: Archive 상태 확인 없이 바로 추출 시도"
- MASTER_GUIDE.md:36 "핵심 문제: 리포트 완료 대기 로직 누락"
- 20% 성공률의 직접적 원인

수용 기준:
✅ quick_archive_check.py:156-198 로직이 main_generator.py에 통합됨
✅ generate_report_html() 메서드가 Archive 완료를 대기함
✅ "No documents found" 에러가 발생하지 않음
✅ 5회 연속 테스트에서 95% 이상 성공

예상 소요: 5시간 (IMPLEMENTATION_ROADMAP.md 기준)
```

#### P1 (중요, 사용자 요청 관련)
```
요구사항 1: "일반 보고서 DAY 변경" - Past Day 설정 확인 및 수정
근거:
- six_reports_config.json 모든 리포트가 "past_day": 30
- 사용자가 특정 일수 변경을 원하는 것으로 추정

명확화 필요 질문:
❓ 어떤 보고서의 Past Day를 변경하시겠습니까?
   - 특정 1개 보고서? (예: Crypto Analysis)
   - 모든 6개 보고서?
❓ 몇 일로 변경하시겠습니까?
   - Past 7 days?
   - Past 14 days?
   - Past 60 days?
❓ 일시적 변경인가요, 영구적 변경인가요?
   - 일시적: 실행 시 파라미터로 전달
   - 영구적: six_reports_config.json 수정

수용 기준 (가정: 모든 보고서를 Past 7일로 변경):
✅ six_reports_config.json에서 "past_day": 7로 변경됨
✅ 또는 실행 시 --past-days 7 옵션 지원
✅ TerminalX UI에서 "Past Day" 드롭다운이 올바르게 설정됨
✅ 생성된 리포트가 실제로 7일 데이터를 포함함

예상 소요: 30분 (설정 파일 수정) ~ 2시간 (파라미터 시스템 추가)
```

```
요구사항 2: "제대로 동작되는지 확인" - 전체 시스템 검증
근거:
- 사용자가 현재 시스템 상태를 신뢰하지 못함
- 과거 실패 이력 (2025-08-25)

명확화 필요 질문:
❓ 검증 범위는?
   - 단일 리포트 생성만?
   - 전체 6개 리포트 생성?
   - 11단계 전체 워크플로우 (JSON 변환, HTML 빌드 포함)?
❓ 검증 기준은?
   - 1회 성공으로 충분?
   - 3회 연속 성공?
   - 5회 중 95% 성공?

수용 기준 (가정: 6개 리포트 3회 연속 성공):
✅ 3회 독립 실행에서 각각 6개 리포트 모두 생성 성공
✅ 각 리포트가 supersearchx-body 클래스 포함
✅ "No documents found" 에러 0건
✅ Archive 타임아웃 0건
✅ HTML → JSON 변환 성공
✅ 최종 Daily Wrap HTML 생성 성공

예상 소요: 3-6시간 (P0 완료 후 테스트)
```

#### P2 (선택, 장기 개선)
```
요구사항 3: "체크리스트" - 작업 항목 명확화 및 추적
근거:
- 사용자가 진행 상황을 추적하고 싶어함
- 복잡한 워크플로우 관리 필요

명확화 필요 질문:
❓ 체크리스트 용도는?
   - 개발 작업 추적?
   - 실행 시 워크플로우 단계 표시?
   - 검증 항목 리스트?

수용 기준 (가정: 개발 작업 추적):
✅ 실행 가능한 작업 항목 목록 작성
✅ 각 항목에 명확한 수용 기준 정의
✅ 예상 소요 시간 표시
✅ 의존 관계 명시

예상 소요: 1시간 (문서 작성)
```

```
요구사항 4: "plan 디자인" - 실행 계획 수립
근거:
- IMPLEMENTATION_ROADMAP.md 이미 존재 (Phase 1 Quick Fix)
- 사용자가 명확한 실행 계획을 원함

명확화 필요 질문:
❓ Quick Fix (5시간) vs Full Refactor (5일) 중 선택은?
❓ 즉시 시작 가능한가, 계획만 검토?
❓ 단계별 승인을 원하시나, 자율 진행?

수용 기준 (가정: Quick Fix 선택):
✅ Hour-by-hour 실행 계획 수립
✅ 각 단계 산출물 명시
✅ 검증 체크포인트 설정
✅ 롤백 계획 포함

예상 소요: 30분 (기존 IMPLEMENTATION_ROADMAP.md 커스터마이즈)
```

---

## 4. 미완성 항목 분석

### 4.1 개발 단계 (Fenomeno Workflow 기준)

| 단계 | 상태 | 증거 | 미완성 이유 |
|-----|------|------|------------|
| **Phase 1: As-Is Analysis** | ✅ 완료 | `docs/90_ANALYSIS_20251006.md` | - |
| **Phase 2: To-Be Design** | ✅ 완료 | `docs/98_ARCHITECTURE.md` | - |
| **Phase 3: Master Plan** | ✅ 완료 | `docs/IMPLEMENTATION_ROADMAP.md` | - |
| **Phase 4: Implementation** | ❌ 부분완료 | `main_generator.py:1056줄` | **Archive 로직 미통합** |

### 4.2 기능 완성도

| 기능 영역 | 완성도 | 증거 | 차단 요소 |
|----------|--------|------|-----------|
| 로그인 | ✅ 100% | `main_generator.py:45-78` | - |
| 브라우저 설정 | ✅ 100% | `main_generator.py:25-43` | - |
| Past Day 설정 | ✅ 100% | `free_explorer.py:317-335` | - |
| Archive 확인 | ✅ 100% | `quick_archive_check.py:156-198` | **미통합** |
| 리포트 제출 | ✅ 100% | `main_generator.py:272-506` | - |
| **완료 대기** | ❌ 0% | - | **P0 차단 요소** |
| HTML 추출 | ✅ 100% | `main_generator.py:733-804` | 완료 대기 후 실행 필요 |
| JSON 변환 | ✅ 100% | `json_converter.py` | - |
| Daily Wrap 빌드 | ✅ 100% | `main_generator.py:805-920` | - |

**결론**: 11단계 워크플로우 중 5단계 (Archive 완료 대기)만 누락

### 4.3 테스트 커버리지

| 테스트 유형 | 상태 | 파일 | 비고 |
|------------|------|------|------|
| 단위 테스트 | ❌ 없음 | - | 수동 테스트만 존재 |
| 통합 테스트 | ⚠️ 수동 | `test_full_6reports.py` | 자동화 미흡 |
| E2E 테스트 | ⚠️ 수동 | - | 성공 로그만 증거 |
| Archive 모니터 테스트 | ❌ 없음 | - | **P0 차단 요소** |

### 4.4 문서화 상태

| 문서 유형 | 상태 | 파일 | 최신성 |
|----------|------|------|--------|
| 프로젝트 가이드 | ✅ 완료 | `MASTER_GUIDE.md` | 2025-10-06 |
| 아키텍처 | ✅ 완료 | `docs/98_ARCHITECTURE.md` | 2025-10-07 |
| 실행 계획 | ✅ 완료 | `docs/IMPLEMENTATION_ROADMAP.md` | 2025-10-07 |
| 실행 가이드 | ⚠️ 부분 | `README.md` | Quick Fix 반영 필요 |
| API 문서 | ❌ 없음 | - | Full Refactor 후 필요 |

---

## 5. 요구사항 명확화 질문 (사용자 응답 필요)

### 5.1 긴급 질문 (P0/P1 실행 전 필수)

```
Q1. Archive 완료 대기 로직 통합 (P0)
    즉시 진행하시겠습니까?
    ☐ 예 - 지금 바로 5시간 Quick Fix 시작
    ☐ 아니오 - 계획만 검토하고 나중에 실행

Q2. "일반 보고서 DAY 변경" 구체화
    ☐ Crypto Analysis 리포트만 Past 7일로 변경
    ☐ 모든 6개 리포트를 Past 7일로 변경
    ☐ 모든 6개 리포트를 Past 14일로 변경
    ☐ 기타: _________________

Q3. "제대로 동작되는지 확인" 범위
    ☐ 단일 리포트 1회 생성 성공 확인
    ☐ 6개 리포트 1회 생성 성공 확인
    ☐ 6개 리포트 3회 연속 생성 성공 확인 (권장)
    ☐ 전체 워크플로우 (JSON 변환 포함) 검증

Q4. Quick Fix vs Full Refactor 선택
    ☐ Quick Fix 우선 (5시간, 95% 성공률)
    ☐ Full Refactor 우선 (5일, 99% 성공률, 장기 유지보수)
    ☐ Quick Fix → Full Refactor 순차 진행 (권장)
```

### 5.2 부가 질문 (P2, 선택사항)

```
Q5. 체크리스트 용도
    ☐ 개발 작업 추적 (Task list)
    ☐ 실행 시 워크플로우 단계 표시
    ☐ 검증 항목 리스트

Q6. 실행 계획 상세도
    ☐ Hour-by-hour 상세 계획 필요
    ☐ Phase-level 개요만 필요
    ☐ 기존 IMPLEMENTATION_ROADMAP.md로 충분

Q7. 단계별 승인 프로세스
    ☐ 각 단계마다 사용자 승인 필요 (Fenomeno Workflow)
    ☐ P0 완료 후 1회 승인
    ☐ 자율 진행 (최종 결과만 보고)
```

---

## 6. 추천 실행 계획 (Requirements Analyst 제안)

### 6.1 즉시 실행 가능한 시나리오

**시나리오 A: Minimal Viable Fix (3시간)**
```
목표: 가장 빠르게 작동하는 시스템 확보

1. [1시간] Archive 로직 통합
   - quick_archive_check.py → main_generator.py
   - generate_report_html() 수정

2. [1시간] 단일 리포트 테스트
   - Crypto Analysis 1회 생성
   - supersearchx-body 확인

3. [1시간] 6개 리포트 1회 테스트
   - 전체 워크플로우 검증
   - 문제 발생 시 디버깅

성공 기준:
✅ 6개 리포트 모두 생성 성공
✅ "No documents found" 에러 0건
✅ HTML 파일에 supersearchx-body 포함

리스크: 🟡 중간 (1회 성공이 재현성을 보장하지 않음)
```

**시나리오 B: Validated Fix (5시간) - 권장**
```
목표: 재현 가능한 95% 성공률 확보

1. [2시간] Archive 로직 통합 + 단위 테스트
   - 로직 통합
   - Report ID 추출 테스트
   - Archive 폴링 테스트

2. [2시간] 3회 연속 전체 테스트
   - 6개 리포트 × 3회 실행
   - 성공률 측정 (목표: 95%+)

3. [1시간] 문서화 및 사용자 인수
   - 실행 가이드 업데이트
   - 알려진 제약사항 문서화

성공 기준:
✅ 18개 리포트 생성 (6×3) 중 17개 이상 성공
✅ Archive 타임아웃 < 5%
✅ 사용자가 독립 실행 가능

리스크: 🟢 낮음 (검증된 성공 패턴)
```

**시나리오 C: Complete Solution (2주) - 장기 권장**
```
목표: 유지보수 가능한 프로덕션 시스템

Week 1: Quick Fix + Validation
- Day 1-2: 시나리오 B 실행
- Day 3-4: 프로덕션 사용 및 모니터링
- Day 5: 개선사항 수집

Week 2: Full Refactor
- Day 1-2: 12-file 아키텍처 구현
- Day 3: 테스트 커버리지 > 85%
- Day 4: 문서화 및 CI/CD
- Day 5: 사용자 트레이닝 및 인수

성공 기준:
✅ Quick Fix 성공률 95%+ 달성
✅ Full Refactor 코드 중복 < 15%
✅ 테스트 자동화 완료
✅ 사용자 독립 운영 가능

리스크: 🟢 낮음 (점진적 개선)
```

### 6.2 권장 선택

```
추천: 시나리오 B (Validated Fix, 5시간)

근거:
1. ✅ 즉각적 가치 제공 (5시간 내 95% 성공률)
2. ✅ 낮은 리스크 (검증된 로직 사용)
3. ✅ 재현 가능성 보장 (3회 연속 테스트)
4. ✅ 향후 개선 가능 (시나리오 C로 전환 가능)

다음 단계:
1. 사용자 승인 (Q1-Q4 응답)
2. IMPLEMENTATION_ROADMAP.md 기반 실행
3. 3회 테스트 후 프로덕션 배포
4. 2주 후 Full Refactor 검토
```

---

## 7. 수용 기준 상세 (Acceptance Criteria)

### 7.1 P0: Archive 로직 통합

```
기능 요구사항:
✅ generate_report_html() 메서드가 Archive 완료를 대기함
✅ 최대 5분 (300초) 타임아웃 설정
✅ 5초 간격으로 폴링
✅ "GENERATED" 상태 감지 시 True 반환
✅ "FAILED" 또는 타임아웃 시 False 반환

기술 요구사항:
✅ quick_archive_check.py:156-198 로직 재사용
✅ _extract_report_id_from_url() 메서드 구현
✅ _wait_for_archive_completion() 메서드 구현
✅ WebDriverWait 및 타임아웃 예외 처리

테스트 요구사항:
✅ 단일 리포트 생성 성공 (1회)
✅ 6개 리포트 연속 생성 성공 (1회)
✅ 타임아웃 시나리오 테스트 (모의 데이터)
✅ "No documents found" 에러 0건

문서화 요구사항:
✅ 코드 주석 추가 (한글)
✅ CLAUDE.md 업데이트 (성공 기록)
✅ EXECUTION_GUIDE.md 업데이트 (새 워크플로우)

배포 요구사항:
✅ Git 커밋 메시지: "feat: Integrate Archive completion monitoring (P0 fix)"
✅ 사용자 인수 테스트 통과
✅ 롤백 계획 문서화 (이전 버전 보관)
```

### 7.2 P1: Past Day 설정 (가정: 모든 리포트 7일)

```
기능 요구사항:
✅ six_reports_config.json의 모든 "past_day" 값이 7로 변경됨
✅ TerminalX UI에서 "Past Day" 드롭다운 올바르게 설정
✅ 생성된 리포트가 실제로 7일 데이터 포함 (검증 필요)

테스트 요구사항:
✅ 1개 리포트 생성 후 날짜 범위 확인
✅ HTML 내용에서 과거 7일 날짜 검증

문서화 요구사항:
✅ six_reports_config.json 주석 추가
✅ CLAUDE.md 업데이트 (Past Day 설정 확인됨)

배포 요구사항:
✅ Git 커밋: "feat: Change all reports to Past 7 days"
✅ 사용자 확인 (생성된 리포트 내용 검증)
```

### 7.3 P1: 전체 시스템 검증 (3회 연속 테스트)

```
기능 요구사항:
✅ 3회 독립 실행에서 각각 6개 리포트 생성 성공
✅ 총 18개 리포트 중 17개 이상 성공 (95%)

품질 요구사항:
✅ "No documents found" 에러 0건
✅ Archive 타임아웃 < 5% (1/18)
✅ HTML 파일 크기 > 10KB (실제 데이터 포함)
✅ supersearchx-body 클래스 존재

성능 요구사항:
✅ 리포트당 평균 생성 시간 3-6분
✅ 전체 6개 리포트 생성 시간 < 40분

문서화 요구사항:
✅ 테스트 결과 로그 저장
✅ 실패 사례 분석 (있는 경우)
✅ 알려진 제약사항 문서화

배포 요구사항:
✅ 사용자에게 3회 테스트 결과 공유
✅ 프로덕션 사용 승인 획득
```

---

## 8. 의존성 및 제약사항

### 8.1 기술적 의존성

| 의존성 | 현재 상태 | 차단 요소 | 해결 방법 |
|--------|----------|-----------|----------|
| ChromeDriver | ✅ 있음 | - | - |
| Selenium | ✅ 설치됨 | - | - |
| TerminalX 계정 | ✅ 있음 | - | - |
| Archive 페이지 접근 | ✅ 가능 | - | - |
| quick_archive_check.py | ✅ 있음 | **통합 필요** | P0 작업 |

### 8.2 환경 제약사항

| 제약사항 | 영향 | 완화 방법 |
|---------|------|-----------|
| 리포트 생성 시간 2-5분 | 전체 테스트 시간 증가 | 병렬 실행 (향후) |
| TerminalX UI 변경 가능성 | 셀렉터 실패 | 다중 셀렉터 전략 |
| 네트워크 타임아웃 | 간헐적 실패 | 재시도 로직 추가 |
| Windows 환경 전용 | 이식성 제한 | 추상화 계층 (Full Refactor) |

### 8.3 프로세스 제약사항

| 제약사항 | 영향 | 완화 방법 |
|---------|------|-----------|
| 단계별 사용자 승인 | 진행 속도 | 명확한 수용 기준 제시 |
| 수동 테스트 의존 | 재현성 보장 어려움 | 자동화 테스트 추가 |
| 문서 업데이트 필요 | 추가 시간 소요 | 단순화된 템플릿 사용 |

---

## 9. 리스크 평가

### 9.1 기술 리스크

| 리스크 | 확률 | 영향 | 완화 전략 | 우선순위 |
|--------|------|------|----------|----------|
| Archive 로직 통합 실패 | 🟢 낮음 | 🔴 높음 | 검증된 코드 재사용 | P0 |
| 타임아웃 조정 필요 | 🟡 중간 | 🟡 중간 | 5분 → 7분 확장 가능 | P1 |
| 셀렉터 변경 | 🟡 중간 | 🟡 중간 | 다중 셀렉터 전략 유지 | P2 |
| Past Day 설정 미작동 | 🟢 낮음 | 🟡 중간 | free_explorer.py 로직 검증됨 | P1 |

### 9.2 프로세스 리스크

| 리스크 | 확률 | 영향 | 완화 전략 | 우선순위 |
|--------|------|------|----------|----------|
| 요구사항 오해 | 🟡 중간 | 🟡 중간 | 명확화 질문 (Q1-Q7) | P0 |
| 테스트 시간 부족 | 🟡 중간 | 🔴 높음 | 3회 테스트 필수화 | P1 |
| 문서화 누락 | 🟡 중간 | 🟡 중간 | 체크리스트 사용 | P2 |

---

## 10. 다음 단계

### 10.1 즉시 실행 (사용자 응답 대기)

```
☐ 사용자에게 Q1-Q7 질문 제시
☐ 응답 수신 후 요구사항 최종 확정
☐ 시나리오 A/B/C 중 선택
☐ 실행 계획 승인
```

### 10.2 승인 후 실행

```
☐ Phase 4 Implementation 시작 (P0)
☐ Hour-by-hour 진행 상황 보고
☐ 각 체크포인트에서 검증
☐ 테스트 결과 문서화
☐ 사용자 인수 테스트
```

### 10.3 프로덕션 배포

```
☐ Git 커밋 및 푸시
☐ CLAUDE.md 및 MASTER_GUIDE.md 업데이트
☐ 사용자 트레이닝 (필요시)
☐ 모니터링 시작
☐ 개선사항 수집
```

---

## 부록 A: 증거 기반 분석

### A.1 Past Day 설정 증거

**six_reports_config.json 분석**:
```json
"past_day": 30  // 모든 6개 리포트 동일
```

**free_explorer.py:317-335 분석**:
- ✅ "Past Day" 드롭다운 클릭 로직 존재
- ✅ 옵션 선택 로직 작동 확인됨
- ⚠️ 현재 30일로 설정됨 (사용자가 변경 원함)

### A.2 Archive 확인 로직 증거

**quick_archive_check.py:156-198 분석**:
```python
def wait_for_completion(report_id, timeout=300):
    # ✅ 작동 확인된 로직
    # ✅ 5초 간격 폴링
    # ✅ "GENERATED" 상태 감지
    # ⚠️ main_generator.py에 미통합
```

### A.3 성공/실패 증거

**2025-08-20 성공 로그**:
```
Report 1198-1203: GENERATED
HTML extraction: supersearchx-body found
JSON conversion: success
```

**2025-08-25 실패 로그**:
```
Generate button clicked
Waiting 300 seconds... (blind wait)
ERROR: No documents found
HTML contains: MuiTable-root (1,057 bytes)
```

**결론**: Archive 완료 확인 없이 추출 시도 → 실패

---

## 부록 B: 체크리스트 템플릿

### B.1 P0 작업 체크리스트

```
Archive 로직 통합 (5시간)

Hour 1-2: 코드 통합
☐ quick_archive_check.py:156-198 로직 복사
☐ _extract_report_id_from_url() 메서드 구현
☐ _wait_for_archive_completion() 메서드 구현
☐ generate_report_html()에 통합 (line ~507 이후)

Hour 3: 단위 테스트
☐ Report ID 추출 테스트
☐ Archive 폴링 테스트 (모의 데이터)
☐ 타임아웃 테스트

Hour 4: 통합 테스트
☐ 단일 리포트 생성 테스트
☐ supersearchx-body 확인
☐ "No documents found" 없음 확인

Hour 5: 전체 테스트
☐ 6개 리포트 생성 테스트
☐ 성공률 측정 (목표: 100%)
☐ 문서화 (CLAUDE.md, EXECUTION_GUIDE.md)
```

### B.2 P1 작업 체크리스트

```
Past Day 설정 변경 (30분)

☐ six_reports_config.json 백업
☐ "past_day": 30 → 7 변경 (모든 6개 리포트)
☐ 1개 리포트 생성 테스트
☐ 날짜 범위 확인 (HTML 내용 검증)
☐ Git 커밋
```

```
전체 시스템 검증 (3-6시간)

☐ 1차 실행: 6개 리포트 생성
  ☐ 성공 개수 기록: __/6
  ☐ 실패 원인 분석 (있는 경우)

☐ 2차 실행: 6개 리포트 생성
  ☐ 성공 개수 기록: __/6
  ☐ 재현 가능성 확인

☐ 3차 실행: 6개 리포트 생성
  ☐ 성공 개수 기록: __/6
  ☐ 전체 성공률 계산: __% (목표: 95%+)

☐ 테스트 결과 문서화
☐ 사용자 인수 테스트
```

---

**문서 상태**: 사용자 응답 대기
**다음 액션**: Q1-Q7 질문 응답 수신
**예상 응답 시간**: 10-30분
**응답 후 즉시 실행 가능**: 예 (시나리오 B 권장)
