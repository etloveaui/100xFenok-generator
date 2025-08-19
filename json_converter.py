#!/usr/bin/env python3
"""
HTML → JSON 변환기 (100xFenok 특화)
- TerminalX HTML 구조에 최적화
- 금융 데이터 테이블 특별 처리
- 기존 Python_Lexi_Convert 기능 개선
"""

import os
import json
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
import pandas as pd
from io import StringIO
import logging
import re

logger = logging.getLogger(__name__)

class TerminalXJSONConverter:
    """TerminalX HTML을 JSON으로 변환하는 클래스"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.base_dir = self.project_dir.parent.parent
        self.communication_dir = self.base_dir / "communication" / "shared" / "100xfenok"
        
    def convert_html_file(self, html_file_path, output_file_path=None):
        """단일 HTML 파일을 JSON으로 변환"""
        try:
            html_path = Path(html_file_path)
            if not html_path.exists():
                logger.error(f"HTML 파일을 찾을 수 없음: {html_file_path}")
                return None
            
            # HTML 파일 읽기
            with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
                html_content = f.read()
            
            # JSON 변환
            json_data = self._parse_html_to_json(html_content, html_path.name)
            
            # 출력 파일 경로 결정
            if not output_file_path:
                output_file_path = html_path.with_suffix('.json')
            
            # JSON 파일 저장
            output_path = Path(output_file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"JSON 변환 완료: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"HTML → JSON 변환 실패: {e}")
            return None
    
    def _parse_html_to_json(self, html_content, filename):
        """HTML 내용을 JSON으로 파싱"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        json_data = {
            "metadata": {
                "source_file": filename,
                "conversion_date": datetime.now().isoformat(),
                "converter": "TerminalXJSONConverter v1.0"
            },
            "sections": []
        }
        
        # 1. 제목 추출
        title = self._extract_title(soup)
        if title:
            json_data["title"] = title
        
        # 2. 메인 컨텐츠 영역 찾기
        main_content = self._find_main_content(soup)
        
        if main_content:
            # 3. 섹션별로 파싱
            sections = self._parse_sections(main_content)
            json_data["sections"] = sections
        else:
            # 전체 문서를 하나의 섹션으로 처리
            json_data["sections"] = [self._parse_full_document(soup)]
        
        return json_data
    
    def _extract_title(self, soup):
        """HTML에서 제목 추출"""
        title_selectors = [
            'h1',
            '.title',
            '.text-\\[22px\\]',
            '.text-\\[\\#121212\\]',
            '[class*="title"]'
        ]
        
        for selector in title_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text().strip()
                    if title and len(title) < 200:  # 제목은 200자 미만
                        return title
            except:
                continue
        
        return None
    
    def _find_main_content(self, soup):
        """메인 컨텐츠 영역 찾기"""
        content_selectors = [
            '.text-\\[\\#121212\\]',
            '.main-content',
            'main',
            '.content',
            '[class*="content"]',
            'body'
        ]
        
        for selector in content_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    return element
            except:
                continue
        
        return soup
    
    def _parse_sections(self, main_content):
        """메인 컨텐츠를 섹션별로 파싱"""
        sections = []
        current_section = None
        
        # 모든 직접 하위 요소들을 순회
        for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'table', 'ul', 'ol'], recursive=False):
            # 헤딩 태그를 만나면 새 섹션 시작
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if current_section:
                    sections.append(current_section)
                
                current_section = {
                    "title": element.get_text().strip(),
                    "level": int(element.name[1]),  # h1 → 1, h2 → 2
                    "content": []
                }
            else:
                # 현재 섹션이 없으면 기본 섹션 생성
                if not current_section:
                    current_section = {
                        "title": "Main Content",
                        "level": 1,
                        "content": []
                    }
                
                # 요소를 컨텐츠에 추가
                content_item = self._parse_element(element)
                if content_item:
                    current_section["content"].append(content_item)
        
        # 마지막 섹션 추가
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _parse_full_document(self, soup):
        """전체 문서를 하나의 섹션으로 파싱"""
        section = {
            "title": "Document Content",
            "level": 1,
            "content": []
        }
        
        # 모든 의미있는 요소들을 찾아서 파싱
        for element in soup.find_all(['p', 'div', 'table', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            content_item = self._parse_element(element)
            if content_item:
                section["content"].append(content_item)
        
        return section
    
    def _parse_element(self, element):
        """개별 HTML 요소를 JSON 형태로 파싱"""
        if element.name == 'table':
            return self._parse_table(element)
        elif element.name in ['ul', 'ol']:
            return self._parse_list(element)
        elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return self._parse_heading(element)
        elif element.name in ['p', 'div']:
            return self._parse_text_content(element)
        else:
            # 기본 텍스트 처리
            text = element.get_text().strip()
            if text:
                return {
                    "type": "text",
                    "content": text
                }
        
        return None
    
    def _parse_table(self, table_element):
        """테이블 파싱"""
        try:
            table_data = {
                "type": "table",
                "headers": [],
                "data": []
            }
            
            # 헤더 추출
            header_row = table_element.find('thead')
            if header_row:
                headers = header_row.find_all(['th', 'td'])
                table_data["headers"] = [h.get_text().strip() for h in headers]
            else:
                # thead가 없으면 첫 번째 행을 헤더로 사용
                first_row = table_element.find('tr')
                if first_row:
                    headers = first_row.find_all(['th', 'td'])
                    table_data["headers"] = [h.get_text().strip() for h in headers]
                    # 첫 번째 행 제거 (이미 헤더로 사용)
                    first_row.decompose()
            
            # 데이터 행 추출
            tbody = table_element.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
            else:
                rows = table_element.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text().strip() for cell in cells]
                if any(row_data):  # 빈 행이 아닌 경우만 추가
                    table_data["data"].append(row_data)
            
            # pandas를 사용한 추가 검증 및 정제
            if table_data["headers"] and table_data["data"]:
                try:
                    df = pd.DataFrame(table_data["data"], columns=table_data["headers"])
                    # 금융 데이터 특별 처리
                    table_data = self._enhance_financial_table(table_data, df)
                except Exception as e:
                    logger.warning(f"테이블 검증 실패: {e}")
            
            return table_data
            
        except Exception as e:
            logger.error(f"테이블 파싱 실패: {e}")
            return {
                "type": "table",
                "error": str(e),
                "raw_html": str(table_element)
            }
    
    def _enhance_financial_table(self, table_data, df):
        """금융 데이터 테이블 특별 처리"""
        try:
            # 숫자 데이터 형식 정리
            for i, row in enumerate(table_data["data"]):
                enhanced_row = []
                for j, cell in enumerate(row):
                    # 통화 기호, 퍼센트 기호 등 처리
                    enhanced_cell = self._clean_financial_data(cell)
                    enhanced_row.append(enhanced_cell)
                table_data["data"][i] = enhanced_row
            
            # 테이블 유형 감지
            table_type = self._detect_table_type(table_data["headers"])
            if table_type:
                table_data["table_type"] = table_type
            
        except Exception as e:
            logger.warning(f"금융 테이블 처리 실패: {e}")
        
        return table_data
    
    def _clean_financial_data(self, cell_value):
        """금융 데이터 정제"""
        if not cell_value or not isinstance(cell_value, str):
            return cell_value
        
        # 공통 정제 작업
        cleaned = cell_value.strip()
        
        # 퍼센트 처리
        if '%' in cleaned:
            try:
                # "3.85%" → {"value": 3.85, "unit": "%", "formatted": "3.85%"}
                numeric = re.findall(r'(-?\d+\.?\d*)', cleaned)
                if numeric:
                    return {
                        "value": float(numeric[0]),
                        "unit": "%",
                        "formatted": cleaned
                    }
            except:
                pass
        
        # 통화 처리
        if '$' in cleaned or '€' in cleaned or '¥' in cleaned:
            try:
                # "$150.25" → {"value": 150.25, "unit": "$", "formatted": "$150.25"}
                numeric = re.findall(r'(-?\d+\.?\d*)', cleaned.replace(',', ''))
                if numeric:
                    currency_symbol = '$' if '$' in cleaned else '€' if '€' in cleaned else '¥'
                    return {
                        "value": float(numeric[0]),
                        "unit": currency_symbol,
                        "formatted": cleaned
                    }
            except:
                pass
        
        # 일반 숫자 처리
        try:
            if cleaned.replace('.', '').replace('-', '').replace(',', '').isdigit():
                return float(cleaned.replace(',', ''))
        except:
            pass
        
        return cleaned
    
    def _detect_table_type(self, headers):
        """테이블 타입 자동 감지"""
        if not headers:
            return None
        
        header_text = ' '.join(headers).lower()
        
        if any(keyword in header_text for keyword in ['ticker', 'symbol', 'stock']):
            return 'stock_data'
        elif any(keyword in header_text for keyword in ['rate', 'yield', 'bond']):
            return 'interest_rates'
        elif any(keyword in header_text for keyword in ['action', 'rating', 'upgrade', 'downgrade']):
            return 'analyst_ratings'
        elif any(keyword in header_text for keyword in ['sector', 'industry']):
            return 'sector_data'
        else:
            return 'general'
    
    def _parse_list(self, list_element):
        """리스트 파싱"""
        list_data = {
            "type": "list",
            "ordered": list_element.name == 'ol',
            "items": []
        }
        
        for li in list_element.find_all('li', recursive=False):
            item_text = li.get_text().strip()
            if item_text:
                list_data["items"].append(item_text)
        
        return list_data
    
    def _parse_heading(self, heading_element):
        """헤딩 파싱"""
        return {
            "type": "heading",
            "level": int(heading_element.name[1]),  # h1 → 1
            "text": heading_element.get_text().strip()
        }
    
    def _parse_text_content(self, text_element):
        """텍스트 컨텐츠 파싱"""
        text = text_element.get_text().strip()
        
        if not text:
            return None
        
        # 텍스트 길이에 따라 타입 결정
        if len(text) > 500:
            return {
                "type": "paragraph",
                "content": text
            }
        else:
            return {
                "type": "text",
                "content": text
            }
    
    def batch_convert_directory(self, input_dir, output_dir=None):
        """디렉터리 내 모든 HTML 파일 일괄 변환"""
        input_path = Path(input_dir)
        if not input_path.exists():
            logger.error(f"입력 디렉터리를 찾을 수 없음: {input_dir}")
            return []
        
        if not output_dir:
            output_dir = input_path / "json_output"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        converted_files = []
        
        # HTML 파일들 찾기
        html_files = list(input_path.glob("*.html"))
        
        logger.info(f"{len(html_files)}개 HTML 파일 변환 시작...")
        
        for html_file in html_files:
            try:
                output_file = output_path / f"{html_file.stem}.json"
                result = self.convert_html_file(html_file, output_file)
                
                if result:
                    converted_files.append(result)
                    logger.info(f"변환 완료: {html_file.name}")
                else:
                    logger.error(f"변환 실패: {html_file.name}")
                    
            except Exception as e:
                logger.error(f"파일 {html_file.name} 변환 중 오류: {e}")
        
        logger.info(f"일괄 변환 완료: {len(converted_files)}/{len(html_files)}")
        return converted_files

def main():
    """메인 실행 함수"""
    import argparse
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description="TerminalX HTML → JSON 변환기")
    parser.add_argument("--file", help="변환할 HTML 파일 경로")
    parser.add_argument("--dir", help="변환할 HTML 파일들이 있는 디렉터리")
    parser.add_argument("--output", help="출력 파일/디렉터리 경로")
    parser.add_argument("--test", action="store_true", help="테스트 모드 (샘플 데이터 사용)")
    
    args = parser.parse_args()
    
    converter = TerminalXJSONConverter()
    
    if args.test:
        # 테스트 모드: 샘플 HTML 생성 및 변환
        test_html = '''
        <html>
        <head><title>Test Report</title></head>
        <body>
            <div class="text-[#121212]">
                <h1>Test Financial Report</h1>
                <p>This is a test paragraph.</p>
                <table>
                    <thead>
                        <tr><th>Ticker</th><th>Price</th><th>Change</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>AAPL</td><td>$150.25</td><td>+2.5%</td></tr>
                        <tr><td>GOOGL</td><td>$2800.50</td><td>-1.2%</td></tr>
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        '''
        
        # 임시 파일로 저장 후 변환
        test_file = converter.project_dir / "test_sample.html"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_html)
        
        result = converter.convert_html_file(test_file)
        
        if result:
            print(f"테스트 변환 성공: {result}")
            # 결과 출력
            with open(result, 'r', encoding='utf-8') as f:
                print("\n변환 결과:")
                print(json.dumps(json.load(f), indent=2, ensure_ascii=False))
        else:
            print("테스트 변환 실패")
        
        # 임시 파일 정리
        test_file.unlink(missing_ok=True)
        
    elif args.file:
        # 단일 파일 변환
        result = converter.convert_html_file(args.file, args.output)
        if result:
            print(f"변환 성공: {result}")
        else:
            print("변환 실패")
            
    elif args.dir:
        # 디렉터리 일괄 변환
        results = converter.batch_convert_directory(args.dir, args.output)
        print(f"일괄 변환 완료: {len(results)}개 파일")
        for result in results:
            print(f"  - {result}")
    else:
        print("사용법:")
        print("  --file <HTML파일>     : 단일 파일 변환")
        print("  --dir <디렉터리>      : 디렉터리 일괄 변환")
        print("  --test               : 테스트 모드")

if __name__ == "__main__":
    main()