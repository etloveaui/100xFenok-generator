"""
Archive 모니터링 통합 수정 코드

main_generator.py의 extract_and_validate_html() 메서드를
아래 코드로 교체하세요.

핵심 개선사항:
1. 10초 고정 대기 → 폴링 방식 (최대 2분, 5초 간격)
2. 한 번만 확인 → 렌더링 완료까지 반복 확인
3. "No documents found" 무시 → 완료 신호까지 대기
"""

def extract_and_validate_html(self, report, output_path: str) -> bool:
    """Archive 상태 확인 후 HTML 추출 및 검증 (폴링 방식 렌더링 대기)"""
    try:
        # 1. 리포트 페이지로 이동
        print(f"  - '{report.title}' HTML 추출 시작...")
        self.driver.get(report.url)

        # 2. 렌더링 완료 폴링 (최대 2분, 5초 간격)
        print(f"  - 리포트 렌더링 완료 대기 중...")
        max_wait_time = 120  # 최대 2분
        check_interval = 5   # 5초마다 체크
        elapsed = 0

        while elapsed < max_wait_time:
            time.sleep(check_interval)
            elapsed += check_interval

            # markdown-body 확인
            try:
                self.driver.find_element(By.XPATH, "//div[contains(@class, 'markdown-body')]")

                # "No documents found" 확인
                page_source = self.driver.page_source
                if "No documents found" in page_source:
                    print(f"  - {elapsed}초 경과: 아직 'No documents found' 상태...")
                    continue

                # 콘텐츠 크기 검증 (완전히 렌더링된 리포트는 >50KB)
                html_size = len(page_source)
                if html_size < 50000:
                    print(f"  - {elapsed}초 경과: HTML 크기 너무 작음 ({html_size} bytes)...")
                    continue

                # 성공: 모든 조건 충족
                print(f"  - 렌더링 완료 확인 ({elapsed}초 소요)")
                print(f"  - HTML 크기 검증 통과: {html_size} bytes")

                # HTML 저장
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                print(f"  - HTML 저장 완료: {output_path}")

                return True

            except NoSuchElementException:
                print(f"  - {elapsed}초 경과: markdown-body 아직 없음...")
                continue

        # 타임아웃
        print(f"  - 오류: {max_wait_time}초 대기 후에도 렌더링 완료되지 않음")
        return False

    except Exception as e:
        print(f"  - HTML 추출 중 예외 발생: {e}")
        return False


"""
교체 방법:

1. main_generator.py의 720-761줄 찾기
2. extract_and_validate_html() 메서드 전체를 위 코드로 교체
3. imports 확인:
   - time (이미 있음)
   - NoSuchElementException (이미 있음 - 줄 10)
   - By (이미 있음 - 줄 7)

4. 테스트 실행:
   python main_generator.py

기대 결과:
- Archive에서 "GENERATED" 확인 후 HTML 추출 시도
- 렌더링 완료까지 최대 2분 폴링
- "No documents found" 사라질 때까지 대기
- HTML 크기 50KB 이상 확인 후 저장
"""
