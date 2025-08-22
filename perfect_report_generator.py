#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
완벽한 TerminalX 리포트 생성기
정확한 Past Day 설정 + 완전한 로딩 대기 + 6개 기본보고서 생성
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

# 인코딩 문제 완전 방지
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class PerfectReportGenerator:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.abspath(os.path.join(self.project_dir, '..', '..'))
        self.secrets_file = os.path.join(self.base_dir, 'secrets', 'my_sensitive_data.md')
        self.output_dir = os.path.join(self.project_dir, 'perfect_reports_output')
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
            
            print("[SUCCESS] TerminalX 로그인 성공")
            return True
            
        except Exception as e:
            print(f"[ERROR] 로그인 실패: {e}")
            return False
    
    def set_past_day_period(self):
        """정확한 Past Day 설정"""
        print("   Past Day 기간 설정...")
        try:
            # 1. 드롭다운 클릭 (Any Time 또는 현재 설정)
            period_dropdown = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'cursor-pointer') and contains(@class, 'flex-row')]//div[contains(@class, 'text-[#262626]')]"))
            )
            period_dropdown.click()
            time.sleep(2)
            print("   드롭다운 열림")
            
            # 2. Past Day 옵션 선택
            past_day_option = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'text-[#262626]') and contains(text(), 'Past Day')]"))
            )
            past_day_option.click()
            time.sleep(1)
            print("   [SUCCESS] Past Day 선택 완료!")
            return True
            
        except Exception as e:
            print(f"   [ERROR] Past Day 설정 실패: {e}")
            return False
    
    def generate_perfect_report(self, prompt_text, title, report_id):
        """완벽한 리포트 생성"""
        print(f"\n=== 완벽한 리포트 {report_id}: {title} ===")
        
        try:
            # 1. 메인 페이지로 이동
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(3)
            
            # 2. 프롬프트 입력
            prompt_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea | //input[@type='text']"))
            )
            prompt_input.clear()
            prompt_input.send_keys(prompt_text)
            print(f"   프롬프트 입력: {prompt_text[:30]}...")
            
            # 3. Past Day 설정
            if self.set_past_day_period():
                print("   Past Day 설정 성공")
            else:
                print("   Past Day 설정 실패, 계속 진행...")
            
            # 4. Generate 버튼 클릭
            try:
                generate_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate')]"))
                )
                generate_btn.click()
                print("   Generate 버튼 클릭 완료")
            except:
                prompt_input.send_keys(Keys.RETURN)
                print("   엔터키로 제출")
            
            time.sleep(3)
            
            # 5. answer URL 확인
            current_url = self.driver.current_url
            print(f"   URL: {current_url}")
            
            if "/answer/" not in current_url:
                print("   [ERROR] answer URL로 이동하지 않음")
                return False
            
            # 6. 완전한 답변 로딩 대기 (개선됨)
            print("   완전한 답변 로딩 대기 중...")
            answer_content = self.wait_for_complete_answer(current_url)
            
            if answer_content:
                # 7. 저장
                self.save_perfect_report(title, prompt_text, answer_content, current_url, report_id)
                print(f"   [SUCCESS] 리포트 {report_id} 완료!")
                self.report_count += 1
                return True
            else:
                print(f"   [ERROR] 리포트 {report_id} 답변 로딩 실패")
                return False
                
        except Exception as e:
            print(f"   [ERROR] 리포트 {report_id} 생성 실패: {e}")
            return False
    
    def wait_for_complete_answer(self, answer_url, max_wait=180):
        """완전한 답변 로딩까지 대기 (3분)"""
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait:
            try:
                # URL 확인 및 복귀
                if self.driver.current_url != answer_url:
                    print(f"   URL 변경됨, 복귀: {answer_url}")
                    self.driver.get(answer_url)
                    time.sleep(3)
                
                # 페이지 소스 분석
                page_source = self.driver.page_source
                
                # 로딩 중 표시 확인
                loading_indicators = [
                    "processing your query",
                    "loading",
                    "generating", 
                    "searching",
                    "P r o c e s s i n g"
                ]
                
                is_loading = any(indicator.lower() in page_source.lower() for indicator in loading_indicators)
                
                # 충분한 내용과 완료 상태 확인
                has_content = len(page_source) > 80000  # 더 큰 페이지 요구
                
                if not is_loading and has_content:
                    print("   로딩 완료 감지, 내용 추출 중...")
                    content = self.extract_final_answer(page_source)
                    
                    if content and len(content) > 500:  # 최소 500자 이상
                        elapsed = int(time.time() - start_time)
                        print(f"   [SUCCESS] 완전한 답변 로딩 완료 ({elapsed}초, 길이: {len(content)})")
                        return content
                
                # 진행 상황 출력
                elapsed = int(time.time() - start_time)
                if elapsed % 15 == 0:  # 15초마다
                    print(f"   대기 중... ({elapsed}/{max_wait}초, 로딩:{is_loading}, 크기:{len(page_source)})")
                
                time.sleep(3)
                
            except Exception as e:
                print(f"   대기 중 오류: {e}")
                time.sleep(3)
        
        print("   [TIMEOUT] 답변 로딩 타임아웃")
        return None
    
    def extract_final_answer(self, page_source):
        """최종 답변 추출"""
        try:
            # HTML 태그 제거 및 정리
            import re
            
            # 스크립트, 스타일 제거
            page_source = re.sub(r'<script[^>]*>.*?</script>', '', page_source, flags=re.DOTALL)
            page_source = re.sub(r'<style[^>]*>.*?</style>', '', page_source, flags=re.DOTALL)
            
            # HTML 태그 제거
            clean_text = re.sub(r'<[^>]+>', ' ', page_source)
            clean_text = re.sub(r'\s+', ' ', clean_text)
            
            # 의미있는 문장들만 추출
            sentences = [s.strip() for s in clean_text.split('.') if len(s.strip()) > 30]
            
            if sentences:
                # 처음 50문장 또는 5000자 중 작은 것
                result = '. '.join(sentences[:50])
                return result[:5000] if len(result) > 5000 else result
            
            return clean_text[:5000] if len(clean_text) > 1000 else ""
            
        except Exception as e:
            print(f"   내용 추출 오류: {e}")
            return ""
    
    def save_perfect_report(self, title, prompt, response, url, report_id):
        """완벽한 리포트 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"perfect_report_{report_id:02d}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        report_data = {
            "id": report_id,
            "type": "perfect_report",
            "title": title,
            "prompt": prompt,
            "response": response,
            "answer_url": url,
            "generated_at": timestamp,
            "content_length": len(response),
            "period_setting": "Past Day"
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"   저장 완료: {filename}")
    
    def generate_6_basic_reports(self):
        """6개 기본보고서 생성"""
        print("\n🚀 6개 완벽한 기본보고서 생성 시작")
        
        reports = [
            ("Market Summary", "Give me a comprehensive market summary for today with major indices, key movers, and market sentiment analysis"),
            ("Economic Indicators", "Analyze today's key economic indicators, employment data, inflation metrics, and their market impact"),
            ("Top Stock Analysis", "Identify and analyze today's top performing stocks and worst performing stocks with detailed reasons"),
            ("Sector Performance", "Provide comprehensive sector analysis showing outperforming and underperforming sectors with data"),
            ("Currency & Forex", "Analyze major currency movements, forex trends, and international market impacts for today"),
            ("Cryptocurrency Report", "Complete cryptocurrency market analysis including Bitcoin, Ethereum, and major altcoins performance")
        ]
        
        successful_reports = 0
        for i, (title, prompt) in enumerate(reports, 1):
            print(f"\n--- 진행률: {i}/6 ---")
            
            if self.generate_perfect_report(prompt, title, i):
                successful_reports += 1
                print(f"✅ 리포트 {i}/{6} 성공!")
            else:
                print(f"❌ 리포트 {i}/{6} 실패")
            
            # 요청 간 간격 (서버 부하 방지)
            if i < 6:
                print("   다음 리포트를 위해 10초 대기...")
                time.sleep(10)
        
        print(f"\n🏆 최종 결과: {successful_reports}/6개 성공!")
        print(f"📁 저장 위치: {self.output_dir}")
        
        # 생성된 파일 목록
        files = os.listdir(self.output_dir)
        perfect_files = [f for f in files if f.startswith('perfect_report_')]
        print(f"📋 생성된 파일: {len(perfect_files)}개")
        
        return successful_reports
    
    def cleanup(self):
        """리소스 정리"""
        if self.driver:
            self.driver.quit()
        print("[INFO] 리소스 정리 완료")

def main():
    print("=== 완벽한 TerminalX 리포트 생성기 ===")
    print("Past Day 설정 + 완전한 로딩 대기")
    
    generator = PerfectReportGenerator()
    
    try:
        # 로그인
        if not generator.login_terminalx():
            print("❌ 로그인 실패")
            return
        
        # 6개 기본보고서 생성
        success_count = generator.generate_6_basic_reports()
        
        if success_count >= 4:
            print("\n🎉 목표 달성! 4개 이상 성공")
        elif success_count >= 2:
            print("\n👍 부분 성공! 계속 개선 필요")
        else:
            print("\n😞 목표 미달성, 문제 분석 필요")
        
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
    finally:
        generator.cleanup()

if __name__ == "__main__":
    main()