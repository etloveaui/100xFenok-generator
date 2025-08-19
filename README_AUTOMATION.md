# 🤖 100xFenok 완전 자동화 시스템

## 📋 개요

100xFenok Daily Wrap을 **완전 무료**로 자동화하는 시스템입니다. 기존의 수동 작업을 90% 이상 줄이고, 일관된 품질의 리포트를 매일 자동으로 생성합니다.

## 🎯 자동화 범위

### ✅ 완전 자동화 단계 (34단계 → 자동)
- **1-15단계**: TerminalX 리포트 생성 (Selenium)
- **16-25단계**: HTML 추출 및 JSON 변환 
- **26-28단계**: JSON 통합 (Local LLM)
- **29-34단계**: 최종 HTML 생성 (Local LLM)

### 🚀 핵심 특징
- **100% 무료**: Ollama (Local LLM) + 오픈소스 도구만 사용
- **품질 보장**: 자동 검증 시스템으로 데이터 정확성 확보
- **완전 자동**: Windows Task Scheduler로 매일 자동 실행
- **모니터링**: 이메일/Discord 알림으로 실행 결과 통지

## 🛠 설치 및 설정

### 1단계: 의존성 설치
```bash
cd C:\\Users\\etlov\\multi-agent-workspace\\projects\\100xFenok-generator
pip install -r requirements_enhanced.txt
```

### 2단계: Ollama 설치 (무료 LLM)
```bash
# 자동 설치
python enhanced_automation.py --setup-only

# 또는 수동 설치
# https://ollama.ai 에서 다운로드 후 설치
ollama pull qwen2.5:7b
```

### 3단계: Windows Task Scheduler 등록
```bash
python daily_automation.py --setup-task
```

### 4단계: 설정 파일 편집 (선택사항)
```bash
python daily_automation.py --config
```

## 📊 사용 방법

### 즉시 실행 (테스트)
```bash
# 기존 데이터로 파이프라인 테스트
python pipeline_integration.py --test-run

# 특정 날짜로 완전 실행
python pipeline_integration.py --date 2025-08-19
```

### 일일 자동화 테스트
```bash
# 테스트 모드로 일일 자동화 실행
python daily_automation.py --test-run
```

### 스케줄 확인
- Windows 작업 스케줄러에서 "100xFenok_Daily_Automation" 작업 확인
- 기본값: 매일 오전 6시 자동 실행

## 🔧 시스템 구성

### 파일 구조
```
100xFenok-generator/
├── enhanced_automation.py      # 메인 자동화 엔진 (Local LLM 통합)
├── data_validator.py          # 금융 데이터 검증 시스템
├── pipeline_integration.py    # 전체 파이프라인 관리
├── daily_automation.py        # 일일 스케줄링 및 모니터링
├── main_generator.py          # 기존 TerminalX 자동화
└── automation_config.json     # 자동 생성되는 설정 파일
```

### 데이터 흐름
```
TerminalX → HTML 추출 → JSON 변환 → Local LLM 통합 → HTML 생성 → 품질 검증 → 완료
```

## ⚙️ 설정 옵션

### automation_config.json 주요 설정
```json
{
  "schedule": {
    "time": "06:00",           // 실행 시간
    "weekdays_only": true      // 평일만 실행
  },
  "ollama": {
    "model": "qwen2.5:7b",     // 사용할 LLM 모델
    "auto_start": true         // 자동 시작
  },
  "quality_threshold": 70,      // 품질 점수 임계값
  "notification": {
    "enabled": false,          // 알림 활성화
    "email": { ... },          // 이메일 설정
    "discord": { ... }         // Discord 웹훅 설정
  }
}
```

## 🔍 문제 해결

### 일반적인 문제들

#### 1. TerminalX 리다이렉션 문제
```bash
# 디버깅 모드로 문제 확인
python main_generator.py --debug
```

#### 2. Ollama 연결 실패
```bash
# Ollama 서비스 재시작
ollama serve

# 모델 재다운로드
ollama pull qwen2.5:7b
```

#### 3. JSON 통합 실패
- `communication/shared/100xfenok/` 디렉터리의 소스 파일들 확인
- 로그 파일 `pipeline.log` 확인

#### 4. HTML 생성 오류
- 템플릿 파일 경로 확인
- LLM 응답 품질 확인

### 로그 위치
```
100xFenok-generator/
├── automation.log              # 자동화 로그
├── pipeline.log               # 파이프라인 로그
└── logs/daily_automation_YYYYMMDD.log  # 일별 로그
```

## 📈 성능 및 품질

### 예상 성능
- **시간 단축**: 6-8시간 → 30-60분 (90% 단축)
- **품질 점수**: 70점 이상 (자동 검증)
- **성공률**: 95% 이상 (안정된 환경에서)

### 품질 관리
- ✅ 금리 데이터 논리성 검증
- ✅ 주가 데이터 범위 확인  
- ✅ 애널리스트 등급 표준화
- ✅ 인용 부호 자동 제거
- ✅ HTML 구조 유효성 검사

## 🔄 업그레이드 계획

### Phase 1: 현재 (완료)
- [x] 기본 자동화 구축
- [x] Local LLM 통합
- [x] 품질 검증 시스템
- [x] 스케줄링 시스템

### Phase 2: 개선 (예정)
- [ ] Claude API 옵션 추가
- [ ] 웹 UI 대시보드
- [ ] 모바일 알림
- [ ] 성능 최적화

### Phase 3: 확장 (예정) 
- [ ] 다중 리포트 형식 지원
- [ ] 실시간 데이터 연동
- [ ] AI 분석 기능 추가

## 💡 사용 팁

1. **첫 실행**: 테스트 모드로 시작하여 시스템 확인
2. **품질 확인**: 생성된 리포트를 며칠간 수동 검토
3. **알림 설정**: 이메일 또는 Discord로 실행 결과 모니터링
4. **백업 활용**: 자동 백업된 파일로 과거 데이터 추적

## 🆘 지원

문제 발생 시:
1. 로그 파일 확인
2. GitHub Issues에 문제 보고
3. Discord 채널에서 실시간 도움

---

**🎉 이제 100xFenok Daily Wrap을 완전 자동으로 생성하세요!**