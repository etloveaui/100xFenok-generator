#!/usr/bin/env python3
"""
브라우저 컨트롤러 - Claude Code와 직접 연동
input() 사용 없이 함수 호출로 브라우저 제어
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import json

logger = logging.getLogger(__name__)

class BrowserController:
    """브라우저 직접 제어 클래스"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.base_dir = self.project_dir.parent.parent
        self.secrets_file = self.base_dir / "secrets" / "my_sensitive_data.md"
        self.chromedriver_path = self.project_dir / "chromedriver.exe"
        
        self.driver = None
        self.username = None
        self.password = None
        
        self._setup_logging()
        self._load_credentials()
    
    def _setup_logging(self):
        """로깅 설정"""
        log_file = self.project_dir / f"browser_controller_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def _load_credentials(self):
        """TerminalX 로그인 자격증명 로드"""
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
                        
            if not self.username or not self.password:
                raise ValueError("TerminalX 자격 증명을 찾을 수 없습니다.")
                
            logger.info("TerminalX 자격 증명 로드 완료")
            
        except Exception as e:
            logger.error(f"자격 증명 로드 실패: {e}")
            raise
    
    def start_browser(self):
        """브라우저 시작"""
        try:
            service = Service(executable_path=str(self.chromedriver_path))
            options = webdriver.ChromeOptions()
            
            # 브라우저 설정
            options.add_argument('--start-maximized')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(60)
            
            logger.info("🌐 Chrome 브라우저 시작 완료")
            return True
            
        except Exception as e:
            logger.error(f"브라우저 시작 실패: {e}")
            return False
    
    def get_status(self):
        """현재 브라우저 상태 반환"""
        try:
            if not self.driver:
                return "브라우저가 시작되지 않았습니다."
            
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            status = f"""
📍 현재 URL: {current_url}
📄 페이지 제목: {page_title}
⏰ 시간: {datetime.now().strftime("%H:%M:%S")}
"""
            logger.info(status)
            return status
            
        except Exception as e:
            error_msg = f"상태 확인 실패: {e}"
            logger.error(error_msg)
            return error_msg
    
    def navigate_to(self, url):
        """URL로 이동"""
        try:
            logger.info(f"🔄 페이지 이동: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            return self.get_status()
            
        except Exception as e:
            error_msg = f"페이지 이동 실패: {e}"
            logger.error(error_msg)
            return error_msg
    
    def click_element(self, selector, selector_type="xpath"):
        """요소 클릭"""
        try:
            logger.info(f"🖱️ 요소 클릭: {selector}")
            
            if selector_type == "xpath":
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            elif selector_type == "css":
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
            
            element.click()
            logger.info("✅ 요소 클릭 성공")
            time.sleep(2)
            
            return "클릭 성공"
            
        except Exception as e:
            error_msg = f"요소 클릭 실패: {e}"
            logger.error(error_msg)
            return error_msg
    
    def input_text(self, selector, text, selector_type="xpath"):
        """텍스트 입력"""
        try:
            logger.info(f"⌨️ 텍스트 입력: {text}")
            
            if selector_type == "xpath":
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            elif selector_type == "css":
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
            
            element.clear()
            element.send_keys(text)
            logger.info("✅ 텍스트 입력 성공")
            
            return "텍스트 입력 성공"
            
        except Exception as e:
            error_msg = f"텍스트 입력 실패: {e}"
            logger.error(error_msg)
            return error_msg
    
    def find_elements(self, selector, selector_type="xpath"):
        """요소들 찾기"""
        try:
            logger.info(f"🔍 요소 검색: {selector}")
            
            if selector_type == "xpath":
                elements = self.driver.find_elements(By.XPATH, selector)
            elif selector_type == "css":
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            
            results = []
            for i, element in enumerate(elements[:10]):  # 최대 10개만
                try:
                    results.append(f"[{i}] {element.text[:100].strip()}")
                except:
                    results.append(f"[{i}] (텍스트 없음)")
            
            result_text = f"발견된 요소 {len(elements)}개:\n" + "\n".join(results)
            logger.info(result_text)
            return result_text
            
        except Exception as e:
            error_msg = f"요소 검색 실패: {e}"
            logger.error(error_msg)
            return error_msg
    
    def login_terminalx(self):
        """TerminalX 자동 로그인"""
        try:
            logger.info("🔐 TerminalX 자동 로그인 시작")
            
            # 1. 메인 페이지 접근
            result = self.navigate_to("https://theterminalx.com/agent/enterprise")
            logger.info(f"메인 페이지 접근 결과: {result}")
            
            # 2. 로그인 버튼 클릭
            result = self.click_element("//button[contains(., 'Log in')]")
            logger.info(f"로그인 버튼 클릭 결과: {result}")
            
            if "성공" not in result:
                return f"로그인 버튼 클릭 실패: {result}"
            
            time.sleep(3)
            
            # 3. 이메일 입력
            result = self.input_text("//input[@placeholder='Enter your email']", self.username)
            logger.info(f"이메일 입력 결과: {result}")
            
            if "성공" not in result:
                return f"이메일 입력 실패: {result}"
            
            # 4. 비밀번호 입력
            result = self.input_text("//input[@placeholder='Enter your password']", self.password)
            logger.info(f"비밀번호 입력 결과: {result}")
            
            if "성공" not in result:
                return f"비밀번호 입력 실패: {result}"
            
            # 5. 로그인 실행 버튼 클릭
            result = self.click_element("//button[contains(., 'Log In')]")
            logger.info(f"로그인 실행 결과: {result}")
            
            if "성공" not in result:
                return f"로그인 실행 실패: {result}"
            
            # 6. 로그인 성공 확인
            time.sleep(5)
            status = self.get_status()
            
            if "enterprise" in status.lower():
                logger.info("✅ TerminalX 로그인 성공!")
                return "✅ TerminalX 로그인 성공!\n" + status
            else:
                return f"로그인 확인 실패:\n{status}"
            
        except Exception as e:
            error_msg = f"로그인 중 오류: {e}"
            logger.error(error_msg)
            return error_msg
    
    def check_archive_top6(self):
        """아카이브 상위 6개 보고서 상태 확인"""
        try:
            # 아카이브 페이지로 이동
            self.navigate_to("https://theterminalx.com/agent/archive")
            time.sleep(5)
            
            # 테이블 행들 찾기
            rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            if len(rows) < 6:
                return f"테이블 행 부족: {len(rows)}/6개"
            
            results = []
            generated_count = 0
            
            for i in range(6):
                try:
                    row = rows[i]
                    
                    # 제목과 상태 추출
                    title_cell = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)")
                    status_cell = row.find_element(By.CSS_SELECTOR, "td:nth-child(3)")
                    
                    title = title_cell.text.strip()
                    status = status_cell.text.strip().lower()
                    
                    results.append(f"[{i+1}] {title}: {status}")
                    
                    if "generated" in status:
                        generated_count += 1
                        
                except Exception as e:
                    results.append(f"[{i+1}] 파싱 실패: {e}")
            
            summary = f"Generated: {generated_count}/6개\n" + "\n".join(results)
            logger.info(summary)
            return summary
            
        except Exception as e:
            error_msg = f"아카이브 확인 실패: {e}"
            logger.error(error_msg)
            return error_msg
    
    def close_browser(self):
        """브라우저 종료"""
        if self.driver:
            logger.info("🔒 브라우저 종료")
            self.driver.quit()
            self.driver = None
            return "브라우저 종료됨"
        return "브라우저가 이미 종료됨"

# 전역 컨트롤러 인스턴스
browser_controller = None

def start():
    """브라우저 시작"""
    global browser_controller
    browser_controller = BrowserController()
    return browser_controller.start_browser()

def status():
    """현재 상태"""
    if browser_controller:
        return browser_controller.get_status()
    return "브라우저가 시작되지 않았습니다."

def goto(url):
    """페이지 이동"""
    if browser_controller:
        return browser_controller.navigate_to(url)
    return "브라우저가 시작되지 않았습니다."

def click(selector):
    """클릭"""
    if browser_controller:
        return browser_controller.click_element(selector)
    return "브라우저가 시작되지 않았습니다."

def type_text(selector, text):
    """텍스트 입력"""
    if browser_controller:
        return browser_controller.input_text(selector, text)
    return "브라우저가 시작되지 않았습니다."

def find(selector):
    """요소 찾기"""
    if browser_controller:
        return browser_controller.find_elements(selector)
    return "브라우저가 시작되지 않았습니다."

def login():
    """TerminalX 로그인"""
    if browser_controller:
        return browser_controller.login_terminalx()
    return "브라우저가 시작되지 않았습니다."

def archive():
    """아카이브 확인"""
    if browser_controller:
        return browser_controller.check_archive_top6()
    return "브라우저가 시작되지 않았습니다."

def close():
    """브라우저 종료"""
    global browser_controller
    if browser_controller:
        result = browser_controller.close_browser()
        browser_controller = None
        return result
    return "브라우저가 이미 종료됨"

if __name__ == "__main__":
    print("브라우저 컨트롤러 함수들:")
    print("- start(): 브라우저 시작")
    print("- login(): TerminalX 로그인")
    print("- status(): 현재 상태")
    print("- archive(): 아카이브 확인")
    print("- close(): 브라우저 종료")