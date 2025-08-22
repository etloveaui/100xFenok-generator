#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalX 자유 탐색기
보고서 산출 과정의 모든 element와 소스 완전 분석
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

# 인코딩 문제 완전 방지
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class FreeTerminalXExplorer:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.abspath(os.path.join(self.project_dir, '..', '..'))
        self.secrets_file = os.path.join(self.base_dir, 'secrets', 'my_sensitive_data.md')
        self.chromedriver_path = os.path.join(self.project_dir, 'chromedriver.exe')
        self.analysis_dir = os.path.join(self.project_dir, 'terminalx_analysis')
        
        os.makedirs(self.analysis_dir, exist_ok=True)
        
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
    
    def login_terminalx(self):
        """TerminalX 로그인"""
        print("=== TerminalX 로그인 ===")
        try:
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(3)
            
            login_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Log in')]"))
            )
            login_btn.click()
            time.sleep(2)
            
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='email' or contains(@placeholder, 'email')]"))
            )
            email_input.clear()
            email_input.send_keys(self.username)
            
            password_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
            password_input.clear()
            password_input.send_keys(self.password)
            
            final_login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Log In')]")
            final_login_btn.click()
            time.sleep(5)
            
            print("[SUCCESS] 로그인 완료")
            return True
            
        except Exception as e:
            print(f"[ERROR] 로그인 실패: {e}")
            return False
    
    def analyze_main_page_completely(self):
        """메인 페이지 완전 분석"""
        print("\n=== 메인 페이지 완전 분석 ===")
        
        self.driver.get("https://theterminalx.com/agent/enterprise")
        time.sleep(5)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 전체 페이지 소스 저장
        page_source = self.driver.page_source
        source_file = os.path.join(self.analysis_dir, f"page_source_{timestamp}.html")
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"   페이지 소스 저장: {source_file}")
        
        # 2. 모든 elements 분석
        analysis_data = {
            "timestamp": timestamp,
            "url": self.driver.current_url,
            "title": self.driver.title,
            "page_size": len(page_source),
            "elements_analysis": {}
        }
        
        # 3. 입력 필드들 분석
        print("   입력 필드 분석...")
        input_elements = self.driver.find_elements(By.XPATH, "//input | //textarea")
        analysis_data["elements_analysis"]["inputs"] = []
        
        for i, elem in enumerate(input_elements):
            try:
                elem_data = {
                    "index": i,
                    "tag": elem.tag_name,
                    "type": elem.get_attribute("type"),
                    "placeholder": elem.get_attribute("placeholder"),
                    "class": elem.get_attribute("class"),
                    "id": elem.get_attribute("id"),
                    "name": elem.get_attribute("name"),
                    "visible": elem.is_displayed(),
                    "enabled": elem.is_enabled()
                }
                analysis_data["elements_analysis"]["inputs"].append(elem_data)
                print(f"     입력 {i}: {elem.tag_name} type={elem_data['type']} placeholder={elem_data['placeholder']}")
            except:
                continue
        
        # 4. 버튼들 분석
        print("   버튼 분석...")
        button_elements = self.driver.find_elements(By.XPATH, "//button | //input[@type='submit']")
        analysis_data["elements_analysis"]["buttons"] = []
        
        for i, elem in enumerate(button_elements):
            try:
                elem_data = {
                    "index": i,
                    "tag": elem.tag_name,
                    "text": elem.text,
                    "type": elem.get_attribute("type"),
                    "class": elem.get_attribute("class"),
                    "visible": elem.is_displayed(),
                    "enabled": elem.is_enabled(),
                    "clickable": elem.is_enabled() and elem.is_displayed()
                }
                analysis_data["elements_analysis"]["buttons"].append(elem_data)
                print(f"     버튼 {i}: '{elem.text}' class={elem_data['class']}")
            except:
                continue
        
        # 5. 드롭다운/선택 요소들 분석
        print("   드롭다운/선택 요소 분석...")
        dropdown_selectors = [
            "//select",
            "//*[contains(@class, 'dropdown')]",
            "//*[contains(@class, 'cursor-pointer') and contains(text(), 'Any')]",
            "//*[contains(@class, 'cursor-pointer') and contains(text(), 'Time')]",
            "//*[contains(@class, 'cursor-pointer') and contains(text(), 'Day')]"
        ]
        
        analysis_data["elements_analysis"]["dropdowns"] = []
        for selector in dropdown_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for i, elem in enumerate(elements):
                    elem_data = {
                        "selector": selector,
                        "index": i,
                        "tag": elem.tag_name,
                        "text": elem.text,
                        "class": elem.get_attribute("class"),
                        "visible": elem.is_displayed(),
                        "clickable": elem.is_enabled() and elem.is_displayed()
                    }
                    analysis_data["elements_analysis"]["dropdowns"].append(elem_data)
                    print(f"     드롭다운: '{elem.text}' class={elem_data['class']}")
            except:
                continue
        
        # 6. 분석 결과 저장
        analysis_file = os.path.join(self.analysis_dir, f"analysis_{timestamp}.json")
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        
        print(f"   분석 결과 저장: {analysis_file}")
        return analysis_data
    
    def test_report_generation_step_by_step(self):
        """보고서 생성 과정 단계별 테스트"""
        print("\n=== 보고서 생성 과정 단계별 테스트 ===")
        
        test_prompt = "Give me today's market summary"
        
        # 1. 프롬프트 입력 테스트
        print("1. 프롬프트 입력 테스트...")
        try:
            # 모든 가능한 입력 필드 시도
            input_selectors = [
                "//textarea",
                "//input[@type='text']",
                "//input[not(@type)]",
                "//*[@contenteditable='true']"
            ]
            
            prompt_input = None
            for selector in input_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            prompt_input = elem
                            print(f"   프롬프트 입력 필드 발견: {selector}")
                            break
                    if prompt_input:
                        break
                except:
                    continue
            
            if prompt_input:
                prompt_input.clear()
                prompt_input.send_keys(test_prompt)
                print(f"   프롬프트 입력 완료: {test_prompt}")
            else:
                print("   [ERROR] 프롬프트 입력 필드를 찾을 수 없음")
                return False
        except Exception as e:
            print(f"   [ERROR] 프롬프트 입력 실패: {e}")
            return False
        
        # 2. 기간 설정 요소 상세 분석 및 테스트
        print("2. 기간 설정 요소 분석...")
        self.analyze_period_elements_detailed()
        
        # 3. Generate 버튼 분석 및 클릭
        print("3. Generate 버튼 분석...")
        generate_clicked = self.find_and_click_generate_button()
        
        if not generate_clicked:
            print("   [ERROR] Generate 버튼 클릭 실패")
            return False
        
        # 4. URL 변경 및 페이지 전환 추적
        print("4. URL 변경 추적...")
        initial_url = self.driver.current_url
        
        for i in range(10):  # 10초 동안 URL 변경 대기
            time.sleep(1)
            current_url = self.driver.current_url
            if current_url != initial_url:
                print(f"   [SUCCESS] URL 변경됨: {current_url}")
                
                # 5. answer 페이지 완전 분석
                if "/answer/" in current_url:
                    self.analyze_answer_page_completely(current_url)
                    return True
                else:
                    print(f"   [WARNING] 예상치 못한 URL: {current_url}")
                    return False
        
        print("   [ERROR] URL 변경되지 않음")
        return False
    
    def analyze_period_elements_detailed(self):
        """기간 설정 요소 상세 분석"""
        print("   기간 설정 요소 상세 분석...")
        
        # 가능한 모든 기간 관련 요소들 찾기
        period_selectors = [
            "//*[contains(text(), 'Any Time')]",
            "//*[contains(text(), 'Any time')]", 
            "//*[contains(text(), 'Time')]",
            "//*[contains(text(), 'Day')]",
            "//*[contains(text(), 'Past')]",
            "//*[contains(@class, 'cursor-pointer')]"
        ]
        
        for selector in period_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for i, elem in enumerate(elements):
                    try:
                        text = elem.text
                        classes = elem.get_attribute('class')
                        clickable = elem.is_displayed() and elem.is_enabled()
                        
                        if 'time' in text.lower() or 'day' in text.lower():
                            print(f"     기간 요소: '{text}' 클릭가능:{clickable} 클래스:{classes}")
                            
                            # 클릭 테스트
                            if clickable and ('Any Time' in text or 'Past Day' in text):
                                print(f"       클릭 테스트 시도: {text}")
                                elem.click()
                                time.sleep(2)
                                
                                # 드롭다운이 열렸는지 확인
                                page_source_after = self.driver.page_source
                                if 'Past' in page_source_after or 'Today' in page_source_after:
                                    print("       [SUCCESS] 드롭다운 열림 확인")
                                    
                                    # Past Day 옵션 찾기
                                    past_options = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Past Day') or contains(text(), 'Past day') or contains(text(), '1 day')]")
                                    for option in past_options:
                                        if option.is_displayed():
                                            print(f"         Past Day 옵션 발견: {option.text}")
                                            option.click()
                                            time.sleep(1)
                                            print("         [SUCCESS] Past Day 선택 완료")
                                            return True
                                
                    except Exception as e:
                        continue
            except:
                continue
        
        print("     [WARNING] 기간 설정 요소 클릭 실패")
        return False
    
    def find_and_click_generate_button(self):
        """Generate 버튼 찾기 및 클릭"""
        generate_selectors = [
            "//button[contains(text(), 'Generate')]",
            "//button[contains(text(), 'GENERATE')]",
            "//input[@type='submit']",
            "//button[@type='submit']",
            "//button[contains(@class, 'submit')]",
            "//*[contains(text(), 'Search')]"
        ]
        
        for selector in generate_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        print(f"   Generate 버튼 발견: {elem.text} ({selector})")
                        elem.click()
                        print("   [SUCCESS] Generate 버튼 클릭")
                        return True
            except:
                continue
        
        print("   Generate 버튼 못 찾음, 엔터키 시도...")
        # 마지막 시도: 현재 활성 요소에 엔터키
        active_element = self.driver.switch_to.active_element
        active_element.send_keys(Keys.RETURN)
        print("   엔터키로 제출")
        return True
    
    def analyze_answer_page_completely(self, answer_url):
        """답변 페이지 완전 분석"""
        print(f"5. 답변 페이지 완전 분석: {answer_url}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 페이지 로딩 상태 추적
        for wait_time in range(120):  # 2분 대기
            try:
                page_source = self.driver.page_source
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                
                # 로딩 상태 확인
                is_loading = any(indicator in page_text.lower() for indicator in [
                    'processing', 'loading', 'generating', 'searching'
                ])
                
                # 컨텐츠 확인
                has_content = len(page_text) > 5000
                
                print(f"   대기 {wait_time}초: 로딩={is_loading}, 컨텐츠크기={len(page_text)}")
                
                if not is_loading and has_content:
                    print("   [SUCCESS] 답변 생성 완료!")
                    
                    # 답변 페이지 소스 저장
                    answer_source_file = os.path.join(self.analysis_dir, f"answer_page_{timestamp}.html")
                    with open(answer_source_file, 'w', encoding='utf-8') as f:
                        f.write(page_source)
                    
                    # 답변 텍스트 저장
                    answer_text_file = os.path.join(self.analysis_dir, f"answer_text_{timestamp}.txt")
                    with open(answer_text_file, 'w', encoding='utf-8') as f:
                        f.write(page_text)
                    
                    print(f"   답변 저장 완료: {answer_text_file}")
                    
                    # 답변 요소들 분석
                    self.analyze_answer_elements()
                    
                    return True
                
                time.sleep(1)
                
            except Exception as e:
                print(f"   대기 중 오류: {e}")
                time.sleep(1)
        
        print("   [TIMEOUT] 답변 대기 시간 초과")
        return False
    
    def analyze_answer_elements(self):
        """답변 페이지 요소들 분석"""
        print("   답변 페이지 요소 분석...")
        
        # 답변 내용 요소들 찾기
        content_selectors = [
            "//*[contains(@class, 'answer')]",
            "//*[contains(@class, 'response')]", 
            "//*[contains(@class, 'result')]",
            "//*[contains(@class, 'content')]",
            "//p[string-length(text()) > 100]",
            "//div[string-length(text()) > 100]"
        ]
        
        for selector in content_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for i, elem in enumerate(elements):
                    text = elem.text
                    if text and len(text) > 100:
                        print(f"     답변 요소 {i}: {text[:100]}... (길이: {len(text)})")
            except:
                continue
    
    def keep_browser_open(self):
        """분석 완료 후 브라우저 열어둠"""
        print("\n=== 분석 완료 ===")
        print("결과 파일들:")
        files = os.listdir(self.analysis_dir)
        for file in files:
            print(f"  - {file}")
        
        print("\n브라우저를 열어둡니다. 수동 확인 후 닫아주세요.")
        try:
            input("아무 키나 눌러서 종료...")
        except:
            time.sleep(60)
        
        self.driver.quit()

def main():
    print("=== TerminalX 자유 탐색기 ===")
    print("보고서 산출 과정 완전 분석")
    
    explorer = FreeTerminalXExplorer()
    
    try:
        # 로그인
        if not explorer.login_terminalx():
            print("❌ 로그인 실패")
            return
        
        # 메인 페이지 완전 분석
        explorer.analyze_main_page_completely()
        
        # 보고서 생성 과정 테스트
        explorer.test_report_generation_step_by_step()
        
        # 브라우저 열어둠
        explorer.keep_browser_open()
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        explorer.driver.quit()

if __name__ == "__main__":
    main()