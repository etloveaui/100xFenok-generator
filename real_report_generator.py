#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 TerminalX 리포트 생성 및 저장 시스템
기본 리포트 6개 + 메인 리포트 6개 = 총 12개 리포트 자동 생성
"""
import os
import sys
import time
import json
from datetime import datetime, timedelta
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

class RealReportGenerator:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.abspath(os.path.join(self.project_dir, '..', '..'))
        self.secrets_file = os.path.join(self.base_dir, 'secrets', 'my_sensitive_data.md')
        self.output_dir = os.path.join(self.project_dir, 'real_reports_output')
        self.chromedriver_path = os.path.join(self.project_dir, 'chromedriver.exe')
        
        # 출력 디렉터리 생성
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
            # 브라우저를 보이게 설정 (headless 제거)
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--lang=en-US')
            # 사용자가 볼 수 있도록 브라우저 창 유지
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(60)
            self.driver.maximize_window()
            print("[SUCCESS] WebDriver 설정 완료 (브라우저 창 보이기 모드)")
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
            
            # 로그인 성공 확인
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
    
    def generate_basic_report(self, prompt_text, title, report_id):
        """기본 리포트 생성 (즉시 저장)"""
        print(f"\n=== 기본 리포트 {report_id} 생성: {title} ===")
        
        try:
            # 메인 페이지로 이동
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(5)  # 더 오래 대기
            initial_url = self.driver.current_url
            print(f"   초기 URL: {initial_url}")
            
            # 프롬프트 입력 필드 찾기 (더 넓은 선택자)
            prompt_selectors = [
                "//textarea[contains(@placeholder, 'Ask')]",
                "//input[contains(@placeholder, 'Ask')]", 
                "//textarea[contains(@placeholder, 'prompt')]",
                "//input[contains(@placeholder, 'prompt')]",
                "//textarea",
                "//input[@type='text']"
            ]
            
            prompt_input = None
            for selector in prompt_selectors:
                try:
                    prompt_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    print(f"   프롬프트 입력 필드 발견: {selector}")
                    break
                except:
                    continue
            
            if not prompt_input:
                print("   [ERROR] 프롬프트 입력 필드를 찾을 수 없음")
                return False
            
            # 프롬프트 입력
            prompt_input.clear()
            prompt_input.send_keys(prompt_text)
            time.sleep(2)
            print(f"   프롬프트 입력 완료: {prompt_text[:50]}...")
            
            # 기간 설정 (Any time → Today)
            try:
                print("   기간 설정 시도...")
                time_period_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Any time') or contains(text(), 'time')]")
                if time_period_elements:
                    time_period_elements[0].click()
                    time.sleep(2)
                    
                    # Today 옵션 찾아서 클릭
                    today_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Today') or contains(text(), '1 day')]")
                    if today_elements:
                        today_elements[0].click()
                        print("   기간을 Today로 설정 완료")
                        time.sleep(1)
            except Exception as e:
                print(f"   기간 설정 실패 (계속 진행): {e}")
            
            # Generate 버튼 찾기 (더 정확한 선택자들)
            generate_selectors = [
                "//button[contains(text(), 'Generate')]",
                "//button[contains(text(), 'GENERATE')]", 
                "//button[contains(@class, 'generate')]",
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//button[contains(text(), 'Send')]",
                "//button[contains(text(), 'Search')]"
            ]
            
            generate_clicked = False
            for selector in generate_selectors:
                try:
                    generate_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"   Generate 버튼 발견: {selector}")
                    generate_btn.click()
                    generate_clicked = True
                    print(f"   Generate 버튼 클릭 완료!")
                    break
                except:
                    continue
            
            if not generate_clicked:
                # 엔터키로 시도
                print("   Generate 버튼 못 찾음, 엔터키로 시도...")
                prompt_input.send_keys(Keys.RETURN)
                generate_clicked = True
                print("   엔터키로 제출 완료")
            
            # URL 변경 확인 (중요!)
            time.sleep(3)
            new_url = self.driver.current_url
            print(f"   URL 변경 확인: {initial_url} → {new_url}")
            
            if new_url != initial_url:
                print("   [SUCCESS] URL이 변경됨 - 리포트 생성 시작된 것으로 판단")
            else:
                print("   [WARNING] URL이 변경되지 않음 - 다시 시도 필요할 수 있음")
            
            # 결과 대기 (최대 60초)
            print("   결과 생성 대기 중...")
            response_found = False
            for wait_time in range(60):
                time.sleep(1)
                try:
                    # 응답 결과 찾기
                    response_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'response') or contains(@class, 'result') or contains(@class, 'output')]")
                    if response_elements:
                        response_text = ""
                        for elem in response_elements:
                            if elem.text and len(elem.text) > 50:
                                response_text = elem.text
                                break
                        
                        if response_text:
                            response_found = True
                            break
                            
                    # 페이지 소스에서 직접 찾기
                    page_source = self.driver.page_source
                    if len(page_source) > 100000 and "market" in page_source.lower():
                        response_text = self.extract_response_from_source(page_source)
                        if response_text:
                            response_found = True
                            break
                            
                except Exception as e:
                    continue
                    
                if wait_time % 10 == 0:
                    print(f"   대기 중... ({wait_time}/60초)")
            
            if response_found:
                # 리포트 저장
                self.save_basic_report(title, prompt_text, response_text, report_id)
                print(f"   [SUCCESS] 기본 리포트 {report_id} 완료 및 저장")
                self.report_count += 1
                return True
            else:
                print(f"   [ERROR] 리포트 {report_id} 응답 타임아웃")
                return False
                
        except Exception as e:
            print(f"   [ERROR] 기본 리포트 {report_id} 생성 실패: {e}")
            return False
    
    def extract_response_from_source(self, page_source):
        """페이지 소스에서 응답 텍스트 추출"""
        try:
            # 간단한 패턴으로 응답 텍스트 찾기
            import re
            patterns = [
                r'<div[^>]*class="[^"]*response[^"]*"[^>]*>(.*?)</div>',
                r'<p[^>]*>(.*?market.*?)</p>',
                r'<div[^>]*>(.*?analysis.*?)</div>'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE | re.DOTALL)
                if matches:
                    # HTML 태그 제거
                    clean_text = re.sub(r'<[^>]+>', '', matches[0])
                    if len(clean_text) > 100:
                        return clean_text[:2000]  # 처음 2000자만
            return None
        except:
            return None
    
    def save_basic_report(self, title, prompt, response, report_id):
        """기본 리포트 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"basic_report_{report_id}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        report_data = {
            "id": report_id,
            "type": "basic_report",
            "title": title,
            "prompt": prompt,
            "response": response,
            "generated_at": timestamp,
            "url": self.driver.current_url
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"   저장 완료: {filename}")
    
    def generate_all_basic_reports(self):
        """기본 리포트 6개 생성"""
        print("\n🚀 기본 리포트 6개 생성 시작")
        
        basic_prompts = [
            ("Market Summary Today", "Give me a comprehensive market summary for today including major indices, key movers, and market sentiment"),
            ("Economic Indicators", "Provide an analysis of current economic indicators and their impact on markets"),
            ("Top Stock Movers", "Identify and analyze the top stock movers today with reasons for their performance"),
            ("Sector Analysis", "Give me a detailed sector analysis showing which sectors are outperforming and underperforming"),
            ("Currency Markets", "Analyze current currency market trends and major forex movements"),
            ("Crypto Market Update", "Provide an update on cryptocurrency markets including Bitcoin, Ethereum, and major altcoins")
        ]
        
        successful_reports = 0
        for i, (title, prompt) in enumerate(basic_prompts, 1):
            if self.generate_basic_report(prompt, title, i):
                successful_reports += 1
            
            # 요청 간 간격
            time.sleep(5)
            
            # limit 체크
            if i % 2 == 0:
                print(f"\n💡 진행률: {i}/6 완료. 계속하려면 사용자 확인 필요할 수 있음")
        
        print(f"\n✅ 기본 리포트 완료: {successful_reports}/6개 성공")
        return successful_reports
    
    def cleanup(self):
        """리소스 정리"""
        if self.driver:
            self.driver.quit()
        print("[INFO] 리소스 정리 완료")

def main():
    print("=== 실제 TerminalX 리포트 생성 시스템 ===")
    
    generator = RealReportGenerator()
    
    try:
        # 로그인
        if not generator.login_terminalx():
            print("❌ 로그인 실패로 종료")
            return
        
        # 기본 리포트 6개 생성
        success_count = generator.generate_all_basic_reports()
        
        print(f"\n🏆 최종 결과: {success_count}개 리포트 성공적으로 생성 및 저장!")
        print(f"📁 저장 위치: {generator.output_dir}")
        
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
    finally:
        generator.cleanup()

if __name__ == "__main__":
    main()