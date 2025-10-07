# Architecture Documentation Index

**100xFenok-Generator 아키텍처 설계 문서 모음**

---

## 📚 문서 구성

### 🎯 의사결정용 (시작점)
1. **ARCHITECTURE_SUMMARY.md** ⭐ **먼저 읽으세요**
   - Executive Summary: 현재 상황 및 문제점
   - 2가지 솔루션 비교 (Quick Integration vs Complete Redesign)
   - 권장 접근법: Option A (5시간)
   - 의사결정 체크리스트

### 📖 상세 설계 (구현용)
2. **ARCHITECTURE_DESIGN.md**
   - 전체 시스템 아키텍처 (Component, Data Model, Sequence)
   - 구현 전략 (Option A/B 상세)
   - 리스크 분석 및 완화 전략
   - 성공 지표 및 테스트 전략
   - 구현 체크리스트

3. **SYSTEM_DIAGRAM.md**
   - 시각화 다이어그램 (6개)
   - High-Level System Architecture
   - Report Generation Workflow
   - Data Flow Diagram
   - Component Interaction Diagram
   - Error Handling & Recovery Flow
   - State Transition Diagram

---

## 🚀 Quick Start Guide

### Step 1: 상황 이해 (5분)
```bash
# ARCHITECTURE_SUMMARY.md 읽기
# - Current Situation 섹션
# - Architectural Analysis 섹션
```

**핵심 포인트**:
- Custom 6개 ✅ 완료, 일반 12개 ❌ 누락
- 총 18개 리포트 목표
- Archive 모니터링 누락이 핵심 실패 원인

### Step 2: 솔루션 선택 (5분)
```bash
# ARCHITECTURE_SUMMARY.md 읽기
# - Recommended Solution 섹션
# - Decision Gate 섹션
```

**2가지 옵션**:
- **Option A**: 5시간, 최소 변경, 즉시 사용 ⭐ 권장
- **Option B**: 5일, 전체 재설계, 코드 품질 향상

### Step 3: 구현 계획 (10분)
```bash
# Option A 선택 시:
# ARCHITECTURE_DESIGN.md → "Option A: Quick Integration"

# Option B 선택 시:
# ARCHITECTURE_DESIGN.md → "Option B: Complete Redesign"
```

### Step 4: 시각화 확인 (10분)
```bash
# SYSTEM_DIAGRAM.md 읽기
# - Workflow 이해
# - Error Handling 확인
# - State Transition 숙지
```

---

## 📊 문서 사용 흐름도

```
시작
 │
 ▼
ARCHITECTURE_SUMMARY.md
 ├─ 현재 상황 파악
 ├─ 문제점 이해
 └─ 솔루션 선택 (Option A/B)
    │
    ├─ Option A 선택
    │  │
    │  ▼
    │  ARCHITECTURE_DESIGN.md
    │  ├─ Quick Integration 구현 전략
    │  ├─ 5시간 타임라인
    │  └─ Implementation Checklist
    │     │
    │     ▼
    │  SYSTEM_DIAGRAM.md
    │  ├─ Workflow 시각화
    │  ├─ Error Handling 패턴
    │  └─ Component 상호작용
    │     │
    │     ▼
    │  구현 시작
    │
    └─ Option B 선택
       │
       ▼
       ARCHITECTURE_DESIGN.md
       ├─ Complete Redesign 구조
       ├─ 5일 타임라인
       └─ 새로운 파일 구조
          │
          ▼
       SYSTEM_DIAGRAM.md
       ├─ 리팩토링 후 아키텍처
       └─ 마이그레이션 전략
          │
          ▼
       구현 시작
```

---

## 🎯 각 문서의 목적 및 대상

### ARCHITECTURE_SUMMARY.md
**목적**: 의사결정 지원
**대상**: 프로젝트 관리자, 기술 리더
**읽는 시간**: 15분
**핵심 질문**:
- 현재 무엇이 문제인가?
- 어떤 솔루션이 있는가?
- 어떤 것을 선택해야 하는가?

### ARCHITECTURE_DESIGN.md
**목적**: 구현 가이드
**대상**: 개발자, 시스템 아키텍트
**읽는 시간**: 45분
**핵심 질문**:
- 어떻게 구현하는가?
- 어떤 컴포넌트가 필요한가?
- 리스크는 무엇이며 어떻게 완화하는가?

### SYSTEM_DIAGRAM.md
**목적**: 시각화 및 이해
**대상**: 모든 이해관계자
**읽는 시간**: 20분
**핵심 질문**:
- 시스템이 어떻게 동작하는가?
- 컴포넌트 간 상호작용은?
- 데이터는 어떻게 흐르는가?

---

## 📋 구현 체크리스트

### Before Implementation (준비 단계)
- [ ] ARCHITECTURE_SUMMARY.md 읽고 이해
- [ ] Option A vs B 결정
- [ ] ARCHITECTURE_DESIGN.md에서 선택한 옵션 상세 읽기
- [ ] SYSTEM_DIAGRAM.md에서 워크플로우 확인
- [ ] 기존 코드 백업 (git commit)

### During Implementation (구현 단계)
- [ ] ARCHITECTURE_DESIGN.md "Implementation Checklist" 따라가기
- [ ] SYSTEM_DIAGRAM.md 참조하여 각 단계 검증
- [ ] 각 Phase 완료 시 승인 게이트 통과
- [ ] 리스크 완화 전략 적용

### After Implementation (검증 단계)
- [ ] ARCHITECTURE_DESIGN.md "Success Metrics" 확인
- [ ] 18개 리포트 모두 생성 확인
- [ ] 성능 지표 측정
- [ ] 문서 업데이트 (실제 구현과 차이점)

---

## 🔍 핵심 개념 용어집

### Custom Reports
- Part1 3개, Part2 3개 (총 6개)
- Template ID 10 사용
- PDF 업로드 필요 (Source + Prompt)
- 날짜 범위 설정 (Start ~ End)

### 일반 리포트 (General Reports)
- Feno_Docs/일반리포트/*.md (12개)
- Past Day 드롭다운 설정 (예: 90일)
- Prompt만 입력 (PDF 불필요)
- Keywords/URLs 옵션 설정 가능

### Template ID
- TerminalX 플랫폼의 리포트 템플릿 번호
- Custom Reports: ID 10 (검증 완료)
- 일반 리포트: ID 10 시도, 실패 시 5, 1로 fallback

### Archive Monitoring
- Phase 2: Monitor & Retry
- 리포트 상태 폴링 (30초마다)
- GENERATING → GENERATED 전환 대기
- 최대 20분 타임아웃

### Fire-and-Forget
- Phase 1 전략
- 18개 리포트 생성 요청만 일괄 제출
- 완료 대기 없이 다음 리포트 진행
- Archive에서 일괄 모니터링

---

## ⚠️ 중요 주의사항

### 절대 금지 (Critical)
1. **새 파일 생성 금지**: 35개 존재, 더 만들지 마라
2. **기존 성공 코드 무시 금지**: main_generator.py (2025-08-20 검증)
3. **Archive 확인 생략 금지**: Phase 2 필수
4. **임의 진행 금지**: 각 Gate마다 승인 받기

### 필수 확인 (Mandatory)
1. **로그인 성공**: _login_terminalx() multi-fallback
2. **폼 접근 성공**: Template ID 10, 리다이렉션 우회
3. **Archive GENERATED**: monitor_and_retry() 상태 확인
4. **HTML 추출 성공**: supersearchx-body + 50KB 이상

---

## 🔗 관련 문서

### 프로젝트 문서
- `MASTER_GUIDE.md`: 전체 프로젝트 가이드
- `CLAUDE.md`: 프로젝트별 지침 (Claude Code용)
- `docs/99_TROUBLESHOOTING.md`: 과거 실패 사례
- `docs/90_ANALYSIS_20251006.md`: As-Is 분석

### 기술 참조
- `main_generator.py`: Custom 6개 생성 (검증 완료)
- `free_explorer.py`: Past Day 설정 로직
- `quick_archive_check.py`: Archive 모니터링 참조
- `report_manager.py`: Batch 관리

---

## 📈 버전 히스토리

### v1.0 (2025-10-07)
- **ARCHITECTURE_SUMMARY.md**: 의사결정용 요약
- **ARCHITECTURE_DESIGN.md**: 상세 설계 문서
- **SYSTEM_DIAGRAM.md**: 시각화 다이어그램
- **README_ARCHITECTURE.md**: 문서 인덱스 (현재 파일)

### 작성자
- System Architect Agent
- Based on: main_generator.py (2025-08-20 success pattern)
- Analyzed: 35 files, 85% code duplication

---

## 🚀 다음 단계

### Immediate (지금 바로)
1. **ARCHITECTURE_SUMMARY.md** 읽기 (15분)
2. Option A vs B 결정
3. 선택한 옵션의 상세 구현 계획 읽기

### Short-term (5시간 or 5일)
1. **Option A**: Quick Integration 구현
2. **Option B**: Complete Redesign 구현
3. 테스트 및 검증

### Long-term (추후)
1. Option A 선택 시: 코드 리팩토링 (Phase 2)
2. 성능 모니터링 및 최적화
3. 추가 리포트 확장 (18개 → N개)

---

## 💡 FAQ

### Q1: 어떤 문서부터 읽어야 하나요?
**A**: `ARCHITECTURE_SUMMARY.md` → 의사결정 → 선택한 옵션의 `ARCHITECTURE_DESIGN.md` 섹션 → `SYSTEM_DIAGRAM.md`

### Q2: Option A와 B 중 어떤 것을 선택해야 하나요?
**A**:
- **긴급도 High & 즉시 사용**: Option A (5시간)
- **코드 품질 우선 & 시간 여유**: Option B (5일)
- **대부분의 경우**: Option A 권장 (검증된 패턴 재사용)

### Q3: 18개 리포트가 모두 다른 설정인가요?
**A**:
- **Custom 6개**: 같은 폼, 다른 Part (Part1/2)
- **일반 12개**: Prompt만 다름, Past Day는 대부분 90일 (조정 가능)

### Q4: 기존 35개 파일은 어떻게 되나요?
**A**:
- **Option A**: 그대로 유지, main_generator.py만 수정
- **Option B**: 35개 → 12개로 재구성

### Q5: 리스크가 가장 큰 부분은?
**A**:
1. **Past Day 드롭다운**: Multi-fallback으로 완화
2. **Archive 타임아웃**: 20분 대기 + Retry로 완화
3. **18개 동시 생성**: 실패 시 6개씩 분할

---

## 📞 Support & Contact

### 문서 문의
- **작성자**: System Architect Agent
- **작성일**: 2025-10-07
- **기반 코드**: main_generator.py (2025-08-20 검증)

### 이슈 리포팅
1. 문서 오류: 해당 .md 파일에 주석 추가
2. 구현 질문: ARCHITECTURE_DESIGN.md 참조
3. 시각화 문의: SYSTEM_DIAGRAM.md 확인

---

**문서 끝**
**다음**: ARCHITECTURE_SUMMARY.md 읽기 시작
