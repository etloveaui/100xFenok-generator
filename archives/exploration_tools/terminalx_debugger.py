#!/usr/bin/env python3
"""
TerminalX 리다이렉션 문제 디버깅 및 해결
- 단계별 접근으로 리다이렉션 문제 진단
- 개선된 retry 로직
"""

import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TerminalXDebugger:
    """TerminalX 리다이렉션 문제 진단 및 해결"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.base_dir = self.project_dir.parent.parent
        self.secrets_file = self.base_dir / "secrets" / "my_sensitive_data.md"
        self.chromedriver_path = self.project_dir / "chromedriver.exe"
        
        self.driver = None
        self.username = None
        self.password = None
        
        self._load_credentials()
        self._setup_webdriver()
    
    def _load_credentials(self):
        """로그인 자격증명 로드"""
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
                        
            if not self.username or not self.password:
                raise ValueError("TerminalX 자격 증명을 찾을 수 없습니다.")
                
            logger.info("✅ TerminalX 자격 증명 로드 완료")
            
        except Exception as e:
            logger.error(f"❌ 자격 증명 로드 실패: {e}")
            raise
    
    def _setup_webdriver(self):
        """WebDriver 설정"""
        try:
            service = Service(executable_path=str(self.chromedriver_path))
            options = webdriver.ChromeOptions()
            
            # 디버깅을 위해 헤드리스 모드 비활성화
            # options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(60)
            self.driver.maximize_window()
            
            logger.info("✅ WebDriver 설정 완료")
            
        except Exception as e:
            logger.error(f"❌ WebDriver 설정 실패: {e}")
            raise
    
    def test_login_flow(self):
        """로그인 플로우 테스트"""
        logger.info("🔍 TerminalX 로그인 플로우 테스트 시작")
        
        try:
            # 1. 메인 페이지 접근
            logger.info("1️⃣ 메인 페이지 접근 중...")
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(3)
            
            # 현재 URL 확인
            current_url = self.driver.current_url
            logger.info(f"📍 현재 URL: {current_url}")
            
            # 2. 로그인 버튼 찾기
            logger.info("2️⃣ 로그인 버튼 찾는 중...")
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in')]"))
            )
            login_button.click()
            logger.info("✅ 초기 로그인 버튼 클릭 완료")
            time.sleep(2)
            
            # 3. 로그인 폼 입력
            logger.info("3️⃣ 로그인 폼 입력 중...")
            email_input = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter your email']"))
            )
            password_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Enter your password']")
            
            email_input.clear()
            email_input.send_keys(self.username)
            logger.info(f"📧 이메일 입력: {self.username}")
            
            password_input.clear()
            password_input.send_keys(self.password)
            logger.info("🔐 비밀번호 입력 완료")
            
            # 4. 로그인 실행
            login_submit = self.driver.find_element(By.XPATH, "//button[contains(., 'Log In')]")
            login_submit.click()
            logger.info("✅ 로그인 버튼 클릭")
            
            # 5. 로그인 성공 확인
            logger.info("5️⃣ 로그인 성공 확인 중...")
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Subscriptions')]"))
            )
            logger.info("✅ 로그인 성공 확인됨")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 로그인 실패: {e}")
            return False
    
    def test_form_access_methods(self):
        """다양한 방법으로 폼 접근 테스트"""
        logger.info("🔍 폼 접근 방법 테스트 시작")
        
        methods = [
            ("직접 URL", self._test_direct_url_access),
            ("대시보드에서 네비게이션", self._test_dashboard_navigation),  
            ("아카이브에서 새 리포트", self._test_archive_new_report),
            ("메뉴에서 Reports", self._test_menu_reports)
        ]
        
        successful_methods = []
        
        for method_name, test_method in methods:
            logger.info(f"🧪 {method_name} 방법 테스트 중...")
            try:
                if test_method():
                    successful_methods.append(method_name)
                    logger.info(f"✅ {method_name} 방법 성공")
                else:
                    logger.warning(f"❌ {method_name} 방법 실패")
            except Exception as e:
                logger.error(f"❌ {method_name} 방법 오류: {e}")
        
        return successful_methods
    
    def _test_direct_url_access(self):
        """직접 URL 접근 테스트"""
        target_url = "https://theterminalx.com/agent/enterprise/report/form/10"
        
        logger.info(f"🔗 직접 URL 접근: {target_url}")
        self.driver.get(target_url)
        time.sleep(5)
        
        current_url = self.driver.current_url
        logger.info(f"📍 도착한 URL: {current_url}")
        
        # 리다이렉션 확인
        if "archive" in current_url:
            logger.warning("⚠️ 아카이브 페이지로 리다이렉션됨")
            return False
        
        # 폼 필드 확인
        try:
            title_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder=\"What's the title?\"]"))
            )
            logger.info("✅ Report Title 필드 발견")
            return True
        except TimeoutException:
            logger.error("❌ Report Title 필드를 찾을 수 없음")
            return False
    
    def _test_dashboard_navigation(self):
        """대시보드에서 네비게이션 테스트"""
        try:
            # 대시보드로 이동
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(3)
            
            # Reports 메뉴 찾기
            reports_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Reports') or contains(., 'Report')]"))
            )
            reports_button.click()
            time.sleep(2)
            
            # New Report 또는 Create Report 찾기
            new_report_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'report/form') or contains(text(), 'New') or contains(text(), 'Create')]"))
            )
            new_report_link.click()
            time.sleep(3)
            
            # 폼 필드 확인
            title_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder=\"What's the title?\"]"))
            )
            
            return True
            
        except Exception as e:
            logger.error(f"대시보드 네비게이션 실패: {e}")
            return False
    
    def _test_archive_new_report(self):
        """아카이브에서 새 리포트 접근 테스트"""
        try:
            # 아카이브 페이지로 이동
            self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")
            time.sleep(3)
            
            # 새 리포트 버튼 찾기
            new_report_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'form') or contains(text(), 'New') or contains(text(), 'Create')]"))
            )
            new_report_button.click()
            time.sleep(3)
            
            # 폼 필드 확인
            title_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder=\"What's the title?\"]"))
            )
            
            return True
            
        except Exception as e:
            logger.error(f"아카이브에서 새 리포트 접근 실패: {e}")
            return False
    
    def _test_menu_reports(self):
        """메인 메뉴에서 Reports 접근 테스트"""
        try:
            # 메인 페이지로 이동
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(3)
            
            # 네비게이션 메뉴에서 Reports 찾기
            reports_menu = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(text(), 'Reports') or contains(@href, 'report')]"))
            )
            reports_menu.click()
            time.sleep(3)
            
            # 새 리포트 생성 링크 찾기
            create_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'form') or contains(text(), 'Create')]"))
            )
            create_link.click()
            time.sleep(3)
            
            # 폼 필드 확인
            title_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder=\"What's the title?\"]"))
            )
            
            return True
            
        except Exception as e:
            logger.error(f"메뉴에서 Reports 접근 실패: {e}")
            return False
    
    def test_form_interaction(self):
        """폼 상호작용 테스트"""
        logger.info("🔍 폼 상호작용 테스트 시작")
        
        try:
            # 테스트 데이터
            test_title = f"Test Report {datetime.now().strftime('%H%M%S')}"
            
            # Title 입력
            title_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder=\"What's the title?\"]"))
            )
            title_field.clear()
            title_field.send_keys(test_title)
            logger.info(f"📝 Title 입력 완료: {test_title}")
            
            # 다른 필드들 확인
            fields_to_check = [
                ("Reference Date Start", "//input[@type='date' or contains(@placeholder, 'Start')]"),
                ("Reference Date End", "//input[@type='date' or contains(@placeholder, 'End')]"),
                ("Prompt Area", "//textarea"),
                ("Upload Section", "//input[@type='file']")
            ]
            
            for field_name, xpath in fields_to_check:
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    logger.info(f"✅ {field_name} 필드 발견")
                except NoSuchElementException:
                    logger.warning(f"⚠️ {field_name} 필드 없음")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 폼 상호작용 테스트 실패: {e}")
            return False
    
    def run_complete_diagnostic(self):
        """완전한 진단 실행"""
        logger.info("🚀 TerminalX 완전 진단 시작")
        
        results = {
            "login_success": False,
            "successful_access_methods": [],
            "form_interaction": False,
            "recommendations": []
        }
        
        try:
            # 1. 로그인 테스트
            results["login_success"] = self.test_login_flow()
            
            if not results["login_success"]:
                results["recommendations"].append("로그인 자격증명 또는 로그인 플로우 확인 필요")
                return results
            
            # 2. 폼 접근 방법 테스트
            results["successful_access_methods"] = self.test_form_access_methods()
            
            if not results["successful_access_methods"]:
                results["recommendations"].append("모든 폼 접근 방법 실패 - 권한 또는 웹사이트 변경 확인 필요")
                return results
            
            # 3. 폼 상호작용 테스트  
            results["form_interaction"] = self.test_form_interaction()
            
            # 4. 추천사항 생성
            if results["successful_access_methods"]:
                best_method = results["successful_access_methods"][0]
                results["recommendations"].append(f"추천 접근 방법: {best_method}")
            
            if not results["form_interaction"]:
                results["recommendations"].append("폼 필드 구조 변경 가능성 - XPath 업데이트 필요")
            
        except Exception as e:
            logger.error(f"❌ 진단 중 오류: {e}")
            results["recommendations"].append(f"진단 중 오류 발생: {e}")
        
        finally:
            if self.driver:
                logger.info("🔚 브라우저 종료 (5초 후)")
                time.sleep(5)  # 결과 확인을 위한 대기
                self.driver.quit()
        
        return results

def main():
    """메인 실행 함수"""
    debugger = TerminalXDebugger()
    
    try:
        results = debugger.run_complete_diagnostic()
        
        # 결과 출력
        print("\n" + "="*60)
        print("🔍 TerminalX 진단 결과")
        print("="*60)
        
        print(f"✅ 로그인 성공: {results['login_success']}")
        print(f"✅ 폼 상호작용: {results['form_interaction']}")
        
        if results['successful_access_methods']:
            print(f"✅ 성공한 접근 방법:")
            for method in results['successful_access_methods']:
                print(f"  - {method}")
        else:
            print("❌ 성공한 접근 방법 없음")
        
        if results['recommendations']:
            print(f"\n💡 추천사항:")
            for rec in results['recommendations']:
                print(f"  - {rec}")
        
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 중단됨")
    except Exception as e:
        print(f"❌ 진단 실행 실패: {e}")

if __name__ == "__main__":
    main()