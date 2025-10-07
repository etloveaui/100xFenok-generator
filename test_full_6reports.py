#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
100xFenok Generator - 6개 리포트 전체 테스트
개선된 폴링 방식 HTML 추출 로직 적용
"""

from main_generator import FenokReportGenerator
from report_manager import Report, ReportBatchManager
import time
import json
from datetime import datetime, timedelta

def test_full_six_reports():
    """6개 리포트 전체 생성 및 추출 테스트"""

    print("=" * 80)
    print(" 100xFenok Generator - 6개 리포트 전체 테스트")
    print(" 개선된 폴링 방식 HTML 추출 적용")
    print("=" * 80)

    # 생성기 초기화
    generator = FenokReportGenerator()
    batch_manager = ReportBatchManager(generator.driver)

    # 리포트 설정 로드
    with open('six_reports_config.json', 'r', encoding='utf-8') as f:
        six_reports_config = json.load(f)

    # 결과 추적
    results = {
        "total": len(six_reports_config),
        "generated": 0,
        "extracted": 0,
        "failed": 0,
        "reports": []
    }

    try:
        # 1. 로그인
        print("\n[Phase 1] TerminalX 로그인...")
        generator._login_terminalx()
        print("✅ 로그인 성공")

        # 날짜 설정
        today = datetime.now()
        report_date_str = today.strftime('%Y%m%d')
        ref_date_start = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        ref_date_end = today.strftime('%Y-%m-%d')

        # 2. 6개 리포트 생성 요청
        print("\n[Phase 2] 6개 리포트 생성 요청...")
        print("-" * 60)

        for idx, config in enumerate(six_reports_config, 1):
            print(f"\n[{idx}/6] {config['name']} 생성 요청...")

            report = Report(
                part_type="custom",
                title=config["name"]
            )

            # 리포트 생성 요청 (4개 인자만 사용)
            success = generator.generate_report_html(
                report,
                report_date_str,
                ref_date_start,
                ref_date_end
            )

            if success:
                batch_manager.reports.append(report)
                print(f"  ✅ 생성 요청 성공 - URL: {report.url}")
                results["reports"].append({
                    "name": config["name"],
                    "url": report.url,
                    "title": report.title,
                    "status": "REQUESTED"
                })
            else:
                print(f"  ❌ 생성 요청 실패")
                results["failed"] += 1

            # 다음 요청까지 약간 대기
            time.sleep(5)

        print(f"\n요청 완료: {len(batch_manager.reports)}/{results['total']} 리포트")

        # 3. Archive 모니터링
        print("\n[Phase 3] Archive 모니터링 (최대 20분)...")
        print("-" * 60)

        monitor_success = batch_manager.monitor_and_retry(
            timeout=1200,  # 20분
            initial_interval=30  # 30초마다 체크
        )

        # 생성 완료된 리포트 카운트
        for report in batch_manager.reports:
            if report.status == "GENERATED":
                results["generated"] += 1
                # results 업데이트
                for r in results["reports"]:
                    if r["url"] == report.url:
                        r["status"] = "GENERATED"
                        break

        print(f"\n생성 완료: {results['generated']}/{results['total']} 리포트")

        # 4. HTML 추출 (개선된 폴링 방식)
        print("\n[Phase 4] HTML 추출 (개선된 폴링 방식)...")
        print("-" * 60)

        for report in batch_manager.reports:
            if report.status == "GENERATED":
                print(f"\n[추출] {report.title}")
                output_path = f"generated_html/{report_date_str}_{report.title.replace(' ', '_')}.html"

                extract_success = generator.extract_and_validate_html(report, output_path)

                if extract_success:
                    results["extracted"] += 1
                    # 파일 검증
                    with open(output_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                        file_size = len(html_content)
                        has_markdown = 'markdown-body' in html_content
                        has_supersearch = 'supersearchx-body' in html_content

                    print(f"  ✅ 추출 성공")
                    print(f"     - 파일: {output_path}")
                    print(f"     - 크기: {file_size:,} bytes")
                    print(f"     - markdown-body: {'✅' if has_markdown else '❌'}")
                    print(f"     - supersearchx-body: {'✅' if has_supersearch else '❌'}")

                    # results 업데이트
                    for r in results["reports"]:
                        if r["url"] == report.url:
                            r["status"] = "EXTRACTED"
                            r["file_size"] = file_size
                            r["file_path"] = output_path
                            break
                else:
                    print(f"  ❌ 추출 실패")

        # 5. 최종 결과
        print("\n" + "=" * 80)
        print(" 테스트 결과 요약")
        print("=" * 80)

        print(f"""
📊 전체 통계:
  - 총 리포트: {results['total']}개
  - 생성 성공: {results['generated']}개 ({results['generated']/results['total']*100:.1f}%)
  - 추출 성공: {results['extracted']}개 ({results['extracted']/results['total']*100:.1f}%)
  - 실패: {results['failed']}개
""")

        print("📑 개별 리포트 상태:")
        for r in results["reports"]:
            status_icon = "✅" if r["status"] == "EXTRACTED" else "🔄" if r["status"] == "GENERATED" else "❌"
            print(f"  {status_icon} {r['name']}: {r['status']}")
            if r.get("file_size"):
                print(f"     └─ {r['file_size']:,} bytes")

        # 성공 판단
        success_rate = results["extracted"] / results["total"] * 100
        overall_success = success_rate >= 80  # 80% 이상 성공

        print(f"\n{'🎉 테스트 성공!' if overall_success else '⚠️ 부분 성공'}")
        print(f"성공률: {success_rate:.1f}%")

        # 결과 저장
        with open(f"test_results_{report_date_str}.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n결과 저장: test_results_{report_date_str}.json")

        return overall_success

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
    """메인 실행"""
    print("\n시작 시간:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    success = test_full_six_reports()

    print("\n종료 시간:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)