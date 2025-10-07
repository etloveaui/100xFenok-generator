#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수동 TerminalX 탐색기
Any Time 요소를 정확히 클릭하고 Past day로 변경하는 방법 탐색
"""
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# 인코딩 문제 완전 방지
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class ManualTerminalXExplorer:
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
        """Chrome WebDriver 설정"""
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
    
    def login_and_setup(self):
        """로그인하고 메인 페이지로 이동"""
        print("=== 로그인 및 설정 ===")
        
        self.driver.get("https://theterminalx.com/agent/enterprise")
        time.sleep(3)
        
        try:
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
            
            # 비밀번호 입력
            password_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
            password_input.clear()
            password_input.send_keys(self.password)
            
            # 로그인
            final_login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Log In')]")
            final_login_btn.click()
            time.sleep(5)
            
            print("[SUCCESS] 로그인 완료")
            return True
            
        except Exception as e:
            print(f"[ERROR] 로그인 실패: {e}")
            return False
    
    def test_period_change(self):
        """기간 변경 테스트"""
        print("\n=== 기간 변경 테스트 ===")
        
        # 메인 페이지로 이동
        self.driver.get("https://theterminalx.com/agent/enterprise")
        time.sleep(3)
        
        print("1. Any Time 요소 찾기...")
        
        # 정확한 Any Time 요소 찾기
        try:
            any_time_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'text-[#262626]') and contains(text(), 'Any Time')]"))
            )
            print(f"   [SUCCESS] Any Time 요소 발견: {any_time_element.text}")
            print(f"   클래스: {any_time_element.get_attribute('class')}")
            print(f"   클릭 가능: {any_time_element.is_enabled() and any_time_element.is_displayed()}")
            
            # 클릭 시도
            print("2. Any Time 클릭 시도...")
            any_time_element.click()
            time.sleep(2)
            print("   [SUCCESS] Any Time 클릭됨")
            
            # 드롭다운 옵션들 찾기
            print("3. 드롭다운 옵션들 찾기...")
            dropdown_options = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'day') or contains(text(), 'Day') or contains(text(), 'Today') or contains(text(), 'Past')]")
            
            print(f"   발견된 옵션: {len(dropdown_options)}개")
            for i, option in enumerate(dropdown_options):
                try:
                    text = option.text
                    tag = option.tag_name
                    classes = option.get_attribute('class')
                    visible = option.is_displayed()
                    print(f"   옵션 {i+1}: '{text}' (태그:{tag}, 보임:{visible})")
                    if classes:
                        print(f"             클래스: {classes}")
                except Exception as e:
                    print(f"   옵션 {i+1}: [분석 실패] {e}")
            
            # Past day, Today, 1 day 중 찾아서 클릭
            print("4. Past day/Today 옵션 클릭 시도...")
            target_texts = ['Past day', 'Today', '1 day', '24 hours']
            
            for target_text in target_texts:
                try:
                    target_option = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{target_text}')]"))
                    )
                    print(f"   [SUCCESS] {target_text} 옵션 발견!")
                    target_option.click()
                    time.sleep(1)
                    print(f"   [SUCCESS] {target_text} 클릭 완료!")
                    
                    # 변경 확인
                    time.sleep(2)
                    current_period = self.driver.find_element(By.XPATH, "//div[contains(@class, 'text-[#262626]')]").text
                    print(f"   현재 기간: {current_period}")
                    
                    return True
                    
                except Exception as e:
                    print(f"   {target_text} 클릭 실패: {e}")
                    continue
            
            print("   [ERROR] 적절한 옵션을 찾을 수 없음")
            return False
            
        except Exception as e:
            print(f"   [ERROR] Any Time 요소 클릭 실패: {e}")
            return False
    
    def test_full_workflow(self):
        """전체 워크플로우 테스트"""
        print("\n=== 전체 워크플로우 테스트 ===")
        
        # 1. 프롬프트 입력
        test_prompt = "Give me today's market summary"
        print(f"1. 프롬프트 입력: {test_prompt}")
        
        try:
            prompt_input = self.driver.find_element(By.XPATH, "//textarea | //input[@type='text']")
            prompt_input.clear()
            prompt_input.send_keys(test_prompt)
            print("   프롬프트 입력 완료")
        except Exception as e:
            print(f"   [ERROR] 프롬프트 입력 실패: {e}")
            return False
        
        # 2. 기간 변경
        print("2. 기간 변경 시도...")
        if not self.test_period_change():
            print("   [WARNING] 기간 변경 실패, 계속 진행...")
        
        # 3. Generate 클릭
        print("3. Generate 버튼 클릭...")
        try:
            generate_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Generate')]")
            generate_btn.click()
            print("   Generate 버튼 클릭 완료")
        except:
            prompt_input.send_keys(Keys.RETURN)
            print("   엔터키로 제출")
        
        time.sleep(3)
        
        # 4. URL 확인
        current_url = self.driver.current_url
        print(f"4. 현재 URL: {current_url}")
        
        if "/answer/" in current_url:
            print("   [SUCCESS] answer URL로 이동됨")
            
            # 5. 결과 대기
            print("5. 결과 대기 중...")
            for i in range(30):  # 30초 대기
                page_source = self.driver.page_source
                if "loading" not in page_source.lower() and len(page_source) > 50000:
                    print(f"   [SUCCESS] 결과 생성 완료 (페이지 크기: {len(page_source)})")
                    
                    # 6. 내용 추출 테스트
                    self.extract_answer_content()
                    return True
                
                time.sleep(1)
                if i % 5 == 0:
                    print(f"   대기 중... ({i}/30초)")
            
            print("   [ERROR] 결과 대기 타임아웃")
            return False
        else:
            print("   [ERROR] answer URL로 이동하지 않음")
            return False
    
    def extract_answer_content(self):
        """답변 내용 추출 테스트"""
        print("6. 답변 내용 추출...")
        
        try:
            # 페이지 텍스트 추출
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # 답변 부분만 추출 (간단한 방법)
            lines = page_text.split('\n')
            long_lines = [line.strip() for line in lines if len(line.strip()) > 50]
            
            if long_lines:
                answer_text = '\n'.join(long_lines[:10])  # 처음 10줄
                print(f"   추출된 내용 (길이: {len(answer_text)}):")
                print(f"   {answer_text[:200]}...")
                return answer_text
            else:
                print("   [ERROR] 충분한 내용을 찾을 수 없음")
                return ""
                
        except Exception as e:
            print(f"   [ERROR] 내용 추출 실패: {e}")
            return ""
    
    def keep_browser_open(self):
        """브라우저를 열어둠"""
        print("\n=== 탐색 완료 ===")
        print("브라우저를 열어둡니다. 수동으로 확인하고 닫아주세요.")
        print("아무 키나 눌러서 브라우저를 닫을 수 있습니다...")
        
        try:
            input()  # 사용자 입력 대기
        except:
            time.sleep(60)  # 1분 대기
        
        self.driver.quit()

def main():
    print("=== 수동 TerminalX 탐색기 ===")
    
    explorer = ManualTerminalXExplorer()
    
    try:
        # 로그인
        if not explorer.login_and_setup():
            print("❌ 로그인 실패")
            return
        
        # 기간 변경 테스트
        print("\n--- 기간 변경만 테스트 ---")
        explorer.test_period_change()
        
        # 전체 워크플로우 테스트
        print("\n--- 전체 워크플로우 테스트 ---")  
        explorer.test_full_workflow()
        
        # 브라우저 열어둠
        explorer.keep_browser_open()
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        explorer.driver.quit()

if __name__ == "__main__":
    main()