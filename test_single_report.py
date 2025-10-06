"""
단위 테스트: report_manager.py Archive 대기 로직 검증
1개 리포트 생성 → Archive 모니터링 → "Generated" 확인
"""

import os
import sys
from datetime import datetime, timedelta

# 프로젝트 루트를 sys.path에 추가
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from main_generator import FenokReportGenerator
from report_manager import ReportBatchManager

def test_single_report():
    """1개 리포트 생성 테스트"""
    print("=" * 60)
    print("단위 테스트: 1개 리포트 생성 및 Archive 모니터링")
    print("=" * 60)

    # 1. 초기화
    print("\n[STEP 1] FenokReportGenerator 초기화...")
    gen = FenokReportGenerator()

    # 2. 로그인
    print("\n[STEP 2] TerminalX 로그인...")
    if not gen._login_terminalx():
        print("[FAIL] Login failed")
        return False
    print("[OK] Login success")

    # 3. Batch Manager 초기화
    print("\n[STEP 3] ReportBatchManager 초기화...")
    batch_manager = ReportBatchManager(gen.driver)

    # 4. 날짜 설정
    today = datetime.now()
    report_date_str = today.strftime('%Y%m%d')
    ref_date_start = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    ref_date_end = today.strftime('%Y-%m-%d')

    print(f"리포트 날짜: {report_date_str}")
    print(f"참조 기간: {ref_date_start} ~ {ref_date_end}")

    # 5. 리포트 1개 추가 (Part1만 테스트)
    print("\n[STEP 4] 테스트 리포트 추가...")
    test_title = f"{report_date_str} TEST Archive Check Part1"
    batch_manager.add_report("Part1", test_title)
    report = batch_manager.reports[0]
    print(f"리포트 제목: {test_title}")

    # 6. 리포트 생성 요청
    print("\n[STEP 5] 리포트 생성 요청...")
    success = gen.generate_report_html(report, report_date_str, ref_date_start, ref_date_end)

    if not success:
        print("[FAIL] Report generation request failed")
        gen.driver.quit()
        return False

    print("[OK] Report generation request success")
    print(f"   URL: {report.url}")
    print(f"   Status: {report.status}")

    # 7. Archive 모니터링
    print("\n[STEP 6] Archive 페이지 모니터링 시작...")
    print("=" * 60)

    monitoring_success = batch_manager.monitor_and_retry()

    print("=" * 60)
    print("\n[STEP 7] 모니터링 결과 확인...")

    if not monitoring_success:
        print("[FAIL] Monitoring timeout or failed")
        gen.driver.quit()
        return False

    # 8. 최종 결과 확인
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    print(f"리포트 제목: {report.title}")
    print(f"리포트 URL: {report.url}")
    print(f"최종 상태: {report.status}")
    print(f"재시도 횟수: {report.retry_count}")

    if report.status == "GENERATED":
        print("\n[SUCCESS] Test passed: Report reached 'GENERATED' status!")

        # 9. HTML extraction test (optional)
        print("\n[STEP 8] HTML extraction test...")
        gen.driver.get(report.url)
        html_content = gen.driver.page_source

        if "supersearchx-body" in html_content:
            print("[OK] HTML extraction success: supersearchx-body found")
        elif "No documents found" in html_content:
            print("[FAIL] HTML extraction failed: No documents found")
        else:
            print(f"[WARN] HTML extraction: unexpected content (length: {len(html_content)} chars)")

        gen.driver.quit()
        return True
    else:
        print(f"\n[FAIL] Test failed: Report ended with status '{report.status}'")
        gen.driver.quit()
        return False

if __name__ == "__main__":
    try:
        success = test_single_report()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n사용자 중단 (Ctrl+C)")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n예외 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)
