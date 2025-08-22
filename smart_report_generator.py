#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스마트 TerminalX 리포트 생성기
answer URL에서 기다리고 저장하는 방식으로 완전 재작성
"""
import os
import sys
import time
import json
import re
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

class SmartReportGenerator:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.abspath(os.path.join(self.project_dir, '..', '..'))
        self.secrets_file = os.path.join(self.base_dir, 'secrets', 'my_sensitive_data.md')
        self.output_dir = os.path.join(self.project_dir, 'smart_reports_output')
        self.chromedriver_path = os.path.join(self.project_dir, 'chromedriver.exe')
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.driver = None
        self.username = None
        self.password = None
        self.report_count = 0
        
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
        """Chrome WebDriver 설정"""
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
    
    def generate_and_wait_report(self, prompt_text, title, report_id):
        """리포트 생성하고 answer URL에서 기다리면서 저장"""
        print(f"\n=== 스마트 리포트 {report_id}: {title} ===")
        
        try:
            # 1단계: 메인 페이지에서 프롬프트 입력
            print("   1단계: 메인 페이지 접근")
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(3)
            
            # 프롬프트 입력 필드 찾기
            prompt_input = None
            prompt_selectors = ["//textarea", "//input[@type='text']"]
            
            for selector in prompt_selectors:
                try:
                    prompt_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if not prompt_input:
                print("   [ERROR] 프롬프트 입력 필드 없음")
                return False
            
            # 프롬프트 입력
            prompt_input.clear()
            prompt_input.send_keys(prompt_text)
            time.sleep(1)
            print(f"   프롬프트 입력: {prompt_text[:30]}...")
            
            # 1.5단계: 기간을 Past day로 변경 (필수!)
            print("   기간을 Past day로 변경 중...")
            try:
                # Any time 요소 찾아서 클릭
                time_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Any time') or contains(text(), 'time')]")
                if time_elements:
                    time_elements[0].click()
                    time.sleep(2)
                    print("   기간 드롭다운 열림")
                    
                    # Past day, 1 day, Today 중 하나 찾아서 클릭
                    day_options = [
                        "//*[contains(text(), 'Past day')]",
                        "//*[contains(text(), '1 day')]", 
                        "//*[contains(text(), 'Today')]",
                        "//*[contains(text(), '24 hours')]"
                    ]
                    
                    day_selected = False
                    for option_xpath in day_options:
                        try:
                            day_element = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, option_xpath))
                            )
                            day_element.click()
                            print(f"   기간을 Past day로 설정 완료: {option_xpath}")
                            day_selected = True
                            time.sleep(1)
                            break
                        except:
                            continue
                    
                    if not day_selected:
                        print("   [WARNING] Past day 옵션을 찾을 수 없음, Any time으로 진행")
                else:
                    print("   [WARNING] 기간 설정 요소를 찾을 수 없음")
                    
            except Exception as e:
                print(f"   [WARNING] 기간 설정 실패 (계속 진행): {e}")
            
            # 2단계: Generate 버튼 클릭 또는 엔터
            print("   2단계: Generate 버튼 클릭")
            try:
                generate_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate')]"))
                )
                generate_btn.click()
                print("   Generate 버튼 클릭 완료")
            except:
                # 엔터키로 제출
                prompt_input.send_keys(Keys.RETURN)
                print("   엔터키로 제출 완료")
            
            time.sleep(3)
            
            # 3단계: answer URL로 이동 확인
            print("   3단계: answer URL 이동 확인")
            current_url = self.driver.current_url
            print(f"   현재 URL: {current_url}")
            
            if "/answer/" not in current_url:
                print("   [ERROR] answer URL로 이동하지 않음")
                return False
            
            answer_url = current_url
            print(f"   [SUCCESS] answer URL 확인: {answer_url}")
            
            # 4단계: answer URL에서 결과 대기 (절대 다른 곳으로 이동하지 않음)
            print("   4단계: answer URL에서 결과 대기 중...")
            
            result_content = ""
            wait_time = 0
            max_wait_time = 120  # 2분 대기
            
            while wait_time < max_wait_time:
                try:
                    # 현재 URL 확인 (이동되었다면 다시 돌아가기)
                    if self.driver.current_url != answer_url:
                        print(f"   [WARNING] URL 변경됨, answer URL로 복귀: {answer_url}")
                        self.driver.get(answer_url)
                        time.sleep(2)
                    
                    # 결과 텍스트 찾기
                    page_source = self.driver.page_source
                    
                    # 로딩 표시가 없고 충분한 내용이 있는지 확인
                    if ("loading" not in page_source.lower() and 
                        "generating" not in page_source.lower() and
                        len(page_source) > 50000):
                        
                        # 답변 텍스트 추출
                        result_content = self.extract_answer_content(page_source)
                        
                        if result_content and len(result_content) > 200:
                            print(f"   [SUCCESS] 결과 생성 완료 (길이: {len(result_content)})")
                            break
                    
                    time.sleep(2)
                    wait_time += 2
                    
                    if wait_time % 10 == 0:
                        print(f"   대기 중... ({wait_time}/{max_wait_time}초)")
                        
                except Exception as e:
                    print(f"   대기 중 오류 (계속): {e}")
                    time.sleep(2)
                    wait_time += 2
            
            # 5단계: 결과 저장
            if result_content:
                self.save_smart_report(title, prompt_text, result_content, answer_url, report_id)
                print(f"   [SUCCESS] 리포트 {report_id} 완료 및 저장")
                self.report_count += 1
                return True
            else:
                print(f"   [ERROR] 리포트 {report_id} 타임아웃 또는 내용 없음")
                return False
                
        except Exception as e:
            print(f"   [ERROR] 리포트 {report_id} 생성 실패: {e}")
            return False
    
    def extract_answer_content(self, page_source):
        """페이지에서 답변 내용 추출"""
        try:
            # HTML 태그 제거
            import re
            # 스크립트와 스타일 태그 제거
            page_source = re.sub(r'<script[^>]*>.*?</script>', '', page_source, flags=re.DOTALL)
            page_source = re.sub(r'<style[^>]*>.*?</style>', '', page_source, flags=re.DOTALL)
            
            # HTML 태그 모두 제거
            clean_text = re.sub(r'<[^>]+>', ' ', page_source)
            
            # 불필요한 공백 정리
            clean_text = re.sub(r'\s+', ' ', clean_text)
            
            # 답변 부분만 추출 (보통 긴 텍스트가 답변)
            sentences = clean_text.split('.')
            long_sentences = [s.strip() for s in sentences if len(s.strip()) > 50]
            
            if long_sentences:
                result = '. '.join(long_sentences[:20])  # 처음 20문장
                return result[:3000]  # 최대 3000자
            
            return clean_text[:3000] if len(clean_text) > 200 else ""
            
        except Exception as e:
            print(f"   내용 추출 오류: {e}")
            return ""
    
    def save_smart_report(self, title, prompt, response, url, report_id):
        """리포트 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"smart_report_{report_id:02d}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        report_data = {
            "id": report_id,
            "type": "smart_report",
            "title": title,
            "prompt": prompt,
            "response": response,
            "answer_url": url,
            "generated_at": timestamp,
            "content_length": len(response)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"   저장 완료: {filename}")
    
    def generate_all_reports(self):
        """6개 리포트 생성"""
        print("\n🚀 스마트 리포트 6개 생성 시작")
        
        prompts = [
            ("Market Summary", "Give me a comprehensive market summary for today including major indices and key movers"),
            ("Economic Analysis", "Analyze current economic indicators and their market impact"),
            ("Top Stocks", "Identify today's top performing and worst performing stocks with analysis"),
            ("Sector Review", "Provide sector analysis showing outperforming and underperforming sectors"),
            ("Currency Update", "Analyze major currency movements and forex trends today"),
            ("Crypto Report", "Give me cryptocurrency market update including Bitcoin, Ethereum and altcoins")
        ]
        
        successful_reports = 0
        for i, (title, prompt) in enumerate(prompts, 1):
            print(f"\n--- 진행률: {i}/6 ---")
            if self.generate_and_wait_report(prompt, title, i):
                successful_reports += 1
            else:
                print(f"   리포트 {i} 실패, 계속 진행...")
            
            # 요청 간 간격
            time.sleep(3)
        
        print(f"\n✅ 스마트 리포트 완료: {successful_reports}/6개 성공")
        print(f"📁 저장 위치: {self.output_dir}")
        return successful_reports
    
    def cleanup(self):
        """리소스 정리"""
        if self.driver:
            self.driver.quit()
        print("[INFO] 리소스 정리 완료")

def main():
    print("=== 스마트 TerminalX 리포트 생성기 ===")
    
    generator = SmartReportGenerator()
    
    try:
        # 로그인
        if not generator.login_terminalx():
            print("❌ 로그인 실패로 종료")
            return
        
        # 리포트 6개 생성
        success_count = generator.generate_all_reports()
        
        print(f"\n🏆 최종 결과: {success_count}개 리포트 성공!")
        
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
    finally:
        generator.cleanup()

if __name__ == "__main__":
    main()