#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalX 브라우저 계속 열어두기
- 브라우저 열고 닫지 않음
- 사용자가 직접 작업 가능
"""
import os
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# 인코딩 문제 방지
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class StayOpenBrowser:
    """브라우저를 계속 열어두는 도우미"""
    
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
            print(f"[CREDENTIALS] 로그인 계정: {self.username}")
            print(f"[CREDENTIALS] 비밀번호: {self.password}")
        except Exception as e:
            print(f"[ERROR] 자격 증명 로드 실패: {e}")
    
    def open_browser_and_stay(self):
        """브라우저 열고 계속 열어두기"""
        try:
            service = Service(executable_path=self.chromedriver_path)
            options = webdriver.ChromeOptions()
            
            # 브라우저 보이기 설정
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            # headless 모드 제거 -> 브라우저가 보임
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(60)
            self.driver.maximize_window()
            
            print("[SUCCESS] 브라우저 열기 완료 (계속 열려있음)")
            
            # Enterprise 페이지로 이동
            self.driver.get("https://theterminalx.com/agent/enterprise")
            print("[NAV] Enterprise 페이지로 이동 완료")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 브라우저 열기 실패: {e}")
            return False
    
    def print_instructions(self):
        """작업 지시사항 출력"""
        print("\n" + "="*80)
        print("🚀 TerminalX Enterprise 페이지가 열렸습니다!")
        print()
        print("📋 다음 순서로 작업하세요:")
        print("1. 🔑 로그인하기 (필요시)")
        print(f"   - 이메일: {self.username}")
        print(f"   - 비밀번호: {self.password}")
        print()
        print("2. ⏰ 기간 설정을 'past day'로 변경")
        print("   - 페이지에서 날짜/기간 설정 옵션 찾기")
        print("   - 기본값에서 'past day'로 변경")
        print()
        print("3. 💬 프롬프트 입력")
        print("   - 메인 입력창: 'Give me a market summary for today'")
        print("   - Enter 키 또는 전송 버튼 클릭")
        print()
        print("4. ⏳ 보고서 생성 대기")
        print("   - 완료될 때까지 기다리기")
        print("   - 생성 전후 화면 차이점 관찰")
        print()
        print("5. 💾 보고서 다운로드")
        print("   - 저장/다운로드/내보내기 버튼 찾기")
        print("   - 가능한 형식으로 저장")
        print()
        print("⚠️  브라우저는 계속 열려있습니다!")
        print("❌ 작업 완료하면 이 스크립트를 Ctrl+C로 종료하세요")
        print("="*80)
    
    def keep_alive(self):
        """브라우저 계속 살아있게 유지"""
        try:
            while True:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 브라우저 실행 중... (Ctrl+C로 종료)")
                time.sleep(30)  # 30초마다 상태 출력
                
                # 브라우저가 살아있는지 확인
                try:
                    current_url = self.driver.current_url
                    print(f"[INFO] 현재 페이지: {current_url}")
                except:
                    print("[WARNING] 브라우저가 닫혔을 수 있습니다")
                    break
                    
        except KeyboardInterrupt:
            print("\n[STOP] 사용자가 종료를 요청했습니다")
            return True
        except Exception as e:
            print(f"[ERROR] Keep alive 실패: {e}")
            return False
    
    def close(self):
        """브라우저 종료"""
        if self.driver:
            print("\n[CLOSING] 브라우저 종료 중...")
            try:
                self.driver.quit()
                print("[CLOSED] 브라우저 종료 완료")
            except:
                print("[INFO] 브라우저가 이미 종료됨")

if __name__ == "__main__":
    browser = StayOpenBrowser()
    
    try:
        print("🌟 TerminalX 브라우저 계속 열어두기")
        print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 브라우저 열기
        if browser.open_browser_and_stay():
            # 2. 작업 지시사항 출력
            browser.print_instructions()
            
            # 3. 브라우저 계속 열어두기
            browser.keep_alive()
        else:
            print("❌ 브라우저 열기 실패")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        browser.close()