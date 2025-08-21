#!/usr/bin/env python3
"""
TerminalX 웹사이트 완전 탐구 및 분석 도구
- 모든 페이지 자동 탐색
- 요소 및 구조 분석
- 워크플로우 매핑
- 상세 문서화
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

class TerminalXExplorer:
    """TerminalX 웹사이트 완전 탐구 클래스"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.analysis_dir = self.project_dir / "terminalx_analysis"
        self.analysis_dir.mkdir(exist_ok=True)
        
        # 브라우저 컨트롤러 인스턴스
        self.browser = bc.BrowserController()
        
        # 탐구 결과 저장
        self.site_map = {}
        self.page_analysis = {}
        self.discovered_urls = set()
        self.visited_pages = set()
        
        self._setup_logging()
    
    def _setup_logging(self):
        """로깅 설정"""
        log_file = self.analysis_dir / f"exploration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def start_exploration(self):
        """탐구 시작"""
        logger.info("🚀 TerminalX 웹사이트 완전 탐구 시작!")
        
        # 브라우저 시작 및 로그인
        if not self.browser.start_browser():
            logger.error("❌ 브라우저 시작 실패")
            return False
        
        if not self.browser.login_terminalx():
            logger.error("❌ TerminalX 로그인 실패")
            return False
        
        logger.info("✅ 탐구 준비 완료!")
        return True
    
    def discover_all_links(self, base_url="https://theterminalx.com"):
        """모든 링크 발견"""
        logger.info(f"🔍 {base_url}에서 모든 링크 발견 중...")
        
        try:
            # Selenium WebDriver를 직접 사용하여 링크 찾기
            links = self.browser.driver.find_elements(By.XPATH, '//a[@href]')
            
            discovered_count = 0
            for link in links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    
                    if href and href.startswith(base_url):
                        if href not in self.discovered_urls:
                            self.discovered_urls.add(href)
                            discovered_count += 1
                            logger.info(f"  📌 발견: {href} ({text})")
                
                except Exception as e:
                    continue
            
            logger.info(f"✅ 총 {discovered_count}개 새로운 링크 발견")
            return list(self.discovered_urls)
            
        except Exception as e:
            logger.error(f"링크 발견 실패: {e}")
            return []
    
    def analyze_page_structure(self, url):
        """페이지 구조 분석"""
        logger.info(f"🔬 페이지 구조 분석: {url}")
        
        try:
            # 페이지로 이동
            self.browser.navigate_to(url)
            time.sleep(3)
            
            page_info = {
                "url": url,
                "title": self.browser.driver.title,
                "timestamp": datetime.now().isoformat(),
                "elements": {},
                "navigation": [],
                "forms": [],
                "buttons": [],
                "inputs": [],
                "links": []
            }
            
            # 네비게이션 요소 분석
            nav_elements = self.browser.driver.find_elements(By.XPATH, '//nav//a | //header//a | //menu//a')
            for nav in nav_elements:
                try:
                    nav_info = {
                        "text": nav.text.strip(),
                        "href": nav.get_attribute('href'),
                        "class": nav.get_attribute('class')
                    }
                    page_info["navigation"].append(nav_info)
                except:
                    continue
            
            # 폼 요소 분석
            forms = self.browser.driver.find_elements(By.XPATH, '//form')
            for form in forms:
                try:
                    form_info = {
                        "action": form.get_attribute('action'),
                        "method": form.get_attribute('method'),
                        "class": form.get_attribute('class'),
                        "inputs": []
                    }
                    
                    # 폼 내 입력 요소들
                    inputs = form.find_elements(By.XPATH, './/input | .//textarea | .//select')
                    for inp in inputs:
                        inp_info = {
                            "type": inp.get_attribute('type'),
                            "name": inp.get_attribute('name'),
                            "placeholder": inp.get_attribute('placeholder'),
                            "required": inp.get_attribute('required')
                        }
                        form_info["inputs"].append(inp_info)
                    
                    page_info["forms"].append(form_info)
                except:
                    continue
            
            # 버튼 분석
            buttons = self.browser.driver.find_elements(By.XPATH, '//button | //input[@type="button"] | //input[@type="submit"]')
            for btn in buttons:
                try:
                    btn_info = {
                        "text": btn.text.strip(),
                        "type": btn.get_attribute('type'),
                        "class": btn.get_attribute('class'),
                        "onclick": btn.get_attribute('onclick')
                    }
                    page_info["buttons"].append(btn_info)
                except:
                    continue
            
            # 주요 콘텐츠 영역 분석
            content_areas = self.browser.driver.find_elements(By.XPATH, '//main | //article | //section | //div[contains(@class, "content")]')
            page_info["content_areas"] = len(content_areas)
            
            # 테이블 분석 (특히 아카이브 페이지용)
            tables = self.browser.driver.find_elements(By.XPATH, '//table')
            table_info = []
            for table in tables:
                try:
                    rows = table.find_elements(By.XPATH, './/tr')
                    headers = table.find_elements(By.XPATH, './/th')
                    
                    table_data = {
                        "rows": len(rows),
                        "columns": len(headers),
                        "headers": [h.text.strip() for h in headers]
                    }
                    table_info.append(table_data)
                except:
                    continue
            
            page_info["tables"] = table_info
            
            self.page_analysis[url] = page_info
            self.visited_pages.add(url)
            
            logger.info(f"✅ 페이지 분석 완료: {page_info['title']}")
            return page_info
            
        except Exception as e:
            logger.error(f"페이지 분석 실패: {e}")
            return None
    
    def explore_all_pages(self):
        """모든 페이지 탐구"""
        logger.info("🌐 전체 페이지 탐구 시작!")
        
        # 시작 페이지들
        start_pages = [
            "https://theterminalx.com/agent/enterprise",
            "https://theterminalx.com/agent/archive",
            "https://theterminalx.com/agent/dashboard",
            "https://theterminalx.com/",
        ]
        
        # 각 시작 페이지에서 링크 발견
        for page in start_pages:
            try:
                self.browser.navigate_to(page)
                time.sleep(2)
                self.discover_all_links()
            except Exception as e:
                logger.error(f"페이지 {page} 탐구 실패: {e}")
                continue
        
        # 발견된 모든 페이지 분석
        total_pages = len(self.discovered_urls)
        logger.info(f"📊 총 {total_pages}개 페이지 분석 시작")
        
        for i, url in enumerate(self.discovered_urls, 1):
            if url not in self.visited_pages:
                logger.info(f"🔍 진행률: {i}/{total_pages} - {url}")
                self.analyze_page_structure(url)
                time.sleep(1)  # 서버 부하 방지
        
        logger.info("✅ 전체 페이지 탐구 완료!")
    
    def generate_site_map(self):
        """사이트 맵 생성"""
        logger.info("🗺️ 사이트 맵 생성 중...")
        
        self.site_map = {
            "discovery_time": datetime.now().isoformat(),
            "total_pages": len(self.visited_pages),
            "total_discovered": len(self.discovered_urls),
            "pages": {}
        }
        
        # 페이지 분류
        for url, analysis in self.page_analysis.items():
            page_type = self._classify_page(url, analysis)
            
            if page_type not in self.site_map["pages"]:
                self.site_map["pages"][page_type] = []
            
            self.site_map["pages"][page_type].append({
                "url": url,
                "title": analysis.get("title", ""),
                "navigation_count": len(analysis.get("navigation", [])),
                "forms_count": len(analysis.get("forms", [])),
                "buttons_count": len(analysis.get("buttons", [])),
                "tables_count": len(analysis.get("tables", []))
            })
        
        return self.site_map
    
    def _classify_page(self, url, analysis):
        """페이지 유형 분류"""
        if "enterprise" in url:
            return "메인/엔터프라이즈"
        elif "archive" in url:
            return "아카이브"
        elif "dashboard" in url:
            return "대시보드"
        elif "login" in url or "auth" in url:
            return "인증"
        elif "api" in url:
            return "API"
        else:
            return "기타"
    
    def save_analysis_results(self):
        """분석 결과 저장"""
        logger.info("💾 분석 결과 저장 중...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 사이트 맵 저장
        sitemap_file = self.analysis_dir / f"sitemap_{timestamp}.json"
        with open(sitemap_file, 'w', encoding='utf-8') as f:
            json.dump(self.site_map, f, indent=2, ensure_ascii=False)
        
        # 상세 분석 저장
        analysis_file = self.analysis_dir / f"detailed_analysis_{timestamp}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(self.page_analysis, f, indent=2, ensure_ascii=False)
        
        # 요약 보고서 생성
        self._generate_summary_report(timestamp)
        
        logger.info(f"✅ 분석 결과 저장 완료: {self.analysis_dir}")
        
        return {
            "sitemap": sitemap_file,
            "analysis": analysis_file,
            "summary": self.analysis_dir / f"summary_report_{timestamp}.md"
        }
    
    def _generate_summary_report(self, timestamp):
        """요약 보고서 생성"""
        report_file = self.analysis_dir / f"summary_report_{timestamp}.md"
        
        report_content = f"""# TerminalX 웹사이트 완전 분석 보고서

**분석 일시:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**분석자:** Claude (AI Agent)

## 📊 전체 통계

- **발견된 총 URL 수:** {len(self.discovered_urls)}
- **분석 완료된 페이지 수:** {len(self.visited_pages)}
- **페이지 유형별 분류:**

"""
        
        # 페이지 유형별 통계
        for page_type, pages in self.site_map.get("pages", {}).items():
            report_content += f"  - **{page_type}:** {len(pages)}개\n"
        
        report_content += f"""

## 🗺️ 사이트 구조 분석

### 주요 발견사항
"""
        
        # 각 페이지 유형별 상세 분석
        for page_type, pages in self.site_map.get("pages", {}).items():
            report_content += f"\n#### {page_type} 페이지들\n"
            for page in pages:
                report_content += f"- [{page['title']}]({page['url']})\n"
                report_content += f"  - 네비게이션: {page['navigation_count']}개\n"
                report_content += f"  - 폼: {page['forms_count']}개\n"
                report_content += f"  - 버튼: {page['buttons_count']}개\n"
                report_content += f"  - 테이블: {page['tables_count']}개\n"
        
        report_content += f"""

## 🔍 상세 분석 결과

각 페이지의 상세 분석 결과는 `detailed_analysis_{timestamp}.json` 파일을 참조하세요.

## 🎯 권장사항

1. **가장 활용도가 높은 페이지:** [자동 분석 결과]
2. **개선이 필요한 영역:** [자동 분석 결과]
3. **자동화 가능한 워크플로우:** [자동 분석 결과]

---
*이 보고서는 Claude AI Agent가 자동으로 생성했습니다.*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
    
    def close(self):
        """탐구 종료"""
        if self.browser.driver:
            self.browser.close_browser()
        logger.info("🏁 TerminalX 탐구 완료!")

# CLI 인터페이스
if __name__ == "__main__":
    explorer = TerminalXExplorer()
    
    try:
        # 탐구 시작
        if explorer.start_exploration():
            # 전체 페이지 탐구
            explorer.explore_all_pages()
            
            # 사이트 맵 생성
            sitemap = explorer.generate_site_map()
            
            # 결과 저장
            results = explorer.save_analysis_results()
            
            print("\n🎉 TerminalX 완전 탐구 성공!")
            print(f"📁 결과 저장 위치: {explorer.analysis_dir}")
            print(f"📊 분석된 페이지 수: {len(explorer.visited_pages)}")
            print(f"🔗 발견된 URL 수: {len(explorer.discovered_urls)}")
            
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 탐구가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 탐구 중 오류 발생: {e}")
    finally:
        explorer.close()