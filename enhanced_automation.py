#!/usr/bin/env python3
"""
100xFenok Daily Wrap 완전 자동화 시스템 (무료 버전)
- TerminalX 자동화 + Local LLM 기반 JSON 통합
- 무료 리소스만 사용하여 완전 자동화 구현
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import requests
from typing import List, Dict, Any, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FenokAutomationEngine:
    """100xFenok 완전 자동화 엔진"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.base_dir = self.project_dir.parent.parent
        
        # 디렉터리 경로 설정
        self.communication_dir = self.base_dir / "communication" / "shared" / "100xfenok"
        self.output_dir = self.base_dir / "projects" / "100xFenok" / "100x" / "daily-wrap"
        self.secrets_file = self.base_dir / "secrets" / "my_sensitive_data.md"
        
        # 무료 LLM 설정 (Ollama)
        self.ollama_base_url = "http://localhost:11434"
        self.model_name = "qwen2.5:7b"  # 또는 "llama3.1:8b"
        
        self._ensure_directories()
        
    def _ensure_directories(self):
        """필요한 디렉터리 생성"""
        directories = [
            self.communication_dir / "002_terminalx",
            self.communication_dir / "003_terminalx", 
            self.communication_dir / "004_Lexi_Convert",
            self.communication_dir / "005_Json",
            self.communication_dir / "006_HTML",
            self.output_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def check_ollama_status(self) -> bool:
        """Ollama 서버 상태 확인"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
            
    def setup_ollama(self):
        """Ollama 및 모델 설치 (최초 1회)"""
        logger.info("Ollama 설정 확인 중...")
        
        if not self.check_ollama_status():
            logger.info("Ollama 설치 필요. 설치를 시작합니다...")
            # Ollama 설치 스크립트 실행
            subprocess.run(["powershell", "-Command", 
                          "Invoke-WebRequest -UseBasicParsing https://ollama.ai/install.ps1 | Invoke-Expression"],
                          check=True)
            
        # 모델 다운로드
        logger.info(f"{self.model_name} 모델 다운로드 중...")
        subprocess.run(["ollama", "pull", self.model_name], check=True)
        
    def call_local_llm(self, prompt: str, system_prompt: str = "") -> str:
        """로컬 LLM 호출 (무료)"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=300  # 5분 타임아웃
            )
            
            return response.json().get("response", "")
            
        except Exception as e:
            logger.error(f"LLM 호출 실패: {e}")
            return ""
    
    def integrate_json_data(self, part1_files: List[Path], part2_files: List[Path], 
                           html_files: List[Path]) -> Dict[str, Any]:
        """JSON 데이터 통합 (로컬 LLM 사용)"""
        logger.info("JSON 데이터 통합 시작...")
        
        # Instruction 프롬프트 로드
        instruction_file = self.communication_dir / "005_Json" / "Instruction_Json_20250726.md"
        with open(instruction_file, 'r', encoding='utf-8') as f:
            instruction = f.read()
            
        # 모든 소스 파일 내용 수집
        source_data = {
            "part1_files": [],
            "part2_files": [],
            "html_files": []
        }
        
        for file_list, key in [(part1_files, "part1_files"), 
                              (part2_files, "part2_files"),
                              (html_files, "html_files")]:
            for file_path in file_list:
                try:
                    if file_path.suffix == '.json':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = json.load(f)
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    
                    source_data[key].append({
                        "filename": file_path.name,
                        "content": content
                    })
                except Exception as e:
                    logger.error(f"파일 읽기 실패 {file_path}: {e}")
        
        # LLM 프롬프트 구성
        prompt = f"""
{instruction}

=== 소스 데이터 ===
{json.dumps(source_data, indent=2, ensure_ascii=False)}

위의 지시사항과 소스 데이터를 바탕으로 Part1과 Part2를 각각 통합한 JSON을 생성해주세요.
"""
        
        system_prompt = "당신은 월스트리트 수준의 금융 데이터 분석가입니다. 제공된 지시사항을 정확히 따라 고품질의 금융 리포트를 생성하세요."
        
        # LLM 호출
        result = self.call_local_llm(prompt, system_prompt)
        
        try:
            # JSON 파싱 시도
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_content = result[json_start:json_end]
                return json.loads(json_content)
        except:
            logger.error("LLM 응답에서 JSON 파싱 실패")
            
        return {}
    
    def generate_final_html(self, part1_json: Dict, part2_json: Dict) -> str:
        """최종 HTML 생성"""
        logger.info("최종 HTML 생성 시작...")
        
        # HTML 생성 프롬프트 로드
        prompt_file = self.communication_dir / "006_HTML" / "wrap-generate-prompt.txt"
        template_file = self.communication_dir / "006_HTML" / "100x-daily-wrap-template.html"
        agent_file = self.communication_dir / "006_HTML" / "100x-wrap-agent.md"
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            base_prompt = f.read()
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        with open(agent_file, 'r', encoding='utf-8') as f:
            agent_guide = f.read()
            
        # LLM 프롬프트 구성
        prompt = f"""
{base_prompt}

=== 에이전트 가이드 ===
{agent_guide}

=== 템플릿 ===
{template}

=== Part 1 데이터 ===
{json.dumps(part1_json, indent=2, ensure_ascii=False)}

=== Part 2 데이터 ===
{json.dumps(part2_json, indent=2, ensure_ascii=False)}

위의 템플릿에 Part1과 Part2 데이터를 채워서 완전한 HTML 파일을 생성해주세요.
"""
        
        system_prompt = "당신은 전문적인 웹 개발자이자 금융 리포트 전문가입니다. 제공된 템플릿에 데이터를 정확히 매핑하여 완성된 HTML 파일을 생성하세요."
        
        # LLM 호출
        html_result = self.call_local_llm(prompt, system_prompt)
        
        return html_result
    
    def run_full_automation(self, target_date: str = None) -> bool:
        """완전 자동화 실행"""
        if not target_date:
            target_date = datetime.now().strftime("%Y-%m-%d")
            
        logger.info(f"=== 100xFenok 완전 자동화 시작 ({target_date}) ===")
        
        try:
            # 1. Ollama 설정 확인
            if not self.check_ollama_status():
                logger.info("Ollama 설정 필요")
                self.setup_ollama()
                
            # 2. 기존 TerminalX 자동화 실행 (1-25단계)
            logger.info("TerminalX 자동화 실행...")
            from main_generator import FenokReportGenerator
            
            terminalx_generator = FenokReportGenerator()
            # 여기에 기존 TerminalX 자동화 로직 호출
            
            # 3. 생성된 데이터 수집
            part1_files = list((self.communication_dir / "004_Lexi_Convert").glob("part1_*.json"))
            part2_files = list((self.communication_dir / "004_Lexi_Convert").glob("part2_*.json"))
            html_files = list((self.communication_dir / "003_terminalx").glob("*.html"))
            
            # 4. JSON 통합 (26-28단계)
            integrated_data = self.integrate_json_data(part1_files, part2_files, html_files)
            
            if not integrated_data:
                logger.error("JSON 통합 실패")
                return False
                
            # 5. 최종 HTML 생성 (29-34단계)
            final_html = self.generate_final_html(
                integrated_data.get("part1", {}),
                integrated_data.get("part2", {})
            )
            
            # 6. 결과 저장
            output_file = self.output_dir / f"{target_date.replace('-', '')}_100x-daily-wrap.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_html)
                
            logger.info(f"✅ 자동화 완료! 파일 생성: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"자동화 실패: {e}")
            return False

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="100xFenok 완전 자동화")
    parser.add_argument("--date", help="대상 날짜 (YYYY-MM-DD)")
    parser.add_argument("--setup-only", action="store_true", help="Ollama 설정만 실행")
    
    args = parser.parse_args()
    
    engine = FenokAutomationEngine()
    
    if args.setup_only:
        engine.setup_ollama()
        print("✅ Ollama 설정 완료")
        return
        
    success = engine.run_full_automation(args.date)
    
    if success:
        print("🎉 100xFenok 데일리랩 자동화 성공!")
    else:
        print("❌ 자동화 실패. 로그를 확인하세요.")

if __name__ == "__main__":
    main()