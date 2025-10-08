# 100xFenok Generator - Daily Usage Guide

**일상적인 사용 및 운영 가이드**

---

## 목차

1. [일일 실행 루틴](#일일-실행-루틴)
2. [모니터링 및 검증](#모니터링-및-검증)
3. [유지보수 작업](#유지보수-작업)
4. [성능 최적화](#성능-최적화)
5. [자동화 팁](#자동화-팁)

---

## 일일 실행 루틴

### 아침 실행 절차 (권장: 09:00)

#### 1단계: 환경 준비 (2분)

```bash
# 작업 디렉토리 이동
cd C:\Users\etlov\agents-workspace\projects\100xFenok-generator

# 브라우저 및 ChromeDriver 확인
tasklist | grep -i chrome  # Chrome 프로세스 확인
ls -la chromedriver.exe    # ChromeDriver 존재 확인
```

**체크리스트**:
- [ ] Chrome 브라우저 업데이트 없음
- [ ] ChromeDriver 버전 호환
- [ ] 네트워크 연결 안정
- [ ] 디스크 공간 충분 (최소 500MB)

**소요 시간**: 2분

---

#### 2단계: 사전 점검 (1분)

```bash
# 설정 파일 확인
ls -la six_reports_config.json report_configs.json

# 이전 실행 로그 확인
tail -20 log/main_generator_*.log | grep -E "ERROR|FAILED"

# 이전 생성 파일 백업 (선택사항)
mkdir -p archives/$(date +%Y%m%d)
mv generated_html/*.html archives/$(date +%Y%m%d)/ 2>/dev/null || true
```

**체크리스트**:
- [ ] 설정 파일 최신 상태
- [ ] 이전 실행 에러 없음
- [ ] 이전 파일 백업됨 (필요시)

**소요 시간**: 1분

---

#### 3단계: 실행 시작 (30초)

```bash
# 6개 리포트 전체 실행
python test_full_6reports.py

# 또는 프로덕션 실행
python main_generator.py
```

**예상 출력 (시작)**:
```
[Phase 1] TerminalX 로그인...
  브라우저 시작...
  로그인 페이지 접근...
  자격 증명 입력...
  로그인 성공 ✅

[Phase 2] 6개 리포트 생성 요청...
  - Crypto Analysis 요청 중...
  - AI Technology Report 요청 중...
  ...
```

**실행 시각 기록**: ___:___ (예: 09:05)

**소요 시간**: 30초 (스크립트 시작)

---

#### 4단계: 진행 모니터링 (20-30분)

**모니터링 포인트**:

**09:05-09:10 (5분)**: Phase 2 완료 확인
```
예상 로그:
[Phase 2] 6개 리포트 생성 요청... ✅
  - 모든 리포트 요청 완료
```

**09:10-09:25 (15분)**: Archive 모니터링
```
예상 로그:
[Phase 3] Archive 모니터링...
[체크 #1] Archive 상태 확인...
  ⏳ Crypto Analysis: PENDING
  ⏳ AI Technology Report: PENDING
  ...
[체크 #3] Archive 상태 확인...
  🔄 Crypto Analysis: GENERATING
  🔄 AI Technology Report: GENERATING
  ...
[체크 #5] Archive 상태 확인...
  ✅ Crypto Analysis: GENERATED
  ✅ AI Technology Report: GENERATED
  ...
```

**09:25-09:30 (5분)**: HTML 추출
```
예상 로그:
[Phase 4] HTML 추출...
  HTML 저장 완료: generated_html/20251007_Crypto_Analysis.html (150KB)
  HTML 저장 완료: generated_html/20251007_AI_Technology_Report.html (140KB)
  ...
```

**모니터링 체크리스트**:
- [ ] Phase 1 완료 (로그인)
- [ ] Phase 2 완료 (리포트 요청)
- [ ] Phase 3 진행 중 (Archive 모니터링)
- [ ] Phase 4 완료 (HTML 추출)

**소요 시간**: 20-30분

---

#### 5단계: 결과 검증 (3분)

```bash
# 생성된 파일 확인
ls -lh generated_html/

# 예상 출력:
# -rw-r--r-- 1 etlov 197609 150K Oct  7 09:30 20251007_Crypto_Analysis.html
# -rw-r--r-- 1 etlov 197609 140K Oct  7 09:30 20251007_AI_Technology_Report.html
# -rw-r--r-- 1 etlov 197609 160K Oct  7 09:30 20251007_Stock_Market_Analysis.html
# -rw-r--r-- 1 etlov 197609 130K Oct  7 09:30 20251007_Tech_Innovation_Report.html
# -rw-r--r-- 1 etlov 197609 145K Oct  7 09:30 20251007_Economic_Indicators.html
# -rw-r--r-- 1 etlov 197609 155K Oct  7 09:30 20251007_Energy_Market_Report.html

# 품질 검증
for file in generated_html/*.html; do
    echo "파일: $file"
    echo "  크기: $(stat -f%z "$file" 2>/dev/null || stat -c%s "$file") bytes"
    echo "  markdown-body: $(grep -c "markdown-body" "$file")"
    echo "  에러 체크: $(grep -c "No documents found" "$file")"
    echo ""
done
```

**검증 체크리스트**:
- [ ] 6개 파일 모두 생성됨
- [ ] 각 파일 크기 > 50KB
- [ ] markdown-body 클래스 포함
- [ ] "No documents found" 없음

**성공 기준**:
- 6개 중 5개 이상 성공 (83%+)
- 평균 파일 크기 100KB 이상

**소요 시간**: 3분

---

#### 6단계: 백업 및 정리 (2분)

```bash
# 날짜별 백업 디렉토리 생성
backup_dir="backups/$(date +%Y%m%d)"
mkdir -p "$backup_dir"

# HTML 파일 백업
cp generated_html/*.html "$backup_dir/"

# 로그 파일 백업
cp log/main_generator_*.log "$backup_dir/"

# 실행 요약 생성
cat > "$backup_dir/SUMMARY.txt" << EOF
실행 일시: $(date +"%Y-%m-%d %H:%M:%S")
생성 파일: $(ls generated_html/ | wc -l)개
총 크기: $(du -sh generated_html/ | cut -f1)
상태: 성공
EOF

echo "✅ 백업 완료: $backup_dir"
```

**백업 체크리스트**:
- [ ] HTML 파일 백업됨
- [ ] 로그 파일 백업됨
- [ ] 요약 파일 생성됨

**소요 시간**: 2분

---

### 전체 일일 루틴 요약

| 단계 | 작업 | 소요 시간 | 완료 |
|------|------|-----------|------|
| 1 | 환경 준비 | 2분 | [ ] |
| 2 | 사전 점검 | 1분 | [ ] |
| 3 | 실행 시작 | 30초 | [ ] |
| 4 | 진행 모니터링 | 20-30분 | [ ] |
| 5 | 결과 검증 | 3분 | [ ] |
| 6 | 백업 및 정리 | 2분 | [ ] |
| **총계** | | **약 30-40분** | |

---

## 모니터링 및 검증

### 실시간 모니터링

#### 로그 실시간 확인
```bash
# 최신 로그 파일 실시간 확인 (별도 터미널)
tail -f log/main_generator_*.log
```

**모니터링 키워드**:
- `✅` - 성공 단계
- `❌` - 실패 단계
- `⚠️` - 경고
- `🔄` - 진행 중
- `⏳` - 대기 중

---

#### Archive 페이지 수동 확인 (선택사항)

1. 브라우저에서 TerminalX 로그인
2. Archive 페이지 접근:
   ```
   https://theterminalx.com/agent/enterprise/report/archive
   ```
3. 리포트 상태 확인:
   - PENDING: 대기 중
   - GENERATING: 생성 중
   - GENERATED: 완료
   - FAILED: 실패

---

### 성공률 추적

#### 일일 성공률 기록

**기록 템플릿** (Excel 또는 Google Sheets):

| 날짜 | 실행 시각 | 완료 시각 | 성공/전체 | 성공률 | 평균 크기 | 비고 |
|------|-----------|-----------|-----------|--------|-----------|------|
| 2025-10-07 | 09:05 | 09:35 | 6/6 | 100% | 145KB | 완벽 |
| 2025-10-08 | 09:10 | 09:42 | 5/6 | 83% | 138KB | Crypto 실패 |
| 2025-10-09 | 09:05 | 09:40 | 6/6 | 100% | 152KB | 완벽 |

**성공률 계산**:
```bash
# 자동 계산 스크립트
success_count=$(ls generated_html/*.html 2>/dev/null | wc -l)
total_count=6
success_rate=$((success_count * 100 / total_count))
echo "성공률: $success_rate% ($success_count/$total_count)"
```

**목표 성공률**: 90% 이상 (6개 중 5개 이상)

---

### 품질 지표 추적

#### HTML 품질 점수

**자동 품질 검사 스크립트**:
```bash
#!/bin/bash
# quality_check.sh

for file in generated_html/*.html; do
    filename=$(basename "$file")
    size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file")
    has_markdown=$(grep -c "markdown-body" "$file")
    has_error=$(grep -c "No documents found" "$file")

    # 점수 계산
    score=0
    [ $size -gt 50000 ] && score=$((score + 40))      # 크기 > 50KB
    [ $size -gt 100000 ] && score=$((score + 20))     # 크기 > 100KB
    [ $has_markdown -gt 0 ] && score=$((score + 30))  # markdown-body 존재
    [ $has_error -eq 0 ] && score=$((score + 10))     # 에러 없음

    echo "$filename: $score/100 (크기: ${size}B, markdown: $has_markdown, 에러: $has_error)"
done
```

**품질 기준**:
- 90-100점: 우수
- 70-89점: 양호
- 50-69점: 보통
- 50점 미만: 재실행 권장

---

## 유지보수 작업

### 주간 유지보수 (권장: 매주 월요일)

#### 1. 의존성 업데이트 확인 (5분)

```bash
# 현재 버전 확인
pip list --outdated | grep -E "selenium|beautifulsoup4"

# 업데이트 가능 시 (주의: 테스트 필요)
# pip install --upgrade selenium beautifulsoup4
```

**업데이트 전 백업**:
```bash
# 현재 버전 기록
pip freeze > requirements_backup_$(date +%Y%m%d).txt
```

---

#### 2. 로그 파일 정리 (3분)

```bash
# 30일 이상 오래된 로그 삭제
find log/ -name "*.log" -mtime +30 -delete

# 또는 아카이브
mkdir -p log/archives
find log/ -name "*.log" -mtime +30 -exec mv {} log/archives/ \;
```

---

#### 3. 백업 정리 (5분)

```bash
# 90일 이상 오래된 백업 삭제
find backups/ -type d -mtime +90 -exec rm -rf {} +

# 압축 백업 (선택사항)
for dir in backups/2025*; do
    if [ -d "$dir" ] && [ ! -f "$dir.tar.gz" ]; then
        tar -czf "$dir.tar.gz" "$dir"
        rm -rf "$dir"
    fi
done
```

---

#### 4. ChromeDriver 버전 확인 (2분)

```bash
# Chrome 버전 확인
google-chrome --version  # Linux/Mac
# 또는 Chrome 설정 > 정보 확인 (Windows)

# ChromeDriver 버전 확인
./chromedriver --version

# 버전 불일치 시 업데이트 필요
# https://chromedriver.chromium.org/downloads
```

---

### 월간 유지보수 (권장: 매월 1일)

#### 1. 성능 분석 (10분)

```bash
# 지난 30일 성공률 분석
echo "=== 월간 성공률 분석 ==="
total_days=$(ls -1 backups/ | wc -l)
success_days=$(grep -l "성공" backups/*/SUMMARY.txt | wc -l)
monthly_rate=$((success_days * 100 / total_days))
echo "월간 성공률: $monthly_rate% ($success_days/$total_days days)"

# 평균 실행 시간 분석
echo "=== 월간 평균 실행 시간 ==="
# 로그 파일에서 시간 추출 및 계산
```

---

#### 2. 설정 최적화 검토 (15분)

**검토 항목**:
- [ ] 타임아웃 설정 적절성
- [ ] 폴링 간격 최적화
- [ ] 재시도 횟수 조정
- [ ] 리포트 설정 업데이트 (six_reports_config.json)

---

#### 3. 문서 업데이트 (10분)

**업데이트 대상**:
- [ ] TROUBLESHOOTING.md - 새로운 문제 추가
- [ ] DAILY_USAGE.md - 운영 경험 반영
- [ ] CHECKLIST.md - 체크리스트 개선

---

## 성능 최적화

### 실행 시간 단축

#### 1. 병렬 처리 최적화

**현재 방식** (순차):
```python
# 6개 리포트를 순차적으로 처리
for config in six_reports_config:
    generate_report(config)  # 각 5분 = 총 30분
```

**최적화 방식** (배치):
```python
# 6개 리포트를 동시에 요청 후 일괄 모니터링
for config in six_reports_config:
    submit_report_request(config)  # 각 30초 = 총 3분

# 일괄 Archive 모니터링
monitor_all_reports()  # 15분
extract_all_html()     # 3분
# 총 21분 (30% 단축)
```

---

#### 2. Archive 폴링 최적화

**현재 설정**:
```python
poll_interval = 30  # 30초마다 확인
timeout = 1800      # 30분 타임아웃
```

**최적화 설정** (adaptive polling):
```python
# 초기에는 자주 확인, 시간이 지날수록 간격 증가
if elapsed < 300:      # 처음 5분
    poll_interval = 15
elif elapsed < 900:    # 5-15분
    poll_interval = 30
else:                  # 15분 이후
    poll_interval = 60
```

**예상 효과**: Archive 확인 횟수 30% 감소

---

#### 3. HTML 추출 최적화

**현재 방식**:
```python
# 각 리포트 페이지를 순차 방문
for report in reports:
    driver.get(report.url)
    html = extract_html()  # 각 30초 = 총 3분
```

**최적화 방식** (빠른 검증):
```python
# 렌더링 완료 여부만 빠르게 확인
if is_content_loaded():  # 5초 내 확인
    html = extract_html()
else:
    retry_later()
```

**예상 효과**: HTML 추출 시간 50% 단축

---

### 리소스 사용 최적화

#### 1. 메모리 관리

```python
# 주기적 메모리 정리
import gc

def cleanup_memory():
    """메모리 정리"""
    gc.collect()  # 가비지 컬렉션
    print(f"메모리 정리 완료")

# 각 리포트 처리 후 호출
for report in reports:
    process_report(report)
    cleanup_memory()
```

---

#### 2. 브라우저 최적화

```python
# Chrome 옵션 최적화
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')           # GPU 비활성화
chrome_options.add_argument('--disable-dev-shm-usage') # 공유 메모리 제한 우회
chrome_options.add_argument('--no-sandbox')            # 샌드박스 비활성화
chrome_options.add_argument('--disable-extensions')    # 확장 프로그램 비활성화
```

**예상 효과**: 메모리 사용량 20% 감소

---

## 자동화 팁

### Windows 작업 스케줄러 설정

#### 1. 배치 파일 생성 (run_daily.bat)

```batch
@echo off
cd C:\Users\etlov\agents-workspace\projects\100xFenok-generator

echo [%date% %time%] 실행 시작 >> daily_run.log

python test_full_6reports.py >> daily_run.log 2>&1

if %errorlevel% equ 0 (
    echo [%date% %time%] 실행 성공 >> daily_run.log
) else (
    echo [%date% %time%] 실행 실패 (코드: %errorlevel%) >> daily_run.log
)

echo. >> daily_run.log
```

---

#### 2. 작업 스케줄러 등록

1. Windows 작업 스케줄러 열기
2. "기본 작업 만들기" 선택
3. 설정:
   - 이름: "100xFenok Daily Report"
   - 트리거: 매일 09:00
   - 작업: `run_daily.bat` 실행
   - 조건: 전원 연결 시에만 실행

---

### 실패 알림 설정

#### 이메일 알림 (선택사항)

```python
import smtplib
from email.mime.text import MIMEText

def send_failure_notification(error_message):
    """실패 시 이메일 알림"""
    msg = MIMEText(f"실행 실패:\n\n{error_message}")
    msg['Subject'] = '100xFenok Generator 실행 실패'
    msg['From'] = 'noreply@example.com'
    msg['To'] = 'admin@example.com'

    # SMTP 서버 설정 (예시)
    # server = smtplib.SMTP('smtp.gmail.com', 587)
    # server.starttls()
    # server.login('user', 'password')
    # server.send_message(msg)
    # server.quit()

# 사용 예시
try:
    run_full_automation()
except Exception as e:
    send_failure_notification(str(e))
    raise
```

---

### 성능 대시보드 (선택사항)

#### 간단한 HTML 리포트 생성

```python
def generate_daily_report():
    """일일 실행 리포트 생성"""
    html = f"""
    <html>
    <head><title>일일 실행 리포트</title></head>
    <body>
        <h1>100xFenok Generator - 일일 실행 리포트</h1>
        <p>실행 일시: {datetime.now()}</p>
        <h2>결과 요약</h2>
        <ul>
            <li>생성 파일: {len(os.listdir('generated_html'))}개</li>
            <li>성공률: {calculate_success_rate()}%</li>
            <li>평균 크기: {calculate_avg_size()}KB</li>
        </ul>
        <h2>파일 목록</h2>
        <table border="1">
            <tr><th>파일명</th><th>크기</th><th>품질 점수</th></tr>
            {generate_file_table()}
        </table>
    </body>
    </html>
    """

    with open(f'reports/daily_report_{datetime.now():%Y%m%d}.html', 'w') as f:
        f.write(html)
```

---

## 빠른 참조 카드

### 일일 명령어 치트시트

```bash
# 실행
python test_full_6reports.py

# 결과 확인
ls -lh generated_html/

# 품질 검증
grep -c "markdown-body" generated_html/*.html

# 로그 확인
tail -50 log/main_generator_*.log

# 백업
cp generated_html/*.html backups/$(date +%Y%m%d)/

# 정리
rm generated_html/*.html  # 백업 후에만!
```

---

### 문제 발생 시 긴급 조치

```bash
# 1. 실행 중지
# Ctrl+C (터미널)
# 또는 Chrome 프로세스 종료

# 2. 상태 확인
ls -la generated_html/
tail -20 log/main_generator_*.log

# 3. 재실행
python test_full_6reports.py

# 4. 여전히 실패 시
# TROUBLESHOOTING.md 참조
```

---

## 마치며

### 일일 운영 체크리스트 요약

**매일**:
- [ ] 09:00 실행 시작
- [ ] 진행 모니터링 (20-30분)
- [ ] 결과 검증
- [ ] 백업

**매주 월요일**:
- [ ] 의존성 확인
- [ ] 로그 정리
- [ ] ChromeDriver 버전 확인

**매월 1일**:
- [ ] 성능 분석
- [ ] 설정 최적화
- [ ] 문서 업데이트

---

**마지막 업데이트**: 2025-10-07
**관련 문서**: QUICKSTART.md, CHECKLIST.md, TROUBLESHOOTING.md
**문의**: 문제 발생 시 TROUBLESHOOTING.md 참조
