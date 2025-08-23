#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalX Enterprise 페이지 전용 워크플로우 탐색
- 기본 보고서 프롬프트 입력
- 기간 변경 방법 찾기  
- 보고서 생성 대기
- 결과물 파악 및 저장
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

# 인코딩 문제 방지
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class EnterpriseWorkflowExplorer:
    """TerminalX Enterprise 페이지 전용 워크플로우 탐색기"""
    
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.abspath(os.path.join(self.project_dir, '..', '..'))
        self.secrets_file = os.path.join(self.base_dir, 'secrets', 'my_sensitive_data.md')
        self.chromedriver_path = os.path.join(self.project_dir, 'chromedriver.exe')
        
        self.driver = None
        self.username = None
        self.password = None
        
        # 작업 결과 저장
        self.workflow_results = {
            'timestamp': datetime.now().isoformat(),
            'target_url': 'https://theterminalx.com/agent/enterprise',
            'steps_completed': [],
            'found_elements': {},
            'report_generation': {},
            'save_methods': {}
        }
        
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
            print(f"[LOGIN] 자격 증명 로드: {self.username}")
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
            print("[SETUP] Chrome WebDriver 준비 완료")
        except Exception as e:
            print(f"[ERROR] WebDriver 설정 실패: {e}")
            sys.exit(1)
    
    def login_terminalx(self):
        """TerminalX 로그인 후 enterprise 페이지 이동"""
        print("\n[STEP 1] TerminalX 로그인 및 Enterprise 페이지 진입")
        
        try:
            # 로그인 페이지로 이동
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(3)
            
            # 로그인 버튼 클릭
            try:
                login_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log In')]"))
                )
                login_btn.click()
                print("[LOGIN] 로그인 버튼 클릭 완료")
                time.sleep(2)
            except:
                print("[INFO] 이미 로그인된 상태이거나 로그인 버튼 없음")
            
            # 이메일 입력
            try:
                email_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='email']"))
                )
                email_field.clear()
                email_field.send_keys(self.username)
                print("[LOGIN] 이메일 입력 완료")
                time.sleep(1)
            except:
                print("[INFO] 이메일 필드를 찾을 수 없음 - 이미 로그인됨")
            
            # 비밀번호 입력
            try:
                password_field = self.driver.find_element(By.XPATH, "//input[@type='password']")
                password_field.clear()
                password_field.send_keys(self.password)
                print("[LOGIN] 비밀번호 입력 완료")
                time.sleep(1)
            except:
                print("[INFO] 비밀번호 필드를 찾을 수 없음")
            
            # 로그인 실행
            try:
                submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                submit_btn.click()
                print("[LOGIN] 로그인 실행")
                time.sleep(5)
            except:
                print("[INFO] Submit 버튼을 찾을 수 없음")
            
            # Enterprise 페이지 확인
            WebDriverWait(self.driver, 30).until(
                lambda driver: "theterminalx.com/agent/enterprise" in driver.current_url
            )
            
            print(f"[SUCCESS] Enterprise 페이지 진입: {self.driver.current_url}")
            self.workflow_results['steps_completed'].append('login_success')
            return True
            
        except Exception as e:
            print(f"[ERROR] 로그인 실패: {e}")
            return False
    
    def find_prompt_input(self):
        """프롬프트 입력창 찾기"""
        print("\n[STEP 2] 프롬프트 입력창 찾기")
        
        try:
            # textarea 찾기 (Ask Anything...)
            prompt_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "textarea"))
            )
            
            input_info = {
                'tag': prompt_input.tag_name,
                'placeholder': prompt_input.get_attribute('placeholder'),
                'class': prompt_input.get_attribute('class'),
                'is_enabled': prompt_input.is_enabled(),
                'is_displayed': prompt_input.is_displayed()
            }
            
            self.workflow_results['found_elements']['prompt_input'] = input_info
            print(f"[FOUND] 프롬프트 입력창: {input_info['placeholder']}")
            self.workflow_results['steps_completed'].append('prompt_input_found')
            
            return prompt_input
            
        except Exception as e:
            print(f"[ERROR] 프롬프트 입력창 찾기 실패: {e}")
            return None
    
    def input_test_prompt(self, prompt_input):
        """테스트 프롬프트 입력"""
        print("\n[STEP 3] 테스트 프롬프트 입력")
        
        test_prompt = "Give me a market summary for today with key events"
        
        try:
            prompt_input.clear()
            prompt_input.send_keys(test_prompt)
            print(f"[INPUT] 테스트 프롬프트 입력: {test_prompt}")
            time.sleep(2)
            
            # Enter 키로 전송
            prompt_input.send_keys(Keys.RETURN)
            print("[SUBMIT] 프롬프트 전송 (Enter)")
            
            self.workflow_results['report_generation']['test_prompt'] = test_prompt
            self.workflow_results['steps_completed'].append('prompt_submitted')
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 프롬프트 입력 실패: {e}")
            return False
    
    def wait_for_response(self):
        """응답 대기 및 결과 확인"""
        print("\n[STEP 4] 응답 대기 중...")
        
        start_time = time.time()
        timeout = 120  # 2분 대기
        
        try:
            while time.time() - start_time < timeout:
                # 응답이 나타났는지 확인
                try:
                    # 응답 영역 찾기 (다양한 선택자 시도)
                    response_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'response') or contains(@class, 'message') or contains(@class, 'result')]")
                    
                    if response_elements:
                        print(f"[RESPONSE] 응답 요소 {len(response_elements)}개 발견")
                        
                        # 응답 내용 수집
                        responses = []
                        for elem in response_elements[:3]:  # 처음 3개만
                            if elem.is_displayed() and elem.text.strip():
                                responses.append({
                                    'text': elem.text[:200] + '...' if len(elem.text) > 200 else elem.text,
                                    'class': elem.get_attribute('class')
                                })
                        
                        if responses:
                            self.workflow_results['report_generation']['responses'] = responses
                            self.workflow_results['steps_completed'].append('response_received')
                            print(f"[SUCCESS] 응답 수신 완료: {len(responses)}개 요소")
                            break
                    
                    time.sleep(3)
                    print(".", end="", flush=True)
                    
                except Exception as e:
                    time.sleep(3)
                    continue
            
            elapsed = time.time() - start_time
            print(f"\n[INFO] 대기 시간: {elapsed:.1f}초")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 응답 대기 실패: {e}")
            return False
    
    def explore_period_settings(self):
        """기간 설정 옵션 탐색"""
        print("\n[STEP 5] 기간 설정 옵션 찾기")
        
        period_elements = []
        
        # 다양한 기간 관련 요소 찾기
        selectors = [
            "//button[contains(text(), 'period') or contains(text(), 'time') or contains(text(), 'date')]",
            "//select[contains(@class, 'period') or contains(@class, 'time')]",
            "//input[@type='date']",
            "//div[contains(@class, 'date') or contains(@class, 'period')]"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for elem in elements:
                    if elem.is_displayed():
                        period_elements.append({
                            'selector': selector,
                            'tag': elem.tag_name,
                            'text': elem.text,
                            'class': elem.get_attribute('class'),
                            'type': elem.get_attribute('type')
                        })
            except:
                continue
        
        self.workflow_results['found_elements']['period_settings'] = period_elements
        print(f"[FOUND] 기간 관련 요소: {len(period_elements)}개")
        
        return period_elements
    
    def explore_save_options(self):
        """보고서 저장 옵션 탐색"""
        print("\n[STEP 6] 보고서 저장 옵션 찾기")
        
        save_elements = []
        
        # 저장 관련 요소 찾기
        selectors = [
            "//button[contains(text(), 'save') or contains(text(), 'download') or contains(text(), 'export')]",
            "//a[contains(@href, 'download') or contains(@href, 'export')]",
            "//div[contains(@class, 'save') or contains(@class, 'download')]"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for elem in elements:
                    if elem.is_displayed():
                        save_elements.append({
                            'selector': selector,
                            'tag': elem.tag_name,
                            'text': elem.text,
                            'class': elem.get_attribute('class'),
                            'href': elem.get_attribute('href')
                        })
            except:
                continue
        
        self.workflow_results['save_methods']['elements'] = save_elements
        print(f"[FOUND] 저장 관련 요소: {len(save_elements)}개")
        
        return save_elements
    
    def save_results(self):
        """결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.project_dir, f"enterprise_workflow_analysis_{timestamp}.json")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.workflow_results, f, indent=2, ensure_ascii=False)
            
            print(f"\n[SAVE] 분석 결과 저장: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"[ERROR] 결과 저장 실패: {e}")
            return None
    
    def run_workflow(self):
        """전체 워크플로우 실행"""
        print("[START] Enterprise 워크플로우 탐색 시작")
        print(f"[TARGET] {self.workflow_results['target_url']}")
        
        try:
            # 1. 로그인
            if not self.login_terminalx():
                return False
            
            # 2. 프롬프트 입력창 찾기
            prompt_input = self.find_prompt_input()
            if not prompt_input:
                return False
            
            # 3. 테스트 프롬프트 입력
            if not self.input_test_prompt(prompt_input):
                return False
            
            # 4. 응답 대기
            self.wait_for_response()
            
            # 5. 기간 설정 탐색
            self.explore_period_settings()
            
            # 6. 저장 옵션 탐색
            self.explore_save_options()
            
            # 7. 결과 저장
            output_file = self.save_results()
            
            print(f"\n[COMPLETE] Enterprise 워크플로우 분석 완료!")
            print(f"[RESULTS] 완료된 단계: {len(self.workflow_results['steps_completed'])}개")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 워크플로우 실행 실패: {e}")
            return False
        finally:
            self.close()
    
    def close(self):
        """브라우저 종료"""
        if self.driver:
            print("\n[CLOSE] 브라우저 종료")
            self.driver.quit()

if __name__ == "__main__":
    explorer = EnterpriseWorkflowExplorer()
    
    try:
        success = explorer.run_workflow()
        
        if success:
            print("\n[SUCCESS] Enterprise 페이지 워크플로우 분석 성공!")
        else:
            print("\n[FAILED] 워크플로우 분석 실패")
            
    except KeyboardInterrupt:
        print("\n[STOP] 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n[ERROR] 예외 발생: {e}")
    finally:
        explorer.close()