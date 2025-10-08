# 100xFenok Generator - Technical Specification v2.0

## 1. 시스템 개요

### 1.1 목적
TerminalX 플랫폼에서 6개의 금융 리포트를 완전 자동으로 생성하고 HTML로 추출하는 시스템

### 1.2 핵심 요구사항
- **6개 리포트 동시 생성**: Part1, Part2 + 4개 추가 리포트
- **Archive 모니터링**: PENDING → GENERATING → GENERATED 상태 추적
- **HTML 추출**: markdown-body 또는 supersearchx-body 클래스 지원
- **품질 검증**: 50KB 이상 크기, "No documents found" 체크

### 1.3 성공 기준
- 6개 리포트 모두 GENERATED 상태 달성 (90% 이상)
- HTML 파일 크기 50KB 이상
- markdown-body 또는 supersearchx-body 클래스 포함
- 전체 프로세스 30분 이내 완료

## 2. 아키텍처 설계

### 2.1 시스템 구조
```
┌─────────────────────────────────────────────────────┐
│                   main_generator.py                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │   Login    │→ │  Generate  │→ │  Monitor   │   │
│  │  Module    │  │   Module   │  │   Module   │   │
│  └────────────┘  └────────────┘  └────────────┘   │
│                           ↓                         │
│  ┌────────────────────────────────────────────┐   │
│  │           report_manager.py                 │   │
│  │  - Archive Monitoring                       │   │
│  │  - Status Tracking                          │   │
│  │  - Retry Logic                              │   │
│  └────────────────────────────────────────────┘   │
│                           ↓                         │
│  ┌────────────────────────────────────────────┐   │
│  │          HTML Extraction Module             │   │
│  │  - Polling-based Wait                       │   │
│  │  - Multi-class Support                      │   │
│  │  - Content Validation                       │   │
│  └────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 2.2 데이터 플로우
```
1. 리포트 설정 로드 (six_reports_config.json)
2. TerminalX 로그인
3. 6개 리포트 병렬 생성 요청
4. Archive 모니터링 (폴링)
5. GENERATED 상태 확인 후 HTML 추출
6. 검증 및 저장
```

## 3. 상세 구현 스펙

### 3.1 HTML 추출 개선 (main_generator.py)

#### 3.1.1 현재 문제점
- 고정 10초 대기로 렌더링 미완료 시 실패
- markdown-body 클래스만 체크 (supersearchx-body 미지원)
- "No documents found" 체크 누락

#### 3.1.2 개선된 구현
```python
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
            # markdown-body 또는 supersearchx-body 찾기
            elements = self.driver.find_elements(
                By.XPATH,
                "//div[contains(@class, 'markdown-body') or contains(@class, 'supersearchx-body')]"
            )

            if elements:
                # HTML 추출
                html_content = self.driver.page_source

                # "No documents found" 체크
                if "No documents found" not in html_content:
                    # 크기 검증
                    if len(html_content) > 50000:  # 50KB 이상
                        # 저장
                        with open(output_html_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        print(f"  HTML 저장 완료: {output_html_path}")
                        return True

            time.sleep(poll_interval)
            elapsed += poll_interval

        except Exception as e:
            print(f"  렌더링 대기중... ({elapsed}초)")
            time.sleep(poll_interval)
            elapsed += poll_interval

    return False
```

### 3.2 Archive 모니터링 (report_manager.py)

#### 3.2.1 상태 추적 로직
```python
def monitor_and_retry(self, timeout: int = 1800, initial_interval: int = 30):
    """Archive 페이지에서 리포트 상태 모니터링"""

    start_time = time.time()
    check_count = 0

    while time.time() - start_time < timeout:
        check_count += 1
        print(f"\n[체크 #{check_count}] Archive 상태 확인...")

        # Archive 페이지 접속
        self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")
        time.sleep(10)  # JavaScript 렌더링 대기

        # 테이블 파싱
        rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")

        for row in rows:
            try:
                title_elem = row.find_element(By.XPATH, ".//td[2]")
                status_elem = row.find_element(By.XPATH, ".//td[4]")

                title = title_elem.text.strip()
                status = status_elem.text.strip().upper()

                # 우리 리포트인지 확인
                for report in self.reports:
                    if report.title in title:
                        if status == "GENERATED":
                            report.status = "GENERATED"
                            print(f"  ✅ {report.title}: GENERATED")
                        elif status == "GENERATING":
                            print(f"  🔄 {report.title}: GENERATING...")
                        elif status == "PENDING":
                            print(f"  ⏳ {report.title}: PENDING")
            except:
                continue

        # 모든 리포트 완료 확인
        completed = [r for r in self.reports if r.status == "GENERATED"]
        if len(completed) == len(self.reports):
            print(f"✅ 모든 리포트 생성 완료!")
            return True

        # 대기
        time.sleep(initial_interval)

    return False
```

### 3.3 전체 자동화 플로우 (run_full_automation)

```python
def run_full_automation(self):
    """6개 리포트 전체 자동화"""

    # Phase 1: 로그인
    self._login_terminalx()

    # Phase 2: 6개 리포트 생성 요청
    batch_manager = ReportBatchManager(self.driver)

    for config in self.six_reports_config:
        report = Report(
            part_type="custom",
            title=config["name"]
        )
        batch_manager.add_report(report)

        # 리포트 생성 요청
        self.generate_report_html(
            report,
            report_date_str,
            ref_date_start,
            ref_date_end,
            prompt=config["prompt"],
            keywords=config["keywords"],
            urls=config.get("urls", []),
            past_day=config["past_day"],
            num_pages=30
        )

    # Phase 3: Archive 모니터링
    success = batch_manager.monitor_and_retry(timeout=1800)

    # Phase 4: HTML 추출
    if success:
        for report in batch_manager.reports:
            if report.status == "GENERATED":
                output_path = f"generated_html/{report.title}.html"
                self.extract_and_validate_html(report, output_path)

    return success
```

## 4. 검증 체크리스트

### 4.1 사전 검증
- [ ] Selenium WebDriver 설치 확인
- [ ] Chrome/Edge 브라우저 버전 호환성
- [ ] TerminalX 로그인 정보 유효성
- [ ] six_reports_config.json 파일 존재

### 4.2 실행 중 검증
- [ ] 로그인 성공
- [ ] 6개 리포트 생성 요청 완료
- [ ] Archive 페이지 접근 가능
- [ ] 상태 변경 감지 (PENDING → GENERATING → GENERATED)
- [ ] HTML 렌더링 완료 확인

### 4.3 사후 검증
- [ ] 6개 HTML 파일 생성됨
- [ ] 각 파일 크기 > 50KB
- [ ] markdown-body 또는 supersearchx-body 클래스 포함
- [ ] "No documents found" 문자열 없음
- [ ] 섹션 구조 완전성 (s01-thesis, s02-market-pulse 등)

## 5. 구현 계획

### Phase 1: 코드 수정 (30분)
1. main_generator.py extract_and_validate_html 메서드 개선
2. 폴링 로직 구현
3. 다중 클래스 지원 추가

### Phase 2: 단위 테스트 (30분)
1. 단일 리포트 생성 테스트
2. HTML 추출 검증
3. Archive 모니터링 테스트

### Phase 3: 통합 테스트 (1시간)
1. 6개 리포트 동시 생성
2. 전체 플로우 검증
3. 성공률 측정

### Phase 4: 최종 검증 (30분)
1. 생성된 HTML 품질 확인
2. 샘플 HTML과 비교
3. 문서화 업데이트

## 6. 성공 지표

### 6.1 정량적 지표
- 성공률: 90% 이상 (6개 중 5개 이상 성공)
- 처리 시간: 30분 이내
- HTML 크기: 평균 100KB 이상
- 에러율: 10% 이하

### 6.2 정성적 지표
- HTML 구조 완전성
- 콘텐츠 품질 (Gemini 생성 품질)
- 시스템 안정성 (크래시 없음)
- 재시도 로직 작동

## 7. 리스크 및 대응

### 7.1 식별된 리스크
1. **TerminalX 서버 응답 지연**
   - 대응: 타임아웃 증가, 재시도 로직

2. **브라우저 메모리 부족**
   - 대응: 주기적 메모리 정리, 페이지 새로고침

3. **HTML 렌더링 실패**
   - 대응: 폴링 간격 조정, 최대 대기 시간 증가

### 7.2 롤백 계획
- 기존 작동 코드 백업 (main_generator_backup.py)
- Git 커밋으로 버전 관리
- 실패 시 이전 버전 복원

## 8. 다음 단계

1. **즉시**: extract_and_validate_html 메서드 수정
2. **10분 후**: 단일 리포트 테스트
3. **30분 후**: 6개 리포트 통합 테스트
4. **1시간 후**: 최종 검증 및 배포