#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalX 완전 자동 작업 수행
1. 로그인
2. past day 기간 설정 찾기
3. 프롬프트 입력
4. 보고서 생성 대기
5. 다운로드 확인
브라우저 꺼지지 않게 계속 실행
"""
import os
import sys
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import browser_controller as bc

# 인코딩 문제 방지
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class FullAutoTerminalX:
    """TerminalX 완전 자동 작업"""
    
    def __init__(self):
        self.browser = bc.BrowserController()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'steps': [],
            'findings': {},
            'errors': []
        }
        print("[INIT] 완전 자동 TerminalX 작업 준비")
    
    def add_step(self, step_name, success=True, details=None):
        """단계 기록"""
        step = {
            'step': step_name,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.results['steps'].append(step)
        status = "✅" if success else "❌"
        print(f"{status} {step_name}: {details.get('message', 'OK') if details else 'OK'}")
    
    def full_workflow(self):
        """전체 워크플로우 자동 실행"""
        print("🤖 TerminalX 완전 자동 작업 시작")
        print("목표: 로그인→기간설정→프롬프트→보고서→다운로드")
        print()
        
        try:
            # 1. 브라우저 시작 및 로그인
            if not self.browser.start_browser():
                self.add_step("브라우저 시작", False, {"message": "실패"})
                return False
            self.add_step("브라우저 시작", True)
            
            if not self.browser.login_terminalx():
                self.add_step("로그인", False, {"message": "실패"})
                return False
            self.add_step("로그인", True)
            
            # 2. 기간 설정 찾기 및 변경
            self.find_and_set_period()
            
            # 3. 프롬프트 입력
            self.input_test_prompt()
            
            # 4. 보고서 생성 대기
            self.wait_for_report_generation()
            
            # 5. 다운로드 옵션 찾기
            self.find_download_options()
            
            # 6. 결과 출력
            self.print_final_results()
            
            # 7. 브라우저 계속 실행
            self.keep_browser_alive()
            
            return True
            
        except Exception as e:
            self.add_step("전체 워크플로우", False, {"message": f"예외: {e}"})
            print(f"❌ 오류: {e}")
            return False
    
    def find_and_set_period(self):
        """기간 설정 찾기 및 past day 설정"""
        print("\n🔍 [2/6] 기간 설정 옵션 찾기...")
        
        try:
            # 다양한 기간 관련 요소 찾기 시도
            period_selectors = [
                "//select[contains(@class, 'period') or contains(@class, 'time')]",
                "//button[contains(text(), 'period') or contains(text(), 'time') or contains(text(), 'Past')]",
                "//div[contains(@class, 'date') or contains(@class, 'period')]//button",
                "//input[@type='date']",
                "//select[contains(@name, 'period')]",
                "//button[contains(text(), 'Today') or contains(text(), 'Week') or contains(text(), 'Day')]"
            ]
            
            found_elements = []
            
            for selector in period_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            element_info = {
                                'selector': selector,
                                'text': elem.text,
                                'tag': elem.tag_name,
                                'class': elem.get_attribute('class'),
                                'name': elem.get_attribute('name')
                            }
                            found_elements.append(element_info)
                            print(f"  발견: {elem.tag_name} - {elem.text} - {elem.get_attribute('class')}")
                except Exception as e:
                    continue
            
            self.results['findings']['period_elements'] = found_elements
            
            if found_elements:
                self.add_step("기간 설정 요소 찾기", True, {"count": len(found_elements)})
                
                # 'Past' 또는 'Day' 관련 요소 클릭 시도
                for elem_info in found_elements:
                    if any(keyword in elem_info['text'].lower() for keyword in ['past', 'day', 'period']):
                        try:
                            element = self.browser.driver.find_element(By.XPATH, elem_info['selector'])
                            element.click()
                            print(f"  클릭 시도: {elem_info['text']}")
                            time.sleep(2)
                            
                            # 'past day' 옵션 찾기
                            past_day_options = self.browser.driver.find_elements(By.XPATH, "//*[contains(text(), 'past day') or contains(text(), 'Past Day')]")
                            if past_day_options:
                                past_day_options[0].click()
                                self.add_step("Past Day 설정", True, {"text": past_day_options[0].text})
                                break
                        except Exception as e:
                            continue
            else:
                self.add_step("기간 설정 요소 찾기", False, {"message": "요소 없음"})
            
        except Exception as e:
            self.add_step("기간 설정", False, {"message": str(e)})
    
    def input_test_prompt(self):
        """테스트 프롬프트 입력"""
        print("\n💬 [3/6] 프롬프트 입력...")
        
        try:
            # textarea 찾기
            prompt_input = WebDriverWait(self.browser.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "textarea"))
            )
            
            test_prompt = "Give me a market summary for today with key events and trends"
            
            prompt_input.clear()
            time.sleep(1)
            prompt_input.send_keys(test_prompt)
            time.sleep(2)
            
            # Enter 키로 전송
            prompt_input.send_keys(Keys.RETURN)
            
            self.add_step("프롬프트 입력", True, {"prompt": test_prompt})
            
        except Exception as e:
            self.add_step("프롬프트 입력", False, {"message": str(e)})
    
    def wait_for_report_generation(self):
        """보고서 생성 대기"""
        print("\n⏳ [4/6] 보고서 생성 대기...")
        
        start_time = time.time()
        timeout = 180  # 3분
        
        try:
            while time.time() - start_time < timeout:
                # 응답 영역 확인
                response_elements = self.browser.driver.find_elements(By.XPATH, 
                    "//div[contains(@class, 'response') or contains(@class, 'message') or contains(@class, 'result') or contains(@class, 'output')]")
                
                if response_elements:
                    responses = []
                    for elem in response_elements[:3]:
                        if elem.is_displayed() and elem.text.strip() and len(elem.text) > 50:
                            responses.append({
                                'text_preview': elem.text[:150] + '...',
                                'length': len(elem.text),
                                'class': elem.get_attribute('class')
                            })
                    
                    if responses:
                        self.results['findings']['responses'] = responses
                        self.add_step("보고서 생성", True, {"responses": len(responses)})
                        print(f"  📄 응답 {len(responses)}개 생성됨")
                        return True
                
                print(".", end="", flush=True)
                time.sleep(5)
            
            self.add_step("보고서 생성", False, {"message": "타임아웃"})
            
        except Exception as e:
            self.add_step("보고서 생성", False, {"message": str(e)})
    
    def find_download_options(self):
        """다운로드 옵션 찾기"""
        print("\n💾 [5/6] 다운로드 옵션 찾기...")
        
        try:
            download_selectors = [
                "//button[contains(text(), 'download') or contains(text(), 'Download')]",
                "//button[contains(text(), 'save') or contains(text(), 'Save')]",
                "//button[contains(text(), 'export') or contains(text(), 'Export')]",
                "//a[contains(@href, 'download')]",
                "//button[contains(@class, 'download')]",
                "//*[contains(@aria-label, 'download') or contains(@aria-label, 'save')]"
            ]
            
            download_options = []
            
            for selector in download_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            option_info = {
                                'text': elem.text,
                                'tag': elem.tag_name,
                                'class': elem.get_attribute('class'),
                                'href': elem.get_attribute('href')
                            }
                            download_options.append(option_info)
                            print(f"  다운로드 옵션: {elem.text} ({elem.tag_name})")
                except Exception as e:
                    continue
            
            self.results['findings']['download_options'] = download_options
            
            if download_options:
                self.add_step("다운로드 옵션 발견", True, {"count": len(download_options)})
            else:
                self.add_step("다운로드 옵션 발견", False, {"message": "옵션 없음"})
            
        except Exception as e:
            self.add_step("다운로드 옵션 찾기", False, {"message": str(e)})
    
    def print_final_results(self):
        """최종 결과 출력"""
        print("\n" + "="*80)
        print("🎉 TerminalX 자동 작업 완료!")
        print(f"⏰ 소요 시간: {datetime.now().isoformat()}")
        print()
        
        successful_steps = [s for s in self.results['steps'] if s['success']]
        failed_steps = [s for s in self.results['steps'] if not s['success']]
        
        print(f"✅ 성공한 단계: {len(successful_steps)}/{len(self.results['steps'])}")
        for step in successful_steps:
            print(f"  ✅ {step['step']}")
        
        if failed_steps:
            print(f"\n❌ 실패한 단계: {len(failed_steps)}")
            for step in failed_steps:
                print(f"  ❌ {step['step']}: {step['details'].get('message', 'Unknown')}")
        
        print(f"\n📊 발견된 요소들:")
        for key, value in self.results['findings'].items():
            if isinstance(value, list):
                print(f"  {key}: {len(value)}개")
            else:
                print(f"  {key}: {value}")
        
        print("="*80)
    
    def keep_browser_alive(self):
        """브라우저 계속 살려두기"""
        print("\n🖥️ [6/6] 브라우저 계속 실행 중...")
        print("⏹️ 종료하려면 Ctrl+C를 누르세요")
        
        try:
            while True:
                current_time = datetime.now().strftime('%H:%M:%S')
                url = self.browser.driver.current_url
                print(f"[{current_time}] 실행 중: {url}")
                time.sleep(60)  # 1분마다 상태 출력
                
        except KeyboardInterrupt:
            print("\n⏹️ 사용자가 종료를 요청했습니다")
        except Exception as e:
            print(f"\n❌ 오류: {e}")
        finally:
            self.browser.close_browser()
            print("🔚 브라우저 종료")

if __name__ == "__main__":
    worker = FullAutoTerminalX()
    worker.full_workflow()