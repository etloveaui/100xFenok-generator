#!/usr/bin/env python3
"""
100xFenok 일일 자동화 스케줄러
- Windows Task Scheduler 연동
- 자동 실행 및 모니터링
- 오류 처리 및 알림
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import schedule
import time
import subprocess
from typing import Dict, Any, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 로컬 모듈
from pipeline_integration import FullPipelineManager

logger = logging.getLogger(__name__)

class DailyAutomationScheduler:
    """일일 자동화 스케줄러"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.base_dir = self.project_dir.parent.parent
        self.config_file = self.project_dir / "automation_config.json"
        self.log_dir = self.project_dir / "logs"
        
        # 설정 로드
        self.config = self._load_config()
        
        # 로그 디렉터리 생성
        self.log_dir.mkdir(exist_ok=True)
        
        # 파이프라인 매니저
        self.pipeline = FullPipelineManager()
        
        # 로깅 설정
        self._setup_logging()
        
    def _load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        default_config = {
            "schedule": {
                "enabled": True,
                "time": "06:00",  # 아침 6시
                "timezone": "Asia/Seoul",
                "weekdays_only": True
            },
            "notification": {
                "enabled": False,
                "email": {
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "to_address": ""
                },
                "discord": {
                    "webhook_url": ""
                }
            },
            "ollama": {
                "auto_start": True,
                "model": "qwen2.5:7b",
                "max_retries": 3
            },
            "quality_threshold": 70,
            "backup": {
                "enabled": True,
                "keep_days": 30
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 기본 설정과 병합
                    default_config.update(user_config)
            except Exception as e:
                logger.error(f"설정 파일 로드 실패: {e}")
                
        # 설정 파일 저장 (누락된 항목 추가)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
            
        return default_config
    
    def _setup_logging(self):
        """일일 로깅 설정"""
        today = datetime.now().strftime("%Y%m%d")
        log_file = self.log_dir / f"daily_automation_{today}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def setup_windows_task(self):
        """Windows Task Scheduler에 작업 등록"""
        try:
            script_path = str(Path(__file__).absolute())
            python_exe = sys.executable
            
            schedule_time = self.config["schedule"]["time"]
            
            # XML 작업 정의
            task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().isoformat()}</Date>
    <Author>100xFenok Automation</Author>
    <Description>100xFenok Daily Wrap 자동 생성</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>{datetime.now().strftime("%Y-%m-%d")}T{schedule_time}:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
  </Settings>
  <Actions>
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>"{script_path}" --scheduled-run</Arguments>
      <WorkingDirectory>{str(self.project_dir)}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
            
            # 임시 XML 파일 생성
            temp_xml = self.project_dir / "temp_task.xml"
            with open(temp_xml, 'w', encoding='utf-16') as f:
                f.write(task_xml)
            
            # schtasks 명령으로 작업 등록
            cmd = [
                'schtasks', '/create',
                '/tn', '100xFenok_Daily_Automation',
                '/xml', str(temp_xml),
                '/f'  # 기존 작업 덮어쓰기
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Windows Task Scheduler에 작업 등록 완료")
                print(f"📅 매일 {schedule_time}에 자동 실행됩니다.")
            else:
                logger.error(f"❌ Task Scheduler 등록 실패: {result.stderr}")
                
            # 임시 파일 정리
            temp_xml.unlink(missing_ok=True)
            
        except Exception as e:
            logger.error(f"Windows 작업 스케줄러 설정 실패: {e}")
    
    def run_daily_automation(self) -> Dict[str, Any]:
        """일일 자동화 실행"""
        logger.info("🌅 100xFenok 일일 자동화 시작")
        
        automation_result = {
            'success': False,
            'start_time': datetime.now(),
            'end_time': None,
            'execution_time': 0,
            'pipeline_result': {},
            'errors': [],
            'notifications_sent': []
        }
        
        try:
            # 1. Ollama 상태 확인 및 자동 시작
            if self.config["ollama"]["auto_start"]:
                self._ensure_ollama_running()
            
            # 2. 파이프라인 실행
            today = datetime.now().strftime("%Y-%m-%d")
            pipeline_result = self.pipeline.run_complete_pipeline(target_date=today)
            
            automation_result['pipeline_result'] = pipeline_result
            automation_result['success'] = pipeline_result['success']
            
            # 3. 품질 검증
            if pipeline_result['success']:
                quality_score = pipeline_result.get('validation_results', {}).get('quality_score', 0)
                
                if quality_score < self.config['quality_threshold']:
                    logger.warning(f"⚠️ 품질 점수가 임계값보다 낮음: {quality_score}/{self.config['quality_threshold']}")
                    automation_result['success'] = False
                    automation_result['errors'].append(f"품질 점수 미달: {quality_score}")
                else:
                    logger.info(f"✅ 품질 점수 통과: {quality_score}")
            
            # 4. 백업 수행
            if self.config["backup"]["enabled"] and automation_result['success']:
                self._backup_output_files(pipeline_result.get('output_files', []))
            
            # 5. 알림 발송
            if self.config["notification"]["enabled"]:
                self._send_notifications(automation_result)
            
        except Exception as e:
            logger.error(f"일일 자동화 실행 중 오류: {e}")
            automation_result['errors'].append(str(e))
            
        finally:
            automation_result['end_time'] = datetime.now()
            automation_result['execution_time'] = (
                automation_result['end_time'] - automation_result['start_time']
            ).total_seconds()
            
            logger.info(f"🏁 일일 자동화 완료 - 성공: {automation_result['success']}")
            
        return automation_result
    
    def _ensure_ollama_running(self):
        """Ollama 서비스 상태 확인 및 시작"""
        try:
            # Ollama 상태 확인
            result = subprocess.run(
                ['ollama', 'list'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info("✅ Ollama 서비스 실행 중")
                return True
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Ollama 시작 시도
        try:
            logger.info("🚀 Ollama 서비스 시작 중...")
            subprocess.Popen(['ollama', 'serve'], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            # 시작 대기
            time.sleep(10)
            
            # 재확인
            result = subprocess.run(
                ['ollama', 'list'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info("✅ Ollama 서비스 시작 완료")
                return True
            else:
                logger.error("❌ Ollama 서비스 시작 실패")
                return False
                
        except Exception as e:
            logger.error(f"Ollama 서비스 시작 중 오류: {e}")
            return False
    
    def _backup_output_files(self, output_files: List[str]):
        """출력 파일 백업"""
        try:
            backup_dir = self.project_dir / "backups" / datetime.now().strftime("%Y%m")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in output_files:
                if os.path.exists(file_path):
                    source = Path(file_path)
                    backup_file = backup_dir / source.name
                    
                    # 파일 복사
                    import shutil
                    shutil.copy2(source, backup_file)
                    logger.info(f"💾 백업 완료: {backup_file}")
            
            # 오래된 백업 정리
            self._cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"백업 중 오류: {e}")
    
    def _cleanup_old_backups(self):
        """오래된 백업 파일 정리"""
        try:
            backup_root = self.project_dir / "backups"
            if not backup_root.exists():
                return
            
            keep_days = self.config["backup"]["keep_days"]
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            
            for backup_dir in backup_root.iterdir():
                if backup_dir.is_dir():
                    try:
                        # 디렉터리 이름에서 날짜 추출 (YYYYMM)
                        dir_date = datetime.strptime(backup_dir.name, "%Y%m")
                        
                        if dir_date < cutoff_date:
                            import shutil
                            shutil.rmtree(backup_dir)
                            logger.info(f"🗑️ 오래된 백업 삭제: {backup_dir}")
                            
                    except ValueError:
                        # 날짜 형식이 아닌 디렉터리는 무시
                        continue
                        
        except Exception as e:
            logger.error(f"백업 정리 중 오류: {e}")
    
    def _send_notifications(self, automation_result: Dict[str, Any]):
        """알림 발송"""
        try:
            success = automation_result['success']
            execution_time = automation_result['execution_time']
            
            # 이메일 알림
            if self.config["notification"]["email"]["to_address"]:
                email_sent = self._send_email_notification(automation_result)
                if email_sent:
                    automation_result['notifications_sent'].append('email')
            
            # Discord 웹훅 알림
            if self.config["notification"]["discord"]["webhook_url"]:
                discord_sent = self._send_discord_notification(automation_result)
                if discord_sent:
                    automation_result['notifications_sent'].append('discord')
                    
        except Exception as e:
            logger.error(f"알림 발송 중 오류: {e}")
    
    def _send_email_notification(self, automation_result: Dict[str, Any]) -> bool:
        """이메일 알림 발송"""
        try:
            email_config = self.config["notification"]["email"]
            
            success = automation_result['success']
            execution_time = automation_result['execution_time']
            
            subject = f"100xFenok 일일 자동화 {'성공' if success else '실패'}"
            
            body = f"""
100xFenok Daily Wrap 자동화 결과

📅 실행 날짜: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
✅ 상태: {'성공' if success else '실패'}
⏱️ 실행 시간: {execution_time:.2f}초

"""
            
            if not success:
                body += "❌ 오류 목록:\n"
                for error in automation_result['errors']:
                    body += f"  - {error}\n"
            
            if automation_result['pipeline_result'].get('output_files'):
                body += "\n📄 생성된 파일:\n"
                for file_path in automation_result['pipeline_result']['output_files']:
                    body += f"  - {file_path}\n"
            
            # 이메일 발송
            msg = MIMEMultipart()
            msg['From'] = email_config['username']
            msg['To'] = email_config['to_address']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['username'], email_config['password'])
                server.send_message(msg)
            
            logger.info("📧 이메일 알림 발송 완료")
            return True
            
        except Exception as e:
            logger.error(f"이메일 발송 실패: {e}")
            return False
    
    def _send_discord_notification(self, automation_result: Dict[str, Any]) -> bool:
        """Discord 웹훅 알림 발송"""
        try:
            import requests
            
            webhook_url = self.config["notification"]["discord"]["webhook_url"]
            success = automation_result['success']
            
            color = 0x00FF00 if success else 0xFF0000  # 녹색 또는 빨간색
            title = f"100xFenok 자동화 {'성공' if success else '실패'}"
            
            embed = {
                "title": title,
                "color": color,
                "timestamp": datetime.now().isoformat(),
                "fields": [
                    {
                        "name": "실행 시간",
                        "value": f"{automation_result['execution_time']:.2f}초",
                        "inline": True
                    }
                ]
            }
            
            if not success:
                error_text = "\n".join(automation_result['errors'][:5])  # 최대 5개 오류만
                embed["fields"].append({
                    "name": "오류",
                    "value": error_text[:1000],  # Discord 제한
                    "inline": False
                })
            
            payload = {"embeds": [embed]}
            
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 204:
                logger.info("💬 Discord 알림 발송 완료")
                return True
            else:
                logger.error(f"Discord 알림 발송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Discord 알림 발송 실패: {e}")
            return False

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="100xFenok 일일 자동화 스케줄러")
    parser.add_argument("--setup-task", action="store_true", help="Windows Task Scheduler 작업 등록")
    parser.add_argument("--scheduled-run", action="store_true", help="스케줄된 자동 실행")
    parser.add_argument("--test-run", action="store_true", help="테스트 실행")
    parser.add_argument("--config", help="설정 파일 편집")
    
    args = parser.parse_args()
    
    scheduler = DailyAutomationScheduler()
    
    if args.setup_task:
        print("📋 Windows Task Scheduler 작업 등록 중...")
        scheduler.setup_windows_task()
        return
    
    if args.config:
        import subprocess
        subprocess.run(['notepad', str(scheduler.config_file)])
        return
    
    if args.scheduled_run or args.test_run:
        print("🚀 일일 자동화 실행 시작...")
        result = scheduler.run_daily_automation()
        
        # 결과 출력
        print("\n" + "="*60)
        print("📊 일일 자동화 실행 결과")
        print("="*60)
        print(f"✅ 성공: {result['success']}")
        print(f"⏱️ 실행 시간: {result['execution_time']:.2f}초")
        
        if result['pipeline_result'].get('output_files'):
            print("📄 생성된 파일:")
            for file_path in result['pipeline_result']['output_files']:
                print(f"  - {file_path}")
        
        if result['errors']:
            print("❌ 오류:")
            for error in result['errors']:
                print(f"  - {error}")
        
        if result['notifications_sent']:
            print(f"📨 알림 발송: {', '.join(result['notifications_sent'])}")
    
    else:
        print("100xFenok 일일 자동화 스케줄러")
        print("사용법:")
        print("  --setup-task    Windows Task Scheduler에 작업 등록")
        print("  --scheduled-run 스케줄된 자동 실행")
        print("  --test-run      테스트 실행")
        print("  --config        설정 파일 편집")

if __name__ == "__main__":
    main()