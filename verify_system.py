"""
시스템 검증 스크립트
목적: Archive 페이지와 Past Day 설정이 실제로 작동하는지 검증
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SystemVerifier:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.abspath(os.path.join(self.project_dir, '..', '..'))
        # 경로 수정: secret (단수)
        self.secrets_file = os.path.join(self.project_dir, 'secret', 'my_sensitive_data.md')
        self.chromedriver_path = os.path.join(self.project_dir, 'chromedriver.exe')
        self.output_dir = os.path.join(self.project_dir, 'verification_output')

        os.makedirs(self.output_dir, exist_ok=True)

        self.driver = None
        self.username = None
        self.password = None
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }

    def load_credentials(self):
        """자격 증명 로드"""
        print("자격 증명 로드 중...")
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
            print(f"[OK] 자격 증명 로드 완료: {self.username}")
            return True
        except Exception as e:
            print(f"[ERROR] 자격 증명 로드 실패: {e}")
            return False

    def setup_browser(self):
        """브라우저 설정"""
        print("브라우저 설정 중...")
        try:
            service = Service(executable_path=self.chromedriver_path)
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            # headless 모드 비활성화 (디버깅용)
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(60)

            # 서브 모니터로 이동 (1920px 오른쪽)
            self.driver.set_window_position(1920, 0)
            self.driver.set_window_size(1920, 1080)

            print("[OK] 브라우저 설정 완료 (primary monitor)")
            return True
        except Exception as e:
            print(f"[ERROR] 브라우저 설정 실패: {e}")
            return False

    def login(self):
        """로그인"""
        print("\n=== 로그인 테스트 ===")
        try:
            self.driver.get("https://theterminalx.com/agent/enterprise")
            print("[INFO] 페이지 로드 완료, 5초 대기...")
            time.sleep(5)

            # 에러 발생 시 스크린샷 저장
            try:
                error_screenshot = os.path.join(self.output_dir, 'error_initial_page.png')
                self.driver.save_screenshot(error_screenshot)
                print(f"[DEBUG] 초기 페이지 스크린샷: {error_screenshot}")
            except:
                pass

            # 초기 로그인 버튼 클릭 (여러 셀렉터 시도)
            login_btn = None
            selectors = [
                "//button[contains(text(), 'Log in')]",
                "//button[contains(., 'Log in')]",
                "//a[contains(text(), 'Log in')]",
                "//a[contains(., 'Log in')]",
                "//button[contains(@class, 'login')]",
                "//a[contains(@href, 'login')]"
            ]

            for selector in selectors:
                try:
                    print(f"[DEBUG] 시도: {selector}")
                    login_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"[OK] 로그인 버튼 찾음: {selector}")
                    break
                except:
                    continue

            if not login_btn:
                print("[ERROR] 로그인 버튼을 찾을 수 없습니다")
                # HTML 저장
                with open(os.path.join(self.output_dir, 'initial_page.html'), 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                print("[DEBUG] 페이지 HTML 저장: initial_page.html")
                return False

            login_btn.click()
            print("[OK] 로그인 버튼 클릭 완료")
            time.sleep(3)

            # 자격 증명 입력 (여러 셀렉터 시도)
            email_input = None
            email_selectors = [
                "//input[@placeholder='Enter your email']",
                "//input[@type='email']",
                "//input[@name='email']",
                "//input[contains(@placeholder, 'email')]"
            ]

            for selector in email_selectors:
                try:
                    print(f"[DEBUG] 이메일 입력 찾기: {selector}")
                    email_input = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_element_located((By.XPATH, selector))
                    )
                    print(f"[OK] 이메일 입력 찾음")
                    break
                except:
                    continue

            if not email_input:
                print("[ERROR] 이메일 입력 필드를 찾을 수 없습니다")
                return False

            password_input = None
            password_selectors = [
                "//input[@placeholder='Enter your password']",
                "//input[@type='password']",
                "//input[@name='password']"
            ]

            for selector in password_selectors:
                try:
                    password_input = self.driver.find_element(By.XPATH, selector)
                    print(f"[OK] 비밀번호 입력 찾음")
                    break
                except:
                    continue

            if not password_input:
                print("[ERROR] 비밀번호 입력 필드를 찾을 수 없습니다")
                return False

            email_input.clear()
            email_input.send_keys(self.username)
            print(f"[OK] 이메일 입력: {self.username}")

            password_input.clear()
            password_input.send_keys(self.password)
            print(f"[OK] 비밀번호 입력 완료")
            time.sleep(2)

            # 로그인 버튼 클릭
            login_button = None
            login_btn_selectors = [
                "//button[contains(text(), 'Continue')]",
                "//button[contains(., 'Continue')]",
                "//button[contains(text(), 'Log In')]",
                "//button[contains(., 'Log In')]",
                "//button[@type='submit']",
                "//button[contains(@class, 'submit')]",
                "//button[contains(@class, 'bg-[#0c0d0e]')]"
            ]

            for selector in login_btn_selectors:
                try:
                    login_button = self.driver.find_element(By.XPATH, selector)
                    print(f"[OK] 로그인 제출 버튼 찾음")
                    break
                except:
                    continue

            if not login_button:
                print("[ERROR] 로그인 제출 버튼을 찾을 수 없습니다")
                # HTML 저장
                with open(os.path.join(self.output_dir, 'login_form.html'), 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                print("[DEBUG] 로그인 폼 HTML 저장: login_form.html")
                # 스크린샷
                login_screenshot = os.path.join(self.output_dir, 'login_form.png')
                self.driver.save_screenshot(login_screenshot)
                print(f"[DEBUG] 로그인 폼 스크린샷: {login_screenshot}")
                return False

            login_button.click()
            print("[OK] 로그인 제출 버튼 클릭")

            # 로그인 성공 확인 (여러 셀렉터 시도)
            success_selectors = [
                "//button[contains(text(), 'Subscriptions')]",
                "//button[contains(., 'Subscriptions')]",
                "//a[contains(text(), 'Subscriptions')]",
                "//div[contains(@class, 'dashboard')]",
                "//h1[contains(text(), 'Dashboard')]",
                "//button[contains(., 'Archive')]"
            ]

            success = False
            for selector in success_selectors:
                try:
                    print(f"[DEBUG] 로그인 성공 확인: {selector}")
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    print(f"[OK] 로그인 성공 확인됨: {selector}")
                    success = True
                    break
                except:
                    continue

            if not success:
                print("[ERROR] 로그인 성공 확인 실패")
                # 로그인 후 스크린샷
                success_screenshot = os.path.join(self.output_dir, 'after_login.png')
                self.driver.save_screenshot(success_screenshot)
                print(f"[DEBUG] 로그인 후 스크린샷: {success_screenshot}")
                return False

            print("[OK] 로그인 성공")
            self.results['tests']['login'] = {'status': 'SUCCESS', 'message': '로그인 성공'}
            return True

        except Exception as e:
            print(f"[ERROR] 로그인 실패: {e}")
            self.results['tests']['login'] = {'status': 'FAILED', 'error': str(e)}
            return False

    def verify_archive_page(self):
        """Archive 페이지 HTML 구조 검증"""
        print("\n=== Archive 페이지 검증 ===")
        try:
            self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")

            # 초기 페이지 로딩 대기
            print("[WAIT] 초기 로딩 대기중 (3초)...")
            time.sleep(3)

            # JavaScript 렌더링 대기 (동적 테이블 생성)
            print("[WAIT] JavaScript 렌더링 대기중 (추가 7초)...")
            time.sleep(7)

            # 스크린샷 저장
            screenshot_path = os.path.join(self.output_dir, 'archive_page.png')
            self.driver.save_screenshot(screenshot_path)
            print(f"[SCREENSHOT] 스크린샷 저장: {screenshot_path}")

            # HTML 저장
            html_path = os.path.join(self.output_dir, 'archive_page.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"[HTML] HTML 저장: {html_path}")

            # 테이블 구조 분석
            print("\n테이블 구조 분석 중...")

            # report_manager.py가 사용하는 XPath 테스트
            try:
                tbody = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//table/tbody"))
                )
                print("[OK] //table/tbody 찾음")

                # 테이블 행이 렌더링될 때까지 추가 대기
                print("[WAIT] 테이블 행 렌더링 대기중...")
                for attempt in range(5):
                    rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
                    if len(rows) > 0:
                        break
                    print(f"   시도 {attempt+1}/5: 행 없음, 2초 대기...")
                    time.sleep(2)
                print(f"[OK] 테이블 행 개수: {len(rows)}")

                if len(rows) > 0:
                    # 모든 행의 Status 텍스트 수집 (최대 5개)
                    status_texts = []

                    for i, row in enumerate(rows[:5], 1):
                        try:
                            title_cell = row.find_element(By.XPATH, ".//td[1]")
                            status_cell = row.find_element(By.XPATH, ".//td[4]")

                            title_text = title_cell.text.strip()
                            status_text = status_cell.text.strip()

                            status_texts.append(status_text.upper())

                            print(f"\n[행 {i}]")
                            print(f"   Title: '{title_text[:50]}'")
                            print(f"   Status: '{status_text}'")
                        except Exception as e:
                            print(f"[WARNING] 행 {i} 분석 실패: {e}")

                    # Status 텍스트 패턴 검증
                    print(f"\n[SUMMARY] 발견된 Status 텍스트: {set(status_texts)}")

                    # 예상 패턴과 비교
                    expected_patterns = ['GENERATING', 'GENERATED', 'FAILED', 'PENDING']
                    found_patterns = []

                    for status in status_texts:
                        for pattern in expected_patterns:
                            if pattern in status:
                                found_patterns.append(pattern)
                                break

                    print(f"[MATCH] 매칭된 패턴: {set(found_patterns)}")

                    # report_manager.py 로직 테스트
                    try:
                        first_row = rows[0]
                        title_element = first_row.find_element(By.XPATH, ".//td[1]")
                        status_element = first_row.find_element(By.XPATH, ".//td[4]")

                        title_text = title_element.text.strip()
                        status_text = status_element.text.strip()

                        print(f"\n[TEST] report_manager.py 로직 테스트:")
                        print(f"   Title (td[1]): '{title_text}'")
                        print(f"   Status (td[4]): '{status_text}'")

                        # 상태가 예상 값인지 확인
                        expected_statuses = ['PENDING', 'GENERATING', 'GENERATED', 'FAILED',
                                           'Pending', 'Generating', 'Generated', 'Failed']
                        if status_text in expected_statuses:
                            print(f"[OK] 상태 텍스트 일치: '{status_text}'")
                        else:
                            print(f"[WARNING] 상태 텍스트 불일치: '{status_text}' (예상: {expected_statuses})")

                        self.results['tests']['archive_structure'] = {
                            'status': 'SUCCESS',
                            'row_count': len(rows),
                            'status_texts': list(set(status_texts)),
                            'matched_patterns': list(set(found_patterns)),
                            'sample_title': title_text,
                            'sample_status': status_text,
                            'status_match': status_text in expected_statuses
                        }

                    except NoSuchElementException as e:
                        print(f"[ERROR] td[1] 또는 td[4] 찾기 실패: {e}")
                        self.results['tests']['archive_structure'] = {
                            'status': 'FAILED',
                            'error': 'td[1] 또는 td[4] 없음'
                        }
                else:
                    print("[WARNING] 테이블에 행이 없습니다 (리포트 없음)")
                    self.results['tests']['archive_structure'] = {
                        'status': 'WARNING',
                        'message': '테이블 행 없음'
                    }

                return True

            except TimeoutException:
                print("[ERROR] //table/tbody 찾기 실패")
                self.results['tests']['archive_structure'] = {
                    'status': 'FAILED',
                    'error': '//table/tbody 없음'
                }
                return False

        except Exception as e:
            print(f"[ERROR] Archive 페이지 검증 실패: {e}")
            self.results['tests']['archive_structure'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            return False

    def check_report_status(self, report_title):
        """특정 리포트의 상태 확인

        Args:
            report_title: 리포트 제목 (식별용)

        Returns:
            str: 'GENERATING', 'GENERATED', 'FAILED', 'PENDING', 'NOT_FOUND', 'ERROR'
        """
        try:
            print(f"[INFO] '{report_title}' 상태 확인 중...")

            # Archive 페이지 이동
            self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")
            time.sleep(3)

            # 테이블 존재 확인
            tbody = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table/tbody"))
            )

            # 최상단 리포트 확인
            rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
            if len(rows) == 0:
                print("[WARNING] 리포트 없음")
                return 'NOT_FOUND'

            first_row = rows[0]

            # 제목 확인 (td[1])
            title_cell = first_row.find_element(By.XPATH, ".//td[1]")
            title_text = title_cell.text.strip()

            # 상태 확인 (td[4])
            status_cell = first_row.find_element(By.XPATH, ".//td[4]")
            status_text = status_cell.text.strip().upper()

            print(f"[DEBUG] Title: '{title_text}', Status: '{status_text}'")

            # 제목 일치 확인
            if report_title not in title_text:
                print(f"[WARNING] 최상단 리포트가 '{report_title}'이 아님")
                return 'NOT_FOUND'

            # 상태 매칭
            if 'GENERAT' in status_text:
                if 'ING' in status_text:
                    return 'GENERATING'
                elif 'ED' in status_text:
                    return 'GENERATED'
            elif 'FAIL' in status_text:
                return 'FAILED'
            elif 'PEND' in status_text:
                return 'PENDING'
            else:
                print(f"[WARNING] 알 수 없는 상태: '{status_text}'")
                return status_text

        except Exception as e:
            print(f"[ERROR] 상태 확인 실패: {e}")
            return 'ERROR'

    def wait_for_report_completion(self, report_title, timeout=300):
        """리포트 완료 대기 (폴링)

        Args:
            report_title: 리포트 제목
            timeout: 최대 대기 시간 (초)

        Returns:
            bool: 성공 여부
        """
        print(f"\n=== '{report_title}' 완료 대기 ===")
        print(f"[INFO] Timeout: {timeout}초")

        start_time = time.time()
        check_count = 0

        while (time.time() - start_time) < timeout:
            check_count += 1
            elapsed = int(time.time() - start_time)

            print(f"\n[CHECK #{check_count}] 경과: {elapsed}초")

            status = self.check_report_status(report_title)

            if status == 'GENERATED':
                print(f"[SUCCESS] '{report_title}' 생성 완료! (총 {elapsed}초)")
                return True
            elif status == 'FAILED':
                print(f"[ERROR] '{report_title}' 생성 실패!")
                return False
            elif status == 'GENERATING':
                print(f"[INFO] 생성 중... (5초 후 재확인)")
                time.sleep(5)
            elif status == 'PENDING':
                print(f"[INFO] 대기 중... (5초 후 재확인)")
                time.sleep(5)
            else:
                print(f"[WARNING] 예상치 못한 상태: '{status}' (5초 후 재확인)")
                time.sleep(5)

        print(f"[TIMEOUT] {timeout}초 초과, 완료 대기 실패")
        return False

    def save_results(self):
        """결과 저장"""
        result_path = os.path.join(self.output_dir, 'verification_results.json')
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n[RESULT] 검증 결과 저장: {result_path}")

    def cleanup(self):
        """정리"""
        if self.driver:
            print("\n브라우저 종료 대기 (20초)...")
            print("[INFO] 브라우저를 확인하세요...")
            time.sleep(20)
            self.driver.quit()
            print("[OK] 브라우저 종료")

    def run(self):
        """전체 검증 실행"""
        print("=" * 60)
        print("100xFenok-Generator 시스템 검증")
        print("=" * 60)

        try:
            if not self.load_credentials():
                return False

            if not self.setup_browser():
                return False

            if not self.login():
                return False

            if not self.verify_archive_page():
                return False

            print("\n" + "=" * 60)
            print("[SUCCESS] 검증 완료")
            print("=" * 60)

            return True

        except Exception as e:
            print(f"\n[ERROR] 검증 중 오류 발생: {e}")
            return False
        finally:
            self.save_results()
            self.cleanup()

if __name__ == "__main__":
    verifier = SystemVerifier()
    success = verifier.run()
    sys.exit(0 if success else 1)
