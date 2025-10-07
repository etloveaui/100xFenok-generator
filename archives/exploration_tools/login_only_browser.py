#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로그인만 해두는 브라우저
사용자가 수동으로 리포트 뽑는 과정을 관찰하기 위해
"""
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 인코딩 문제 완전 방지
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class LoginOnlyBrowser:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.abspath(os.path.join(self.project_dir, '..', '..'))
        self.secrets_file = os.path.join(self.base_dir, 'secrets', 'my_sensitive_data.md')
        self.chromedriver_path = os.path.join(self.project_dir, 'chromedriver.exe')
        
        self.driver = None
        self.username = None
        self.password = None
        
        self.load_credentials()
        self.setup_webdriver()
    
    def load_credentials(self):
        """로그인 자격 증명 로드"""
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
            print(f"[SUCCESS] 자격 증명 로드: {self.username}")
        except Exception as e:
            print(f"[ERROR] 자격 증명 로드 실패: {e}")
            sys.exit(1)
    
    def setup_webdriver(self):
        """Chrome WebDriver 설정 (브라우저 보이기)"""
        try:
            service = Service(executable_path=self.chromedriver_path)
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(60)
            self.driver.maximize_window()
            print("[SUCCESS] WebDriver 설정 완료")
        except Exception as e:
            print(f"[ERROR] WebDriver 설정 실패: {e}")
            sys.exit(1)
    
    def login_terminalx(self):
        """TerminalX 로그인만 수행"""
        print("=== TerminalX 로그인만 수행 ===")
        
        try:
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(3)
            
            # 로그인 버튼 클릭
            login_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Log in')]"))
            )
            login_btn.click()
            time.sleep(2)
            
            # 이메일 입력
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='email' or contains(@placeholder, 'email')]"))
            )
            email_input.clear()
            email_input.send_keys(self.username)
            time.sleep(1)
            
            # 비밀번호 입력
            password_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
            password_input.clear()
            password_input.send_keys(self.password)
            time.sleep(1)
            
            # 로그인 버튼 클릭
            final_login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Log In')]")
            final_login_btn.click()
            time.sleep(5)
            
            # 메인 페이지로 이동
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(3)
            
            current_url = self.driver.current_url
            print(f"[SUCCESS] 로그인 완료! 현재 URL: {current_url}")
            print("\n🎯 이제 사용자가 수동으로 리포트를 뽑을 차례입니다!")
            print("브라우저에서 다음 과정을 진행해주세요:")
            print("1. 프롬프트 입력")
            print("2. Any Time → Past day로 기간 변경")  
            print("3. Generate 버튼 클릭")
            print("4. answer URL에서 결과 확인")
            print("5. 결과 내용 저장")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 로그인 실패: {e}")
            return False
    
    def keep_browser_open(self):
        """브라우저를 계속 열어둠"""
        print("\n=== 브라우저 열어둠 모드 ===")
        print("사용자가 수동으로 작업하는 동안 브라우저를 열어둡니다.")
        print("작업이 끝나면 이 창에서 Ctrl+C로 종료하거나")
        print("브라우저를 직접 닫아주세요.")
        
        try:
            # 무한 대기 (사용자가 중단할 때까지)
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n사용자에 의해 종료됨")
        except Exception as e:
            print(f"\n예상치 못한 오류: {e}")
        finally:
            print("브라우저 종료 중...")
            self.driver.quit()

def main():
    print("=== 로그인만 해두는 브라우저 ===")
    print("사용자 수동 조작 관찰 모드")
    
    browser = LoginOnlyBrowser()
    
    try:
        # 로그인만 수행
        if browser.login_terminalx():
            # 브라우저 열어둠
            browser.keep_browser_open()
        else:
            print("❌ 로그인 실패")
            browser.driver.quit()
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        browser.driver.quit()

if __name__ == "__main__":
    main()