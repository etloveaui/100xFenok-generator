import os
import json
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip

from report_manager import Report, ReportBatchManager

class FenokReportGenerator:
    def __init__(self):
        # 1. 경로 표준화: 스크립트 위치를 기준으로 모든 경로를 설정
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.abspath(os.path.join(self.project_dir, '..', '..'))

        # secrets 파일 경로: projects/100xFenok-generator/secret/
        self.secrets_file = os.path.join(self.project_dir, 'secret', 'my_sensitive_data.md')
        self.generated_html_dir = os.path.join(self.project_dir, 'generated_html')
        self.generated_json_dir = os.path.join(self.project_dir, 'generated_json')
        self.input_data_dir = os.path.join(self.project_dir, 'input_data')
        self.lexi_convert_dir = os.path.join(self.base_dir, 'projects', 'Python_Lexi_Convert')
        self.integrated_json_instruction_file = os.path.join(self.project_dir, 'docs', 'Instruction_Json.md')
        self.template_html_path = os.path.join(self.base_dir, 'projects', '100xFenok', '100x', 'daily-wrap', '100x-daily-wrap-template.html')
        self.output_daily_wrap_dir = os.path.join(self.base_dir, 'projects', '100xFenok', '100x', 'daily-wrap')
        self.main_html_path = os.path.join(self.base_dir, 'projects', '100xFenok', 'main.html')
        self.version_js_path = os.path.join(self.base_dir, 'projects', '100xFenok', 'version.js')
        self.chromedriver_path = os.path.join(self.project_dir, 'chromedriver.exe') # Chromedriver 경로 명시

        self.driver = None
        self.terminalx_username = None
        self.terminalx_password = None

        self._load_credentials()
        self._setup_webdriver()
        self._create_directories()

    def _load_credentials(self):
        """secrets/my_sensitive_data.md에서 TerminalX 로그인 자격 증명을 로드합니다."""
        try:
            with open(self.secrets_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 정규 표현식 등을 사용하여 사용자 이름과 비밀번호를 파싱해야 합니다.
                # 여기서는 간단한 예시로 직접 파싱하는 로직을 가정합니다.
                # 실제 구현에서는 더 견고한 파싱 로직이 필요합니다.
                if "The TerminalX Credentials" in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if "The TerminalX Credentials" in line:
                            self.terminalx_username = lines[i+1].split(':')[-1].strip().replace('`', '').replace('**', '')
                            self.terminalx_password = lines[i+2].split(':')[-1].strip().replace('`', '').replace('**', '')
                            break
            if not self.terminalx_username or not self.terminalx_password:
                raise ValueError("TerminalX 자격 증명을 찾을 수 없습니다.")
            print("TerminalX 자격 증명 로드 완료.")
        except FileNotFoundError:
            print(f"오류: {self.secrets_file} 파일을 찾을 수 없습니다.")
            exit()
        except Exception as e:
            print(f"자격 증명 로드 중 오류 발생: {e}")
            exit()

    def _setup_webdriver(self):
        """Selenium WebDriver를 설정합니다."""
        try:
            # 2. Chromedriver 경로 수정: 명시적으로 정의된 경로 사용
            service = Service(executable_path=self.chromedriver_path)
            options = webdriver.ChromeOptions()
            # headless 모드 (백그라운드 실행)
            # options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(60) # 페이지 로드 타임아웃 60초

            # 좌측 FHD 모니터 (1920x1080)
            self.driver.set_window_position(-1920, 0)
            self.driver.maximize_window()
            print("WebDriver 설정 완료 (좌측 FHD 모니터, 전체 화면).")
        except Exception as e:
            print(f"WebDriver 설정 중 오류 발생: {e}")
            exit()

    def _create_directories(self):
        """필요한 출력 디렉토리를 생성합니다."""
        os.makedirs(self.generated_html_dir, exist_ok=True)
        os.makedirs(self.generated_json_dir, exist_ok=True)
        print("출력 디렉토리 생성 완료.")

    def _login_terminalx(self):
        """TerminalX에 로그인합니다. (verify_system.py 검증된 multi-fallback 전략)"""
        print("TerminalX 로그인 시도...")
        try:
            self.driver.get("https://theterminalx.com/agent/enterprise")
            print("페이지 로드 완료, 5초 대기...")
            time.sleep(5)

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
                    login_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"로그인 버튼 찾음: {selector}")
                    break
                except:
                    continue

            if not login_btn:
                print("로그인 버튼을 찾을 수 없습니다.")
                return False

            login_btn.click()
            print("로그인 버튼 클릭 완료")
            time.sleep(3)

            # 이메일 입력 (여러 셀렉터 시도)
            email_input = None
            email_selectors = [
                "//input[@placeholder='Enter your email']",
                "//input[@type='email']",
                "//input[@name='email']",
                "//input[contains(@placeholder, 'email')]"
            ]

            for selector in email_selectors:
                try:
                    email_input = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_element_located((By.XPATH, selector))
                    )
                    print("이메일 입력 필드 찾음")
                    break
                except:
                    continue

            if not email_input:
                print("이메일 입력 필드를 찾을 수 없습니다.")
                return False

            # 비밀번호 입력 (여러 셀렉터 시도)
            password_input = None
            password_selectors = [
                "//input[@placeholder='Enter your password']",
                "//input[@type='password']",
                "//input[@name='password']"
            ]

            for selector in password_selectors:
                try:
                    password_input = self.driver.find_element(By.XPATH, selector)
                    print("비밀번호 입력 필드 찾음")
                    break
                except:
                    continue

            if not password_input:
                print("비밀번호 입력 필드를 찾을 수 없습니다.")
                return False

            email_input.clear()
            email_input.send_keys(self.terminalx_username)
            print(f"이메일 입력: {self.terminalx_username}")

            password_input.clear()
            password_input.send_keys(self.terminalx_password)
            print("비밀번호 입력 완료")
            time.sleep(2)

            # 로그인 제출 버튼 (여러 셀렉터 시도)
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
                    print("로그인 제출 버튼 찾음")
                    break
                except:
                    continue

            if not login_button:
                print("로그인 제출 버튼을 찾을 수 없습니다.")
                return False

            login_button.click()
            print("로그인 제출 버튼 클릭")

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
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    print(f"로그인 성공 확인: {selector}")
                    success = True
                    break
                except:
                    continue

            if not success:
                print("로그인 성공 확인 실패")
                return False

            print("TerminalX 로그인 성공")
            return True

        except Exception as e:
            print(f"로그인 실패: {e}")
            return False

    def _input_date_directly(self, date_str: str, is_start: bool):
        """
        Hybrid V2: contenteditable 세그먼트에 직접 입력.
        is_start=True => 시작일, False => 종료일
        """
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        seg_css = "[contenteditable='true'][aria-label*='시작일']" if is_start \
                  else "[contenteditable='true'][aria-label*='종료일']"

        wait   = WebDriverWait(self.driver, 10)
        fields = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, seg_css)))
        fields.sort(key=lambda e: e.location['x'])   # 월·일·년 순 정렬

        for elm, txt in zip(fields, (dt.strftime("%m"), dt.strftime("%d"), dt.strftime("%Y"))):
            elm.click(); time.sleep(0.05)
            elm.send_keys(Keys.CONTROL, 'a', Keys.DELETE, txt, Keys.TAB)

        # 3. 버그 수정: 주석의 특수문자 제거
        # 숨은 input 동기화 백업
        self.driver.execute_script("""
            const n=arguments[2]?'start-date-hidden':'end-date-hidden';
            const h=document.querySelector(`input[name='${n}']`);
            if(h){h.value=arguments[0];
                 h.dispatchEvent(new Event('input',{bubbles:true}));
                 h.dispatchEvent(new Event('change',{bubbles:true}));}
        """, date_str, None, is_start)

    def generate_simple_report(self, prompt: str, report: Report, past_day: int = 1):
        """
        /agent/enterprise 페이지에서 간단한 일반 리포트 생성

        Args:
            prompt: 프롬프트 텍스트
            report: Report 객체 (URL과 상태 저장용)
            past_day: 기간 설정 (1, 90, 180, 365 등)

        Returns:
            bool: 성공 여부
        """
        try:
            print(f"\n=== 일반 리포트 생성 시작 ===")
            print(f"프롬프트: {prompt[:100]}...")
            print(f"Past Day: {past_day}일")

            # 1. Enterprise 페이지로 이동
            self.driver.get('https://theterminalx.com/agent/enterprise')
            time.sleep(3)

            # 2. Textarea 찾아서 프롬프트 입력
            textarea = self.driver.find_element(By.TAG_NAME, 'textarea')
            textarea.clear()
            textarea.send_keys(prompt)
            print(f"✅ 프롬프트 입력 완료")
            time.sleep(1)

            # 2.5. Past Day 설정 (문서화된 로직 적용)
            if past_day != 1:  # 1일이 아니면 Past Day 드롭다운 설정
                try:
                    print(f"📅 Past Day {past_day}일로 설정 시도...")
                    period_selectors = [
                        "//select[contains(@name, 'period')]",
                        "//button[contains(text(), 'Any Time')]",
                        "//div[contains(@class, 'date')]//select",
                        "//*[contains(text(), 'Any Time')]"
                    ]

                    for selector in period_selectors:
                        try:
                            elements = self.driver.find_elements(By.XPATH, selector)
                            for elem in elements:
                                if elem.is_displayed():
                                    elem.click()
                                    time.sleep(2)

                                    # Past Day 옵션 찾기
                                    past_day_options = self.driver.find_elements(
                                        By.XPATH, f"//*[contains(text(), 'Past {past_day} Day') or contains(text(), '{past_day} day')]"
                                    )
                                    for option in past_day_options:
                                        if option.is_displayed():
                                            option.click()
                                            print(f"✅ Past {past_day} Day 설정 완료")
                                            time.sleep(1)
                                            break
                                    break
                        except:
                            continue
                except Exception as e:
                    print(f"⚠️ Past Day 설정 실패 (계속 진행): {e}")

            # 3. Enter 키로 제출
            textarea = self.driver.find_element(By.TAG_NAME, 'textarea')  # Re-locate after potential UI changes
            textarea.send_keys(Keys.RETURN)
            print(f"⏎ Enter 전송")
            time.sleep(3)

            # 4. URL 확인 (/answer/ 경로로 이동)
            current_url = self.driver.current_url
            print(f"📍 생성된 URL: {current_url}")

            if '/answer/' not in current_url:
                print(f"❌ 예상치 못한 URL: {current_url}")
                report.status = "FAILED"
                return False

            # Report 객체에 URL 저장
            report.url = current_url
            report.status = "REQUESTED"

            print(f"✅ 일반 리포트 생성 요청 성공")
            return True

        except Exception as e:
            print(f"❌ 일반 리포트 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            report.status = "FAILED"
            return False

    def generate_report_html(self, report: Report, report_date_str: str, ref_date_start_str: str, ref_date_end_str: str):
        """
        TerminalX에서 보고서를 생성하고, 생성 요청 후 URL과 제목을 반환합니다.
        """
        print(f"\n=== generate_report_html 함수 시작 ===")
        print(f"--- {report.part_type} 보고서 생성 요청 시작 ---")
        print(f"Report: {report.title}")
        print(f"Date: {report_date_str}, Range: {ref_date_start_str} ~ {ref_date_end_str}")
        
        # 템플릿 파일들 - 고정된 날짜 사용 (템플릿이므로 매번 같은 파일 사용)
        template_date = "20250723"  # Part1용 템플릿
        template_date_part2 = "20250709"  # Part2용 템플릿
        
        if report.part_type == "Part1":
            prompt_file = os.path.join(self.input_data_dir, f"21_100x_Daily_Wrap_Prompt_1_{template_date}.md")
            source_pdf_file = os.path.join(self.input_data_dir, f"10_100x_Daily_Wrap_My_Sources_1_{template_date}.pdf")
            prompt_pdf_file = os.path.join(self.input_data_dir, f"21_100x_Daily_Wrap_Prompt_1_{template_date}.pdf")
        else:  # Part2
            prompt_file = os.path.join(self.input_data_dir, f"21_100x_Daily_Wrap_Prompt_2_20250708.md")
            source_pdf_file = os.path.join(self.input_data_dir, f"10_100x_Daily_Wrap_My_Sources_2_20250709.pdf")
            prompt_pdf_file = os.path.join(self.input_data_dir, f"21_100x_Daily_Wrap_Prompt_2_20250708.pdf")

        # 필요한 파일들 존재 여부 확인
        print(f"파일 존재 확인:")
        print(f"  - Prompt 파일: {prompt_file} ({'존재' if os.path.exists(prompt_file) else '없음'})")
        print(f"  - Source PDF: {source_pdf_file} ({'존재' if os.path.exists(source_pdf_file) else '없음'})")
        print(f"  - Prompt PDF: {prompt_pdf_file} ({'존재' if os.path.exists(prompt_pdf_file) else '없음'})")

        # Prompt 내용 로드
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
            print(f"Prompt 파일 로드 성공 (길이: {len(prompt_content)}자)")
        except FileNotFoundError:
            print(f"[ERROR] 오류: 프롬프트 파일 {prompt_file}을 찾을 수 없습니다.")
            report.status = "FAILED"
            return False
        
        # 템플릿 ID를 10으로 고정하여 바로 진입
        report_form_url = "https://theterminalx.com/agent/enterprise/report/form/10"
        
        # 디버깅: 리다이렉션 추적을 위한 로깅
        print(f"  - 리포트 폼 URL로 이동 시도: {report_form_url}")
        self.driver.get(report_form_url)
        
        # 실제 도착한 URL 확인 및 디버깅  
        time.sleep(3)  # 리다이렉션 완료 대기
        current_url = self.driver.current_url
        print(f"  - 실제 도착한 URL: {current_url}")
        
        # 아카이브 페이지로 리다이렉션된 경우 강력한 다중 우회 처리
        if "archive" in current_url:
            print("  - [REDIRECT DETECTED] 아카이브 페이지로 리다이렉션됨. 강력한 우회 시도...")
            
            success = False
            # 방법 1: 세션 쿠키 확인 후 직접 재시도
            print("  - 방법 1: 세션 상태 확인 후 직접 재시도")
            time.sleep(3)
            self.driver.get(report_form_url)
            time.sleep(5)  # 더 오래 대기
            current_url_retry = self.driver.current_url
            print(f"    → 재시도 후 URL: {current_url_retry}")
            
            if "form" in current_url_retry:
                print("    → [SUCCESS] 직접 재시도로 폼 페이지 접근 성공!")
                success = True
            else:
                print("    → [FAILED] 직접 재시도 실패")
                
                # 방법 2: 다른 템플릿 ID로 우회 시도  
                print("  - 방법 2: 다른 템플릿 ID로 우회 접근")
                alternative_urls = [
                    "https://theterminalx.com/agent/enterprise/report/form/1",
                    "https://theterminalx.com/agent/enterprise/report/form/5",
                    "https://theterminalx.com/agent/enterprise/report/form"
                ]
                
                for alt_url in alternative_urls:
                    print(f"    → 시도: {alt_url}")
                    self.driver.get(alt_url)
                    time.sleep(4)
                    alt_current_url = self.driver.current_url
                    print(f"    → 결과: {alt_current_url}")
                    
                    if "form" in alt_current_url and "archive" not in alt_current_url:
                        print(f"    → [SUCCESS] 대안 URL로 폼 접근 성공: {alt_url}")
                        success = True
                        break
                
                if not success:
                    print("  - 방법 3: 아카이브에서 새 리포트 버튼 클릭")
                    try:
                        # 먼저 아카이브 페이지로 명시적 이동
                        self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")
                        time.sleep(3)
                        
                        # 다양한 버튼 셀렉터 시도
                        button_selectors = [
                            "//a[contains(@href, 'report/form')]",
                            "//button[contains(text(), 'New') or contains(text(), '새')]",
                            "//a[contains(text(), 'Create') or contains(text(), '생성')]",
                            "//button[contains(@class, 'btn') and contains(text(), 'Report')]",
                            ".btn-primary[href*='form']",
                            "a[href*='report/form']"
                        ]
                        
                        for selector in button_selectors:
                            try:
                                print(f"    → 버튼 시도: {selector}")
                                if selector.startswith("//"):
                                    button = WebDriverWait(self.driver, 3).until(
                                        EC.element_to_be_clickable((By.XPATH, selector))
                                    )
                                else:
                                    button = WebDriverWait(self.driver, 3).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                    )
                                button.click()
                                time.sleep(4)
                                button_url = self.driver.current_url
                                print(f"    → 클릭 후 URL: {button_url}")
                                
                                if "form" in button_url:
                                    print("    → [SUCCESS] 버튼 클릭으로 폼 접근 성공!")
                                    success = True
                                    break
                            except:
                                continue
                                
                    except Exception as e:
                        print(f"    → [ERROR] 버튼 클릭 방법 실패: {e}")
                
                if not success:
                    print("  - 방법 4: 강제 JavaScript 네비게이션")
                    try:
                        # JavaScript로 직접 페이지 이동 강제 실행
                        js_navigate = f"window.location.href = '{report_form_url}'; return true;"
                        self.driver.execute_script(js_navigate)
                        time.sleep(5)
                        js_url = self.driver.current_url
                        print(f"    → JS 네비게이션 후 URL: {js_url}")
                        
                        if "form" in js_url:
                            print("    → [SUCCESS] JavaScript 강제 네비게이션 성공!")
                            success = True
                    except Exception as e:
                        print(f"    → [ERROR] JavaScript 네비게이션 실패: {e}")
            
            # 최종 결과 확인
            final_url = self.driver.current_url
            if "form" in final_url:
                print(f"  - [FINAL SUCCESS] 폼 페이지 최종 접근 성공: {final_url}")
            else:
                print(f"  - [FINAL FAILED] 모든 우회 방법 실패. 최종 URL: {final_url}")
                report.status = "FAILED"
                return False

        try:
            # 페이지 로드 대기 (Report Title 입력 필드 기준으로)
            print("  - Report Title 입력 필드 찾는 중...")
            report_title_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder=\"What's the title?\"]"))
            )
            print("  - Report Title 입력 필드 발견됨!")

            # Report Title 입력 (Ctrl+V 시뮬레이션)
            print(f"  - Report Title 입력 중: '{report.title}'")
            report_title_input.click() # 필드 클릭하여 포커스
            report_title_input.send_keys(report.title)
            report_title_input.send_keys(Keys.TAB)
            print("  - Report Title 입력 완료!")
            time.sleep(0.5) # 짧은 대기

            # Report Reference Date 입력 (Hybrid V2 방식)
            print(f"  - Reference Date 입력 중: {ref_date_start_str} ~ {ref_date_end_str}")
            self._input_date_directly(ref_date_start_str, True)
            self._input_date_directly(ref_date_end_str,  False)
            print("  - Report Reference Date 입력 완료!")

            # Upload Sample Report  
            print(f"  - Sample Report 업로드 중: {source_pdf_file}")
            upload_sample_input = self.driver.find_element(By.XPATH, "//input[@type='file' and @placeholder='file-input' and @max='1']")
            upload_sample_input.send_keys(source_pdf_file)
            print(f"  - Sample Report 업로드 완료!")
            time.sleep(2) # 파일 업로드 후 내부 처리 대기

            # Add your Own Sources
            print(f"  - Own Sources 업로드 중: {source_pdf_file}, {prompt_pdf_file}")
            add_sources_input = self.driver.find_element(By.XPATH, "//input[@type='file' and @placeholder='file-input' and @multiple='']")
            add_sources_input.send_keys(f"{source_pdf_file}\n{prompt_pdf_file}")
            print(f"  - Own Sources 업로드 완료!")
            time.sleep(2) # 파일 업로드 후 내부 처리 대기

            # Prompt 입력 (Ctrl+V 시뮬레이션)
            print(f"  - Prompt 입력 중... (길이: {len(prompt_content)}자)")
            prompt_textarea = self.driver.find_element(By.XPATH, "//textarea[@placeholder='Outline, topic, notes, or anything you have in mind that you want the Agent to consider when analyzing data and creating research.']")
            prompt_textarea.click() # 필드 클릭하여 포커스
            pyperclip.copy(prompt_content) # 클립보드에 복사
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform() # Ctrl+V
            print("  - Prompt 입력 완료!")

            # Generate 버튼 활성화 확인 (디버깅용)
            print("  - Generate 버튼 활성화 대기 중...")
            generate_button_element = self.driver.find_element(By.XPATH, "//button[contains(., 'Generate')]")
            print(f"  - Generate 버튼 초기 disabled 상태: {generate_button_element.get_attribute('disabled')}")
            
            # Generate 버튼 클릭 (활성화될 때까지 대기)
            # disabled 속성이 사라질 때까지 기다림
            generate_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Generate') and not(@disabled)]"))
            )
            print("  - Generate 버튼 활성화 확인!")
            print(f"  - Generate 버튼 최종 disabled 상태: {generate_button.get_attribute('disabled')}") # None이 출력되어야 함
            
            generate_button.click()
            print("  - Generate 버튼 클릭! 보고서 생성 시작 대기 중...")

            # 1단계: 산출물 URL 대기 (최대 20분 = 1200초)
            print("  - 산출물 URL 변경 대기 중 (최대 20분)...")
            WebDriverWait(self.driver, 1200).until(
                EC.url_matches(r"https://theterminalx.com/agent/enterprise/report/\d+")
            )
            generated_report_url = self.driver.current_url
            print(f"  - 보고서 URL 확인 완료: {generated_report_url}")

            # 2단계: "Generating..." 메시지 등장 대기 (리포트 생성 시작 확인)
            print("  - 'Generating your report' 메시지 등장 대기 중...")
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Generating your report (it may take up to 5 minutes).')]"))
            )
            print("  - 'Generating your report' 메시지 등장 확인. 리포트 생성 시작됨.")
            
            report.url = generated_report_url
            report.status = "GENERATING"
            return True

        except TimeoutException as e:
            print(f"보고서 생성 요청 타임아웃: {e}")
            print(f"  - 현재 URL: {self.driver.current_url}")
            print(f"  - 페이지 제목: {self.driver.title}")
            print("  - 디버깅용 페이지 소스 일부:")
            try:
                page_source_sample = self.driver.page_source[:1000] + "..."
                print(f"  - 페이지 소스 샘플: {page_source_sample}")
            except:
                print("  - 페이지 소스 확인 불가")
            report.status = "FAILED"
            return False
        except Exception as e:
            print(f"보고서 생성 요청 중 오류 발생: {e}")
            print(f"  - 현재 URL: {self.driver.current_url}")
            report.status = "FAILED"
            return False

    def convert_html_to_json(self, html_file_path):
        """Python_Lexi_Convert 도구를 사용하여 HTML을 JSON으로 변환합니다."""
        print(f"HTML을 JSON으로 변환 중: {html_file_path}")
        # html_to_json 함수를 동적으로 임포트
        import sys
        sys.path.append(self.lexi_convert_dir) # Python_Lexi_Convert 프로젝트의 루트 디렉터리를 추가
        from converters.html_converter import html_to_json # 이제 'converters' 패키지 내의 모듈로 임포트
        
        data, error = html_to_json(html_file_path)
        if error:
            print(f"HTML to JSON 변환 실패: {error}")
            return None
        
        output_json_filename = os.path.basename(html_file_path).replace('.html', '.json')
        output_json_path = os.path.join(self.generated_json_dir, output_json_filename)
        
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"JSON 변환 완료: {output_json_path}")
        return output_json_path

    def integrate_json_data(self, json_file_paths):
        """통합JSON Instruction_Json.md 지침에 따라 JSON 데이터를 가공하고 통합합니다.
        이 부분은 Instruction_Json.md의 복잡한 로직을 구현해야 하므로,
        여기서는 뼈대만 제공하고 실제 구현은 Instruction_Json.md를 참조하여 진행해야 합니다.
        """
        print("JSON 데이터 가공 및 통합 시작...")
        # Instruction_Json.md 로드 및 파싱 (필요시)
        # from 통합JSON.Instruction_Json_parser import parse_instructions # 가상의 파서
        # instructions = parse_instructions(self.integrated_json_instruction_file)

        # PART1 및 PART2 JSON 파일 분류
        part1_jsons = [f for f in json_file_paths if "part1" in os.path.basename(f).lower()]
        part2_jsons = [f for f in json_file_paths if "part2" in os.path.basename(f).lower()]

        # 각 PART별로 통합 JSON 생성 (Instruction_Json.md 지침에 따라)
        integrated_part1_json = self._process_and_integrate_part_jsons(part1_jsons, "Part1")
        integrated_part2_json = self._process_and_integrate_part_jsons(part2_jsons, "Part2")

        # 통합된 JSON 저장 (예시)
        with open(os.path.join(self.generated_json_dir, 'integrated_part1.json'), 'w', encoding='utf-8') as f:
            json.dump(integrated_part1_json, f, ensure_ascii=False, indent=4)
        with open(os.path.join(self.generated_json_dir, 'integrated_part2.json'), 'w', encoding='utf-8') as f:
            json.dump(integrated_part2_json, f, ensure_ascii=False, indent=4)
        
        print("JSON 데이터 가공 및 통합 완료.")
        return integrated_part1_json, integrated_part2_json

    def _process_and_integrate_part_jsons(self, json_files, part_name):
        """
        Instruction_Json.md 지침에 따라 특정 PART의 JSON 파일들을 처리하고 통합합니다.
        이 함수는 Instruction_Json.md의 복잡한 로직을 구현해야 합니다.
        """
        print(f"{part_name} JSON 파일 통합 로직 (Instruction_Json.md 참조)...")
        # 실제 구현:
        # 1. 입력 파일 분류 및 식별
        # 2. 데이터 정제 및 표준화 (불필요한 섹션 제거, 인용 부호 제거, references 배열 제거, 핵심 값 표준화)
        # 3. 섹션별 최우수 답변 선택 및 출처 기록 (특히 7.1, 8.1 특별 규칙)
        # 4. 최종 리포트 결합 및 번역 (한국어 번역 규칙 적용)
        
        # 여기서는 임시로 첫 번째 파일의 내용을 반환하는 것으로 대체
        if json_files:
            with open(json_files[0], 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def build_final_html(self, integrated_part1_json, integrated_part2_json):
        """
        Jinja2를 사용하여 최종 데일리랩 HTML을 빌드합니다.
        """
        print("최종 데일리랩 HTML 빌드 시작...")
        # Jinja2 환경 설정
        # template_dir = os.path.dirname(self.template_html_path)
        # env = Environment(loader=FileSystemLoader(template_dir))
        # template = env.get_template(os.path.basename(self.template_html_path))

        # 통합된 JSON 데이터를 템플릿에 전달하여 렌더링
        # context = {
        #     "part1_data": integrated_part1_json,
        #     "part2_data": integrated_part2_json,
        #     "report_date": datetime.now().strftime("%Y년 %m월 %d일 (%A)") # 예시
        # }
        # rendered_html = template.render(context)

        # 실제 렌더링 로직은 Instruction_Json.md 및 템플릿 구조에 따라 구현
        # 여기서는 임시로 템플릿 파일을 그대로 복사하는 것으로 대체
        with open(self.template_html_path, 'r', encoding='utf-8') as f:
            rendered_html = f.read()

        output_html_filename = f"{datetime.now().strftime('%Y%m%d')}_데일리랩.html" # 예시
        output_html_path = os.path.join(self.output_daily_wrap_dir, output_html_filename)
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        print(f"최종 데일리랩 HTML 빌드 완료: {output_html_path}")
        return output_html_path

    def update_main_html_and_version_js(self, latest_report_date_str):
        """
        main.html의 데일리랩 링크와 version.js를 업데이트합니다.
        latest_report_date_str: YYYY-MM-DD 형식의 최신 보고서 날짜
        """
        print("main.html 및 version.js 업데이트 시작...")
        
        # main.html 업데이트
        try:
            with open(self.main_html_path, 'r', encoding='utf-8') as f:
                main_html_content = f.read()
            
            # 데일리랩 링크 3군데 업데이트 (정규 표현식 사용 권장)
            # 예시: 2025-07-22_100x-daily-wrap.html
            # 실제 구현에서는 더 견고한 정규 표현식 또는 BeautifulSoup 파싱 필요
            old_date_pattern = r"(\d{4}-\d{2}-\d{2})_100x-daily-wrap.html"
            new_date_filename = f"{latest_report_date_str}_100x-daily-wrap.html"
            
            # 첫 번째 링크 (What's New)
            main_html_content = main_html_content.replace(
                f"index.html?path=100x/daily-wrap/{datetime.now().strftime('%Y-%m-%d')}_100x-daily-wrap.html", # 현재 날짜로 가정
                f"index.html?path=100x/daily-wrap/{new_date_filename}"
            )
            main_html_content = main_html_content.replace(
                f"<strong>What's New:</strong> {datetime.now().strftime('%Y-%m-%d')} Daily Wrap", # 현재 날짜로 가정
                f"<strong>What's New:</strong> {latest_report_date_str} Daily Wrap"
            )
            
            # 두 번째 링크 (Daily Wrap 섹션)
            main_html_content = main_html_content.replace(
                f"index.html?path=100x/daily-wrap/{datetime.now().strftime('%Y-%m-%d')}_100x-daily-wrap.html", # 현재 날짜로 가정
                f"index.html?path=100x/daily-wrap/{new_date_filename}"
            )

            with open(self.main_html_path, 'w', encoding='utf-8') as f:
                f.write(main_html_content)
            print("main.html 업데이트 완료.")
        except Exception as e:
            print(f"main.html 업데이트 중 오류 발생: {e}")

        # version.js 업데이트
        try:
            new_version = datetime.now().strftime('%Y%m%dT%H%M')
            version_js_content = f"export const siteVersion = '{new_version}';"
            with open(self.version_js_path, 'w', encoding='utf-8') as f:
                f.write(version_js_content)
            print("version.js 업데이트 완료.")
        except Exception as e:
            print(f"version.js 업데이트 중 오류 발생: {e}")

    def run_full_automation(self):
        """전체 자동화 워크플로우를 실행합니다."""
        print("--- 100xFenok Report Generation Automation Start ---")
        
        if not self._login_terminalx():
            print("로그인 실패. 자동화를 중단합니다.")
            return

        batch_manager = ReportBatchManager(self.driver)

        today = datetime.now()
        weekday = today.weekday()
        delta_days = 2 if weekday == 1 else 1
        report_date_str = today.strftime('%Y%m%d')
        ref_date_start = (today - timedelta(days=delta_days)).strftime('%Y-%m-%d')
        ref_date_end = today.strftime('%Y-%m-%d')

        # Phase 1: Fire-and-Forget - 모든 리포트 생성 요청
        print("\n--- Phase 1: 리포트 생성 요청 시작 ---")
        for part_type in ["Part1", "Part2"]:
            title = f"{report_date_str} 100x Daily Wrap {part_type}"
            batch_manager.add_report(part_type, title)
        
        for report in batch_manager.reports:
            self.generate_report_html(report, report_date_str, ref_date_start, ref_date_end)

        # Phase 2: Monitor & Retry - 모든 리포트가 완료될 때까지 모니터링
        print("\n--- Phase 2: 아카이브 페이지에서 상태 모니터링 시작 ---")
        success = batch_manager.monitor_and_retry()
        
        # Phase 2.5: 실패한 리포트 재시도 로직 (main_generator에서 처리)
        failed_reports_after_monitor = [r for r in batch_manager.reports if r.status == "FAILED" and r.retry_count <= batch_manager.max_retries_per_report]
        if failed_reports_after_monitor:
            print("\n--- Phase 2.5: 실패한 리포트 재시도 시작 ---")
            for report in failed_reports_after_monitor:
                print(f"재시도: {report.title} (시도 {report.retry_count}/{batch_manager.max_retries_per_report})")
                # generate_report_html을 다시 호출하여 리포트 재생성 시도
                self.generate_report_html(report, report_date_str, ref_date_start, ref_date_end)
                # 재시도 후 상태는 다시 GENERATING으로 변경될 것이므로, 다음 모니터링 주기에서 다시 확인됨
            
            # 재시도 후 다시 모니터링을 시작하여 최종 상태 확인
            print("\n--- Phase 2.5: 재시도 후 최종 상태 모니터링 ---")
            success = batch_manager.monitor_and_retry() # 재시도된 리포트의 최종 상태를 확인

        if not success:
            print("오류: 리포트 생성에 최종 실패하여 자동화를 중단합니다.")
            return

    def extract_and_validate_html(self, report, output_path: str) -> bool:
        """Archive 상태 확인 후 HTML 추출 및 검증 - 폴링 방식으로 개선"""
        try:
            # 1. 리포트 페이지로 이동
            print(f"  - '{report.title}' HTML 추출 시작...")
            self.driver.get(report.url)

            # 2. 렌더링 완료까지 폴링 (최대 2분)
            max_wait = 120
            poll_interval = 5
            elapsed = 0

            print(f"  - 페이지 렌더링 대기 (최대 {max_wait}초)...")

            while elapsed < max_wait:
                try:
                    # markdown-body 또는 supersearchx-body 찾기
                    elements = self.driver.find_elements(
                        By.XPATH,
                        "//div[contains(@class, 'markdown-body') or contains(@class, 'supersearchx-body')]"
                    )

                    if elements:
                        # HTML 추출
                        page_source = self.driver.page_source

                        # "No documents found" 체크
                        if "No documents found" in page_source:
                            print(f"  - 오류: 'No documents found' 감지 - 리포트 생성 실패")
                            return False

                        # 크기 검증
                        html_size = len(page_source)
                        if html_size > 50000:  # 50KB 이상
                            print(f"  - 렌더링 완료! HTML 크기: {html_size} bytes")

                            # HTML 저장
                            with open(output_path, 'w', encoding='utf-8') as f:
                                f.write(page_source)
                            print(f"  - HTML 저장 완료: {output_path}")

                            # 클래스 확인
                            if "markdown-body" in page_source:
                                print(f"  - markdown-body 클래스 확인")
                            if "supersearchx-body" in page_source:
                                print(f"  - supersearchx-body 클래스 확인")

                            return True
                        else:
                            print(f"  - 렌더링 대기중... ({elapsed}초, 현재 크기: {html_size} bytes)")
                    else:
                        print(f"  - 콘텐츠 로딩 대기중... ({elapsed}초)")

                    time.sleep(poll_interval)
                    elapsed += poll_interval

                except Exception as e:
                    print(f"  - 렌더링 체크 중 오류 (재시도): {e}")
                    time.sleep(poll_interval)
                    elapsed += poll_interval

            # 타임아웃
            print(f"  - 오류: {max_wait}초 대기 후에도 렌더링 미완료")
            return False

        except Exception as e:
            print(f"  - HTML 추출 중 예외 발생: {e}")
            return False

    def generate_single_report(self, config, output_filename="report.html"):
        """단일 리포트 생성 (test_batch_6reports.py용)

        Args:
            config (dict): 리포트 설정 (name, prompt, keywords, urls, past_day, num_pages)
            output_filename (str): 저장할 파일명

        Returns:
            tuple: (success, html_path, report_id)
        """
        try:
            # 리포트 객체 생성
            from report_manager import Report
            report = Report(
                part_type="custom",
                title=config.get("name", "Custom Report")
            )

            # 날짜 설정
            today = datetime.now()
            report_date_str = today.strftime('%Y%m%d')
            ref_date_start = (today - timedelta(days=1)).strftime('%Y-%m-%d')
            ref_date_end = today.strftime('%Y-%m-%d')

            # 1. 리포트 생성 요청
            print(f"  리포트 생성 요청 시작...")
            success = self.generate_report_html(
                report,
                report_date_str,
                ref_date_start,
                ref_date_end,
                prompt=config.get("prompt", ""),
                keywords=config.get("keywords", ""),
                urls=config.get("urls", []),
                past_day=config.get("past_day", 90),
                num_pages=config.get("num_pages", 30)
            )

            if not success:
                print(f"  리포트 생성 요청 실패")
                return False, None, None

            # Report ID 추출
            report_id = None
            if report.url:
                import re
                match = re.search(r'/report/(\d+)', report.url)
                if match:
                    report_id = match.group(1)
                    print(f"  Report ID: {report_id}")

            # 2. Archive 모니터링 (최대 10분)
            print(f"  Archive 모니터링 시작...")
            max_wait_time = 600  # 10분
            check_interval = 30  # 30초마다 체크
            elapsed_time = 0

            while elapsed_time < max_wait_time:
                # Archive 페이지 방문
                self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")
                time.sleep(5)  # 페이지 로드 대기

                # 상태 확인
                try:
                    from selenium.webdriver.common.by import By
                    rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")

                    for row in rows[:10]:  # 최근 10개만 확인
                        try:
                            title_elem = row.find_element(By.XPATH, ".//td[1]")
                            status_elem = row.find_element(By.XPATH, ".//td[4]")

                            title = title_elem.text.strip()
                            status = status_elem.text.strip()

                            if config.get("name") in title and status.upper() == "GENERATED":
                                print(f"  리포트 생성 완료! 상태: {status}")

                                # 리포트 URL 가져오기
                                try:
                                    # 행 클릭으로 이동
                                    row.click()
                                    time.sleep(3)
                                    report.url = self.driver.current_url
                                except:
                                    pass

                                # 3. HTML 추출
                                print(f"  HTML 추출 시작...")
                                if report.url:
                                    self.driver.get(report.url)
                                    time.sleep(10)  # 페이지 로드 대기

                                    # HTML 추출 및 검증
                                    success = self._extract_html_with_validation(output_filename)

                                    if success:
                                        html_path = os.path.join(self.generated_html_dir, output_filename)
                                        return True, html_path, report_id
                                    else:
                                        return False, None, report_id

                        except:
                            continue

                except Exception as e:
                    print(f"  Archive 확인 중 오류: {e}")

                # 대기
                print(f"  {elapsed_time}초 경과... {check_interval}초 후 재확인")
                time.sleep(check_interval)
                elapsed_time += check_interval

            # 타임아웃
            print(f"  리포트 생성 타임아웃 (10분)")
            return False, None, report_id

        except Exception as e:
            print(f"  리포트 생성 중 예외: {e}")
            return False, None, None

    def run_full_automation(self):
        """전체 자동화 프로세스를 실행합니다."""
        batch_manager = ReportBatchManager(self.driver)

        today = datetime.now()
        weekday = today.weekday()
        delta_days = 2 if weekday == 1 else 1
        report_date_str = today.strftime('%Y%m%d')
        ref_date_start = (today - timedelta(days=delta_days)).strftime('%Y-%m-%d')
        ref_date_end = today.strftime('%Y-%m-%d')

        # Phase 1: Fire-and-Forget - 모든 리포트 생성 요청
        print("\n--- Phase 1: 리포트 생성 요청 시작 ---")
        for part_type in ["Part1", "Part2"]:
            title = f"{report_date_str} 100x Daily Wrap {part_type}"
            batch_manager.add_report(part_type, title)

        for report in batch_manager.reports:
            self.generate_report_html(report, report_date_str, ref_date_start, ref_date_end)

        # Phase 2: Monitor & Retry - 모든 리포트가 완료될 때까지 모니터링
        print("\n--- Phase 2: 아카이브 페이지에서 상태 모니터링 시작 ---")
        success = batch_manager.monitor_and_retry()

        # Phase 2.5: 실패한 리포트 재시도 로직 (main_generator에서 처리)
        failed_reports_after_monitor = [r for r in batch_manager.reports if r.status == "FAILED" and r.retry_count <= batch_manager.max_retries_per_report]
        if failed_reports_after_monitor:
            print("\n--- Phase 2.5: 실패한 리포트 재시도 시작 ---")
            for report in failed_reports_after_monitor:
                print(f"재시도: {report.title} (시도 {report.retry_count}/{batch_manager.max_retries_per_report})")
                # generate_report_html을 다시 호출하여 리포트 재생성 시도
                self.generate_report_html(report, report_date_str, ref_date_start, ref_date_end)
                # 재시도 후 상태는 다시 GENERATING으로 변경될 것이므로, 다음 모니터링 주기에서 다시 확인됨

            # 재시도 후 다시 모니터링을 시작하여 최종 상태 확인
            print("\n--- Phase 2.5: 재시도 후 최종 상태 모니터링 ---")
            success = batch_manager.monitor_and_retry() # 재시도된 리포트의 최종 상태를 확인

        if not success:
            print("오류: 리포트 생성에 최종 실패하여 자동화를 중단합니다.")
            return

        # Phase 3: Extract & Process - 성공한 리포트 데이터 처리
        print("\n--- Phase 3: 데이터 추출 및 처리 시작 ---")
        final_html_paths = []
        for report in batch_manager.reports:
            if report.status == "GENERATED":
                output_html_filename = f"{report_date_str}_{report.part_type.lower()}.html"
                output_html_path = os.path.join(self.generated_html_dir, output_html_filename)

                # extract_and_validate_html() 메서드 사용
                if self.extract_and_validate_html(report, output_html_path):
                    final_html_paths.append(output_html_path)
                else:
                    print(f"  - 오류: '{report.title}' HTML 추출 실패")
            else:
                print(f"  - 오류: 리포트 '{report.title}'가 'Generated' 상태에 도달하지 못했습니다. HTML 추출을 건너뜁니다.")

        if not final_html_paths:
            print("최종 HTML 보고서가 없습니다. 자동화를 중단합니다.")
            return

        # 4. HTML to JSON 변환
        generated_json_paths = []
        for html_path in final_html_paths:
            json_path = self.convert_html_to_json(html_path)
            if json_path:
                generated_json_paths.append(json_path)

        if not generated_json_paths:
            print("변환된 JSON 파일이 없습니다. 자동화를 중단합니다.")
            return

        # 5. JSON 데이터 가공 및 통합
        integrated_part1_json, integrated_part2_json = self.integrate_json_data(generated_json_paths)

        # 6. 최종 데일리랩 HTML 빌드
        final_daily_wrap_html_path = self.build_final_html(integrated_part1_json, integrated_part2_json)

        # 7. main.html 및 version.js 업데이트
        self.update_main_html_and_version_js(today.strftime('%Y-%m-%d'))

        # 8. Git 커밋 및 푸시 (이 부분은 스크립트 외부에서 수동으로 실행하거나, 별도의 Git 자동화 모듈 필요)
        print("\n--- 자동화 완료 ---")
        print("main.html 및 version.js가 업데이트되었습니다. Git 커밋 및 푸시를 수동으로 실행해주세요.")
        print("Git 명령 예시:")
        print("git add projects/100xFenok/main.html projects/100xFenok/version.js")
        print("git commit -m \"feat: Update daily wrap link and site version\"")
        print("git push")

    def close(self):
        """WebDriver를 종료합니다."""
        if self.driver:
            self.driver.quit()
            print("WebDriver 종료.")

    def test_login_and_redirect_debug(self):
        """로그인 및 리다이렉션 문제 디버깅 전용 테스트"""
        print("=== 디버깅 테스트: 로그인 및 리다이렉션 확인 ===")
        
        if not self._login_terminalx():
            print("로그인 실패. 테스트 중단.")
            return False
            
        print("로그인 성공. 폼 페이지 접근 테스트 시작...")
        
        # 리다이렉션 추적 테스트
        report_form_url = "https://theterminalx.com/agent/enterprise/report/form/10"
        print(f"폼 URL로 이동: {report_form_url}")
        self.driver.get(report_form_url)
        
        time.sleep(3)
        current_url = self.driver.current_url
        print(f"도착한 URL: {current_url}")
        
        if "archive" in current_url:
            print("[ERROR] 아카이브 페이지로 리다이렉션됨 - 문제 확인")
            return False
        elif "form" in current_url:
            print("[SUCCESS] 폼 페이지 접근 성공")
            # Report Title 필드 존재 확인
            try:
                title_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder=\"What's the title?\"]"))
                )
                print("[SUCCESS] Report Title 필드 발견")
                return True
            except TimeoutException:
                print("[ERROR] Report Title 필드를 찾을 수 없음")
                return False
        else:
            print(f"[WARNING] 예상치 못한 페이지: {current_url}")
            return False

if __name__ == "__main__":
    import sys
    
    generator = FenokReportGenerator()
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--debug":
            # 디버깅 모드
            generator.test_login_and_redirect_debug()
        else:
            # 일반 실행 모드
            generator.run_full_automation()
    finally:
        generator.close()
