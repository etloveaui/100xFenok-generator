#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
개선된 HTML 추출 로직 테스트
- 폴링 방식
- 다중 클래스 지원 (markdown-body, supersearchx-body)
- 크기 및 콘텐츠 검증
"""

from main_generator import FenokReportGenerator
from report_manager import Report, ReportBatchManager
import time
from datetime import datetime, timedelta

def test_single_report_with_polling():
    """단일 리포트 생성 및 폴링 방식 HTML 추출 테스트"""

    print("=" * 60)
    print("개선된 HTML 추출 로직 테스트 시작")
    print("=" * 60)

    # 생성기 초기화
    generator = FenokReportGenerator()

    try:
        # 1. 로그인
        print("\n[1단계] TerminalX 로그인...")
        generator._login_terminalx()
        print("✅ 로그인 성공")

        # 2. 리포트 생성
        print("\n[2단계] 테스트 리포트 생성 요청...")
        report = Report(
            part_type="custom",
            title="Test Report - Improved Extraction"
        )

        # 날짜 설정
        today = datetime.now()
        report_date_str = today.strftime('%Y%m%d')
        ref_date_start = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        ref_date_end = today.strftime('%Y-%m-%d')

        # 리포트 생성 요청
        success = generator.generate_report_html(
            report,
            report_date_str,
            ref_date_start,
            ref_date_end,
            prompt="Analyze latest cryptocurrency market trends including Bitcoin and Ethereum",
            keywords="bitcoin,ethereum,cryptocurrency",
            urls=[],
            past_day=30,
            num_pages=30
        )

        if not success:
            print("❌ 리포트 생성 요청 실패")
            return False

        print(f"✅ 리포트 생성 요청 완료")
        print(f"   Report URL: {report.url}")
        print(f"   Report Title: {report.title}")

        # 3. Archive 모니터링
        print("\n[3단계] Archive 모니터링...")
        batch_manager = ReportBatchManager(generator.driver)
        batch_manager.reports.append(report)  # Report 객체 직접 추가

        # 모니터링 (최대 10분)
        monitor_success = batch_manager.monitor_and_retry(timeout=600, initial_interval=20)

        if not monitor_success:
            print("❌ Archive 모니터링 타임아웃")
            return False

        print("✅ 리포트 생성 완료 (GENERATED 상태)")

        # 4. HTML 추출 (개선된 폴링 방식)
        print("\n[4단계] HTML 추출 (개선된 폴링 방식)...")
        output_path = f"generated_html/test_{report_date_str}_improved.html"

        extract_success = generator.extract_and_validate_html(report, output_path)

        if extract_success:
            print("✅ HTML 추출 성공!")
            print(f"   파일 경로: {output_path}")

            # 파일 검증
            with open(output_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                print(f"   파일 크기: {len(html_content)} bytes")
                print(f"   markdown-body: {'✅' if 'markdown-body' in html_content else '❌'}")
                print(f"   supersearchx-body: {'✅' if 'supersearchx-body' in html_content else '❌'}")
                print(f"   No documents found: {'❌ 있음' if 'No documents found' in html_content else '✅ 없음'}")
        else:
            print("❌ HTML 추출 실패")

        return extract_success

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 브라우저 종료
        try:
            generator.driver.quit()
            print("\n브라우저 종료 완료")
        except:
            pass

def main():
    """메인 테스트 실행"""
    success = test_single_report_with_polling()

    print("\n" + "=" * 60)
    if success:
        print("🎉 테스트 성공! 개선된 HTML 추출 로직이 정상 작동합니다.")
    else:
        print("❌ 테스트 실패. 로그를 확인하세요.")
    print("=" * 60)

    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)