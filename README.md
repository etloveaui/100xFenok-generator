# 100xFenok-Generator

TerminalX 웹사이트에서 금융 리포트를 자동으로 생성하는 Selenium 기반 자동화 시스템

## 📊 현재 상태

- **상태**: 🔄 구현 중 (2025-10-08 - Part1/Part2 리포트)
- **성공 이력**:
  - ✅ 2025-08-20 11:17 AM (Part1/Part2 리포트 생성 성공)
  - ✅ 2025-10-08 02:30 AM (기본 리포트 6개 - 참고용)
- **핵심 파일**: main_generator.py, report_manager.py, Feno_Docs/ (템플릿)

## 🎯 목표: Part1/Part2 리포트 (각 3개, 총 6개)

**Part1 리포트** (Sections 1-6):
- Executive Summary, Market Pulse, Performance Dashboard
- Correlation Matrix, Wall Street Intelligence, Institutional Flows

**Part2 리포트** (Sections 7-11):
- Sector Rotation, Tech Leadership, Trade Signals
- Tomorrow's Catalysts, Appendix

**템플릿 위치**: `Feno_Docs/`
- `20250829 100x Daily Wrap Part1.json` (Part1 템플릿)
- `20250829 100x Daily Wrap Part2.json` (Part2 템플릿)
- `part1/part1_01-03.json`, `part2/part2_01-03.json` (예제)

## 🔧 구현 방법

**Part1/Part2 생성 방식** (기본 리포트와 다름):
- 방법: TerminalX Archive 모니터링 필요
- 특징: `markdown-body` 클래스 (기본은 `supersearchx-body`)
- 구현: `report_manager.py`의 Archive 폴링 로직
- 검증: HTML 크기 >50KB, `markdown-body` 클래스 확인

**Archive 모니터링**:
- 폴링 간격: 30초 → 120초 (exponential backoff)
- JavaScript 렌더링 대기: 3초 + 7초
- 재시도: 최대 2회

## 🚀 빠른 시작

### Part1/Part2 리포트 생성 (구현 필요)
```bash
cd C:\Users\etlov\agents-workspace\projects\100xFenok-generator
# Part1 리포트 3개 생성
python generate_part1_reports.py

# Part2 리포트 3개 생성
python generate_part2_reports.py
```

**예상 결과**:
- 6개 HTML 파일 (Part1 3개 + Part2 3개)
- 저장 위치: `generated_html/part1_*.html`, `generated_html/part2_*.html`
- 예상 시간: ~20분 (Archive 모니터링 포함)

## 🔑 핵심 정보

### 작동하는 코드 (2025-08-20 성공 케이스)
- **Archive 모니터링**: `report_manager.py:53-143` (monitor_and_retry)
- **리포트 생성**: `main_generator.py` (로그인 + 브라우저 설정)
- **템플릿**: `Feno_Docs/20250829 100x Daily Wrap Part1.json`, `Part2.json`
- **예제**: `Feno_Docs/part1/part1_01-03.json`, `part2/part2_01-03.json`

### Part1/Part2 생성 프로세스
1. TerminalX 로그인
2. 리포트 생성 요청
3. Archive 페이지 모니터링 (30초 간격)
4. 완료 시 HTML 추출 (`markdown-body` 클래스)
5. 크기 검증 (>50KB)

### 폴더 구조
- `Feno_Docs/`: Part1/Part2 템플릿 및 예제
- `generated_html/`: 생성된 리포트 HTML
- `archives/`: 과거 코드 백업
- `docs/`: 문서
- `input_data/`: 입력 데이터
- `secret/`: 로그인 정보

---

**마지막 업데이트**: 2025-10-08
**프로젝트 상태**: 🔄 Part1/Part2 리포트 구현 중
