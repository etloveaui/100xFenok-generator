#!/usr/bin/env python3
"""
금융 데이터 자동 검증 시스템
- 논리적 오류 탐지
- 데이터 품질 확인
- 이상 징후 알림
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class FinancialDataValidator:
    """금융 데이터 검증기"""
    
    def __init__(self):
        # 검증 규칙 정의
        self.validation_rules = {
            'interest_rates': self._validate_interest_rates,
            'stock_prices': self._validate_stock_prices,
            'percentages': self._validate_percentages,
            'consistency': self._validate_consistency,
            'logical_errors': self._validate_logical_errors
        }
        
        # 알려진 금융 상수
        self.financial_constants = {
            'max_stock_price': 10000,  # 현실적인 주가 상한
            'max_interest_rate': 50,   # 현실적인 금리 상한 (%)
            'min_interest_rate': -5,   # 현실적인 금리 하한 (%)
        }
        
    def validate_json_data(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """JSON 데이터 전체 검증"""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'corrections': [],
            'quality_score': 0
        }
        
        try:
            # 각 섹션별 검증
            sections = json_data.get('sections', [])
            
            for i, section in enumerate(sections):
                section_results = self._validate_section(section, i)
                
                validation_results['errors'].extend(section_results['errors'])
                validation_results['warnings'].extend(section_results['warnings'])
                validation_results['corrections'].extend(section_results['corrections'])
                
            # 전체 품질 점수 계산
            validation_results['quality_score'] = self._calculate_quality_score(validation_results)
            
            # 전체 유효성 판단
            validation_results['is_valid'] = len(validation_results['errors']) == 0
            
        except Exception as e:
            logger.error(f"JSON 검증 중 오류: {e}")
            validation_results['errors'].append(f"검증 시스템 오류: {e}")
            validation_results['is_valid'] = False
            
        return validation_results
    
    def _validate_section(self, section: Dict[str, Any], section_index: int) -> Dict[str, Any]:
        """섹션별 데이터 검증"""
        results = {'errors': [], 'warnings': [], 'corrections': []}
        
        section_title = section.get('title', f'Section {section_index}')
        content = section.get('content', [])
        
        for content_item in content:
            if content_item.get('type') == 'table':
                table_results = self._validate_table(content_item, section_title)
                self._merge_results(results, table_results)
                
            elif content_item.get('type') == 'paragraph':
                text_results = self._validate_text_content(content_item, section_title)
                self._merge_results(results, text_results)
                
        return results
    
    def _validate_table(self, table_item: Dict[str, Any], section_title: str) -> Dict[str, Any]:
        """테이블 데이터 검증"""
        results = {'errors': [], 'warnings': [], 'corrections': []}
        
        table_data = table_item.get('data', [])
        headers = table_item.get('headers', [])
        
        # 헤더 분석으로 데이터 유형 판단
        data_type = self._identify_table_type(headers)
        
        for row_idx, row in enumerate(table_data):
            if data_type == 'interest_rates':
                rate_results = self._validate_interest_rates(row, section_title, row_idx)
                self._merge_results(results, rate_results)
                
            elif data_type == 'stock_data':
                stock_results = self._validate_stock_prices(row, section_title, row_idx)
                self._merge_results(results, stock_results)
                
            elif data_type == 'analyst_ratings':
                rating_results = self._validate_analyst_ratings(row, section_title, row_idx)
                self._merge_results(results, rating_results)
        
        return results
    
    def _validate_interest_rates(self, data_row: List[Any], section: str, row_idx: int) -> Dict[str, Any]:
        """금리 데이터 검증"""
        results = {'errors': [], 'warnings': [], 'corrections': []}
        
        # 금리 값 추출 및 검증
        rate_values = []
        for cell in data_row:
            if isinstance(cell, str):
                # 퍼센트 값 추출 (예: "3.85%" -> 3.85)
                rate_match = re.search(r'(\d+\.?\d*)%', cell)
                if rate_match:
                    rate_values.append(float(rate_match.group(1)))
        
        # 논리적 검증
        if len(rate_values) >= 2:
            # 수익률 곡선 검증 (단기 vs 장기)
            short_term = rate_values[0] if len(rate_values) > 0 else None
            long_term = rate_values[-1] if len(rate_values) > 1 else None
            
            if short_term == long_term and short_term is not None:
                results['errors'].append({
                    'type': 'logical_error',
                    'location': f'{section} 테이블 행 {row_idx}',
                    'message': f'단기금리와 장기금리가 동일 ({short_term}%) - 비현실적',
                    'severity': 'high'
                })
                
            # 금리 범위 검증
            for rate in rate_values:
                if rate > self.financial_constants['max_interest_rate']:
                    results['warnings'].append({
                        'type': 'range_warning',
                        'location': f'{section} 테이블 행 {row_idx}',
                        'message': f'금리 {rate}%가 비정상적으로 높음',
                        'severity': 'medium'
                    })
                elif rate < self.financial_constants['min_interest_rate']:
                    results['warnings'].append({
                        'type': 'range_warning',
                        'location': f'{section} 테이블 행 {row_idx}',
                        'message': f'금리 {rate}%가 비정상적으로 낮음',
                        'severity': 'medium'
                    })
        
        return results
    
    def _validate_stock_prices(self, data_row: List[Any], section: str, row_idx: int) -> Dict[str, Any]:
        """주가 데이터 검증"""
        results = {'errors': [], 'warnings': [], 'corrections': []}
        
        # 주가 및 목표주가 추출
        prices = []
        for cell in data_row:
            if isinstance(cell, str):
                # 달러 표시 주가 추출 (예: "$150.25" -> 150.25)
                price_match = re.search(r'\$?(\d+\.?\d*)', cell)
                if price_match:
                    prices.append(float(price_match.group(1)))
        
        # 주가 범위 검증
        for price in prices:
            if price > self.financial_constants['max_stock_price']:
                results['warnings'].append({
                    'type': 'range_warning',
                    'location': f'{section} 테이블 행 {row_idx}',
                    'message': f'주가 ${price}가 비정상적으로 높음',
                    'severity': 'medium'
                })
            elif price <= 0:
                results['errors'].append({
                    'type': 'invalid_value',
                    'location': f'{section} 테이블 행 {row_idx}',
                    'message': f'주가가 0 이하 (${price})',
                    'severity': 'high'
                })
        
        return results
    
    def _validate_analyst_ratings(self, data_row: List[Any], section: str, row_idx: int) -> Dict[str, Any]:
        """애널리스트 등급 검증"""
        results = {'errors': [], 'warnings': [], 'corrections': []}
        
        # 등급 키워드 검증
        valid_actions = ['UPGRADE', 'DOWNGRADE', 'INITIATE', 'REINSTATE', 'RAISE_PT', 'DOUBLE_DOWNGRADE']
        
        for cell in data_row:
            if isinstance(cell, str):
                # Action 필드 검증
                if any(action in cell.upper() for action in valid_actions):
                    found_action = None
                    for action in valid_actions:
                        if action in cell.upper():
                            found_action = action
                            break
                    
                    # 표준화 제안
                    if found_action and cell.upper() != found_action:
                        results['corrections'].append({
                            'type': 'standardization',
                            'location': f'{section} 테이블 행 {row_idx}',
                            'original': cell,
                            'suggested': found_action,
                            'reason': 'Action 필드 표준화'
                        })
        
        return results
    
    def _validate_consistency(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 일관성 검증"""
        results = {'errors': [], 'warnings': [], 'corrections': []}
        
        # 같은 종목이 여러 섹션에서 다른 정보를 갖는지 확인
        ticker_info = {}
        
        sections = json_data.get('sections', [])
        for section in sections:
            content = section.get('content', [])
            for item in content:
                if item.get('type') == 'table':
                    # 티커 정보 수집
                    self._collect_ticker_info(item, ticker_info, section.get('title', ''))
        
        # 일관성 검증
        for ticker, info_list in ticker_info.items():
            if len(info_list) > 1:
                consistency_results = self._check_ticker_consistency(ticker, info_list)
                self._merge_results(results, consistency_results)
        
        return results
    
    def _validate_logical_errors(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """논리적 오류 검증"""
        results = {'errors': [], 'warnings': [], 'corrections': []}
        
        # 날짜 논리성 검증
        report_date = self._extract_report_date(json_data)
        if report_date:
            date_results = self._validate_date_logic(json_data, report_date)
            self._merge_results(results, date_results)
        
        return results
    
    def _identify_table_type(self, headers: List[str]) -> str:
        """테이블 헤더로 데이터 유형 식별"""
        header_text = ' '.join(headers).lower()
        
        if 'yield' in header_text or 'rate' in header_text or '년물' in header_text:
            return 'interest_rates'
        elif 'ticker' in header_text or 'price' in header_text or 'target' in header_text:
            return 'stock_data'
        elif 'action' in header_text or 'rating' in header_text:
            return 'analyst_ratings'
        else:
            return 'unknown'
    
    def _calculate_quality_score(self, validation_results: Dict[str, Any]) -> float:
        """품질 점수 계산 (0-100)"""
        base_score = 100
        
        # 오류와 경고에 따른 점수 차감
        errors = len(validation_results['errors'])
        warnings = len(validation_results['warnings'])
        
        # 오류는 10점씩, 경고는 5점씩 차감
        penalty = (errors * 10) + (warnings * 5)
        
        final_score = max(0, base_score - penalty)
        return final_score
    
    def _merge_results(self, target: Dict[str, Any], source: Dict[str, Any]):
        """검증 결과 병합"""
        for key in ['errors', 'warnings', 'corrections']:
            target[key].extend(source.get(key, []))
    
    def _validate_text_content(self, text_item: Dict[str, Any], section_title: str) -> Dict[str, Any]:
        """텍스트 내용 검증"""
        results = {'errors': [], 'warnings': [], 'corrections': []}
        
        text = text_item.get('text', '')
        
        # 인용 부호 제거 확인
        citation_pattern = r'\[\d+\]'
        if re.search(citation_pattern, text):
            results['corrections'].append({
                'type': 'citation_removal',
                'location': f'{section_title} 텍스트',
                'message': '인용 부호 [숫자] 제거 필요',
                'original_text': text[:100] + '...' if len(text) > 100 else text
            })
        
        return results
    
    def _collect_ticker_info(self, table_item: Dict[str, Any], ticker_info: Dict[str, List], section: str):
        """티커 정보 수집"""
        # 구현 생략 (실제로는 테이블에서 티커 정보를 추출하여 저장)
        pass
    
    def _check_ticker_consistency(self, ticker: str, info_list: List[Dict]) -> Dict[str, Any]:
        """티커 일관성 확인"""
        # 구현 생략 (실제로는 같은 티커의 서로 다른 정보를 비교)
        return {'errors': [], 'warnings': [], 'corrections': []}
    
    def _extract_report_date(self, json_data: Dict[str, Any]) -> Optional[datetime]:
        """리포트 날짜 추출"""
        # 구현 생략
        return None
    
    def _validate_date_logic(self, json_data: Dict[str, Any], report_date: datetime) -> Dict[str, Any]:
        """날짜 논리성 검증"""
        # 구현 생략
        return {'errors': [], 'warnings': [], 'corrections': []}

def main():
    """테스트 실행"""
    validator = FinancialDataValidator()
    
    # 테스트 데이터
    test_data = {
        "sections": [
            {
                "title": "채권 및 금리 정보",
                "content": [
                    {
                        "type": "table",
                        "headers": ["기간", "수익률"],
                        "data": [
                            ["2년물", "3.85%"],
                            ["10년물", "3.85%"]  # 동일한 금리 - 오류
                        ]
                    }
                ]
            }
        ]
    }
    
    results = validator.validate_json_data(test_data)
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()