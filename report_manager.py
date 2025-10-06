from dataclasses import dataclass, field
from typing import List, Dict
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

@dataclass
class Report:
    """개별 리포트의 상태와 정보를 관리하는 데이터 클래스"""
    part_type: str
    title: str
    url: str = ""
    status: str = "PENDING"  # PENDING -> GENERATING -> GENERATED | FAILED
    retry_count: int = 0
    html_path: str = ""
    json_path: str = ""

class ReportBatchManager:
    """여러 리포트의 생명주기를 관리하는 클래스"""
    def __init__(self, driver):
        self.driver = driver
        self.reports: List[Report] = []
        self.max_retries_per_report = 2 # 리포트당 최대 재시도 횟수

    def add_report(self, part_type: str, title: str):
        """처리할 리포트를 배치에 추가합니다."""
        report = Report(part_type=part_type, title=title)
        self.reports.append(report)
        print(f"[Batch Manager] {part_type} ({title}) 리포트가 배치에 추가되었습니다.")

    def get_pending_reports(self) -> List[Report]:
        """아직 최종 상태가 아닌 리포트 목록을 반환합니다."""
        return [r for r in self.reports if r.status in ["PENDING", "GENERATING"]]

    def all_completed(self) -> bool:
        """모든 리포트가 성공적으로 생성되었는지 확인합니다."""
        return all(r.status == 'GENERATED' for r in self.reports)

    def update_report_status(self, status_map: Dict[str, str]):
        """아카이브 페이지에서 읽어온 상태로 각 리포트의 상태를 업데이트합니다."""
        for report in self.get_pending_reports():
            current_status = status_map.get(report.title, "GENERATING") # 못찾으면 일단 생성중으로 간주
            if current_status.upper() == "GENERATED":
                report.status = "GENERATED"
                print(f"[Batch Manager] 상태 업데이트: {report.title} -> GENERATED")
            elif current_status.upper() == "FAILED":
                report.status = "FAILED"
                report.retry_count += 1
                print(f"[Batch Manager] 상태 업데이트: {report.title} -> FAILED (재시도 횟수: {report.retry_count})")

    def monitor_and_retry(self, timeout: int = 1800, initial_interval: int = 30) -> bool:
        """모든 리포트가 완료될 때까지 아카이브 페이지를 모니터링하고, 실패 시 재시도를 관리합니다."""
        overall_start_time = time.time()
        current_interval = initial_interval

        while time.time() - overall_start_time < timeout:
            pending_reports = self.get_pending_reports()
            if not pending_reports:
                print("[Batch Manager] 모든 리포트가 성공적으로 생성되었습니다.")
                return True

            print(f"[Batch Manager] 아카이브 페이지 새로고침. 남은 리포트: {len(pending_reports)}")
            self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")

            # JavaScript 렌더링 대기 추가 (verify_system.py 검증 로직 적용)
            print("[Batch Manager] Archive 페이지 로딩 대기중...")
            time.sleep(3)  # 초기 페이지 로딩

            print("[Batch Manager] JavaScript 렌더링 대기중...")
            time.sleep(7)  # JavaScript 실행 및 테이블 렌더링

            try:
                # tbody 태그 존재 확인 (타임아웃 15초)
                WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//table/tbody")))

                # 테이블 행 렌더링 폴링 (최대 5회 시도)
                print("[Batch Manager] 테이블 행 렌더링 대기중...")
                rows = []
                for attempt in range(5):
                    rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
                    if len(rows) > 0:
                        print(f"[Batch Manager] 테이블 행 {len(rows)}개 발견")
                        break
                    print(f"[Batch Manager] 시도 {attempt+1}/5: 행 없음, 2초 대기...")
                    time.sleep(2)

                # 테이블 행이 렌더링되지 않은 경우 다음 폴링까지 스킵
                if len(rows) == 0:
                    print("[Batch Manager] 경고: 테이블 행이 렌더링되지 않음. 다음 폴링까지 대기.")
                    time.sleep(current_interval)
                    continue

                # 정상 케이스: status_map 생성
                status_map = {}
                for row in rows:
                    try:
                        title_element = row.find_element(By.XPATH, ".//td[1]")
                        status_element = row.find_element(By.XPATH, ".//td[4]")
                        status_map[title_element.text.strip()] = status_element.text.strip()
                    except NoSuchElementException:
                        continue # 행 구조가 다르면 건너뜀

                for report in pending_reports:
                    current_status_from_archive = status_map.get(report.title, "NOT_FOUND")
                    
                    if current_status_from_archive.upper() == "GENERATED":
                        report.status = "GENERATED"
                        print(f"[Batch Manager] 성공: '{report.title}' -> GENERATED")
                    elif current_status_from_archive.upper() == "FAILED":
                        report.status = "FAILED"
                        report.retry_count += 1
                        print(f"[Batch Manager] 실패: '{report.title}' -> FAILED (재시도 횟수: {report.retry_count})")
                        if report.retry_count <= self.max_retries_per_report:
                            print(f"[Batch Manager] '{report.title}' 재시도 가능. 상위 호출자에게 재시도 요청.")
                            # 이 부분은 FenokReportGenerator.run_full_automation에서 처리되어야 합니다.
                            # 여기서는 상태만 업데이트하고, 재시도 결정은 상위 호출자에게 맡깁니다.
                        else:
                            print(f"[Batch Manager] 최종 실패: '{report.title}' 최대 재시도 횟수 초과.")
                            # 이 리포트는 더 이상 처리하지 않음
                    elif current_status_from_archive.upper() == "GENERATING":
                        print(f"[Batch Manager] 대기: '{report.title}' -> GENERATING")
                    elif current_status_from_archive.upper() == "NOT_FOUND":
                        print(f"[Batch Manager] 경고: '{report.title}' 아카이브에서 찾을 수 없음. 계속 대기.")
                    else:
                        print(f"[Batch Manager] 알 수 없는 상태: '{report.title}' -> {current_status_from_archive}")

            except TimeoutException:
                print("[Batch Manager] 아카이브 페이지 로드 타임아웃. 새로고침.")
            except Exception as e:
                print(f"[Batch Manager] 상태 확인 중 예외 발생: {e}. 새로고침.")
            
            # 모든 리포트가 처리되었는지 다시 확인
            if not self.get_pending_reports():
                print("[Batch Manager] 모든 리포트가 최종 상태에 도달했습니다.")
                return True

            time.sleep(current_interval) # 다음 폴링까지 대기
            current_interval = min(current_interval * 1.2, 120) # 지수 백오프 (최대 120초)

        print("[Batch Manager] 오류: 전체 작업 시간 초과.")
        return False