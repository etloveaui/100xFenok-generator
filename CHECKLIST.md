# 100xFenok Generator - Verification Checklist

**작업 검증 체크리스트**

---

## 실행 전 준비 체크리스트

### 환경 설정 확인
- [ ] Python 3.8+ 설치됨
- [ ] Chrome 또는 Edge 브라우저 설치됨
- [ ] ChromeDriver 존재 (chromedriver.exe, 약 19MB)
- [ ] Git 저장소 상태 정상 (선택사항)

**검증 명령**:
```bash
python --version  # 3.8 이상 확인
ls -la chromedriver.exe  # 파일 존재 확인
```

**소요 시간**: 1분

---

### 의존성 설치 확인
- [ ] selenium 설치됨 (4.15.0+)
- [ ] beautifulsoup4 설치됨 (4.12.0+)
- [ ] Jinja2 설치됨
- [ ] pyperclip 설치됨

**검증 명령**:
```bash
pip list | grep -E "selenium|beautifulsoup4|Jinja2|pyperclip"
```

**예상 출력**:
```
beautifulsoup4    4.12.0
Jinja2            3.1.2
pyperclip         1.8.2
selenium          4.15.0
```

**소요 시간**: 30초

---

### 설정 파일 확인
- [ ] `six_reports_config.json` 존재
- [ ] `report_configs.json` 존재
- [ ] TerminalX 자격 증명 확인됨
- [ ] `generated_html/` 디렉토리 존재

**검증 명령**:
```bash
ls -la six_reports_config.json report_configs.json
ls -ld generated_html/
```

**실패 시**: 디렉토리 생성 `mkdir -p generated_html`

**소요 시간**: 30초

---

## 실행 중 모니터링 체크리스트

### Phase 1: 로그인 (1-2분)
- [ ] 브라우저 창 열림 (headless=False 시)
- [ ] TerminalX 로그인 페이지 표시
- [ ] 자격 증명 입력됨
- [ ] 로그인 성공 (Subscriptions 버튼 보임)
- [ ] Enterprise 페이지로 리다이렉트됨

**예상 로그 출력**:
```
[Phase 1] TerminalX 로그인... ✅
로그인 성공
```

**실패 시 확인**:
- 네트워크 연결 상태
- 자격 증명 정확성
- 브라우저 호환성

**소요 시간**: 1-2분

---

### Phase 2: 리포트 생성 요청 (2-3분)
- [ ] Custom Report 페이지 접근
- [ ] 리포트 제목 입력됨
- [ ] 프롬프트 입력됨
- [ ] 키워드 입력됨 (있는 경우)
- [ ] Past Day 설정됨
- [ ] Generate 버튼 클릭 성공
- [ ] 리포트 URL 생성됨

**예상 로그 출력**:
```
[Phase 2] 6개 리포트 생성 요청...
  - Crypto Analysis 요청 완료 ✅
  - AI Technology Report 요청 완료 ✅
  - Stock Market Analysis 요청 완료 ✅
  - Tech Innovation Report 요청 완료 ✅
  - Economic Indicators 요청 완료 ✅
  - Energy Market Report 요청 완료 ✅
```

**실패 시 확인**:
- Past Day 설정 UI 존재 여부
- Generate 버튼 셀렉터 정확성
- JavaScript 렌더링 완료 여부

**소요 시간**: 2-3분

---

### Phase 3: Archive 모니터링 (5-15분)
- [ ] Archive 페이지 접근 성공
- [ ] 리포트 목록 표시됨
- [ ] 상태 "PENDING" 확인
- [ ] 상태 "GENERATING" 변경 감지
- [ ] 상태 "GENERATED" 완료 확인
- [ ] 6개 리포트 모두 완료됨

**예상 로그 출력**:
```
[Phase 3] Archive 모니터링...
[체크 #1] Archive 상태 확인...
  ⏳ Crypto Analysis: PENDING
  ⏳ AI Technology Report: PENDING
  ...
[체크 #2] Archive 상태 확인...
  🔄 Crypto Analysis: GENERATING
  🔄 AI Technology Report: GENERATING
  ...
[체크 #5] Archive 상태 확인...
  ✅ Crypto Analysis: GENERATED
  ✅ AI Technology Report: GENERATED
  ...
✅ 모든 리포트 생성 완료!
```

**실패 시 확인**:
- 타임아웃 설정 (기본 1800초)
- 폴링 간격 (기본 30초)
- Archive 페이지 JavaScript 렌더링

**소요 시간**: 5-15분 (리포트 복잡도에 따라 변동)

---

### Phase 4: HTML 추출 (1-3분)
- [ ] 리포트 페이지 접근 성공
- [ ] JavaScript 렌더링 대기
- [ ] markdown-body 또는 supersearchx-body 클래스 감지
- [ ] "No documents found" 체크 통과
- [ ] HTML 크기 > 50KB
- [ ] 파일 저장 성공

**예상 로그 출력**:
```
[Phase 4] HTML 추출...
  렌더링 대기중... (5초)
  렌더링 대기중... (10초)
  HTML 저장 완료: generated_html/20251007_Crypto_Analysis.html (150KB)
  HTML 저장 완료: generated_html/20251007_AI_Technology_Report.html (140KB)
  ...
```

**실패 시 확인**:
- 폴링 최대 대기 시간 (기본 120초)
- HTML 클래스 셀렉터 정확성
- 페이지 렌더링 완료 여부

**소요 시간**: 1-3분 (리포트당 10-30초)

---

## 실행 후 검증 체크리스트

### 파일 생성 확인
- [ ] 6개 HTML 파일 모두 생성됨
- [ ] 각 파일 크기 > 50KB
- [ ] 파일명 형식: `YYYYMMDD_리포트명.html`
- [ ] 파일 인코딩: UTF-8

**검증 명령**:
```bash
ls -lh generated_html/

# 예상 출력:
# -rw-r--r-- 1 etlov 197609 150K ... 20251007_Crypto_Analysis.html
# -rw-r--r-- 1 etlov 197609 140K ... 20251007_AI_Technology_Report.html
# ... (4개 추가)
```

**실패 시**: 누락된 리포트 개별 재실행

**소요 시간**: 30초

---

### HTML 구조 검증
- [ ] HTML 헤더 존재 (`<!DOCTYPE html>`)
- [ ] 스타일시트 포함
- [ ] markdown-body 또는 supersearchx-body div 존재
- [ ] "No documents found" 문자열 없음
- [ ] 실제 금융 데이터 포함 (테이블, 차트 등)

**검증 명령**:
```bash
# markdown-body 클래스 확인
grep -c "markdown-body" generated_html/*.html

# "No documents found" 체크
grep -l "No documents found" generated_html/*.html

# 예상 출력: (빈 결과 - 에러 없음)
```

**성공 기준**:
- markdown-body 클래스 발견: 6개 파일
- "No documents found": 발견 안됨

**소요 시간**: 1분

---

### 콘텐츠 품질 검증
- [ ] 섹션 구조 완전성 (s01-thesis, s02-market-pulse 등)
- [ ] 테이블 데이터 존재
- [ ] 차트/이미지 참조 존재 (있는 경우)
- [ ] 날짜 범위 정확성
- [ ] 금융 데이터 현실성

**검증 명령**:
```bash
# 섹션 확인
grep -o "s[0-9][0-9]-[a-z-]*" generated_html/20251007_Crypto_Analysis.html | head -10

# 예상 출력:
# s01-thesis
# s02-market-pulse
# s03-sector-performance
# ...
```

**검증 샘플**:
```bash
# HTML 내용 샘플 확인 (첫 100줄)
head -100 generated_html/20251007_Crypto_Analysis.html
```

**소요 시간**: 2-3분

---

### 로그 파일 검증
- [ ] 로그 파일 생성됨 (`log/*.log`)
- [ ] 에러 메시지 없음 또는 처리됨
- [ ] 타임스탬프 정확함
- [ ] 실행 단계별 로그 존재

**검증 명령**:
```bash
ls -lt log/ | head -5

# 최신 로그 확인
tail -50 log/main_generator_*.log
```

**확인 사항**:
- 로그인 성공 메시지
- 리포트 생성 요청 로그
- Archive 모니터링 로그
- HTML 추출 로그

**소요 시간**: 1분

---

## 성능 지표 체크리스트

### 타이밍 검증
- [ ] 전체 실행 시간: 20-30분 이내
- [ ] 로그인: 1-2분
- [ ] 리포트 생성 요청: 2-3분
- [ ] Archive 모니터링: 5-15분
- [ ] HTML 추출: 1-3분

**측정 방법**:
```bash
# 시작 시간 기록
start_time=$(date +%s)

# 스크립트 실행
python test_full_6reports.py

# 종료 시간 계산
end_time=$(date +%s)
elapsed=$((end_time - start_time))
echo "Total time: $elapsed seconds"
```

**목표**: 1800초 (30분) 이내

---

### 성공률 검증
- [ ] 6개 중 5개 이상 성공 (83%+)
- [ ] Archive 모니터링 타임아웃 없음
- [ ] HTML 추출 실패 없음
- [ ] 재시도 로직 작동 (실패 시)

**성공 기준**: 90% 이상 성공률

**실패 허용**: 6개 중 1개 이하

---

### 리소스 사용 검증
- [ ] Chrome 메모리 사용량 < 2GB
- [ ] CPU 사용률 안정적
- [ ] 디스크 공간 충분 (최소 100MB)
- [ ] 네트워크 연결 안정적

**모니터링 명령** (Windows):
```bash
tasklist | grep -i chrome
```

**조치 필요 시**: 브라우저 재시작 또는 메모리 정리

---

## 문제별 체크리스트

### 로그인 실패 시
- [ ] 자격 증명 정확성 재확인
- [ ] 네트워크 연결 확인
- [ ] 브라우저 버전 호환성 확인
- [ ] ChromeDriver 버전 호환성 확인
- [ ] TerminalX 서비스 상태 확인

**복구 단계**:
1. 자격 증명 수동 로그인 테스트
2. 브라우저 수동 실행 테스트
3. `browser_controller.py` 직접 실행

---

### Archive 모니터링 실패 시
- [ ] 타임아웃 설정 증가 (1800 → 2400초)
- [ ] 폴링 간격 조정 (30 → 45초)
- [ ] Archive 페이지 수동 접근 확인
- [ ] JavaScript 렌더링 대기 시간 증가
- [ ] 리포트 상태 셀렉터 정확성 확인

**복구 단계**:
1. Archive 페이지 수동 확인
2. 리포트 ID 확인
3. 상태 컬럼 위치 확인

---

### HTML 추출 실패 시
- [ ] 폴링 최대 대기 시간 증가 (120 → 180초)
- [ ] 클래스 셀렉터 확장 (markdown-body + supersearchx-body)
- [ ] "No documents found" 체크 추가
- [ ] 페이지 렌더링 완료 여부 확인
- [ ] 브라우저 개발자 도구로 DOM 확인

**복구 단계**:
1. 리포트 페이지 수동 접근
2. HTML 구조 확인
3. 셀렉터 업데이트

---

## 최종 승인 체크리스트

### 프로덕션 배포 전
- [ ] 모든 테스트 통과 (단일 + 전체)
- [ ] 성공률 90% 이상
- [ ] 로그 파일 정상
- [ ] HTML 품질 검증 완료
- [ ] 문서화 최신 상태
- [ ] Git 커밋 및 태그 생성 (선택사항)

**최종 검증 명령**:
```bash
# 전체 테스트 실행
python test_full_6reports.py

# 결과 확인
ls -lh generated_html/
grep -c "markdown-body" generated_html/*.html
```

**승인 기준**:
- 6개 파일 생성
- 각 파일 > 50KB
- markdown-body 클래스 포함
- 30분 이내 완료

---

## 일일 운영 체크리스트

### 매일 실행 전
- [ ] 브라우저 버전 확인
- [ ] ChromeDriver 버전 확인
- [ ] 네트워크 연결 안정성 확인
- [ ] 디스크 공간 확인 (최소 500MB)

### 매일 실행 후
- [ ] 생성된 HTML 파일 백업
- [ ] 로그 파일 아카이브
- [ ] 에러 로그 검토
- [ ] 성능 지표 기록

### 주간 점검
- [ ] 성공률 추이 분석
- [ ] 평균 실행 시간 확인
- [ ] 의존성 업데이트 확인
- [ ] 문서 업데이트 필요성 검토

---

**마지막 업데이트**: 2025-10-07
**관련 문서**: QUICKSTART.md, DAILY_USAGE.md, TROUBLESHOOTING.md
