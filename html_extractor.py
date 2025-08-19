#!/usr/bin/env python3
"""
TerminalX HTML 추출기
- F12 개발자도구 자동화
- Element 검색 및 HTML 추출
- 파일 저장 자동화
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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class TerminalXHTMLExtractor:
    """TerminalX HTML 추출 자동화"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.base_dir = self.project_dir.parent.parent
        self.communication_dir = self.base_dir / "communication" / "shared" / "100xfenok"
        self.secrets_file = self.base_dir / "secrets" / "my_sensitive_data.md"
        self.chromedriver_path = self.project_dir / "chromedriver.exe"
        
        self.driver = None
        self.username = None
        self.password = None
        
        # HTML 추출 설정
        self.extraction_patterns = {
            "part1_part2": ".text-\\[\\#121212\\]",
            "additional_reports": "\\[\\&_sup\\]\\:text-\\[9px\\]"
        }
        
        self._ensure_directories()
        self._load_credentials()
    
    def _ensure_directories(self):
        """필요한 디렉터리 생성"""
        directories = [
            self.communication_dir / "002_terminalx",
            self.communication_dir / "003_terminalx"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
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
                
            logger.info("TerminalX 자격 증명 로드 완료")
            
        except Exception as e:
            logger.error(f"자격 증명 로드 실패: {e}")
            raise
    
    def setup_webdriver_with_devtools(self):
        """개발자도구 활성화된 WebDriver 설정"""
        try:
            service = Service(executable_path=str(self.chromedriver_path))
            options = webdriver.ChromeOptions()
            
            # 개발자도구 자동 열기
            options.add_argument('--auto-open-devtools-for-tabs')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(60)
            self.driver.maximize_window()
            
            logger.info("개발자도구 포함 WebDriver 설정 완료")
            return True
            
        except Exception as e:
            logger.error(f"WebDriver 설정 실패: {e}")
            return False
    
    def login_to_terminalx(self):
        """TerminalX 로그인"""
        try:
            logger.info("TerminalX 로그인 중...")
            self.driver.get("https://theterminalx.com/agent/enterprise")
            time.sleep(3)
            
            # 로그인 버튼 클릭
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in')]"))
            )
            login_button.click()
            time.sleep(2)
            
            # 로그인 폼 입력
            email_input = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter your email']"))
            )
            password_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Enter your password']")
            
            email_input.clear()
            email_input.send_keys(self.username)
            password_input.clear()
            password_input.send_keys(self.password)
            
            login_submit = self.driver.find_element(By.XPATH, "//button[contains(., 'Log In')]")
            login_submit.click()
            
            # 로그인 성공 확인
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Subscriptions')]"))
            )
            
            logger.info("TerminalX 로그인 성공")
            return True
            
        except Exception as e:
            logger.error(f"로그인 실패: {e}")
            return False
    
    def extract_html_from_reports_page(self, reports_urls, extraction_type="part1_part2"):
        """리포트 페이지들에서 HTML 추출"""
        extracted_files = []
        
        extraction_pattern = self.extraction_patterns.get(extraction_type, self.extraction_patterns["part1_part2"])
        
        for i, url in enumerate(reports_urls, 1):
            try:
                logger.info(f"리포트 {i}/{len(reports_urls)} 처리 중: {url}")
                
                # 페이지 이동
                self.driver.get(url)
                time.sleep(5)  # 페이지 로딩 대기
                
                # HTML 추출 시도
                extracted_html = self._extract_html_with_pattern(extraction_pattern)
                
                if extracted_html:
                    # 파일 저장
                    filename = f"{extraction_type}_{i:02d}.html"
                    output_dir = self.communication_dir / ("002_terminalx" if extraction_type == "part1_part2" else "003_terminalx")
                    output_file = output_dir / filename
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(extracted_html)
                    
                    extracted_files.append(str(output_file))
                    logger.info(f"HTML 추출 성공: {filename}")
                else:
                    logger.warning(f"HTML 추출 실패: 리포트 {i}")
                    
            except Exception as e:
                logger.error(f"리포트 {i} 처리 중 오류: {e}")
        
        return extracted_files
    
    def _extract_html_with_pattern(self, css_pattern):
        """CSS 패턴으로 HTML 추출"""
        try:
            # F12 개발자도구 활성화 (이미 자동 열림)
            time.sleep(2)
            
            # Console 탭으로 이동하여 JavaScript 실행
            # 패턴에 맞는 요소들 찾기
            script = f"""
            let elements = document.querySelectorAll('[class*="{css_pattern.replace("\\", "")}"]');
            let html = '';
            elements.forEach(el => {{
                html += el.outerHTML + '\\n';
            }});
            return html;
            """
            
            # 스크립트 실행으로 HTML 추출
            extracted_html = self.driver.execute_script(script)
            
            if extracted_html and extracted_html.strip():
                return extracted_html
            else:
                # 대체 방법: 전체 페이지에서 패턴 검색
                return self._extract_html_alternative_method(css_pattern)
                
        except Exception as e:
            logger.error(f"HTML 추출 중 오류: {e}")
            return self._extract_html_alternative_method(css_pattern)
    
    def _extract_html_alternative_method(self, css_pattern):
        """대체 HTML 추출 방법"""
        try:
            # 전체 페이지 HTML 가져오기
            page_html = self.driver.page_source
            
            # BeautifulSoup으로 파싱하여 패턴 매칭
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page_html, 'html.parser')
            
            # 클래스 이름에 패턴이 포함된 요소들 찾기
            pattern_clean = css_pattern.replace("\\", "").replace("[", "").replace("]", "")
            matching_elements = []
            
            for element in soup.find_all():
                if element.get('class'):
                    class_str = ' '.join(element['class'])
                    if pattern_clean in class_str:
                        matching_elements.append(element)
            
            if matching_elements:
                # 매칭된 요소들을 HTML로 변환
                extracted_html = '\n'.join([str(el) for el in matching_elements])
                return extracted_html
            else:
                logger.warning(f"패턴 '{pattern_clean}'에 매칭되는 요소를 찾을 수 없음")
                return None
                
        except Exception as e:
            logger.error(f"대체 HTML 추출 방법 실패: {e}")
            return None
    
    def create_test_reports(self, count=3):
        """테스트용 리포트 생성"""
        logger.info(f"{count}개 테스트 리포트 생성 중...")
        
        report_urls = []
        
        for i in range(count):
            try:
                # 폼 페이지로 이동
                form_url = "https://theterminalx.com/agent/enterprise/report/form/10"
                self.driver.get(form_url)
                time.sleep(3)
                
                # 테스트 제목 입력
                test_title = f"Test HTML Extract {datetime.now().strftime('%H%M%S')}_{i+1}"
                
                title_field = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@placeholder=\"What's the title?\"]"))
                )
                title_field.clear()
                title_field.send_keys(test_title)
                
                # 간단한 프롬프트 입력
                try:
                    prompt_area = self.driver.find_element(By.XPATH, "//textarea")
                    prompt_area.clear()
                    prompt_area.send_keys("Test prompt for HTML extraction")
                except:
                    logger.warning("프롬프트 영역을 찾을 수 없음")
                
                # 리포트 생성 버튼 클릭
                try:
                    generate_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Generate') or contains(text(), 'Create')]")
                    generate_button.click()
                    
                    # 리포트 생성 대기
                    time.sleep(10)
                    
                    # 생성된 리포트 URL 수집
                    current_url = self.driver.current_url
                    if "report" in current_url and current_url not in report_urls:
                        report_urls.append(current_url)
                        logger.info(f"테스트 리포트 {i+1} 생성 완료: {current_url}")
                    
                except Exception as e:
                    logger.warning(f"리포트 {i+1} 생성 실패: {e}")
                    
            except Exception as e:
                logger.error(f"테스트 리포트 {i+1} 생성 중 오류: {e}")
        
        return report_urls
    
    def run_html_extraction_test(self):
        """HTML 추출 전체 테스트"""
        logger.info("HTML 추출 테스트 시작")
        
        results = {
            "success": False,
            "login": False,
            "test_reports_created": 0,
            "html_files_extracted": [],
            "errors": []
        }
        
        try:
            # 1. WebDriver 설정
            if not self.setup_webdriver_with_devtools():
                results["errors"].append("WebDriver 설정 실패")
                return results
            
            # 2. 로그인
            if not self.login_to_terminalx():
                results["errors"].append("로그인 실패")
                return results
            
            results["login"] = True
            
            # 3. 테스트 리포트 생성
            test_report_urls = self.create_test_reports(2)  # 2개만 생성
            results["test_reports_created"] = len(test_report_urls)
            
            if not test_report_urls:
                results["errors"].append("테스트 리포트 생성 실패")
                return results
            
            # 4. HTML 추출
            extracted_files = self.extract_html_from_reports_page(test_report_urls, "part1_part2")
            results["html_files_extracted"] = extracted_files
            
            # 5. 성공 여부 판단
            if extracted_files:
                results["success"] = True
                logger.info(f"HTML 추출 성공: {len(extracted_files)}개 파일")
            else:
                results["errors"].append("HTML 파일 추출 실패")
            
        except Exception as e:
            logger.error(f"HTML 추출 테스트 중 오류: {e}")
            results["errors"].append(str(e))
        
        finally:
            if self.driver:
                logger.info("브라우저 유지 (수동 확인을 위해)")
                # self.driver.quit()  # 디버깅을 위해 브라우저 유지
        
        return results

def main():
    """메인 실행 함수"""
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    extractor = TerminalXHTMLExtractor()
    
    try:
        results = extractor.run_html_extraction_test()
        
        # 결과 출력
        print("\n" + "="*60)
        print("HTML 추출 테스트 결과")
        print("="*60)
        
        print(f"전체 성공: {results['success']}")
        print(f"로그인 성공: {results['login']}")
        print(f"테스트 리포트 생성: {results['test_reports_created']}개")
        print(f"HTML 파일 추출: {len(results['html_files_extracted'])}개")
        
        if results['html_files_extracted']:
            print("\n추출된 파일들:")
            for file_path in results['html_files_extracted']:
                print(f"  - {file_path}")
        
        if results['errors']:
            print("\n오류:")
            for error in results['errors']:
                print(f"  - {error}")
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단됨")
    except Exception as e:
        print(f"실행 실패: {e}")

if __name__ == "__main__":
    main()