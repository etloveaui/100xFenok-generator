#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalX 6개 보고서 제대로 된 자동화
- browser_controller 완전 활용
- Past Day 제대로 설정
- Generate 버튼 제대로 누르기
- supersearchx-body 데이터 제대로 추출
"""
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import browser_controller as bc

# 인코딩 문제 방지
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class TerminalX6ReportsFixed:
    """제대로 된 TerminalX 6개 보고서 자동화"""
    
    def __init__(self):
        self.browser = bc.BrowserController()
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
        print("🔧 제대로 된 TerminalX 6개 보고서 자동화 준비")
    
    def run_automation(self):
        """전체 자동화 실행"""
        print("🚀 TerminalX 6개 보고서 제대로 된 자동화 시작!")
        
        try:
            # 1. 브라우저 시작
            if not self.browser.start_browser():
                print("❌ 브라우저 시작 실패")
                return False
            print("✅ 브라우저 시작")
            
            # 2. 제대로 로그인
            login_result = self.browser.login_terminalx()
            if "성공" not in login_result:
                print(f"❌ 로그인 실패: {login_result}")
                return False
            print("✅ 로그인 완료")
            
            # 3. 각 보고서 순차 처리
            successful_reports = 0
            for i, prompt_info in enumerate(self.prompts):
                print(f"\n🔄 보고서 {i+1}/6 처리 시작: {prompt_info['name']}")
                
                if self.process_single_report(prompt_info, i):
                    successful_reports += 1
                    print(f"✅ {prompt_info['name']} 완료")
                else:
                    print(f"❌ {prompt_info['name']} 실패")
                
                # 다음 보고서를 위해 새 페이지로
                if i < len(self.prompts) - 1:
                    print("🔄 새 페이지 준비...")
                    self.browser.navigate_to("https://theterminalx.com/agent/enterprise")
                    time.sleep(3)
            
            # 4. 결과 저장
            self.save_results()
            
            print(f"\n🎉 자동화 완료! 성공: {successful_reports}/{len(self.prompts)}")
            
            return successful_reports == len(self.prompts)
            
        except Exception as e:
            print(f"❌ 자동화 실행 중 오류: {e}")
            return False
        
        finally:
            self.browser.close_browser()
    
    def process_single_report(self, prompt_info, index):
        """단일 보고서 제대로 처리"""
        try:
            # 1. 프롬프트 읽기
            prompt_text = self.read_prompt(prompt_info['file'])
            if not prompt_text:
                return False
            
            # 2. Past Day 설정 (첫 번째 보고서에서만)
            if index == 0:
                if not self.set_past_day_properly():
                    print("⚠️ Past Day 설정 실패 - 계속 진행")
            
            # 3. 프롬프트 입력
            if not self.input_prompt_properly(prompt_text):
                return False
            
            # 4. Generate 버튼 제대로 누르기
            if not self.click_generate_properly():
                return False
            
            # 5. 실제 보고서 생성 대기
            if not self.wait_for_real_report():
                print("⚠️ 보고서 생성 시간 초과")
                return False
            
            # 6. supersearchx-body 데이터 제대로 추출
            extracted_file = self.extract_real_data(prompt_info['name'])
            if extracted_file:
                result = {
                    "prompt": prompt_info,
                    "success": True,
                    "file": extracted_file,
                    "timestamp": datetime.now().isoformat()
                }
                self.results.append(result)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ {prompt_info['name']} 처리 실패: {e}")
            return False
    
    def read_prompt(self, prompt_file):
        """프롬프트 파일 읽기"""
        prompt_path = self.prompts_dir / prompt_file
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                print(f"📝 프롬프트 읽기 완료: {len(content)} characters")
                return content
        except Exception as e:
            print(f"❌ 프롬프트 파일 읽기 실패: {prompt_file} - {e}")
            return None
    
    def set_past_day_properly(self):
        """Past Day 제대로 설정"""
        print("📅 Past Day 제대로 설정 시도...")
        
        try:
            # Custom Report Builder 버튼 먼저 찾기
            try:
                custom_btn = WebDriverWait(self.browser.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Custom Report Builder')]"))
                )
                custom_btn.click()
                print("✅ Custom Report Builder 클릭")
                time.sleep(3)
            except:
                print("⚠️ Custom Report Builder 버튼 없음 - 계속 진행")
            
            # 기간 설정 찾기 - 다양한 방법으로
            period_selectors = [
                "//select[contains(@name, 'period') or contains(@name, 'time') or contains(@name, 'date')]",
                "//button[contains(text(), 'Past') or contains(text(), 'Day') or contains(text(), 'Yesterday')]",
                "//div[contains(@class, 'date') or contains(@class, 'period')]//select",
                "//input[@type='date' or @type='datetime-local']",
                "//label[contains(text(), 'Period') or contains(text(), 'Time')]//following::select[1]"
            ]
            
            for selector in period_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            print(f"📅 기간 요소 발견: {elem.tag_name} - {elem.text}")
                            
                            # Select 드롭다운인 경우
                            if elem.tag_name == 'select':
                                select = Select(elem)
                                for option in select.options:
                                    print(f"  옵션: {option.text}")
                                    if any(keyword in option.text.lower() for keyword in ['past day', 'yesterday', 'day']):
                                        select.select_by_visible_text(option.text)
                                        print(f"✅ '{option.text}' 선택 완료")
                                        return True
                            
                            # 버튼인 경우
                            elif elem.tag_name == 'button' and any(keyword in elem.text.lower() for keyword in ['past', 'day', 'yesterday']):
                                elem.click()
                                print(f"✅ '{elem.text}' 버튼 클릭 완료")
                                return True
                                
                except Exception as e:
                    continue
            
            print("⚠️ Past Day 설정 요소를 찾지 못했습니다")
            return False
            
        except Exception as e:
            print(f"❌ Past Day 설정 오류: {e}")
            return False
    
    def input_prompt_properly(self, prompt_text):
        """프롬프트 제대로 입력"""
        print("💬 프롬프트 제대로 입력...")
        
        try:
            # textarea 찾기 - 다양한 방법으로
            textarea_selectors = [
                "//textarea[@placeholder='Ask Anything...']",
                "//textarea[contains(@placeholder, 'Ask')]",
                "//textarea",
                "//input[@type='text']",
                "[contenteditable='true']"
            ]
            
            input_element = None
            for selector in textarea_selectors:
                try:
                    if selector.startswith("//"):
                        element = WebDriverWait(self.browser.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    else:
                        element = WebDriverWait(self.browser.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    
                    if element.is_displayed() and element.is_enabled():
                        input_element = element
                        print(f"✅ 입력 요소 발견: {selector}")
                        break
                except:
                    continue
            
            if not input_element:
                print("❌ 입력 요소를 찾을 수 없습니다")
                return False
            
            # 텍스트 입력
            input_element.clear()
            time.sleep(1)
            input_element.send_keys(prompt_text)
            time.sleep(2)
            
            print("✅ 프롬프트 입력 완료")
            return True
            
        except Exception as e:
            print(f"❌ 프롬프트 입력 실패: {e}")
            return False
    
    def click_generate_properly(self):
        """Generate 버튼 제대로 누르기"""
        print("🔄 Generate 버튼 제대로 찾기...")
        
        try:
            # Generate 관련 버튼들 찾기
            generate_selectors = [
                "//button[contains(text(), 'Generate')]",
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), 'Send')]",
                "//button[contains(text(), 'Create')]",
                "//button[@type='submit']",
                "//button[contains(@class, 'submit')]",
                "//button[contains(@class, 'generate')]"
            ]
            
            for selector in generate_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            print(f"🔄 Generate 버튼 발견: {elem.text}")
                            elem.click()
                            print("✅ Generate 버튼 클릭 완료")
                            return True
                except:
                    continue
            
            # Enter 키로 시도
            print("⌨️ Enter 키로 제출 시도...")
            self.browser.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.RETURN)
            print("✅ Enter 키 제출 완료")
            return True
            
        except Exception as e:
            print(f"❌ Generate 버튼 클릭 실패: {e}")
            return False
    
    def wait_for_real_report(self, max_wait_minutes=5):
        """실제 보고서 생성 제대로 대기"""
        print(f"⏳ 실제 보고서 생성 대기 중... (최대 {max_wait_minutes}분)")
        
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        while time.time() - start_time < max_wait_seconds:
            try:
                # supersearchx-body 클래스 있는 실제 보고서 확인
                real_report_elements = self.browser.driver.find_elements(
                    By.CSS_SELECTOR, "[class*='supersearchx-body']"
                )
                
                if real_report_elements:
                    for elem in real_report_elements:
                        if elem.is_displayed() and len(elem.get_attribute('innerHTML')) > 500:
                            print("✅ 실제 보고서 생성 감지!")
                            time.sleep(3)  # 완전히 로드될 때까지 대기
                            return True
                
                # URL 변화 감지
                current_url = self.browser.driver.current_url
                if "/report/" in current_url or "/result/" in current_url:
                    print("✅ 보고서 페이지 URL 감지")
                    time.sleep(3)
                    return True
                
                print(".", end="", flush=True)
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️ 대기 중 오류: {e}")
                time.sleep(5)
        
        print(f"\n⚠️ 최대 대기 시간({max_wait_minutes}분) 초과")
        return False
    
    def extract_real_data(self, report_name):
        """supersearchx-body 실제 데이터 제대로 추출"""
        print(f"📊 실제 데이터 추출 시작: {report_name}")
        
        try:
            # supersearchx-body 클래스로 진짜 데이터 찾기
            target_elements = self.browser.driver.find_elements(
                By.CSS_SELECTOR, "[class*='supersearchx-body']"
            )
            
            if not target_elements:
                print("❌ supersearchx-body 클래스를 찾을 수 없습니다")
                return None
            
            # 가장 내용이 많은 요소 선택
            main_element = max(target_elements, key=lambda x: len(x.get_attribute('outerHTML')))
            extracted_html = main_element.get_attribute('outerHTML')
            
            # [&_sup]:text-[9px] 패턴이 있는지 확인
            if "[&_sup]:text-[9px]" not in extracted_html:
                print("⚠️ 예상 패턴이 없습니다 - 그래도 저장")
            
            # 파일로 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_name}_{timestamp}_REAL.html"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(extracted_html)
            
            print(f"✅ 실제 데이터 추출 완료: {filename} ({len(extracted_html)} characters)")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ 실제 데이터 추출 실패: {e}")
            return None
    
    def save_results(self):
        """결과를 JSON으로 저장"""
        results_file = self.output_dir / f"automation_results_REAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_prompts": len(self.prompts),
                "successful_reports": len(self.results),
                "results": self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📊 결과 저장: {results_file}")

if __name__ == "__main__":
    automator = TerminalX6ReportsFixed()
    automator.run_automation()