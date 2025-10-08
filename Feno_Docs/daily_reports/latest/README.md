# 100x Daily Wrap - 표준 리포트 디렉토리

이 디렉토리는 **Claude Desktop Integration 워크플로우**를 위한 표준 파일 저장소입니다.

## 📁 디렉토리 구조

```
latest/
├── part1_01.json          # Part1 리포트 버전 1
├── part1_02.json          # Part1 리포트 버전 2
├── part1_03.json          # Part1 리포트 버전 3
├── part2_01.json          # Part2 리포트 버전 1
├── part2_02.json          # Part2 리포트 버전 2
├── part2_03.json          # Part2 리포트 버전 3
└── general/               # 일반 리포트 (HTML)
    ├── 3.1_3.2_Gain_Lose.html
    ├── 3.3_Fixed_Income.html
    ├── 5.1_Major_IB_Updates.html
    ├── 6.3_Dark_Pool.html
    ├── 7.1_11_GICS_Sector.html
    └── 8.1_12_Key_Tickers.html
```

## 🔧 사용 방법

### STEP 1: 리포트 파일 저장
TerminalX에서 생성된 모든 리포트 파일을 이 디렉토리에 저장하세요:
- **Part1/Part2 JSON**: `latest/` 디렉토리에 직접 저장
- **일반 리포트 HTML**: `latest/general/` 하위 디렉토리에 저장

### STEP 2: 품질 선택 지시 작성
`Feno_Docs/Claude_Integration/quality_selection_guide.md`를 참고하여 출처 지정 문서를 작성하세요.

**예시**:
```markdown
# 출처 지정

## Part1
- 섹션 1: part1_02.json
- 섹션 3.3: part1_03.json + 3.3_Fixed_Income.html (파일 조합)

## Part2
- 섹션 7.1: 7.1_11_GICS_Sector.html
```

**중요**: 파일명만 입력하면 됩니다. 전체 경로는 Claude가 자동으로 구성합니다.

### STEP 3: 통합 워크플로우 실행
Claude Desktop에서 다음 명령 실행:
```
/full-workflow
```

또는 개별 단계:
```
/integrate-json    # DL01: JSON 통합
/generate-html     # DL02: HTML 생성
/review-html       # DL03: 품질 검토
/update-index      # DL04: 인덱스 업데이트
```

## ⚙️ 자동 경로 구성 방식

사용자가 제공한 파일명은 다음과 같이 자동으로 전체 경로로 변환됩니다:

| 사용자 입력 | 자동 구성 경로 |
|------------|---------------|
| `part1_01.json` | `Feno_Docs/daily_reports/latest/part1_01.json` |
| `3.3_Fixed_Income.html` | `Feno_Docs/daily_reports/latest/general/3.3_Fixed_Income.html` |

## 📝 주의사항

1. **파일 명명 규칙 준수**: 정확한 파일명을 사용해야 자동 탐색이 작동합니다.
2. **디렉토리 구조 유지**: `general/` 하위 디렉토리는 HTML 파일 전용입니다.
3. **경로 입력 금지**: 파일명만 입력하세요. 경로는 자동으로 추가됩니다.

## 🎯 워크플로우 장점

- **이식성**: 다른 환경에서도 동일한 디렉토리 구조로 작동
- **간편성**: 파일명만 입력하면 자동으로 경로 구성
- **안정성**: MCP filesystem을 통한 안전한 파일 접근

---

**마지막 업데이트**: 2025-10-08
**버전**: Claude Integration v1.0
