#!/usr/bin/env python3
"""
TerminalX 기능 탐구 도구
- 일반 세션에서 보고서 산출
- 보고서 탭 다양한 기능 탐구
- Comps Analysis 등 고급 기능
- 메인/부차 리포트 추출 방법
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import browser_controller as bc

logger = logging.getLogger(__name__)

class TerminalXFunctionExplorer:
    """TerminalX 기능 완전 탐구 클래스"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.function_analysis_dir = self.project_dir / "terminalx_function_analysis"
        self.function_analysis_dir.mkdir(exist_ok=True)
        
        # 브라우저 컨트롤러 인스턴스
        self.browser = bc.BrowserController()
        
        # 기능 탐구 결과 저장
        self.session_workflows = {}
        self.report_capabilities = {}
        self.advanced_features = {}
        self.extraction_methods = {}
        
        self._setup_logging()
    
    def _setup_logging(self):
        """로깅 설정"""
        log_file = self.function_analysis_dir / f"function_exploration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def start_exploration(self):
        """기능 탐구 시작"""
        logger.info("🚀 TerminalX 기능 완전 탐구 시작!")
        
        # 브라우저 시작 및 로그인
        if not self.browser.start_browser():
            logger.error("❌ 브라우저 시작 실패")
            return False
        
        if not self.browser.login_terminalx():
            logger.error("❌ TerminalX 로그인 실패")
            return False
        
        logger.info("✅ 기능 탐구 준비 완료!")
        return True
    
    def explore_general_session_reports(self):
        """일반 세션에서 보고서 산출 방법 탐구"""
        logger.info("📋 일반 세션에서 보고서 산출 방법 탐구 시작")
        
        try:
            # 메인 엔터프라이즈 페이지로 이동
            self.browser.navigate_to("https://theterminalx.com/agent/enterprise")
            time.sleep(3)
            
            # 텍스트 입력 영역 찾기
            text_areas = self.browser.driver.find_elements(By.XPATH, '//textarea | //input[@type="text"] | //div[contains(@class, "input")] | //*[contains(@placeholder, "Ask")]')
            
            session_info = {
                "page_url": "https://theterminalx.com/agent/enterprise",
                "timestamp": datetime.now().isoformat(),
                "text_input_areas": [],
                "available_buttons": [],
                "session_workflow": []
            }
            
            # 입력 영역 분석
            for i, area in enumerate(text_areas):
                try:
                    area_info = {
                        "index": i,
                        "tag": area.tag_name,
                        "type": area.get_attribute('type'),
                        "placeholder": area.get_attribute('placeholder'),
                        "class": area.get_attribute('class'),
                        "value": area.get_attribute('value'),
                        "is_visible": area.is_displayed(),
                        "is_enabled": area.is_enabled()
                    }
                    session_info["text_input_areas"].append(area_info)
                    logger.info(f"  📝 입력 영역 {i}: {area_info['placeholder']} ({area_info['tag']})")
                except Exception as e:
                    continue
            
            # 사용 가능한 버튼들 분석
            buttons = self.browser.driver.find_elements(By.XPATH, '//button | //input[@type="submit"] | //input[@type="button"]')
            for i, button in enumerate(buttons):
                try:
                    btn_info = {
                        "index": i,
                        "text": button.text.strip(),
                        "type": button.get_attribute('type'),
                        "class": button.get_attribute('class'),
                        "is_visible": button.is_displayed(),
                        "is_enabled": button.is_enabled()
                    }
                    session_info["available_buttons"].append(btn_info)
                    if btn_info["text"]:
                        logger.info(f"  🔘 버튼 {i}: {btn_info['text']}")
                except Exception as e:
                    continue
            
            # 실제 쿼리 테스트 시도
            logger.info("🔍 실제 쿼리 테스트 시작")
            
            # 가장 적합한 입력 영역 찾기
            main_input = None
            for area_info in session_info["text_input_areas"]:
                if area_info["is_visible"] and area_info["is_enabled"]:
                    if "Ask" in str(area_info["placeholder"]) or "question" in str(area_info["placeholder"]).lower():
                        main_input = area_info
                        break
            
            if main_input:
                logger.info(f"📝 메인 입력 영역 발견: {main_input['placeholder']}")
                
                # 실제 쿼리 입력 시도
                test_queries = [
                    "Give me a market summary for today",
                    "What are the top gainers in the S&P 500?",
                    "Generate a report on AAPL stock performance"
                ]
                
                for query in test_queries:
                    try:
                        logger.info(f"🧪 테스트 쿼리: {query}")
                        
                        # 입력 영역 찾고 클릭
                        input_element = self.browser.driver.find_elements(By.XPATH, '//textarea | //input[@type="text"]')[main_input["index"]]
                        input_element.click()
                        time.sleep(1)
                        
                        # 기존 텍스트 클리어
                        input_element.clear()
                        time.sleep(1)
                        
                        # 쿼리 입력
                        input_element.send_keys(query)
                        time.sleep(2)
                        
                        # Enter 키 또는 제출 버튼 시도
                        input_element.send_keys(Keys.RETURN)
                        time.sleep(5)
                        
                        # 응답 확인
                        page_source = self.browser.driver.page_source
                        response_indicators = ["generating", "response", "result", "analysis"]
                        
                        response_detected = any(indicator in page_source.lower() for indicator in response_indicators)
                        
                        query_result = {
                            "query": query,
                            "timestamp": datetime.now().isoformat(),
                            "response_detected": response_detected,
                            "page_title": self.browser.driver.title,
                            "current_url": self.browser.driver.current_url
                        }
                        
                        session_info["session_workflow"].append(query_result)
                        logger.info(f"  ✅ 쿼리 실행 완료: 응답 감지 = {response_detected}")
                        
                        time.sleep(3)  # 다음 쿼리 전 대기
                        
                    except Exception as e:
                        logger.error(f"  ❌ 쿼리 실행 실패: {e}")
                        continue
            
            self.session_workflows["general_session"] = session_info
            logger.info("✅ 일반 세션 보고서 산출 방법 탐구 완료")
            return session_info
            
        except Exception as e:
            logger.error(f"일반 세션 탐구 실패: {e}")
            return None
    
    def explore_report_tab_features(self):
        """보고서 탭에서 다양한 보고서 작성법 탐구"""
        logger.info("📊 보고서 탭 기능 탐구 시작")
        
        try:
            # 보고서 관련 페이지들 순회
            report_pages = [
                "https://theterminalx.com/agent/enterprise/live-research",
                "https://theterminalx.com/agent/enterprise/admin",
                "https://theterminalx.com/agent/enterprise/watchlist"
            ]
            
            report_analysis = {
                "timestamp": datetime.now().isoformat(),
                "pages_analyzed": [],
                "report_types_found": [],
                "creation_workflows": []
            }
            
            for page_url in report_pages:
                logger.info(f"🔍 보고서 페이지 분석: {page_url}")
                
                self.browser.navigate_to(page_url)
                time.sleep(3)
                
                page_info = {
                    "url": page_url,
                    "title": self.browser.driver.title,
                    "report_elements": [],
                    "creation_buttons": [],
                    "templates": []
                }
                
                # 보고서 관련 요소들 찾기
                report_keywords = ["report", "analysis", "research", "generate", "create", "template"]
                
                for keyword in report_keywords:
                    elements = self.browser.driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}') or contains(@class, '{keyword}') or contains(@placeholder, '{keyword}')]")
                    
                    for element in elements:
                        try:
                            element_info = {
                                "keyword": keyword,
                                "tag": element.tag_name,
                                "text": element.text.strip()[:100],
                                "class": element.get_attribute('class'),
                                "type": element.get_attribute('type'),
                                "is_clickable": element.is_enabled() and element.is_displayed()
                            }
                            page_info["report_elements"].append(element_info)
                        except:
                            continue
                
                # 생성/작성 버튼들 찾기
                creation_buttons = self.browser.driver.find_elements(By.XPATH, '//button[contains(text(), "Generate") or contains(text(), "Create") or contains(text(), "New") or contains(text(), "Add")]')
                
                for button in creation_buttons:
                    try:
                        btn_info = {
                            "text": button.text.strip(),
                            "class": button.get_attribute('class'),
                            "is_clickable": button.is_enabled() and button.is_displayed()
                        }
                        page_info["creation_buttons"].append(btn_info)
                        logger.info(f"  🔘 생성 버튼 발견: {btn_info['text']}")
                    except:
                        continue
                
                report_analysis["pages_analyzed"].append(page_info)
            
            self.report_capabilities = report_analysis
            logger.info("✅ 보고서 탭 기능 탐구 완료")
            return report_analysis
            
        except Exception as e:
            logger.error(f"보고서 탭 탐구 실패: {e}")
            return None
    
    def explore_advanced_features(self):
        """Comps Analysis 및 고급 기능 탐구"""
        logger.info("🔬 고급 기능 탐구 시작")
        
        try:
            advanced_analysis = {
                "timestamp": datetime.now().isoformat(),
                "features_found": [],
                "navigation_paths": [],
                "functionality_tests": []
            }
            
            # 고급 기능 키워드들
            advanced_keywords = [
                "comps", "comparison", "analysis", "valuation", 
                "DCF", "model", "financial", "screening",
                "portfolio", "watchlist", "alerts"
            ]
            
            # 현재 페이지에서 고급 기능 찾기
            current_url = self.browser.driver.current_url
            logger.info(f"🔍 현재 페이지에서 고급 기능 탐색: {current_url}")
            
            for keyword in advanced_keywords:
                elements = self.browser.driver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]")
                
                for element in elements:
                    try:
                        feature_info = {
                            "keyword": keyword,
                            "text": element.text.strip()[:200],
                            "tag": element.tag_name,
                            "class": element.get_attribute('class'),
                            "href": element.get_attribute('href'),
                            "is_interactive": element.is_enabled() and element.is_displayed()
                        }
                        
                        if feature_info["text"]:
                            advanced_analysis["features_found"].append(feature_info)
                            logger.info(f"  🎯 고급 기능 발견: {keyword} - {feature_info['text'][:50]}...")
                    except:
                        continue
            
            # 특별한 고급 기능 페이지들 시도
            advanced_urls = [
                "/agent/enterprise/analysis",
                "/agent/enterprise/models", 
                "/agent/enterprise/comps",
                "/agent/enterprise/screening",
                "/agent/enterprise/portfolio"
            ]
            
            base_url = "https://theterminalx.com"
            for path in advanced_urls:
                try:
                    test_url = base_url + path
                    logger.info(f"🧪 고급 기능 URL 테스트: {test_url}")
                    
                    self.browser.navigate_to(test_url)
                    time.sleep(2)
                    
                    # 페이지가 로드되었는지 확인
                    if self.browser.driver.current_url == test_url:
                        page_title = self.browser.driver.title
                        logger.info(f"  ✅ 접근 성공: {page_title}")
                        
                        # 페이지 내용 간단 분석
                        content_elements = self.browser.driver.find_elements(By.XPATH, '//h1 | //h2 | //h3 | //button | //form')
                        content_summary = []
                        
                        for element in content_elements[:10]:  # 상위 10개만
                            try:
                                text = element.text.strip()
                                if text:
                                    content_summary.append(text[:100])
                            except:
                                continue
                        
                        nav_info = {
                            "url": test_url,
                            "title": page_title,
                            "accessible": True,
                            "content_preview": content_summary
                        }
                        advanced_analysis["navigation_paths"].append(nav_info)
                    else:
                        logger.info(f"  ❌ 접근 실패 또는 리다이렉트")
                        nav_info = {
                            "url": test_url,
                            "accessible": False,
                            "redirected_to": self.browser.driver.current_url
                        }
                        advanced_analysis["navigation_paths"].append(nav_info)
                        
                except Exception as e:
                    logger.error(f"  ❌ URL 테스트 오류: {e}")
                    continue
            
            self.advanced_features = advanced_analysis
            logger.info("✅ 고급 기능 탐구 완료")
            return advanced_analysis
            
        except Exception as e:
            logger.error(f"고급 기능 탐구 실패: {e}")
            return None
    
    def explore_report_extraction_methods(self):
        """메인/부차 리포트 추출 방법 파악"""
        logger.info("📄 리포트 추출 방법 탐구 시작")
        
        try:
            extraction_analysis = {
                "timestamp": datetime.now().isoformat(),
                "main_reports": [],
                "secondary_reports": [],
                "extraction_workflows": [],
                "download_methods": []
            }
            
            # 다양한 페이지에서 리포트 추출 방법 찾기
            pages_to_check = [
                "https://theterminalx.com/agent/enterprise",
                "https://theterminalx.com/agent/enterprise/live-research",
                "https://theterminalx.com/agent/enterprise/admin"
            ]
            
            for page_url in pages_to_check:
                logger.info(f"🔍 리포트 추출 방법 탐색: {page_url}")
                
                self.browser.navigate_to(page_url)
                time.sleep(3)
                
                # 다운로드/내보내기 관련 요소들 찾기
                download_keywords = ["download", "export", "save", "pdf", "csv", "excel", "share"]
                
                for keyword in download_keywords:
                    elements = self.browser.driver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}') or contains(@title, '{keyword}') or contains(@class, '{keyword}')]")
                    
                    for element in elements:
                        try:
                            download_info = {
                                "page": page_url,
                                "keyword": keyword,
                                "element_text": element.text.strip()[:100],
                                "element_tag": element.tag_name,
                                "element_class": element.get_attribute('class'),
                                "href": element.get_attribute('href'),
                                "onclick": element.get_attribute('onclick'),
                                "is_clickable": element.is_enabled() and element.is_displayed()
                            }
                            
                            if download_info["element_text"] or download_info["href"]:
                                extraction_analysis["download_methods"].append(download_info)
                                logger.info(f"  💾 추출 방법 발견: {keyword} - {download_info['element_text'][:30]}...")
                        except:
                            continue
                
                # 보고서 목록이나 테이블 찾기
                tables = self.browser.driver.find_elements(By.XPATH, '//table')
                for i, table in enumerate(tables):
                    try:
                        rows = table.find_elements(By.XPATH, './/tr')
                        if len(rows) > 1:  # 헤더 + 데이터가 있는 테이블
                            table_info = {
                                "page": page_url,
                                "table_index": i,
                                "row_count": len(rows),
                                "headers": [],
                                "sample_data": []
                            }
                            
                            # 헤더 추출
                            headers = table.find_elements(By.XPATH, './/th')
                            for header in headers:
                                table_info["headers"].append(header.text.strip())
                            
                            # 첫 번째 데이터 행 추출
                            if len(rows) > 1:
                                first_data_row = rows[1].find_elements(By.XPATH, './/td')
                                for cell in first_data_row:
                                    table_info["sample_data"].append(cell.text.strip()[:50])
                            
                            extraction_analysis["main_reports"].append(table_info)
                            logger.info(f"  📊 보고서 테이블 발견: {len(rows)}행, 헤더: {table_info['headers'][:3]}")
                    except:
                        continue
            
            self.extraction_methods = extraction_analysis
            logger.info("✅ 리포트 추출 방법 탐구 완료")
            return extraction_analysis
            
        except Exception as e:
            logger.error(f"리포트 추출 방법 탐구 실패: {e}")
            return None
    
    def save_function_analysis_results(self):
        """기능 분석 결과 저장"""
        logger.info("💾 기능 분석 결과 저장 중...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 전체 기능 분석 결과 통합
        complete_analysis = {
            "analysis_timestamp": datetime.now().isoformat(),
            "session_workflows": self.session_workflows,
            "report_capabilities": self.report_capabilities,
            "advanced_features": self.advanced_features,
            "extraction_methods": self.extraction_methods
        }
        
        # JSON 저장
        analysis_file = self.function_analysis_dir / f"terminalx_function_analysis_{timestamp}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(complete_analysis, f, indent=2, ensure_ascii=False)
        
        # 사용자 친화적 보고서 생성
        self._generate_function_report(timestamp, complete_analysis)
        
        logger.info(f"✅ 기능 분석 결과 저장 완료: {self.function_analysis_dir}")
        
        return {
            "analysis": analysis_file,
            "report": self.function_analysis_dir / f"terminalx_function_report_{timestamp}.md"
        }
    
    def _generate_function_report(self, timestamp, analysis_data):
        """사용자 친화적 기능 분석 보고서 생성"""
        report_file = self.function_analysis_dir / f"terminalx_function_report_{timestamp}.md"
        
        report_content = f"""# TerminalX 기능 완전 분석 보고서

**분석 일시:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**분석자:** Claude (AI Agent)

## 🎯 핵심 발견사항

### 1. 일반 세션에서 보고서 산출 방법

"""
        
        # 세션 워크플로우 분석
        session_data = analysis_data.get("session_workflows", {}).get("general_session", {})
        if session_data:
            report_content += f"""
#### 입력 영역 분석
- **총 입력 영역 발견:** {len(session_data.get('text_input_areas', []))}개
- **활성 버튼 수:** {len(session_data.get('available_buttons', []))}개

#### 테스트된 쿼리 결과
"""
            for workflow in session_data.get('session_workflow', []):
                status = "✅ 성공" if workflow.get('response_detected') else "❌ 실패"
                report_content += f"- {workflow.get('query', 'Unknown')}: {status}\n"
        
        # 보고서 기능 분석
        report_content += f"""

### 2. 보고서 탭 기능 분석

"""
        report_data = analysis_data.get("report_capabilities", {})
        if report_data:
            report_content += f"**분석된 페이지 수:** {len(report_data.get('pages_analyzed', []))}개\n\n"
            
            for page in report_data.get('pages_analyzed', []):
                report_content += f"""#### {page.get('url', 'Unknown')}
- 보고서 관련 요소: {len(page.get('report_elements', []))}개
- 생성 버튼: {len(page.get('creation_buttons', []))}개
"""
                for button in page.get('creation_buttons', []):
                    if button.get('text'):
                        report_content += f"  - {button['text']}\n"
        
        # 고급 기능 분석
        report_content += f"""

### 3. 고급 기능 분석

"""
        advanced_data = analysis_data.get("advanced_features", {})
        if advanced_data:
            report_content += f"**발견된 고급 기능:** {len(advanced_data.get('features_found', []))}개\n\n"
            
            feature_summary = {}
            for feature in advanced_data.get('features_found', []):
                keyword = feature.get('keyword', 'unknown')
                if keyword not in feature_summary:
                    feature_summary[keyword] = 0
                feature_summary[keyword] += 1
            
            for keyword, count in feature_summary.items():
                report_content += f"- **{keyword.upper()}**: {count}개 요소 발견\n"
            
            # 접근 가능한 고급 페이지
            accessible_pages = [nav for nav in advanced_data.get('navigation_paths', []) if nav.get('accessible')]
            if accessible_pages:
                report_content += f"\n#### 접근 가능한 고급 페이지\n"
                for page in accessible_pages:
                    report_content += f"- [{page.get('title', 'Unknown')}]({page.get('url')})\n"
        
        # 추출 방법 분석
        report_content += f"""

### 4. 리포트 추출 방법

"""
        extraction_data = analysis_data.get("extraction_methods", {})
        if extraction_data:
            report_content += f"**발견된 추출 방법:** {len(extraction_data.get('download_methods', []))}개\n"
            report_content += f"**메인 리포트 테이블:** {len(extraction_data.get('main_reports', []))}개\n\n"
            
            # 추출 방법별 요약
            method_summary = {}
            for method in extraction_data.get('download_methods', []):
                keyword = method.get('keyword', 'unknown')
                if keyword not in method_summary:
                    method_summary[keyword] = 0
                method_summary[keyword] += 1
            
            for method, count in method_summary.items():
                report_content += f"- **{method.upper()}**: {count}개 방법 발견\n"
        
        report_content += f"""

## 🚀 활용 가능한 워크플로우

### 자동화 가능한 작업들
1. **보고서 자동 생성**: 텍스트 입력 → 쿼리 실행 → 결과 추출
2. **데이터 일괄 다운로드**: 테이블 데이터 → 형식 선택 → 다운로드
3. **고급 분석 실행**: 특정 기능 → 파라미터 설정 → 분석 실행

### 권장 사항
- 가장 효과적인 입력 방법 활용
- 고급 기능들의 체계적 탐구
- 추출된 데이터의 자동 처리 파이프라인 구축

---
*이 보고서는 Claude AI Agent가 실제 기능 테스트를 통해 생성했습니다.*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
    
    def close(self):
        """탐구 종료"""
        if self.browser.driver:
            self.browser.close_browser()
        logger.info("🏁 TerminalX 기능 탐구 완료!")

# CLI 인터페이스
if __name__ == "__main__":
    explorer = TerminalXFunctionExplorer()
    
    try:
        # 기능 탐구 시작
        if explorer.start_exploration():
            
            # 1. 일반 세션에서 보고서 산출 방법 탐구
            logger.info("=" * 60)
            explorer.explore_general_session_reports()
            
            # 2. 보고서 탭에서 다양한 보고서 작성법 탐구
            logger.info("=" * 60)
            explorer.explore_report_tab_features()
            
            # 3. Comps Analysis 및 고급 기능 탐구
            logger.info("=" * 60)
            explorer.explore_advanced_features()
            
            # 4. 메인/부차 리포트 추출 방법 파악
            logger.info("=" * 60)
            explorer.explore_report_extraction_methods()
            
            # 결과 저장
            results = explorer.save_function_analysis_results()
            
            print("\n🎉 TerminalX 기능 완전 탐구 성공!")
            print(f"📁 결과 저장 위치: {explorer.function_analysis_dir}")
            print(f"📊 JSON 분석 파일: {results['analysis']}")
            print(f"📋 사용자 보고서: {results['report']}")
            
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 기능 탐구가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 기능 탐구 중 오류 발생: {e}")
    finally:
        explorer.close()