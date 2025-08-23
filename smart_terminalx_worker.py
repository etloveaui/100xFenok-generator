#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalX 스마트 작업 - 어제 분석 결과 활용
Custom Report Builder를 통한 past day 설정
"""
import os
import sys
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import browser_controller as bc

# 인코딩 문제 방지
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class SmartTerminalXWorker:
    """어제 분석 결과 기반 스마트 작업"""
    
    def __init__(self):
        self.browser = bc.BrowserController()
        print("[SMART] 어제 분석 결과 기반 스마트 작업 준비")
    
    def run_smart_workflow(self):
        """스마트 워크플로우 - 어제 발견한 요소들 활용"""
        print("🧠 TerminalX 스마트 워크플로우 시작")
        print("기반: 어제 13:41 분석 결과 - Custom Report Builder 활용")
        print()
        
        try:
            # 1. 브라우저 시작 및 로그인
            if not self.browser.start_browser():
                print("❌ 브라우저 시작 실패")
                return False
            print("✅ 브라우저 시작")
            
            if not self.browser.login_terminalx():
                print("❌ 로그인 실패")
                return False
            print("✅ 로그인 완료")
            
            # 2. Custom Report Builder 클릭
            print("\n🔧 [1/5] Custom Report Builder 클릭...")
            if self.click_custom_report_builder():
                print("✅ Custom Report Builder 접근")
            else:
                print("❌ Custom Report Builder 접근 실패")
            
            # 3. 기간 설정 찾기 (더 구체적)
            print("\n📅 [2/5] 기간 설정 옵션 탐색...")
            self.find_period_settings()
            
            # 4. 프롬프트 입력
            print("\n💬 [3/5] 프롬프트 입력...")
            self.input_market_prompt()
            
            # 5. 보고서 생성 대기
            print("\n⏳ [4/5] 보고서 생성 대기...")
            self.wait_for_results()
            
            # 6. 다운로드 옵션
            print("\n💾 [5/5] 다운로드 옵션 찾기...")
            self.find_save_options()
            
            print("\n🎉 스마트 워크플로우 완료!")
            self.keep_browser_open()
            
        except Exception as e:
            print(f"❌ 오류: {e}")
        
    def click_custom_report_builder(self):
        """Custom Report Builder 버튼 클릭"""
        try:
            # 어제 발견된 정확한 버튼 찾기
            custom_report_btn = WebDriverWait(self.browser.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Custom Report Builder')]"))
            )
            
            custom_report_btn.click()
            print("  Custom Report Builder 버튼 클릭")
            time.sleep(3)
            
            # 페이지 변화 확인
            current_url = self.browser.driver.current_url
            print(f"  현재 URL: {current_url}")
            
            return True
            
        except Exception as e:
            print(f"  Custom Report Builder 클릭 실패: {e}")
            
            # 대안: Generate Custom Report 버튼 시도
            try:
                generate_btn = WebDriverWait(self.browser.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate Custom Report')]"))
                )
                generate_btn.click()
                print("  Generate Custom Report 버튼 클릭 (대안)")
                time.sleep(3)
                return True
            except:
                return False
    
    def find_period_settings(self):
        """기간 설정 옵션 찾기 - Custom Report Builder 내에서"""
        try:
            # Custom Report Builder 내부의 기간 관련 요소들
            period_selectors = [
                "//select[contains(@name, 'period') or contains(@name, 'time') or contains(@name, 'date')]",
                "//button[contains(text(), 'Past') or contains(text(), 'Day') or contains(text(), 'Week')]",
                "//div[contains(@class, 'date') or contains(@class, 'period')]//select",
                "//input[@type='date' or @type='datetime-local']",
                "//label[contains(text(), 'Period') or contains(text(), 'Time')]//following::select[1]",
                "//div[contains(text(), 'Time Range') or contains(text(), 'Period')]//following::*[1]"
            ]
            
            found_period_elements = []
            
            for selector in period_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            found_period_elements.append({
                                'selector': selector,
                                'text': elem.text,
                                'tag': elem.tag_name,
                                'name': elem.get_attribute('name'),
                                'class': elem.get_attribute('class')
                            })
                            print(f"  발견: {elem.tag_name} - '{elem.text}' - {elem.get_attribute('name')}")
                            
                            # Past Day 설정 시도
                            if elem.tag_name == 'select':
                                try:
                                    from selenium.webdriver.support.ui import Select
                                    select = Select(elem)
                                    
                                    # 옵션들 확인
                                    for option in select.options:
                                        print(f"    옵션: {option.text}")
                                        if 'past day' in option.text.lower() or 'day' in option.text.lower():
                                            select.select_by_visible_text(option.text)
                                            print(f"  ✅ '{option.text}' 선택함")
                                            return True
                                except Exception as select_e:
                                    print(f"    Select 조작 실패: {select_e}")
                            
                            # 버튼인 경우 클릭 시도
                            elif elem.tag_name == 'button' and ('past' in elem.text.lower() or 'day' in elem.text.lower()):
                                try:
                                    elem.click()
                                    print(f"  ✅ '{elem.text}' 버튼 클릭")
                                    return True
                                except Exception as btn_e:
                                    print(f"    버튼 클릭 실패: {btn_e}")
                                    
                except Exception as e:
                    continue
            
            print(f"  기간 설정 요소 {len(found_period_elements)}개 발견")
            
        except Exception as e:
            print(f"  기간 설정 찾기 오류: {e}")
    
    def input_market_prompt(self):
        """시장 요약 프롬프트 입력"""
        try:
            # textarea 찾기
            prompt_input = WebDriverWait(self.browser.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Ask Anything...']"))
            )
            
            market_prompt = "Give me a comprehensive market summary for the past day including key events, price movements, and sector performance"
            
            prompt_input.clear()
            time.sleep(1)
            prompt_input.send_keys(market_prompt)
            print(f"  프롬프트 입력: {market_prompt[:50]}...")
            time.sleep(2)
            
            # Enter 키로 전송
            prompt_input.send_keys(Keys.RETURN)
            print("  프롬프트 전송 완료")
            return True
            
        except Exception as e:
            print(f"  프롬프트 입력 실패: {e}")
            return False
    
    def wait_for_results(self):
        """결과 대기 - 더 스마트하게"""
        print("  보고서 생성 중...")
        
        start_time = time.time()
        timeout = 120  # 2분
        
        try:
            while time.time() - start_time < timeout:
                # 다양한 결과 요소 확인
                result_selectors = [
                    "//div[contains(@class, 'response')]",
                    "//div[contains(@class, 'result')]", 
                    "//div[contains(@class, 'output')]",
                    "//div[contains(@class, 'report')]",
                    "//table",
                    "//canvas",
                    "//div[contains(text(), 'Market') or contains(text(), 'Analysis')]"
                ]
                
                for selector in result_selectors:
                    try:
                        elements = self.browser.driver.find_elements(By.XPATH, selector)
                        visible_elements = [e for e in elements if e.is_displayed() and len(e.text.strip()) > 100]
                        
                        if visible_elements:
                            print(f"  ✅ 결과 생성됨: {selector} ({len(visible_elements)}개)")
                            print(f"  내용 미리보기: {visible_elements[0].text[:100]}...")
                            return True
                    except:
                        continue
                
                print(".", end="", flush=True)
                time.sleep(5)
            
            print(f"\n  ⏰ 타임아웃 ({timeout}초)")
            return False
            
        except Exception as e:
            print(f"  결과 대기 오류: {e}")
            return False
    
    def find_save_options(self):
        """저장/다운로드 옵션 찾기"""
        try:
            save_selectors = [
                "//button[contains(text(), 'Download') or contains(text(), 'Save') or contains(text(), 'Export')]",
                "//a[contains(@href, 'download') or contains(@href, 'export')]",
                "//button[contains(@class, 'download') or contains(@class, 'export')]",
                "//button[contains(@aria-label, 'download') or contains(@aria-label, 'save')]"
            ]
            
            save_options = []
            
            for selector in save_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            save_options.append({
                                'text': elem.text,
                                'tag': elem.tag_name,
                                'href': elem.get_attribute('href')
                            })
                            print(f"  저장 옵션: {elem.text} ({elem.tag_name})")
                except:
                    continue
            
            print(f"  총 {len(save_options)}개 저장 옵션 발견")
            return save_options
            
        except Exception as e:
            print(f"  저장 옵션 찾기 오류: {e}")
            return []
    
    def keep_browser_open(self):
        """브라우저 열어두기"""
        print("\n🖥️ 브라우저 계속 실행 중 (Ctrl+C로 종료)")
        
        try:
            while True:
                current_time = datetime.now().strftime('%H:%M:%S')
                url = self.browser.driver.current_url
                title = self.browser.driver.title
                print(f"[{current_time}] {title} | {url}")
                time.sleep(60)
                
        except KeyboardInterrupt:
            print("\n⏹️ 사용자 종료 요청")
        finally:
            self.browser.close_browser()

if __name__ == "__main__":
    worker = SmartTerminalXWorker()
    worker.run_smart_workflow()