#!/usr/bin/env python3
"""
빠른 아카이브 확인 및 Generated 보고서 저장
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class QuickArchiveChecker:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.base_dir = self.project_dir.parent.parent
        self.communication_dir = self.base_dir / "communication" / "shared" / "100xfenok"
        self.secrets_file = self.base_dir / "secrets" / "my_sensitive_data.md"
        self.chromedriver_path = self.project_dir / "chromedriver.exe"
        
        self.driver = None
        self.username = None
        self.password = None
        
        self._setup_logging()
        self._load_credentials()
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        self.logger = logging.getLogger(__name__)
        
    def _load_credentials(self):
        try:
            with open(self.secrets_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "The TerminalX Credentials" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "The TerminalX Credentials" in line:
                        self.username = lines[i+1].split(':')[-1].strip().replace('`', '').replace('**', '')
                        self.password = lines[i+2].split(':')[-1].strip().replace('`', '').replace('**', '')
                        break
                        
            self.logger.info("TerminalX 자격증명 로드 완료")
            
        except Exception as e:
            self.logger.error(f"자격증명 로드 실패: {e}")
            
    def setup_browser(self):
        try:
            service = Service(executable_path=str(self.chromedriver_path))
            options = webdriver.ChromeOptions()
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--start-maximized')
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(60)
            
            self.logger.info("Chrome 브라우저 설정 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"Chrome 브라우저 설정 실패: {e}")
            return False
    
    def quick_login(self):
        try:
            self.logger.info("빠른 로그인 시작")
            
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(3)
            
            # 로그인 버튼 클릭
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in')]"))
            )
            login_button.click()
            time.sleep(2)
            
            # 로그인 폼 입력
            email_input = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter your email']"))
            )
            password_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Enter your password']")
            
            email_input.clear()
            email_input.send_keys(self.username)
            password_input.clear()
            password_input.send_keys(self.password)
            
            # 로그인 실행
            login_submit = self.driver.find_element(By.XPATH, "//button[contains(., 'Log In')]")
            login_submit.click()
            
            # 로그인 성공 확인
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Subscriptions')]"))
            )
            self.logger.info("로그인 성공!")
            
            return True
            
        except Exception as e:
            self.logger.error(f"로그인 실패: {e}")
            return False
    
    def check_archive_immediately(self):
        """즉시 아카이브 확인하여 Generated 보고서 저장"""
        try:
            self.logger.info("아카이브 페이지로 즉시 이동")
            
            # 아카이브 페이지로 이동
            archive_url = "https://theterminalx.com/agent/enterprise/report/archive"
            self.driver.get(archive_url)
            time.sleep(5)
            
            # 현재 상태 확인
            self.logger.info("보고서 목록 확인 중...")
            
            # Generated 보고서 찾기
            generated_reports = self._find_generated_reports()
            
            if generated_reports:
                self.logger.info(f"Generated 보고서 {len(generated_reports)}개 발견!")
                
                for i, report in enumerate(generated_reports, 1):
                    self.logger.info(f"보고서 {i}/{len(generated_reports)} 저장 중: {report['title']}")
                    
                    # 보고서 클릭하여 이동
                    self.driver.get(report['url'])
                    time.sleep(5)
                    
                    # HTML 추출
                    html_content = self._extract_html()
                    
                    if html_content:
                        # 파일 저장
                        filename = f"generated_report_{i:02d}.html"
                        output_file = self.communication_dir / "002_terminalx" / filename
                        
                        # 폴더 생성
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        
                        self.logger.info(f"저장 완료: {filename}")
                    
                    # 아카이브로 복귀
                    self.driver.get(archive_url)
                    time.sleep(3)
                
                self.logger.info(f"전체 {len(generated_reports)}개 보고서 저장 완료!")
                return True
                
            else:
                self.logger.warning("Generated 상태 보고서를 찾을 수 없음")
                
                # 현재 보고서 상태 출력
                self._print_current_status()
                return False
                
        except Exception as e:
            self.logger.error(f"아카이브 확인 실패: {e}")
            return False
    
    def _find_generated_reports(self):
        """Generated 상태인 보고서들 찾기"""
        try:
            generated_reports = []
            
            # 보고서 행들 찾기 (테이블 또는 리스트 형태)
            report_rows = self.driver.find_elements(By.XPATH, "//tr | //div[contains(@class, 'report')] | //div[contains(@class, 'item')]")
            
            for row in report_rows:
                try:
                    row_text = row.text.lower()
                    
                    # Generated 상태 확인
                    if "generated" in row_text:
                        # 링크 찾기
                        links = row.find_elements(By.XPATH, ".//a[contains(@href, '/report/')]")
                        if links:
                            report_url = links[0].get_attribute('href')
                            generated_reports.append({
                                "url": report_url,
                                "title": row.text.strip()[:50],  # 제목 일부만
                                "element": row
                            })
                            self.logger.info(f"Generated 보고서 발견: {report_url}")
                        
                except Exception as e:
                    continue
            
            return generated_reports
            
        except Exception as e:
            self.logger.error(f"Generated 보고서 검색 실패: {e}")
            return []
    
    def _extract_html(self):
        """현재 페이지에서 HTML 추출"""
        try:
            # TerminalX 특화 CSS 선택자로 추출
            script = """
            let targetElements = document.querySelectorAll('.text-\\\\[\\\\#121212\\\\]');
            if (targetElements.length === 0) {
                targetElements = document.querySelectorAll('[class*="text-"]');
            }
            if (targetElements.length === 0) {
                targetElements = document.querySelectorAll('main, .main, .content, [class*="content"]');
            }
            
            let html = '';
            targetElements.forEach(el => {
                html += el.outerHTML + '\\n';
            });
            
            return html || document.documentElement.outerHTML;
            """
            
            extracted_html = self.driver.execute_script(script)
            
            if extracted_html and len(extracted_html.strip()) > 100:
                return extracted_html
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"HTML 추출 실패: {e}")
            return None
    
    def _print_current_status(self):
        """현재 보고서 상태 출력"""
        try:
            self.logger.info("현재 보고서 상태:")
            
            # 모든 보고서 행 찾기
            rows = self.driver.find_elements(By.XPATH, "//tr | //div[contains(@class, 'report')]")
            
            for i, row in enumerate(rows[:10], 1):  # 상위 10개만
                text = row.text.strip()
                if text and len(text) > 10:
                    self.logger.info(f"{i}. {text[:100]}")
                    
        except Exception as e:
            self.logger.error(f"상태 출력 실패: {e}")
    
    def run_quick_check(self):
        """빠른 확인 실행"""
        try:
            self.logger.info("빠른 아카이브 확인 시작")
            
            # 1. 브라우저 설정
            if not self.setup_browser():
                return False
            
            # 2. 빠른 로그인
            if not self.quick_login():
                return False
            
            # 3. 즉시 아카이브 확인
            success = self.check_archive_immediately()
            
            # 브라우저를 5분간 열어둠
            if success:
                self.logger.info("성공! 브라우저를 5분간 열어둡니다")
                time.sleep(300)
            
            return success
            
        except Exception as e:
            self.logger.error(f"빠른 확인 실패: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    checker = QuickArchiveChecker()
    checker.run_quick_check()