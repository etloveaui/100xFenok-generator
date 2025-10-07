# 100xFenok Generator - 구현 계획

## 1. Feno_Docs 분석 결과

### 발견한 중요 사실들:

1. **HTML 클래스 구조**
   - Feno_Docs 샘플: `supersearchx-body` 사용
   - 생성된 HTML (20251007): `markdown-body` 사용
   - **결론**: TerminalX가 두 클래스 모두 사용 가능

2. **워크플로우 이해**
   - Gemini를 통한 리포트 생성 지침 확인 (Instruction_Html.md)
   - 한국어 번역과 데이터 정제 필요
   - 인용 부호 [##] 제거 필요
   - 섹션별 최우수 콘텐츠 선택

3. **리포트 구조**
   - Part1: Executive Summary, Market Pulse, Multi-Asset Dashboard 등
   - Part2: Sector Analysis, Key Tickers 등
   - 섹션별 ID 매핑 (s01-thesis, s02-market-pulse 등)

## 2. 핵심 문제 재정의

### 기존 판단 (틀림):
- markdown-body 클래스를 못 찾아서 실패

### 실제 문제:
- Archive 모니터링은 작동하지만
- HTML 추출 시 렌더링 완료 대기 부족
- 10초 고정 대기로는 부족할 수 있음

## 3. 수정 계획

### Phase 1: HTML 추출 로직 개선
```python
# main_generator.py 720-761줄 수정
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

### Phase 2: Archive 모니터링 확인
- 이미 구현되어 있음 (report_manager.py)
- run_full_automation()에서 호출됨

### Phase 3: 6개 리포트 설정
- Part1, Part2는 이미 작동
- 나머지 4개 리포트 설정 추가 필요

## 4. 테스트 계획

1. **단일 리포트 테스트**
   - Part1 생성 및 HTML 추출
   - markdown-body 확인
   - 크기 검증

2. **6개 리포트 배치 테스트**
   - 모든 리포트 순차 생성
   - Archive 모니터링 확인
   - HTML 추출 성공률 측정

## 5. 예상 소요 시간

- 코드 수정: 30분
- 테스트: 1시간
- 검증: 30분
- **총 2시간**

## 6. 체크리스트

- [ ] HTML 추출 로직 폴링 방식으로 개선
- [ ] markdown-body와 supersearchx-body 모두 지원
- [ ] "No documents found" 체크 추가
- [ ] 크기 검증 (50KB 이상)
- [ ] 단일 리포트 테스트
- [ ] 6개 리포트 전체 테스트
- [ ] 성공률 90% 이상 달성

## 7. 결론

Feno_Docs 분석 결과:
1. HTML 클래스는 두 가지 모두 가능 (markdown-body, supersearchx-body)
2. Archive 모니터링은 이미 구현됨
3. **핵심은 HTML 렌더링 완료 대기**

다음 단계: HTML 추출 로직 개선 후 테스트