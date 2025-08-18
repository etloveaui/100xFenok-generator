# 100xFenok Generator 디버깅 가이드

## 🔧 개선된 디버깅 기능

### 1. 리다이렉션 추적 로깅
- 리포트 폼 URL로 이동 시도 전후의 URL을 추적
- 아카이브 페이지로 리다이렉션 시 자동 감지 및 대응
- 실제 도착한 URL과 목표 URL 비교

### 2. 자동 복구 시도
- 아카이브 페이지 리다이렉션 시 직접 재시도
- "새 리포트" 버튼을 통한 우회 접근 시도  
- 폼 페이지 도달 여부 최종 확인

### 3. 상세한 오류 처리
- TimeoutException 발생 시 현재 URL, 페이지 제목 출력
- 페이지 소스 일부 출력 (디버깅용)
- 각 단계별 진행 상황 상세 로깅

## 🚀 사용 방법

### 일반 실행
```bash
cd projects/100xFenok-generator
python main_generator.py
```

### 디버깅 모드 실행 
```bash  
python main_generator.py --debug
```

디버깅 모드에서는:
- 로그인만 수행 후 폼 접근 테스트
- 리다이렉션 문제 정확히 파악
- 브라우저를 열린 상태로 유지하여 수동 확인 가능

## 📋 문제 해결 단계

### STEP 1: 디버깅 모드로 문제 파악
```bash
python main_generator.py --debug
```

### STEP 2: 로그 분석
출력되는 로그에서 다음 확인:
- 실제 도착한 URL
- 리다이렉션 발생 여부  
- 폼 필드 발견 여부

### STEP 3: 필요시 추가 수정
디버깅 결과에 따라 `generate_report_html` 함수의 리다이렉션 처리 로직을 추가 개선

## 🎯 예상 출력

### 성공 시:
```
=== 디버깅 테스트: 로그인 및 리다이렉션 확인 ===
로그인 성공. 폼 페이지 접근 테스트 시작...
폼 URL로 이동: https://theterminalx.com/agent/enterprise/report/form/10
도착한 URL: https://theterminalx.com/agent/enterprise/report/form/10
✅ 폼 페이지 접근 성공
✅ Report Title 필드 발견
```

### 문제 발생 시:
```
=== 디버깅 테스트: 로그인 및 리다이렉션 확인 ===  
로그인 성공. 폼 페이지 접근 테스트 시작...
폼 URL로 이동: https://theterminalx.com/agent/enterprise/report/form/10
도착한 URL: https://theterminalx.com/agent/enterprise/report/archive
❌ 아카이브 페이지로 리다이렉션됨 - 문제 확인
```

## 🔍 추가 분석 포인트

1. **세션 만료**: 로그인 후 세션이 유효한 상태인지 확인
2. **권한 문제**: 해당 템플릿(ID: 10)에 대한 접근 권한 확인
3. **브라우저 설정**: User-Agent, 쿠키 등 브라우저 설정 이슈
4. **웹사이트 변경**: TerminalX 웹사이트의 구조 변경 가능성

이 디버깅 개선으로 정확한 문제 지점을 파악하고 효과적인 해결책을 찾을 수 있습니다.