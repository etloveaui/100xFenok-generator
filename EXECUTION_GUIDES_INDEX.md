# 100xFenok Generator - Execution Guides Index

**실행 가이드 통합 인덱스**

---

## 문서 개요

100xFenok Generator 프로젝트의 실행 및 운영을 위한 4가지 핵심 가이드 문서입니다.

**작성 일자**: 2025-10-07
**작성자**: Claude Code Technical Writer
**프로젝트 경로**: `C:\Users\etlov\agents-workspace\projects\100xFenok-generator`

---

## 문서 네비게이션

### 1. QUICKSTART.md - 빠른 시작 가이드 ⚡

**대상**: 처음 사용하는 모든 사용자
**목적**: 5분 안에 시스템을 실행 가능한 상태로 만들기
**소요 시간**: 5분 (설정) + 20-30분 (첫 실행)

**주요 내용**:
- 5단계 빠른 설치 프로세스
- 의존성 설치 및 확인
- 첫 테스트 실행
- 결과 검증 방법
- 빠른 문제 해결

**언제 읽나요?**:
- 프로젝트를 처음 설치할 때
- 새로운 환경에서 설정할 때
- 빠르게 테스트 실행하고 싶을 때

**다음 단계**: DAILY_USAGE.md (일상 사용법)

---

### 2. CHECKLIST.md - 검증 체크리스트 ✅

**대상**: 모든 사용자 (품질 검증 필요 시)
**목적**: 실행 전후 단계별 검증 및 품질 보증
**소요 시간**: 체크리스트당 1-5분

**주요 내용**:
- 실행 전 준비 체크리스트
- 실행 중 모니터링 체크리스트
- 실행 후 검증 체크리스트
- 성능 지표 체크리스트
- 문제별 대응 체크리스트

**언제 읽나요?**:
- 각 실행 전후 품질 검증 시
- 문제 발생 시 단계별 진단
- 프로덕션 배포 전 최종 검증
- 성능 지표 추적 필요 시

**다음 단계**: TROUBLESHOOTING.md (문제 발생 시)

---

### 3. TROUBLESHOOTING.md - 문제 해결 가이드 🔧

**대상**: 문제가 발생한 사용자
**목적**: 일반적인 문제의 원인 파악 및 해결
**소요 시간**: 문제당 5-20분

**주요 내용**:
- 5가지 일반적인 문제와 해결책
- 단계별 문제 진단 방법
- 긴급 복구 절차 (3가지 상황)
- 디버깅 도구 사용법
- 과거 실패 사례 분석

**언제 읽나요?**:
- 로그인 실패 시
- Archive 모니터링 실패 시
- HTML 추출 실패 시
- 특정 리포트만 실패 시
- 시스템이 완전히 작동하지 않을 때

**핵심 해결책**:
- **문제 4** (리포트 완료 대기 실패) ← 가장 중요!

**다음 단계**: DAILY_USAGE.md (정상 복구 후)

---

### 4. DAILY_USAGE.md - 일상 사용 가이드 📅

**대상**: 일일 운영 담당자
**목적**: 효율적인 일상 운영 및 유지보수
**소요 시간**: 일일 30-40분 + 주간/월간 유지보수

**주요 내용**:
- 일일 실행 루틴 (6단계)
- 실시간 모니터링 방법
- 성공률 및 품질 추적
- 주간/월간 유지보수 작업
- 성능 최적화 팁
- 자동화 설정 (Windows 작업 스케줄러)

**언제 읽나요?**:
- 시스템을 매일 운영할 때
- 성능 최적화가 필요할 때
- 자동화 설정을 원할 때
- 장기 운영 계획 수립 시

**다음 단계**: CHECKLIST.md (품질 검증)

---

## 사용 시나리오별 가이드

### 시나리오 1: 완전히 새로 시작

```
1. QUICKSTART.md (5분) → 환경 설정
2. QUICKSTART.md (20-30분) → 첫 실행
3. CHECKLIST.md (5분) → 결과 검증
4. DAILY_USAGE.md (10분) → 일일 루틴 학습
```

**총 소요 시간**: 약 1시간

---

### 시나리오 2: 문제 발생 시

```
1. CHECKLIST.md (3분) → 문제 단계 식별
2. TROUBLESHOOTING.md (10-20분) → 문제 해결
3. CHECKLIST.md (5분) → 해결 후 검증
4. DAILY_USAGE.md → 정상 운영 재개
```

**총 소요 시간**: 약 20-30분

---

### 시나리오 3: 일상 운영

```
1. DAILY_USAGE.md → 아침 루틴 (6단계)
2. CHECKLIST.md → 결과 검증
3. 필요 시 TROUBLESHOOTING.md → 즉시 대응
```

**총 소요 시간**: 30-40분/일

---

### 시나리오 4: 성능 개선

```
1. DAILY_USAGE.md → 성능 분석 섹션
2. CHECKLIST.md → 성능 지표 확인
3. DAILY_USAGE.md → 최적화 적용
4. CHECKLIST.md → 개선 효과 검증
```

**총 소요 시간**: 1-2시간

---

## 문서 간 상호 참조

### QUICKSTART.md 참조 링크
- **실패 시**: TROUBLESHOOTING.md
- **다음 단계**: DAILY_USAGE.md
- **검증**: CHECKLIST.md

### CHECKLIST.md 참조 링크
- **설정**: QUICKSTART.md
- **문제 시**: TROUBLESHOOTING.md
- **일상 운영**: DAILY_USAGE.md

### TROUBLESHOOTING.md 참조 링크
- **기본 설정**: QUICKSTART.md
- **정상 운영**: DAILY_USAGE.md
- **검증**: CHECKLIST.md

### DAILY_USAGE.md 참조 링크
- **초기 설정**: QUICKSTART.md
- **검증**: CHECKLIST.md
- **문제 시**: TROUBLESHOOTING.md

---

## 핵심 정보 빠른 참조

### 프로젝트 기본 정보

**프로젝트 이름**: 100xFenok Generator
**목적**: TerminalX에서 6개 금융 리포트 자동 생성
**현재 상태**: 작동 가능 (개선 완료)
**성공 이력**: 2025-08-20 (6개 리포트 성공)

---

### 실행 명령어

```bash
# 전체 실행 (권장)
python test_full_6reports.py

# 단일 테스트
python test_improved_extraction.py

# 프로덕션 실행
python main_generator.py
```

---

### 핵심 파일 위치

| 항목 | 경로 |
|------|------|
| 프로젝트 루트 | `C:\Users\etlov\agents-workspace\projects\100xFenok-generator` |
| 생성 파일 | `generated_html/*.html` |
| 로그 | `log/*.log` |
| 백업 | `backups/YYYYMMDD/` |
| 설정 | `six_reports_config.json` |

---

### 작동하는 코드 위치

| 기능 | 파일 | 줄 번호 |
|------|------|---------|
| 로그인 | main_generator.py | 45-78 |
| 브라우저 설정 | main_generator.py | 25-43 |
| Past Day 설정 | free_explorer.py | 317-335 |
| Archive 확인 | quick_archive_check.py | 156-198 |
| HTML 추출 | main_generator.py | 720-787 |

---

### 성공 기준

- 6개 리포트 중 5개 이상 성공 (83%+)
- 각 HTML 파일 크기 > 50KB
- markdown-body 또는 supersearchx-body 클래스 포함
- "No documents found" 문자열 없음
- 전체 실행 시간 30분 이내

---

### 예상 소요 시간

| 작업 | 소요 시간 |
|------|-----------|
| 초기 설정 | 5분 |
| 첫 실행 | 20-30분 |
| 일일 실행 | 30-40분 |
| 문제 해결 | 10-30분 |
| 주간 유지보수 | 15분 |
| 월간 유지보수 | 35분 |

---

## 추가 참조 문서

### 프로젝트 전체 문서

1. **README.md** - 프로젝트 개요
2. **MASTER_GUIDE.md** - 완전한 마스터 가이드
3. **TECHNICAL_SPECIFICATION.md** - 기술 사양
4. **SYSTEM_ANALYSIS_SUMMARY.md** - 시스템 분석

### 아키텍처 문서

- **docs/98_ARCHITECTURE.md** - 시스템 아키텍처
- **docs/90_ANALYSIS_20251006.md** - 종합 분석
- **CODE_MIGRATION_GUIDE.md** - 코드 마이그레이션

### 히스토리 문서

- **CHECKPOINT.md** - 체크포인트 기록
- **ROOT_CAUSE_ANALYSIS.md** - 근본 원인 분석
- **TERMINALX_AUTOMATION_LOG.md** - 자동화 로그

---

## 문서 버전 이력

### v2.0 (2025-10-07)
- 4가지 실행 가이드 완성
- 명확한 단계별 지침
- 예상 결과 및 소요 시간 추가
- 실패 시 대응 방안 포함

### v1.0 (2025-10-06)
- MASTER_GUIDE.md 작성
- 기본 문서 구조 수립

---

## 피드백 및 개선

### 문서 개선 제안

문서 사용 중 발견한 문제나 개선 사항이 있다면:

1. 문제 상황 기록
2. 예상했던 내용 vs 실제 내용
3. 개선 제안

**기록 위치**: 각 문서 하단 또는 별도 FEEDBACK.md

---

### 자주 묻는 질문 (FAQ)

**Q: 어떤 문서부터 읽어야 하나요?**
A: QUICKSTART.md부터 시작하세요. 5분이면 충분합니다.

**Q: 문제가 발생했어요. 어떻게 하나요?**
A: TROUBLESHOOTING.md의 "일반적인 문제" 섹션을 먼저 확인하세요.

**Q: 매일 사용하는 방법은?**
A: DAILY_USAGE.md의 "일일 실행 루틴" 섹션을 따르세요.

**Q: 성공률을 높이려면?**
A: DAILY_USAGE.md의 "성능 최적화" 섹션을 참조하세요.

**Q: 자동화하고 싶어요.**
A: DAILY_USAGE.md의 "자동화 팁" 섹션을 참조하세요.

---

## 빠른 시작 플로우차트

```
시작
  ↓
처음 사용? ─── 예 → QUICKSTART.md → 설정 완료
  │                                    ↓
  노                              첫 실행 성공?
  ↓                                    ↓
일일 사용? ─── 예 → DAILY_USAGE.md  노 → TROUBLESHOOTING.md
  │                      ↓                      ↓
  노                실행 성공?            문제 해결
  ↓                      ↓                      ↓
문제 발생? ─── 예 → CHECKLIST.md → TROUBLESHOOTING.md
  │                                              ↓
  노                                        해결됨?
  ↓                                              ↓
성능 개선? ─── 예 → DAILY_USAGE.md          예 → DAILY_USAGE.md
  │                 (최적화 섹션)                  (정상 운영)
  노                                              ↓
  ↓                                          계속 운영
완료
```

---

## 연락처 및 지원

### 문서 관련

**작성자**: Claude Code Technical Writer
**역할**: Technical Writer Persona
**업데이트**: 2025-10-07

### 프로젝트 관련

**프로젝트 소유자**: Fenomeno Team
**Git 저장소**: 독립 프로젝트 (workspace와 별개)
**프로젝트 경로**: `C:\Users\etlov\agents-workspace\projects\100xFenok-generator`

---

## 라이센스 및 면책

이 문서들은 100xFenok Generator 프로젝트의 일부이며, 내부 사용을 목적으로 작성되었습니다.

**면책 조항**:
- 문서는 현재 시스템 상태를 기반으로 작성됨
- TerminalX 플랫폼 변경 시 일부 내용이 유효하지 않을 수 있음
- 실제 결과는 환경에 따라 다를 수 있음

---

**마지막 업데이트**: 2025-10-07
**문서 버전**: v2.0
**상태**: 프로덕션 준비 완료 ✅
