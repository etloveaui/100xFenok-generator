#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalX 자동 로그인 + 계속 열어두기
"""
import os
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# 인코딩 문제 방지
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class AutoLoginBrowser:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.abspath(os.path.join(self.project_dir, '..', '..'))
        self.secrets_file = os.path.join(self.base_dir, 'secrets', 'my_sensitive_data.md')
        self.chromedriver_path = os.path.join(self.project_dir, 'chromedriver.exe')
        
        self.driver = None
        self.username = None
        self.password = None
        self.load_credentials()
        
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
            print(f"[LOAD] 계정: {self.username}")
        except Exception as e:
            print(f"[ERROR] 자격 증명 로드 실패: {e}")
    
    def start_browser(self):
        """브라우저 시작"""
        try:
            service = Service(executable_path=self.chromedriver_path)
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(60)
            self.driver.maximize_window()
            
            print("[START] 브라우저 시작 완료")
            return True
        except Exception as e:
            print(f"[ERROR] 브라우저 시작 실패: {e}")
            return False
    
    def auto_login(self):
        """자동 로그인"""
        print("\n[LOGIN] 자동 로그인 시작")
        
        try:
            # 페이지 이동
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(3)
            
            # 로그인 버튼 찾기 및 클릭
            try:
                login_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log In') or contains(text(), 'Login')]"))
                )
                login_btn.click()
                print("[LOGIN] 로그인 버튼 클릭")
                time.sleep(3)
            except Exception as e:
                print(f"[INFO] 로그인 버튼 없음 (이미 로그인됨?): {e}")
            
            # 이메일 입력
            try:
                email_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='email' or @name='email' or @placeholder*='email' or @placeholder*='Email']"))
                )
                email_input.clear()
                email_input.send_keys(self.username)
                print("[LOGIN] 이메일 입력 완료")
                time.sleep(1)
            except Exception as e:
                print(f"[INFO] 이메일 필드 없음: {e}")
            
            # 비밀번호 입력
            try:
                password_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
                )
                password_input.clear()
                password_input.send_keys(self.password)
                print("[LOGIN] 비밀번호 입력 완료")
                time.sleep(1)
            except Exception as e:
                print(f"[INFO] 비밀번호 필드 없음: {e}")
            
            # 로그인 버튼 클릭 (Submit)
            try:
                submit_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(text(), 'Sign in') or contains(text(), 'Login') or contains(text(), 'Log in')]"))
                )
                submit_btn.click()
                print("[LOGIN] 로그인 실행")
                time.sleep(5)
            except Exception as e:
                print(f"[INFO] Submit 버튼 없음: {e}")
                # Enter 키로 시도
                try:
                    password_input.send_keys(Keys.RETURN)
                    print("[LOGIN] Enter 키로 로그인 시도")
                    time.sleep(5)
                except:
                    pass
            
            # 로그인 성공 확인
            WebDriverWait(self.driver, 30).until(
                lambda driver: "enterprise" in driver.current_url.lower()
            )
            
            print(f"[SUCCESS] 로그인 성공! URL: {self.driver.current_url}")
            return True
            
        except Exception as e:
            print(f"[ERROR] 자동 로그인 실패: {e}")
            print(f"[INFO] 현재 URL: {self.driver.current_url}")
            return False
    
    def print_work_instructions(self):
        """작업 지시사항"""
        print("\n" + "="*80)
        print("🎯 TerminalX Enterprise - 로그인 완료!")
        print()
        print("📝 작업 순서:")
        print("1. ⏰ 기간 설정을 'past day'로 변경")
        print("2. 💬 프롬프트 입력: 'Give me a market summary for today'")
        print("3. ⏳ 보고서 생성 완료까지 대기")
        print("4. 👀 생성 전후 화면 변화 관찰")
        print("5. 💾 다운로드/저장 옵션 찾기")
        print()
        print("🖥️ 브라우저는 계속 열려있습니다")
        print("⏹️ 완료하면 Ctrl+C로 종료하세요")
        print("="*80)
    
    def keep_running(self):
        """브라우저 계속 실행"""
        try:
            while True:
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"[{current_time}] 실행 중... (Ctrl+C로 종료)")
                
                # 페이지 상태 확인
                try:
                    title = self.driver.title
                    url = self.driver.current_url
                    print(f"[INFO] 페이지: {title} | {url}")
                except:
                    print("[WARNING] 브라우저 연결 끊김")
                    break
                
                time.sleep(30)  # 30초 대기
                
        except KeyboardInterrupt:
            print("\n[STOP] 종료 요청")
        except Exception as e:
            print(f"[ERROR] 실행 중 오류: {e}")
    
    def close(self):
        """정리"""
        if self.driver:
            print("\n[CLOSE] 브라우저 종료")
            self.driver.quit()

if __name__ == "__main__":
    browser = AutoLoginBrowser()
    
    try:
        print("🚀 TerminalX 자동 로그인 브라우저")
        
        # 1. 브라우저 시작
        if not browser.start_browser():
            exit(1)
        
        # 2. 자동 로그인
        if browser.auto_login():
            # 3. 작업 지시사항
            browser.print_work_instructions()
            
            # 4. 계속 실행
            browser.keep_running()
        else:
            print("[ERROR] 로그인 실패 - 수동으로 로그인하세요")
            input("로그인 후 Enter를 누르세요...")
            browser.print_work_instructions()
            browser.keep_running()
            
    except Exception as e:
        print(f"[ERROR] 오류: {e}")
    finally:
        browser.close()