#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalX 직접 작업 도구 - browser_controller.py 활용
로그인 -> past day -> 프롬프트 -> 보고서 -> 다운로드
"""
import os
import sys
import time
from datetime import datetime
import browser_controller as bc

# 인코딩 문제 방지
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class DirectTerminalXWorker:
    """기존 browser_controller를 활용한 직접 작업"""
    
    def __init__(self):
        self.browser = bc.BrowserController()
        print("[INIT] 브라우저 컨트롤러 준비 완료")
    
    def run_full_workflow(self):
        """전체 워크플로우 실행"""
        print("🚀 TerminalX 전체 워크플로우 시작")
        print("순서: 로그인 → past day → 프롬프트 → 보고서 → 다운로드")
        print()
        
        try:
            # 1. 브라우저 시작
            if not self.browser.start_browser():
                print("❌ 브라우저 시작 실패")
                return False
            
            # 2. 로그인
            print("\n[1/5] 로그인 진행...")
            if not self.browser.login_terminalx():
                print("❌ 로그인 실패")
                return False
            print("✅ 로그인 완료!")
            
            # 3. Enterprise 페이지 확인
            print("\n[2/5] Enterprise 페이지 확인...")
            current_url = self.browser.driver.current_url
            if "enterprise" not in current_url.lower():
                self.browser.navigate_to("https://theterminalx.com/agent/enterprise")
            print(f"✅ 페이지 위치: {current_url}")
            
            # 4. 수동 작업 안내
            print("\n[3/5] 수동 작업 필요:")
            print("👀 브라우저가 열렸습니다!")
            print("📝 다음 작업을 직접 수행하세요:")
            print("   - 기간 설정을 'past day'로 변경")
            print("   - 프롬프트 입력: 'Give me a market summary for today'")
            print("   - 보고서 생성 완료까지 대기")
            print("   - 다운로드/저장 옵션 확인")
            print()
            
            # 5. 사용자 완료 대기
            print("[4/5] 작업 완료 대기...")
            input("✅ 위 작업들을 완료한 후 Enter를 누르세요...")
            
            print("\n[5/5] 작업 완료!")
            print("🎉 TerminalX 워크플로우 성공!")
            
            # 브라우저 열어두기
            print("\n🖥️ 브라우저를 계속 열어둡니다")
            print("⏹️ 종료하려면 Ctrl+C를 누르세요")
            
            while True:
                time.sleep(30)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 브라우저 실행 중...")
            
        except KeyboardInterrupt:
            print("\n⏹️ 사용자가 종료함")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        finally:
            self.browser.close_browser()
            print("🔚 브라우저 종료")

if __name__ == "__main__":
    worker = DirectTerminalXWorker()
    worker.run_full_workflow()