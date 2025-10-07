#!/usr/bin/env python3
"""
Generated 보고서 직접 접근해서 저장
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

class DirectReportSaver:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.base_dir = self.project_dir.parent.parent
        self.communication_dir = self.base_dir / "communication" / "shared" / "100xfenok"
        self.secrets_file = self.base_dir / "secrets" / "my_sensitive_data.md"
        self.chromedriver_path = self.project_dir / "chromedriver.exe"
        
        self.driver = None
        self.username = None
        self.password = None
        
        # 오늘 생성된 보고서 URL들 (1186-1191)
        self.report_urls = [
            "https://theterminalx.com/agent/enterprise/report/1186",  # Part1-1
            "https://theterminalx.com/agent/enterprise/report/1187",  # Part1-2
            "https://theterminalx.com/agent/enterprise/report/1188",  # Part1-3
            "https://theterminalx.com/agent/enterprise/report/1189",  # Part2-1
            "https://theterminalx.com/agent/enterprise/report/1190",  # Part2-2
            "https://theterminalx.com/agent/enterprise/report/1191",  # Part2-3
        ]
        
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
    
    def save_all_reports(self):
        """모든 Generated 보고서 직접 저장"""
        try:
            saved_count = 0
            
            for i, url in enumerate(self.report_urls, 1):
                try:
                    self.logger.info(f"보고서 {i}/6 저장 중: {url}")
                    
                    # 보고서 페이지로 직접 이동
                    self.driver.get(url)
                    time.sleep(8)  # 로딩 대기
                    
                    # HTML 추출
                    html_content = self._extract_html()
                    
                    if html_content:
                        # 파일명 결정
                        if i <= 3:
                            filename = f"part1_{i:02d}.html"
                        else:
                            filename = f"part2_{i-3:02d}.html"
                        
                        # 파일 저장
                        output_file = self.communication_dir / "002_terminalx" / filename
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        
                        self.logger.info(f"저장 완료: {filename} ({len(html_content)} chars)")
                        saved_count += 1
                    else:
                        self.logger.warning(f"보고서 {i} HTML 추출 실패")
                    
                    time.sleep(2)  # 서버 부하 방지
                    
                except Exception as e:
                    self.logger.error(f"보고서 {i} 저장 실패: {e}")
                    continue
            
            self.logger.info(f"전체 저장 완료: {saved_count}/6개 성공")
            return saved_count > 0
            
        except Exception as e:
            self.logger.error(f"보고서 저장 실패: {e}")
            return False
    
    def _extract_html(self):
        """현재 페이지에서 HTML 추출"""
        try:
            # TerminalX 특화 추출
            script = """
            // 메인 콘텐츠 찾기
            let content = document.querySelector('.text-\\\\[\\\\#121212\\\\]') || 
                         document.querySelector('main') || 
                         document.querySelector('[class*="content"]') ||
                         document.querySelector('body');
            
            return content ? content.outerHTML : document.documentElement.outerHTML;
            """
            
            extracted_html = self.driver.execute_script(script)
            
            if extracted_html and len(extracted_html.strip()) > 500:
                return extracted_html
            else:
                # 대안: 전체 body 내용
                return self.driver.find_element(By.TAG_NAME, "body").get_attribute('outerHTML')
                
        except Exception as e:
            self.logger.error(f"HTML 추출 실패: {e}")
            return None
    
    def run_direct_save(self):
        """직접 저장 실행"""
        try:
            self.logger.info("Generated 보고서 직접 저장 시작")
            
            # 1. 브라우저 설정
            if not self.setup_browser():
                return False
            
            # 2. 로그인
            if not self.quick_login():
                return False
            
            # 3. 모든 보고서 저장
            success = self.save_all_reports()
            
            if success:
                self.logger.info("성공! 브라우저를 2분간 열어둡니다")
                time.sleep(120)
            
            return success
            
        except Exception as e:
            self.logger.error(f"직접 저장 실패: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    saver = DirectReportSaver()
    saver.run_direct_save()