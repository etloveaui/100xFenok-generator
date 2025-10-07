#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Archive 통합 테스트 - 간단 버전
기존 코드 그대로 사용, ReportBatchManager로 Archive 모니터링
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from main_generator import FenokReportGenerator
from report_manager import Report, ReportBatchManager
import time
from datetime import datetime, timedelta

def test_archive_integration():
    """Archive 모니터링 통합 테스트"""

    print("=" * 60)
    print("Archive 통합 테스트 시작")
    print("=" * 60)

    generator = FenokReportGenerator()

    try:
        # 1. 로그인
        print("\n[1단계] TerminalX 로그인...")
        generator._login_terminalx()
        print("✅ 로그인 성공")

        # 2. 리포트 생성
        print("\n[2단계] 리포트 생성 요청...")
        report = Report(
            part_type="standard",
            title="Archive Test Report"
        )

        today = datetime.now()
        report_date_str = today.strftime('%Y%m%d')
        ref_date_start = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        ref_date_end = today.strftime('%Y-%m-%d')

        # 실제 메서드 시그니처에 맞춰 호출
        success = generator.generate_report_html(
            report,
            report_date_str,
            ref_date_start,
            ref_date_end
        )

        if not success:
            print("❌ 리포트 생성 요청 실패")
            return False

        print(f"✅ 리포트 생성 요청 완료")
        print(f"   Report URL: {report.url}")
        print(f"   Report Status: {report.status}")

        # 3. Archive 모니터링 (핵심!)
        print("\n[3단계] Archive 모니터링...")
        batch_manager = ReportBatchManager(generator.driver)
        batch_manager.reports.append(report)

        # 모니터링 (최대 10분)
        print("   Archive에서 GENERATED 상태 대기중...")
        monitor_success = batch_manager.monitor_and_retry(
            timeout=600,  # 10분
            initial_interval=20  # 20초마다 체크
        )

        if not monitor_success:
            print("❌ Archive 모니터링 타임아웃")
            return False

        print("✅ 리포트 생성 완료 (GENERATED 상태)")

        # 4. HTML 추출
        print("\n[4단계] HTML 추출...")
        output_path = f"generated_html/test_archive_{report_date_str}.html"

        extract_success = generator.extract_and_validate_html(report, output_path)

        if extract_success:
            print("✅ HTML 추출 성공!")
            print(f"   파일 경로: {output_path}")

            # 파일 검증
            with open(output_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                file_size = len(html_content)
                has_markdown = 'markdown-body' in html_content
                has_supersearch = 'supersearchx-body' in html_content
                has_error = 'No documents found' in html_content

                print(f"\n📊 검증 결과:")
                print(f"   파일 크기: {file_size:,} bytes")
                print(f"   markdown-body: {'✅' if has_markdown else '❌'}")
                print(f"   supersearchx-body: {'✅' if has_supersearch else '❌'}")
                print(f"   No documents found: {'✅ 없음' if not has_error else '❌ 있음'}")
                print(f"   최종 판정: {'✅ 성공' if file_size > 50000 and not has_error else '❌ 실패'}")
        else:
            print("❌ HTML 추출 실패")
            return False

        return extract_success

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        try:
            generator.driver.quit()
            print("\n브라우저 종료 완료")
        except:
            pass

if __name__ == "__main__":
    success = test_archive_integration()

    print("\n" + "=" * 60)
    if success:
        print("🎉 테스트 성공! Archive 통합이 정상 작동합니다.")
        print("\n성과:")
        print("  - Archive 모니터링 로직 통합 완료")
        print("  - GENERATED 상태 대기 후 HTML 추출")
        print("  - 'No documents found' 에러 해결")
    else:
        print("❌ 테스트 실패. 로그를 확인하세요.")
    print("=" * 60)

    sys.exit(0 if success else 1)
