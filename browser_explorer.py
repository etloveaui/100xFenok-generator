#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalX 브라우저 탐색기
기간 설정 및 산출물 저장 방법을 정확히 파악하는 도구
"""
import os
import sys
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 인코딩 문제 완전 방지
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class TerminalXExplorer:
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
            print(f"[SUCCESS] 자격 증명 로드 완료: {self.username}")
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
            print("[SUCCESS] WebDriver 설정 완료 (브라우저 보이기 모드)")
        except Exception as e:
            print(f"[ERROR] WebDriver 설정 실패: {e}")
            sys.exit(1)
    
    def login_terminalx(self):
        """TerminalX 로그인"""
        print("\n=== TerminalX 로그인 ===")
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
            
            current_url = self.driver.current_url
            if "enterprise" in current_url and "login" not in current_url:
                print("[SUCCESS] TerminalX 로그인 성공")
                return True
            else:
                print(f"[ERROR] 로그인 실패 - URL: {current_url}")
                return False
                
        except Exception as e:
            print(f"[ERROR] 로그인 과정 실패: {e}")
            return False
    
    def explore_main_page(self):
        """메인 페이지 탐색 - 모든 요소 분석"""
        print("\n=== 메인 페이지 탐색 시작 ===")
        
        self.driver.get("https://theterminalx.com/agent/enterprise")
        time.sleep(5)
        
        print("1. 전체 페이지 요소 분석...")
        
        # 모든 클릭 가능한 요소 찾기
        clickable_elements = self.driver.find_elements(By.XPATH, "//*[@onclick or @href or contains(@class, 'btn') or @role='button']")
        print(f"   클릭 가능한 요소: {len(clickable_elements)}개")
        
        # 드롭다운, 선택자 요소 찾기
        dropdowns = self.driver.find_elements(By.XPATH, "//select | //*[contains(@class, 'dropdown') or contains(@class, 'select')]")
        print(f"   드롭다운 요소: {len(dropdowns)}개")
        
        # 시간/기간 관련 텍스트 요소 찾기
        time_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'time') or contains(text(), 'Time') or contains(text(), 'day') or contains(text(), 'Day')]")
        print(f"   시간/기간 관련 요소: {len(time_elements)}개")
        
        for i, elem in enumerate(time_elements):
            try:
                print(f"   - 시간요소 {i+1}: '{elem.text}' (태그: {elem.tag_name}, 클래스: {elem.get_attribute('class')})")
            except:
                print(f"   - 시간요소 {i+1}: [텍스트 읽기 실패]")
        
        return True
    
    def interactive_exploration(self):
        """대화식 탐색 - 사용자가 단계별로 확인"""
        print("\n=== 대화식 탐색 모드 ===")
        print("브라우저 창을 보면서 단계별로 진행합니다.")
        print("각 단계마다 Enter를 눌러 계속하세요.\n")
        
        input("1. 메인 페이지가 로드되었습니다. 프롬프트를 입력할 준비가 되었나요? [Enter]")
        
        # 프롬프트 입력
        test_prompt = "Give me a market summary for today"
        print(f"2. 테스트 프롬프트 입력: {test_prompt}")
        
        try:
            prompt_input = self.driver.find_element(By.XPATH, "//textarea | //input[@type='text']")
            prompt_input.clear()
            prompt_input.send_keys(test_prompt)
            print("   프롬프트 입력 완료")
        except:
            print("   [ERROR] 프롬프트 입력 필드를 찾을 수 없음")
            return
            
        input("3. 프롬프트가 입력되었습니다. 기간 설정을 찾아보세요. [Enter]")
        
        # 기간 설정 요소 상세 분석
        print("4. 기간 설정 요소 상세 분석...")
        self.analyze_time_period_elements()
        
        input("5. 기간 요소 분석 완료. Generate 버튼을 눌러보세요. [Enter]")
        
        # Generate 버튼 클릭
        try:
            generate_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Generate')]")
            print(f"   Generate 버튼 발견: {generate_btn.text}")
            generate_btn.click()
            print("   Generate 버튼 클릭 완료")
        except:
            print("   Generate 버튼 못 찾음, 엔터키 시도...")
            prompt_input.send_keys(Keys.RETURN)
            print("   엔터키로 제출")
        
        time.sleep(3)
        current_url = self.driver.current_url
        print(f"6. 현재 URL: {current_url}")
        
        if "/answer/" in current_url:
            print("   [SUCCESS] answer URL로 이동됨")
            input("7. answer 페이지에서 결과를 기다리세요. 완료되면 [Enter]")
            
            # 결과 페이지 분석
            self.analyze_answer_page()
        else:
            print("   [ERROR] answer URL로 이동하지 않음")
    
    def analyze_time_period_elements(self):
        """기간 설정 요소 상세 분석"""
        print("\n--- 기간 설정 요소 상세 분석 ---")
        
        # 가능한 모든 기간 관련 선택자들
        selectors = [
            "//*[contains(text(), 'Any time')]",
            "//*[contains(text(), 'any time')]", 
            "//*[contains(text(), 'Time')]",
            "//*[contains(text(), 'time')]",
            "//*[contains(@class, 'time')]",
            "//*[contains(@class, 'period')]",
            "//*[contains(@class, 'filter')]",
            "//select",
            "//*[contains(@class, 'dropdown')]"
        ]
        
        for i, selector in enumerate(selectors):
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"선택자 {i+1} '{selector}': {len(elements)}개 발견")
                    for j, elem in enumerate(elements):
                        try:
                            text = elem.text
                            tag = elem.tag_name
                            class_attr = elem.get_attribute('class')
                            clickable = elem.is_enabled() and elem.is_displayed()
                            print(f"   요소 {j+1}: 텍스트='{text}' 태그={tag} 클래스={class_attr} 클릭가능={clickable}")
                        except Exception as e:
                            print(f"   요소 {j+1}: [분석 실패] {e}")
            except:
                continue
    
    def analyze_answer_page(self):
        """답변 페이지 분석"""
        print("\n--- 답변 페이지 분석 ---")
        
        current_url = self.driver.current_url
        page_title = self.driver.title
        page_source_length = len(self.driver.page_source)
        
        print(f"URL: {current_url}")
        print(f"제목: {page_title}")
        print(f"페이지 크기: {page_source_length}바이트")
        
        # 답변 내용 요소 찾기
        content_selectors = [
            "//*[contains(@class, 'answer')]",
            "//*[contains(@class, 'response')]",
            "//*[contains(@class, 'result')]",
            "//*[contains(@class, 'content')]",
            "//p",
            "//div[text()]"
        ]
        
        print("답변 내용 요소 분석:")
        for selector in content_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"   {selector}: {len(elements)}개 발견")
                    for i, elem in enumerate(elements[:3]):  # 처음 3개만
                        text = elem.text[:100]  # 처음 100자만
                        if text.strip():
                            print(f"     요소 {i+1}: {text}...")
            except:
                continue
    
    def cleanup(self):
        """리소스 정리"""
        print("\n브라우저를 열어둡니다. 수동으로 닫아주세요.")
        # self.driver.quit()  # 브라우저를 열어둠

def main():
    print("=== TerminalX 브라우저 탐색기 ===")
    
    explorer = TerminalXExplorer()
    
    try:
        # 로그인
        if not explorer.login_terminalx():
            print("❌ 로그인 실패로 종료")
            return
        
        # 메인 페이지 탐색
        explorer.explore_main_page()
        
        # 대화식 탐색
        explorer.interactive_exploration()
        
        print("\n🔍 탐색 완료!")
        
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
    finally:
        explorer.cleanup()

if __name__ == "__main__":
    main()