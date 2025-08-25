#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalX 6개 보고서 자동화 시스템
- 로그인 → 6개 프롬프트 순차 실행 → Past Day 설정 → 완료 대기 → 데이터 추출
"""

import os
import sys

# UTF-8 출력 설정
sys.stdout.reconfigure(encoding='utf-8')
import time
import json
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TerminalXReportsAutomator:
    """TerminalX 6개 보고서 자동화 클래스"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.project_root = Path(__file__).parent
        self.prompts_dir = Path("C:/Users/etlov/multi-agent-workspace/communication/claude/100x/01_지침")
        self.output_dir = self.project_root / "terminalx_6reports_output"
        self.output_dir.mkdir(exist_ok=True)
        
        # 6개 프롬프트 정보
        self.prompts = [
            {"file": "3.1 3.2 Gain Lose.md", "name": "Top3_GainLose"},
            {"file": "3.3 Fixed Income.md", "name": "Fixed_Income"},
            {"file": "5.1 Major IB Updates.md", "name": "Major_IB_Updates"},
            {"file": "6.3 Dark Pool & Political Donation Flows.md", "name": "Dark_Pool_Political"},
            {"file": "7.1 11 GICS Sector Table.md", "name": "GICS_Sector_Table"},
            {"file": "8.1 12 Key Tickers Table.md", "name": "Key_Tickers_Table"}
        ]
        
        self.results = []
    
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 기존 chromedriver.exe 사용
        driver_path = self.project_root / "chromedriver.exe"
        if not driver_path.exists():
            raise FileNotFoundError(f"ChromeDriver not found: {driver_path}")
        
        self.driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(str(driver_path)),
            options=chrome_options
        )
        
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 30)
        
        print("✅ Chrome 드라이버 설정 완료")
    
    def login_terminalx(self):
        """TerminalX 자동 로그인 - browser_controller 사용"""
        print("🔐 TerminalX 자동 로그인 시작...")
        
        try:
            # browser_controller 임포트 및 사용
            import browser_controller as bc
            browser = bc.BrowserController()
            
            # 자격 증명 로드
            browser._load_credentials()
            
            print("🌐 메인 페이지 접근...")
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(3)
            
            # 로그인이 필요한지 확인
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                print("✅ 이미 로그인됨")
                return
            
            print("🔐 자동 로그인 진행...")
            
            # 로그인 버튼 클릭
            try:
                login_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in')]")))
                login_btn.click()
                time.sleep(3)
            except:
                print("⚠️ 로그인 버튼을 찾을 수 없어 건너뜀")
            
            # 이메일 입력
            email_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter your email']")))
            email_input.clear()
            email_input.send_keys(browser.username)
            
            # 비밀번호 입력
            password_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter your password']")))
            password_input.clear()
            password_input.send_keys(browser.password)
            
            # 로그인 실행
            login_submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log In')]")))
            login_submit.click()
            
            # 로그인 완료 확인
            self.wait.until(EC.url_contains("enterprise"))
            print("✅ TerminalX 자동 로그인 완료")
            
        except Exception as e:
            print(f"❌ 자동 로그인 실패: {e}")
            print("⚠️ 수동으로 로그인을 완료해주세요.")
            print("로그인 완료 후 아무 키나 누르세요...")
            input()
    
    def read_prompt(self, prompt_file):
        """프롬프트 파일 읽기"""
        prompt_path = self.prompts_dir / prompt_file
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"❌ 프롬프트 파일 읽기 실패: {prompt_file} - {e}")
            return None
    
    def find_input_textarea(self):
        """텍스트 입력 영역 찾기"""
        try:
            # 여러 가능한 선택자로 시도
            selectors = [
                "textarea[placeholder*='Ask Anything']",
                "textarea.text-left",
                "textarea[class*='min-h-']",
                "textarea",
                "input[type='text']",
                "[contenteditable='true']"
            ]
            
            for selector in selectors:
                try:
                    element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    if element.is_displayed() and element.is_enabled():
                        return element
                except:
                    continue
            
            raise NoSuchElementException("입력 영역을 찾을 수 없습니다")
            
        except Exception as e:
            print(f"❌ 입력 영역 찾기 실패: {e}")
            return None
    
    def set_past_day(self):
        """Past Day 설정 - 다양한 방법으로 시도"""
        print("📅 Past Day 설정 시도...")
        
        # 방법 1: 날짜 관련 버튼/드롭다운 찾기
        date_selectors = [
            "button[class*='date']",
            "select[class*='date']",
            "div[class*='date']",
            "button:contains('Past Day')",
            "option:contains('Past Day')",
            "[data-testid*='date']",
            "[id*='date']",
            ".date-picker",
            ".time-range",
            ".period-selector"
        ]
        
        for selector in date_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        print(f"📅 날짜 관련 요소 발견: {selector}")
                        element.click()
                        time.sleep(2)
                        
                        # Past Day 옵션 찾기
                        past_day_options = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Past Day') or contains(text(), 'past day') or contains(text(), 'yesterday')]")
                        for option in past_day_options:
                            if option.is_displayed():
                                option.click()
                                print("✅ Past Day 설정 성공")
                                return True
            except Exception as e:
                continue
        
        # 방법 2: 페이지 소스에서 Past Day 관련 요소 찾기
        page_source = self.driver.page_source.lower()
        if "past day" in page_source:
            print("📅 페이지에 'Past Day' 텍스트 발견")
            try:
                past_day_element = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Past Day')]")
                past_day_element.click()
                print("✅ Past Day 클릭 성공")
                return True
            except:
                pass
        
        print("⚠️ Past Day 설정을 자동으로 찾지 못했습니다. 수동 설정이 필요할 수 있습니다.")
        return False
    
    def submit_prompt(self, prompt_text):
        """프롬프트 제출"""
        try:
            # 입력 영역 찾기
            input_element = self.find_input_textarea()
            if not input_element:
                return False
            
            # 기존 텍스트 지우고 새 프롬프트 입력
            input_element.clear()
            time.sleep(1)
            input_element.send_keys(prompt_text)
            time.sleep(2)
            
            # Submit/Generate 버튼 찾기
            submit_selectors = [
                "button[type='submit']",
                "button:contains('Generate')",
                "button:contains('Submit')",
                "button:contains('Send')",
                "button[class*='submit']",
                "button[class*='generate']"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_btn.is_displayed() and submit_btn.is_enabled():
                        submit_btn.click()
                        print("✅ 프롬프트 제출 완료")
                        return True
                except:
                    continue
            
            # Enter 키로 시도
            input_element.send_keys("\n")
            print("✅ Enter 키로 제출 시도")
            return True
            
        except Exception as e:
            print(f"❌ 프롬프트 제출 실패: {e}")
            return False
    
    def wait_for_completion(self, max_wait_minutes=10):
        """완료 대기 - 다양한 트리거 감지"""
        print(f"⏳ 보고서 생성 대기 중... (최대 {max_wait_minutes}분)")
        
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        while time.time() - start_time < max_wait_seconds:
            try:
                # 방법 1: URL 변화 감지
                current_url = self.driver.current_url
                if "/report/" in current_url or "/result/" in current_url:
                    print("✅ URL 변화 감지 - 보고서 페이지로 이동")
                    time.sleep(5)  # 추가 로딩 대기
                    return True
                
                # 방법 2: "Generating" 텍스트 사라짐 감지
                page_source = self.driver.page_source.lower()
                if "generating" not in page_source and "loading" not in page_source:
                    # 실제 데이터가 있는지 확인
                    if "[&_sup]:text-[9px]" in self.driver.page_source or "supersearchx-body" in self.driver.page_source:
                        print("✅ 실제 데이터 감지 - 생성 완료")
                        return True
                
                # 방법 3: 특정 완료 요소 감지
                completion_indicators = [
                    "[class*='supersearchx-body']",
                    "[class*='report-complete']",
                    "[class*='result-ready']",
                    "table",
                    ".table-scroll-wrapper"
                ]
                
                for indicator in completion_indicators:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                        if elements and any(el.is_displayed() for el in elements):
                            print(f"✅ 완료 지표 감지: {indicator}")
                            return True
                    except:
                        continue
                
                print(f"⏳ 대기 중... ({int(time.time() - start_time)}초 경과)")
                time.sleep(10)
                
            except Exception as e:
                print(f"⚠️ 완료 감지 중 오류: {e}")
                time.sleep(5)
        
        print(f"⚠️ 최대 대기 시간({max_wait_minutes}분) 초과")
        return False
    
    def extract_data(self, report_name):
        """데이터 추출 - F12 Elements 방식 시뮬레이션"""
        print(f"📊 데이터 추출 시작: {report_name}")
        
        try:
            # [&_sup]:text-[9px] 패턴으로 검색
            target_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='supersearchx-body']")
            
            if not target_elements:
                # 대안 선택자들
                alternative_selectors = [
                    "[class*='leading-5']",
                    "[class*='text-[9px]']", 
                    ".table-scroll-wrapper",
                    "table",
                    "[class*='report-content']"
                ]
                
                for selector in alternative_selectors:
                    target_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if target_elements:
                        break
            
            if target_elements:
                # 가장 큰 요소 선택 (가장 많은 데이터를 포함할 가능성)
                main_element = max(target_elements, key=lambda x: len(x.get_attribute('innerHTML')))
                extracted_html = main_element.get_attribute('outerHTML')
                
                # 파일로 저장
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{report_name}_{timestamp}.html"
                filepath = self.output_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(extracted_html)
                
                print(f"✅ 데이터 추출 완료: {filename} ({len(extracted_html)} characters)")
                return str(filepath)
            
            else:
                print("❌ 추출할 데이터를 찾을 수 없습니다")
                return None
                
        except Exception as e:
            print(f"❌ 데이터 추출 실패: {e}")
            return None
    
    def process_single_report(self, prompt_info, index):
        """단일 보고서 처리"""
        print(f"\n🔄 보고서 {index+1}/6 처리 시작: {prompt_info['name']}")
        
        try:
            # 1. 프롬프트 읽기
            prompt_text = self.read_prompt(prompt_info['file'])
            if not prompt_text:
                return False
            
            print(f"📝 프롬프트 읽기 완료: {len(prompt_text)} characters")
            
            # 2. Past Day 설정 (첫 번째 보고서에서만)
            if index == 0:
                self.set_past_day()
            
            # 3. 프롬프트 제출
            if not self.submit_prompt(prompt_text):
                return False
            
            # 4. 완료 대기
            if not self.wait_for_completion():
                print(f"⚠️ {prompt_info['name']} 생성 시간 초과")
                return False
            
            # 5. 데이터 추출
            extracted_file = self.extract_data(prompt_info['name'])
            if extracted_file:
                result = {
                    "prompt": prompt_info,
                    "success": True,
                    "file": extracted_file,
                    "timestamp": datetime.now().isoformat()
                }
                self.results.append(result)
                print(f"✅ {prompt_info['name']} 완료")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ {prompt_info['name']} 처리 실패: {e}")
            return False
    
    def run_automation(self):
        """전체 자동화 실행"""
        print("🚀 TerminalX 6개 보고서 자동화 시작!")
        
        try:
            # 1. 드라이버 설정
            self.setup_driver()
            
            # 2. 로그인
            self.login_terminalx()
            
            # 3. 각 보고서 순차 처리
            successful_reports = 0
            for i, prompt_info in enumerate(self.prompts):
                if self.process_single_report(prompt_info, i):
                    successful_reports += 1
                
                # 다음 보고서를 위해 새 세션 시작
                if i < len(self.prompts) - 1:
                    print("🔄 새 세션 준비...")
                    self.driver.get("https://theterminalx.com/agent/enterprise")
                    time.sleep(3)
            
            # 4. 결과 저장
            self.save_results()
            
            print(f"\n🎉 자동화 완료! 성공: {successful_reports}/{len(self.prompts)}")
            
        except Exception as e:
            print(f"❌ 자동화 실행 중 오류: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def save_results(self):
        """결과를 JSON으로 저장"""
        results_file = self.output_dir / f"automation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_prompts": len(self.prompts),
                "successful_reports": len(self.results),
                "results": self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📊 결과 저장: {results_file}")


def main():
    """메인 실행"""
    automator = TerminalXReportsAutomator()
    automator.run_automation()


if __name__ == "__main__":
    main()