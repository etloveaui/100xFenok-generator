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
        
        self.secrets_file = os.path.join(self.base_dir, 'secrets', 'my_sensitive_data.md')
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
            self.driver.maximize_window() # 브라우저 창 최대화
            print("WebDriver 설정 완료.")
        except Exception as e:
            print(f"WebDriver 설정 중 오류 발생: {e}")
            exit()

    def _create_directories(self):
        """필요한 출력 디렉토리를 생성합니다."""
        os.makedirs(self.generated_html_dir, exist_ok=True)
        os.makedirs(self.generated_json_dir, exist_ok=True)
        print("출력 디렉토리 생성 완료.")

    def _login_terminalx(self):
        """TerminalX에 로그인합니다."""
        print("TerminalX 로그인 시도...")
        self.driver.get("https://theterminalx.com/agent/enterprise")
        
        # 페이지 로드 직후 알림 창이 뜨는지 먼저 확인하고 처리
        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present()) # 알림 대기 시간을 5초로 설정
            alert = self.driver.switch_to.alert
            print(f"알림 창 감지: {alert.text}")
            alert.accept() # 알림 창 닫기
        except TimeoutException:
            pass # 알림 창이 없으면 무시

        try:
            # 초기 페이지의 "Log in" 버튼 클릭하여 로그인 폼으로 이동
            initial_login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in')]"))
            )
            initial_login_button.click()
            print("초기 'Log in' 버튼 클릭.")
            
            time.sleep(2) # 페이지 전환을 위한 짧은 대기

            # 로그인 폼 페이지로 이동 후 요소 대기 (visibility_of_element_located 사용)
            email_input = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter your email']"))
            )
            password_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Enter your password']")
            login_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Log In')]")

            # 명시적으로 필드를 비우고 값 입력
            email_input.clear()
            email_input.send_keys(self.terminalx_username)
            print(f"이메일 입력: {self.terminalx_username}")
            print(f"입력된 이메일 확인: {email_input.get_attribute('value')}") # 입력된 값 확인

            password_input.clear()
            password_input.send_keys(self.terminalx_password)
            print(f"비밀번호 입력: {'*' * len(self.terminalx_password)}") # 실제 비밀번호는 출력하지 않음
            print(f"입력된 비밀번호 확인 (일부): {password_input.get_attribute('value')[:3]}...") # 입력된 값 일부 확인

            time.sleep(1) # 잠시 대기 (디버깅용)

            login_button.click()
            print("자격 증명 입력 및 'Log In' 버튼 클릭.")

            # 로그인 버튼 클릭 후 알림 창이 뜨는지 확인하고 처리
            try:
                WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                print(f"로그인 후 알림 창 감지: {alert.text}")
                alert.accept() # 알림 창 닫기
                return False # 알림이 떴다는 것은 로그인 실패를 의미
            except TimeoutException:
                pass # 알림 창이 없으면 무시 (로그인 성공 가능성)

            # 로그인 성공 여부 확인 (subscriptions 버튼 활성화 여부)
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Subscriptions')]"))
                )
                print("TerminalX 로그인 성공 (Subscriptions 버튼 확인).")
                
                # 로그인 성공 후 나타나는 알림 활성화 팝업 처리
                try:
                    # "나중에" 또는 "No Thanks"와 같은 버튼을 찾아서 클릭
                    # 실제 팝업의 HTML 구조에 따라 XPath 또는 CSS Selector 조정 필요
                    # 예시: "No Thanks" 버튼
                    no_thanks_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'No Thanks')]"))
                    )
                    no_thanks_button.click()
                    print("알림 활성화 팝업 'No Thanks' 클릭.")
                except TimeoutException:
                    print("알림 활성화 팝업을 찾을 수 없습니다. (없거나 이미 닫혔을 수 있음)")
                except Exception as e:
                    print(f"알림 활성화 팝업 처리 중 오류 발생: {e}")

                return True
            except TimeoutException:
                print("로그인 실패: Subscriptions 버튼을 찾을 수 없습니다.")
                return False
            except Exception as e:
                print(f"로그인 성공 여부 확인 중 오류 발생: {e}")
                return False
        except TimeoutException:
            print("로그인 타임아웃: 로그인 페이지 로드 또는 로그인 후 리다이렉트 실패.")
            return False
        except NoSuchElementException:
            print("로그인 요소(이메일, 비밀번호, 로그인 버튼)를 찾을 수 없습니다. 이미 로그인되어 있을 수 있습니다.")
            # 이미 로그인되어 있는지 확인하는 로직 추가 (예: 특정 대시보드 요소 확인)
            try:
                self.driver.get("https://theterminalx.com/agent/enterprise/dashboard")
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1")) # 대시보드의 h1 태그 등
                )
                print("이미 TerminalX에 로그인되어 있습니다.")
                return True
            except TimeoutException:
                print("이미 로그인되어 있는지 확인 실패. 수동 확인이 필요합니다.")
                return False
            except Exception as e:
                print(f"로그인 확인 중 예외 발생: {e}")
                return False
        except Exception as e:
            print(f"로그인 중 오류 발생: {e}")
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

    def generate_report_html(self, report: Report, report_date_str: str, ref_date_start_str: str, ref_date_end_str: str):
        """
        TerminalX에서 보고서를 생성하고, 생성 요청 후 URL과 제목을 반환합니다.
        """
        print(f"\n--- {report.part_type} 보고서 생성 요청 시작 ---")
        
        # Prompt 파일 경로
        prompt_file = os.path.join(self.input_data_dir, f"21_100x_Daily_Wrap_Prompt_{'1' if report.part_type == 'Part1' else '2'}_{report_date_str}.md")
        # Source PDF 파일 경로
        source_pdf_file = os.path.join(self.input_data_dir, f"10_100x_Daily_Wrap_My_Sources_{'1' if report.part_type == 'Part1' else '2'}_{report_date_str}.pdf")
        # Add your Own Sources의 두 번째 PDF 파일 경로 (Prompt PDF 버전)
        prompt_pdf_file = os.path.join(self.input_data_dir, f"21_100x_Daily_Wrap_Prompt_{'1' if report.part_type == 'Part1' else '2'}_{report_date_str}.pdf")

        # Prompt 내용 로드
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
        except FileNotFoundError:
            print(f"오류: 프롬프트 파일 {prompt_file}을 찾을 수 없습니다.")
            return False
        
        # 템플릿 ID를 10으로 고정하여 바로 진입
        report_form_url = "https://theterminalx.com/agent/enterprise/report/form/10"
        self.driver.get(report_form_url)

        try:
            # 페이지 로드 대기 (Report Title 입력 필드 기준으로)
            report_title_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder=\"What's the title?\"]"))
            )

            # Report Title 입력 (Ctrl+V 시뮬레이션)
            report_title_input.click() # 필드 클릭하여 포커스
            report_title_input.send_keys(report.title)
            report_title_input.send_keys(Keys.TAB)
            print("Report Title 입력 완료.")
            time.sleep(0.5) # 짧은 대기

            # Report Reference Date 입력 (Hybrid V2 방식)
            self._input_date_directly(ref_date_start_str, True)
            self._input_date_directly(ref_date_end_str,  False)

            print("Report Reference Date 입력 완료.")

            # Upload Sample Report
            upload_sample_input = self.driver.find_element(By.XPATH, "//input[@type='file' and @placeholder='file-input' and @max='1']")
            upload_sample_input.send_keys(source_pdf_file)
            print(f"Upload Sample Report: {source_pdf_file} 업로드 시도.")
            time.sleep(2) # 파일 업로드 후 내부 처리 대기

            # Add your Own Sources
            add_sources_input = self.driver.find_element(By.XPATH, "//input[@type='file' and @placeholder='file-input' and @multiple='']")
            add_sources_input.send_keys(f"{source_pdf_file}\n{prompt_pdf_file}")
            print(f"Add your Own Sources: {source_pdf_file}, {prompt_pdf_file} 업로드 시도.")
            time.sleep(2) # 파일 업로드 후 내부 처리 대기

            # Prompt 입력 (Ctrl+V 시뮬레이션)
            prompt_textarea = self.driver.find_element(By.XPATH, "//textarea[@placeholder='Outline, topic, notes, or anything you have in mind that you want the Agent to consider when analyzing data and creating research.']")
            prompt_textarea.click() # 필드 클릭하여 포커스
            pyperclip.copy(prompt_content) # 클립보드에 복사
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform() # Ctrl+V
            print("Prompt 입력 완료.")

            # Generate 버튼 활성화 확인 (디버깅용)
            generate_button_element = self.driver.find_element(By.XPATH, "//button[contains(., 'Generate')]")
            print(f"Generate 버튼 초기 disabled 상태: {generate_button_element.get_attribute('disabled')}")
            
            # Generate 버튼 클릭 (활성화될 때까지 대기)
            # disabled 속성이 사라질 때까지 기다림
            generate_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Generate') and not(@disabled)]"))
            )
            print("Generate 버튼 활성화 확인.")
            print(f"Generate 버튼 최종 disabled 상태: {generate_button.get_attribute('disabled')}") # None이 출력되어야 함
            
            generate_button.click()
            print("Generate 버튼 클릭. 보고서 생성 시작 대기 중...")

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

        except TimeoutException:
            print("보고서 생성 요청 타임아웃.")
            return False
        except Exception as e:
            print(f"보고서 생성 요청 중 오류 발생: {e}")
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

        # Phase 3: Extract & Process - 성공한 리포트 데이터 처리
        print("\n--- Phase 3: 데이터 추출 및 처리 시작 ---")
        final_html_paths = []
        for report in batch_manager.reports:
            if report.status == "GENERATED":
                print(f"  - 리포트 '{report.title}'가 'Generated' 상태 확인. HTML 추출을 위해 페이지로 이동.")
                self.driver.get(report.url)
                
                # HTML 추출
                report_html_content = self.driver.page_source
                print(f"  - '{report.title}' 페이지 전체 HTML 추출 완료.")

                output_html_filename = f"{report_date_str}_{report.part_type.lower()}.html"
                output_html_path = os.path.join(self.generated_html_dir, output_html_filename)
                with open(output_html_path, 'w', encoding='utf-8') as f:
                    f.write(report_html_content)
                print(f"생성된 HTML 저장 완료: {output_html_path}")
                final_html_paths.append(output_html_path)
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

if __name__ == "__main__":
    generator = FenokReportGenerator()
    try:
        generator.run_full_automation()
    finally:
        generator.close()
