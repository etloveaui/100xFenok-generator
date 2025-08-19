#!/usr/bin/env python3
"""
100xFenok 전체 파이프라인 통합
- TerminalX 자동화 + JSON 통합 + HTML 생성 + 검증
- 모든 단계를 하나의 파이프라인으로 연결
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import time

# 로컬 모듈 임포트
from enhanced_automation import FenokAutomationEngine
from data_validator import FinancialDataValidator

# 기존 TerminalX 자동화 임포트 시도
try:
    from main_generator import FenokReportGenerator
    TERMINALX_AVAILABLE = True
except ImportError as e:
    TERMINALX_AVAILABLE = False
    logging.warning(f"TerminalX 자동화 모듈 로드 실패: {e}")

logger = logging.getLogger(__name__)

class FullPipelineManager:
    """완전 파이프라인 관리자"""
    
    def __init__(self):
        self.automation_engine = FenokAutomationEngine()
        self.validator = FinancialDataValidator()
        self.project_dir = Path(__file__).parent
        
        # 로그 설정
        self._setup_logging()
        
    def _setup_logging(self):
        """로깅 시스템 설정"""
        log_file = self.project_dir / "pipeline.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
    def run_complete_pipeline(self, target_date: Optional[str] = None, 
                            skip_terminalx: bool = False) -> Dict[str, Any]:
        """완전한 파이프라인 실행"""
        
        if not target_date:
            target_date = datetime.now().strftime("%Y-%m-%d")
            
        pipeline_result = {
            'success': False,
            'target_date': target_date,
            'stages_completed': [],
            'stages_failed': [],
            'output_files': [],
            'validation_results': {},
            'execution_time': 0,
            'errors': []
        }
        
        start_time = time.time()
        
        try:
            logger.info(f"🚀 100xFenok 완전 파이프라인 시작 - {target_date}")
            
            # Stage 1: TerminalX 데이터 수집
            if not skip_terminalx and TERMINALX_AVAILABLE:
                stage1_success = self._execute_terminalx_collection(target_date)
                if stage1_success:
                    pipeline_result['stages_completed'].append('terminalx_collection')
                    logger.info("✅ Stage 1: TerminalX 데이터 수집 완료")
                else:
                    pipeline_result['stages_failed'].append('terminalx_collection')
                    logger.error("❌ Stage 1: TerminalX 데이터 수집 실패")
            else:
                logger.info("⏭️ Stage 1: TerminalX 자동화 건너뛰기")
                pipeline_result['stages_completed'].append('terminalx_collection')
                
            # Stage 2: HTML → JSON 변환
            stage2_success = self._execute_html_to_json_conversion(target_date)
            if stage2_success:
                pipeline_result['stages_completed'].append('html_to_json')
                logger.info("✅ Stage 2: HTML → JSON 변환 완료")
            else:
                pipeline_result['stages_failed'].append('html_to_json')
                logger.error("❌ Stage 2: HTML → JSON 변환 실패")
                
            # Stage 3: JSON 통합 및 검증
            stage3_result = self._execute_json_integration(target_date)
            if stage3_result['success']:
                pipeline_result['stages_completed'].append('json_integration')
                pipeline_result['validation_results'] = stage3_result['validation']
                logger.info("✅ Stage 3: JSON 통합 및 검증 완료")
            else:
                pipeline_result['stages_failed'].append('json_integration')
                logger.error("❌ Stage 3: JSON 통합 실패")
                
            # Stage 4: 최종 HTML 생성
            stage4_result = self._execute_final_html_generation(target_date, stage3_result.get('data'))
            if stage4_result['success']:
                pipeline_result['stages_completed'].append('html_generation')
                pipeline_result['output_files'].append(stage4_result['output_file'])
                logger.info(f"✅ Stage 4: HTML 생성 완료 - {stage4_result['output_file']}")
            else:
                pipeline_result['stages_failed'].append('html_generation')
                logger.error("❌ Stage 4: HTML 생성 실패")
                
            # Stage 5: 품질 검증 및 후처리
            stage5_success = self._execute_quality_check(pipeline_result['output_files'])
            if stage5_success:
                pipeline_result['stages_completed'].append('quality_check')
                logger.info("✅ Stage 5: 품질 검증 완료")
            else:
                pipeline_result['stages_failed'].append('quality_check')
                logger.warning("⚠️ Stage 5: 품질 검증에서 문제 발견")
                
            # 전체 성공 여부 판단
            pipeline_result['success'] = len(pipeline_result['stages_failed']) == 0
            
        except Exception as e:
            logger.error(f"파이프라인 실행 중 치명적 오류: {e}")
            pipeline_result['errors'].append(str(e))
            
        finally:
            pipeline_result['execution_time'] = time.time() - start_time
            logger.info(f"⏱️ 총 실행 시간: {pipeline_result['execution_time']:.2f}초")
            
        return pipeline_result
    
    def _execute_terminalx_collection(self, target_date: str) -> bool:
        """Stage 1: TerminalX 데이터 수집"""
        try:
            # 기존 TerminalX 자동화 실행
            generator = FenokReportGenerator()
            
            # 날짜별 리포트 생성 (Part1, Part2 각각 3개씩)
            reports_generated = 0
            
            for part in ['part1', 'part2']:
                for i in range(3):
                    try:
                        # 리포트 생성 시도
                        success = generator.generate_daily_report(target_date, part, i+1)
                        if success:
                            reports_generated += 1
                            logger.info(f"✓ {part} 리포트 {i+1} 생성 완료")
                        else:
                            logger.warning(f"⚠ {part} 리포트 {i+1} 생성 실패")
                            
                    except Exception as e:
                        logger.error(f"❌ {part} 리포트 {i+1} 생성 중 오류: {e}")
                        
            # 추가 6개 프롬프트 리포트 생성
            additional_reports = generator.generate_additional_reports(target_date)
            reports_generated += additional_reports
            
            logger.info(f"📊 총 {reports_generated}개 리포트 생성 완료")
            return reports_generated > 0
            
        except Exception as e:
            logger.error(f"TerminalX 데이터 수집 중 오류: {e}")
            return False
    
    def _execute_html_to_json_conversion(self, target_date: str) -> bool:
        """Stage 2: HTML → JSON 변환"""
        try:
            from converters.html_converter import HTMLToJSONConverter
            
            converter = HTMLToJSONConverter()
            conversion_count = 0
            
            # HTML 파일들을 찾아서 변환
            html_dirs = [
                self.automation_engine.communication_dir / "002_terminalx",
                self.automation_engine.communication_dir / "003_terminalx"
            ]
            
            for html_dir in html_dirs:
                if html_dir.exists():
                    for html_file in html_dir.glob("*.html"):
                        try:
                            json_output_path = self.automation_engine.communication_dir / "004_Lexi_Convert" / f"{html_file.stem}.json"
                            success = converter.convert_html_to_json(html_file, json_output_path)
                            if success:
                                conversion_count += 1
                                logger.info(f"✓ {html_file.name} → JSON 변환 완료")
                        except Exception as e:
                            logger.error(f"❌ {html_file.name} 변환 실패: {e}")
            
            logger.info(f"📄 총 {conversion_count}개 HTML → JSON 변환 완료")
            return conversion_count > 0
            
        except ImportError:
            # Python_Lexi_Convert를 사용할 수 없는 경우 기본 변환기 사용
            logger.info("기본 HTML → JSON 변환기 사용")
            return self._basic_html_to_json_conversion(target_date)
        except Exception as e:
            logger.error(f"HTML → JSON 변환 중 오류: {e}")
            return False
    
    def _basic_html_to_json_conversion(self, target_date: str) -> bool:
        """기본 HTML → JSON 변환 (Python_Lexi_Convert 대체)"""
        try:
            from bs4 import BeautifulSoup
            import html2text
            
            conversion_count = 0
            h = html2text.HTML2Text()
            h.ignore_links = True
            
            html_dirs = [
                self.automation_engine.communication_dir / "002_terminalx",
                self.automation_engine.communication_dir / "003_terminalx"
            ]
            
            for html_dir in html_dirs:
                if html_dir.exists():
                    for html_file in html_dir.glob("*.html"):
                        try:
                            with open(html_file, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            
                            # Beautiful Soup으로 파싱
                            soup = BeautifulSoup(html_content, 'html.parser')
                            
                            # 기본적인 JSON 구조 생성
                            json_data = {
                                "source_file": html_file.name,
                                "conversion_date": datetime.now().isoformat(),
                                "content": []
                            }
                            
                            # 테이블 추출
                            for table in soup.find_all('table'):
                                table_data = self._extract_table_data(table)
                                if table_data:
                                    json_data["content"].append(table_data)
                            
                            # 텍스트 내용 추출
                            text_content = h.handle(html_content)
                            if text_content.strip():
                                json_data["content"].append({
                                    "type": "text",
                                    "content": text_content.strip()
                                })
                            
                            # JSON 파일 저장
                            json_output_path = self.automation_engine.communication_dir / "004_Lexi_Convert" / f"{html_file.stem}.json"
                            with open(json_output_path, 'w', encoding='utf-8') as f:
                                json.dump(json_data, f, indent=2, ensure_ascii=False)
                            
                            conversion_count += 1
                            logger.info(f"✓ {html_file.name} → JSON 변환 완료 (기본 변환기)")
                            
                        except Exception as e:
                            logger.error(f"❌ {html_file.name} 기본 변환 실패: {e}")
            
            return conversion_count > 0
            
        except Exception as e:
            logger.error(f"기본 HTML → JSON 변환 중 오류: {e}")
            return False
    
    def _extract_table_data(self, table_element) -> Optional[Dict[str, Any]]:
        """HTML 테이블에서 데이터 추출"""
        try:
            rows = table_element.find_all('tr')
            if not rows:
                return None
                
            table_data = {
                "type": "table",
                "headers": [],
                "data": []
            }
            
            # 헤더 추출
            header_row = rows[0]
            headers = header_row.find_all(['th', 'td'])
            table_data["headers"] = [header.get_text().strip() for header in headers]
            
            # 데이터 행 추출
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text().strip() for cell in cells]
                if any(row_data):  # 빈 행이 아닌 경우만 추가
                    table_data["data"].append(row_data)
            
            return table_data if table_data["data"] else None
            
        except Exception as e:
            logger.error(f"테이블 데이터 추출 실패: {e}")
            return None
    
    def _execute_json_integration(self, target_date: str) -> Dict[str, Any]:
        """Stage 3: JSON 통합 및 검증"""
        result = {'success': False, 'data': {}, 'validation': {}}
        
        try:
            # JSON 파일들 수집
            json_dir = self.automation_engine.communication_dir / "004_Lexi_Convert"
            part1_files = list(json_dir.glob("part1_*.json"))
            part2_files = list(json_dir.glob("part2_*.json"))
            html_files = list(self.automation_engine.communication_dir.glob("003_terminalx/*.html"))
            
            # 로컬 LLM으로 JSON 통합
            integrated_data = self.automation_engine.integrate_json_data(
                part1_files, part2_files, html_files
            )
            
            if integrated_data:
                # 데이터 검증
                validation_results = self.validator.validate_json_data(integrated_data)
                
                result['success'] = True
                result['data'] = integrated_data
                result['validation'] = validation_results
                
                # 검증 결과 로깅
                if validation_results['errors']:
                    logger.warning(f"⚠️ 검증에서 {len(validation_results['errors'])}개 오류 발견")
                    for error in validation_results['errors']:
                        logger.warning(f"  - {error}")
                
                logger.info(f"📊 품질 점수: {validation_results.get('quality_score', 0)}/100")
                
        except Exception as e:
            logger.error(f"JSON 통합 중 오류: {e}")
            result['success'] = False
            
        return result
    
    def _execute_final_html_generation(self, target_date: str, integrated_data: Optional[Dict]) -> Dict[str, Any]:
        """Stage 4: 최종 HTML 생성"""
        result = {'success': False, 'output_file': None}
        
        try:
            if not integrated_data:
                logger.error("통합된 JSON 데이터가 없음")
                return result
                
            # HTML 생성
            final_html = self.automation_engine.generate_final_html(
                integrated_data.get('part1', {}),
                integrated_data.get('part2', {})
            )
            
            if final_html:
                # 출력 파일 경로
                date_str = target_date.replace('-', '')
                output_file = self.automation_engine.output_dir / f"{date_str}_100x-daily-wrap.html"
                
                # 파일 저장
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(final_html)
                
                result['success'] = True
                result['output_file'] = str(output_file)
                
                logger.info(f"📄 최종 HTML 생성: {output_file}")
                
        except Exception as e:
            logger.error(f"HTML 생성 중 오류: {e}")
            
        return result
    
    def _execute_quality_check(self, output_files: List[str]) -> bool:
        """Stage 5: 품질 검증"""
        try:
            for output_file in output_files:
                if os.path.exists(output_file):
                    # 파일 크기 확인
                    file_size = os.path.getsize(output_file)
                    if file_size < 1000:  # 1KB 미만
                        logger.warning(f"⚠️ 출력 파일이 너무 작음: {output_file} ({file_size} bytes)")
                        return False
                    
                    # HTML 유효성 기본 확인
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    if not content.strip().startswith('<!DOCTYPE html>'):
                        logger.warning(f"⚠️ HTML 문서 타입이 올바르지 않음: {output_file}")
                        return False
                        
                    if '<title>' not in content:
                        logger.warning(f"⚠️ HTML 제목이 없음: {output_file}")
                        return False
                        
                    logger.info(f"✓ 품질 검증 통과: {output_file}")
                    
            return True
            
        except Exception as e:
            logger.error(f"품질 검증 중 오류: {e}")
            return False

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="100xFenok 완전 파이프라인")
    parser.add_argument("--date", help="대상 날짜 (YYYY-MM-DD)")
    parser.add_argument("--skip-terminalx", action="store_true", help="TerminalX 자동화 건너뛰기")
    parser.add_argument("--test-run", action="store_true", help="테스트 실행 (기존 데이터 사용)")
    
    args = parser.parse_args()
    
    pipeline = FullPipelineManager()
    
    # 테스트 실행
    if args.test_run:
        args.skip_terminalx = True
        print("🧪 테스트 모드: 기존 데이터로 파이프라인 테스트")
    
    # 파이프라인 실행
    result = pipeline.run_complete_pipeline(
        target_date=args.date,
        skip_terminalx=args.skip_terminalx
    )
    
    # 결과 출력
    print("\n" + "="*60)
    print("📊 파이프라인 실행 결과")
    print("="*60)
    print(f"✅ 성공: {result['success']}")
    print(f"📅 대상 날짜: {result['target_date']}")
    print(f"⏱️ 실행 시간: {result['execution_time']:.2f}초")
    print(f"✓ 완료된 단계: {len(result['stages_completed'])}")
    print(f"❌ 실패한 단계: {len(result['stages_failed'])}")
    
    if result['output_files']:
        print(f"📄 생성된 파일:")
        for file_path in result['output_files']:
            print(f"  - {file_path}")
    
    if result['validation_results']:
        quality_score = result['validation_results'].get('quality_score', 0)
        print(f"🎯 품질 점수: {quality_score}/100")
    
    if result['errors']:
        print(f"⚠️ 오류:")
        for error in result['errors']:
            print(f"  - {error}")

if __name__ == "__main__":
    main()