#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalX 수동 작업 도우미
- 브라우저만 열어주고 사용자가 직접 작업할 수 있게 도움
"""
import os
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# 인코딩 문제 방지
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class ManualBrowserHelper:
    """사용자 수동 작업을 위한 브라우저 도우미"""
    
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.abspath(os.path.join(self.project_dir, '..', '..'))
        self.secrets_file = os.path.join(self.base_dir, 'secrets', 'my_sensitive_data.md')
        self.chromedriver_path = os.path.join(self.project_dir, 'chromedriver.exe')
        
        self.driver = None
        self.username = None
        self.password = None
        
        self.load_credentials()
        
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
            print(f"[INFO] 로그인 계정: {self.username}")
        except Exception as e:
            print(f"[ERROR] 자격 증명 로드 실패: {e}")
    
    def open_browser(self):
        """브라우저 열기 (사용자가 볼 수 있게)"""
        try:
            service = Service(executable_path=self.chromedriver_path)
            options = webdriver.ChromeOptions()
            
            # 브라우저 보이기 설정
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            # headless 모드 제거 -> 브라우저가 보임
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(60)
            self.driver.maximize_window()
            
            print("[SUCCESS] 브라우저 열기 완료 (사용자 볼 수 있음)")
            return True
            
        except Exception as e:
            print(f"[ERROR] 브라우저 열기 실패: {e}")
            return False
    
    def navigate_to_enterprise(self):
        """Enterprise 페이지로 이동"""
        try:
            self.driver.get("https://theterminalx.com/agent/enterprise")
            print("[NAV] Enterprise 페이지로 이동")
            print("[INFO] 이제 수동으로 작업하세요:")
            print("  1. 로그인 확인")
            print("  2. 프롬프트 입력: 'Give me a market summary for today'")
            print("  3. 기간을 'past day'로 변경")
            print("  4. 보고서 완료 전후 차이 확인")
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"[ERROR] 페이지 이동 실패: {e}")
            return False
    
    def print_credentials(self):
        """로그인 정보 출력"""
        print(f"\n[CREDENTIALS] 로그인 정보:")
        print(f"  이메일: {self.username}")
        print(f"  비밀번호: {self.password}")
        print()
    
    def wait_for_user(self):
        """사용자 작업 완료 대기"""
        print("\n" + "="*60)
        print("🖥️  브라우저가 열렸습니다!")
        print("🔍 다음 작업을 직접 수행하세요:")
        print()
        print("1. 로그인 상태 확인 (필요시 로그인)")
        print("2. 메인 입력창에 테스트 프롬프트 입력:")
        print("   -> 'Give me a market summary for today'")
        print("3. 기간 설정을 'past day'로 변경")
        print("4. 보고서 생성 완료까지 대기")
        print("5. 완료 전후 화면 차이점 관찰")
        print("6. 저장/다운로드 옵션 확인")
        print()
        print("✅ 작업 완료되면 이 터미널에서 Enter를 누르세요")
        print("❌ 중단하려면 Ctrl+C를 누르세요")
        print("="*60)
        
        try:
            input("\n작업 완료 후 Enter를 누르세요...")
            print("\n[DONE] 사용자 작업 완료")
            return True
        except KeyboardInterrupt:
            print("\n[STOP] 사용자가 중단함")
            return False
    
    def close_browser(self):
        """브라우저 종료"""
        if self.driver:
            print("\n[CLOSE] 브라우저 종료 중...")
            self.driver.quit()
            print("[CLOSED] 브라우저 종료 완료")
    
    def run_manual_session(self):
        """수동 작업 세션 실행"""
        print("[START] 수동 브라우저 세션 시작")
        print(f"[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 1. 브라우저 열기
            if not self.open_browser():
                return False
            
            # 2. Enterprise 페이지 이동
            if not self.navigate_to_enterprise():
                return False
            
            # 3. 로그인 정보 표시
            self.print_credentials()
            
            # 4. 사용자 작업 대기
            success = self.wait_for_user()
            
            return success
            
        except Exception as e:
            print(f"[ERROR] 세션 실행 실패: {e}")
            return False
        finally:
            # 브라우저 종료는 사용자가 Enter 누른 후에만
            pass

if __name__ == "__main__":
    helper = ManualBrowserHelper()
    
    try:
        print("\n🚀 TerminalX 수동 작업 도우미")
        print("브라우저를 열어서 직접 작업할 수 있게 도와드립니다.")
        
        success = helper.run_manual_session()
        
        if success:
            print("\n✅ 수동 작업 세션 완료!")
        else:
            print("\n❌ 수동 작업 세션 실패")
            
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 중단됨")
    finally:
        helper.close_browser()