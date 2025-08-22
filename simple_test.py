#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 TerminalX 직접 접근 테스트
인코딩 문제 완전 방지 + 실제 사이트 동작 확인
"""
import os
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 인코딩 문제 완전 방지
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class SimpleTerminalXTest:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.chromedriver_path = os.path.join(self.project_dir, 'chromedriver.exe')
        self.driver = None
        self.setup_webdriver()
    
    def setup_webdriver(self):
        """Chrome WebDriver 설정 (인코딩 안전)"""
        try:
            service = Service(executable_path=self.chromedriver_path)
            options = webdriver.ChromeOptions()
            # 인코딩 관련 설정 추가
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-web-security')
            options.add_argument('--lang=en-US')
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            self.driver.maximize_window()
            print("[SUCCESS] WebDriver 설정 완료")
            return True
        except Exception as e:
            print(f"[ERROR] WebDriver 설정 실패: {str(e)}")
            return False
    
    def test_direct_access(self):
        """https://theterminalx.com/agent/enterprise 직접 접근 테스트"""
        print("\n=== TerminalX 직접 접근 테스트 ===")
        
        try:
            # 1. 메인 페이지 접근
            print("1. TerminalX Enterprise 페이지 접근 중...")
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(5)
            
            current_url = self.driver.current_url
            page_title = self.driver.title
            print(f"   현재 URL: {current_url}")
            print(f"   페이지 제목: {page_title}")
            
            # 2. 페이지 로드 상태 확인
            page_source_length = len(self.driver.page_source)
            print(f"   페이지 소스 길이: {page_source_length}")
            
            if page_source_length < 1000:
                print("[WARNING] 페이지가 제대로 로드되지 않았을 수 있습니다")
                return False
            
            # 3. 주요 요소 확인
            print("2. 주요 요소 찾기...")
            
            # 로그인 버튼 확인
            try:
                login_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Log') or contains(text(), 'login') or contains(text(), 'Login')]")
                print(f"   로그인 관련 요소: {len(login_elements)}개 발견")
                for i, elem in enumerate(login_elements[:3]):
                    print(f"   - 요소 {i+1}: {elem.text}")
            except:
                print("   로그인 요소 찾기 실패")
            
            # 입력 필드 확인
            try:
                input_fields = self.driver.find_elements(By.TAG_NAME, "input")
                print(f"   입력 필드: {len(input_fields)}개 발견")
            except:
                print("   입력 필드 찾기 실패")
            
            # 버튼 확인
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                print(f"   버튼: {len(buttons)}개 발견")
            except:
                print("   버튼 찾기 실패")
            
            print("\n[SUCCESS] 직접 접근 테스트 완료")
            return True
            
        except Exception as e:
            print(f"[ERROR] 직접 접근 테스트 실패: {str(e)}")
            return False
    
    def cleanup(self):
        """리소스 정리"""
        if self.driver:
            self.driver.quit()
            print("[INFO] WebDriver 종료 완료")

def main():
    print("=== TerminalX 간단 테스트 시작 ===")
    
    tester = SimpleTerminalXTest()
    
    try:
        success = tester.test_direct_access()
        
        if success:
            print("\n✅ 모든 테스트 통과!")
        else:
            print("\n❌ 테스트 실패")
            
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n예상치 못한 오류: {str(e)}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()