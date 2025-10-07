#!/usr/bin/env python3
"""
실시간 브라우저 상호작용 도구
- Chrome 브라우저를 열고 실시간으로 사용자와 상호작용
- 사용자가 지시하는 대로 페이지 이동, 요소 클릭, 텍스트 입력 등 수행
- 현재 페이지 상태 실시간 보고
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

class InteractiveBrowser:
    """실시간 브라우저 상호작용 도구"""
    
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
        log_file = self.project_dir / f"interactive_browser_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
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
            
            # 실시간 상호작용을 위한 브라우저 설정
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
    
    def get_current_status(self):
        """현재 브라우저 상태 반환"""
        try:
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            # 페이지의 주요 요소들 확인
            body_text = self.driver.find_element(By.TAG_NAME, "body").text[:500] + "..."
            
            status = {
                "url": current_url,
                "title": page_title,
                "body_preview": body_text,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            
            logger.info(f"📍 현재 위치: {current_url}")
            logger.info(f"📄 페이지 제목: {page_title}")
            
            return status
            
        except Exception as e:
            logger.error(f"상태 확인 실패: {e}")
            return None
    
    def navigate_to_url(self, url):
        """지정된 URL로 이동"""
        try:
            logger.info(f"🔄 페이지 이동: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            return self.get_current_status()
            
        except Exception as e:
            logger.error(f"페이지 이동 실패: {e}")
            return None
    
    def click_element(self, selector, selector_type="xpath"):
        """요소 클릭"""
        try:
            logger.info(f"🖱️ 요소 클릭 시도: {selector} ({selector_type})")
            
            if selector_type == "xpath":
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            elif selector_type == "css":
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
            else:
                logger.error(f"지원하지 않는 셀렉터 타입: {selector_type}")
                return False
            
            element.click()
            logger.info("✅ 요소 클릭 성공")
            time.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"요소 클릭 실패: {e}")
            return False
    
    def input_text(self, selector, text, selector_type="xpath", clear_first=True):
        """텍스트 입력"""
        try:
            logger.info(f"⌨️ 텍스트 입력: {selector} ({selector_type})")
            
            if selector_type == "xpath":
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            elif selector_type == "css":
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
            else:
                logger.error(f"지원하지 않는 셀렉터 타입: {selector_type}")
                return False
            
            if clear_first:
                element.clear()
            
            element.send_keys(text)
            logger.info(f"✅ 텍스트 입력 성공: {text}")
            
            return True
            
        except Exception as e:
            logger.error(f"텍스트 입력 실패: {e}")
            return False
    
    def send_enter(self, selector, selector_type="xpath"):
        """Enter 키 전송"""
        try:
            logger.info(f"⏎ Enter 키 전송: {selector}")
            
            if selector_type == "xpath":
                element = self.driver.find_element(By.XPATH, selector)
            elif selector_type == "css":
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
            else:
                logger.error(f"지원하지 않는 셀렉터 타입: {selector_type}")
                return False
            
            element.send_keys(Keys.RETURN)
            logger.info("✅ Enter 키 전송 성공")
            time.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"Enter 키 전송 실패: {e}")
            return False
    
    def find_elements_info(self, selector, selector_type="xpath", limit=5):
        """요소들 정보 조회"""
        try:
            logger.info(f"🔍 요소 검색: {selector} ({selector_type})")
            
            if selector_type == "xpath":
                elements = self.driver.find_elements(By.XPATH, selector)
            elif selector_type == "css":
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            else:
                logger.error(f"지원하지 않는 셀렉터 타입: {selector_type}")
                return []
            
            elements_info = []
            for i, element in enumerate(elements[:limit]):
                try:
                    info = {
                        "index": i,
                        "text": element.text.strip()[:100],
                        "tag": element.tag_name,
                        "visible": element.is_displayed(),
                        "enabled": element.is_enabled()
                    }
                    elements_info.append(info)
                except:
                    continue
            
            logger.info(f"✅ {len(elements_info)}개 요소 발견")
            for info in elements_info:
                logger.info(f"  [{info['index']}] {info['tag']}: {info['text']}")
            
            return elements_info
            
        except Exception as e:
            logger.error(f"요소 검색 실패: {e}")
            return []
    
    def get_page_source(self, save_to_file=False):
        """페이지 소스 가져오기"""
        try:
            source = self.driver.page_source
            
            if save_to_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"page_source_{timestamp}.html"
                filepath = self.project_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(source)
                
                logger.info(f"💾 페이지 소스 저장: {filename}")
                return str(filepath)
            else:
                return source[:1000] + "..." if len(source) > 1000 else source
                
        except Exception as e:
            logger.error(f"페이지 소스 가져오기 실패: {e}")
            return None
    
    def login_terminalx(self):
        """TerminalX 자동 로그인"""
        try:
            logger.info("🔐 TerminalX 자동 로그인 시작")
            
            # 메인 페이지 접근
            self.navigate_to_url("https://theterminalx.com/agent/enterprise")
            
            # 로그인 버튼 클릭
            if self.click_element("//button[contains(., 'Log in')]"):
                time.sleep(3)
                
                # 이메일 입력
                if self.input_text("//input[@placeholder='Enter your email']", self.username):
                    
                    # 비밀번호 입력
                    if self.input_text("//input[@placeholder='Enter your password']", self.password):
                        
                        # 로그인 버튼 클릭
                        if self.click_element("//button[contains(., 'Log In')]"):
                            
                            # 로그인 성공 확인
                            time.sleep(5)
                            current_status = self.get_current_status()
                            
                            if "enterprise" in current_status['url']:
                                logger.info("✅ TerminalX 로그인 성공!")
                                return True
            
            logger.error("❌ TerminalX 로그인 실패")
            return False
            
        except Exception as e:
            logger.error(f"로그인 중 오류: {e}")
            return False
    
    def interactive_session(self):
        """대화형 세션 시작"""
        logger.info("🚀 실시간 브라우저 상호작용 세션 시작")
        logger.info("="*60)
        logger.info("사용 가능한 명령어:")
        logger.info("- go <url>: 페이지 이동")
        logger.info("- click <selector>: 요소 클릭")  
        logger.info("- type <selector> <text>: 텍스트 입력")
        logger.info("- enter <selector>: Enter 키 전송")
        logger.info("- find <selector>: 요소 찾기")
        logger.info("- status: 현재 상태 확인")
        logger.info("- source: 페이지 소스 확인")
        logger.info("- login: TerminalX 자동 로그인")
        logger.info("- quit: 종료")
        logger.info("="*60)
        
        while True:
            try:
                command = input("\n🤖 명령어 입력 (또는 'quit'): ").strip()
                
                if command.lower() == 'quit':
                    break
                elif command.lower() == 'status':
                    status = self.get_current_status()
                    if status:
                        print(f"\n📍 URL: {status['url']}")
                        print(f"📄 제목: {status['title']}")
                        print(f"⏰ 시간: {status['timestamp']}")
                elif command.lower() == 'login':
                    self.login_terminalx()
                elif command.lower() == 'source':
                    filepath = self.get_page_source(save_to_file=True)
                    print(f"💾 페이지 소스 저장: {filepath}")
                elif command.startswith('go '):
                    url = command[3:].strip()
                    self.navigate_to_url(url)
                elif command.startswith('click '):
                    selector = command[6:].strip()
                    self.click_element(selector)
                elif command.startswith('type '):
                    parts = command[5:].strip().split(' ', 1)
                    if len(parts) >= 2:
                        selector, text = parts[0], parts[1]
                        self.input_text(selector, text)
                    else:
                        print("사용법: type <selector> <text>")
                elif command.startswith('enter '):
                    selector = command[6:].strip()
                    self.send_enter(selector)
                elif command.startswith('find '):
                    selector = command[5:].strip()
                    self.find_elements_info(selector)
                else:
                    print("알 수 없는 명령어입니다.")
                
            except KeyboardInterrupt:
                print("\n\n사용자에 의해 중단됨")
                break
            except Exception as e:
                logger.error(f"명령어 실행 중 오류: {e}")
    
    def close_browser(self):
        """브라우저 종료"""
        if self.driver:
            logger.info("🔒 브라우저 종료")
            self.driver.quit()

def main():
    """메인 실행 함수"""
    print("🌐 실시간 브라우저 상호작용 도구")
    print("이 도구를 사용하여 Claude와 실시간으로 브라우저를 조작할 수 있습니다.")
    
    browser = InteractiveBrowser()
    
    try:
        # 브라우저 시작
        if browser.start_browser():
            print("✅ 브라우저가 시작되었습니다.")
            print("💡 브라우저 창을 확인하고 대화형 세션을 시작하세요.")
            
            # 대화형 세션 시작
            browser.interactive_session()
        else:
            print("❌ 브라우저 시작에 실패했습니다.")
            
    except Exception as e:
        print(f"실행 중 오류 발생: {e}")
    
    finally:
        browser.close_browser()

if __name__ == "__main__":
    main()