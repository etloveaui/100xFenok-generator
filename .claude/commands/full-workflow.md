100x Daily Wrap 전체 통합 워크플로우를 실행합니다.

**사용법**:
```
/full-workflow
```

**전체 파이프라인**:
1. **DL01: JSON 통합** (`/integrate-json`)
   - Part1×3, Part2×3, 일반×6 파일 로드
   - 사용자 품질 선택 지시에 따라 섹션별 최우수 답변 통합
   - 오류 데이터 보정 + 인용 제거 + 표준화
   - 통합 JSON 생성 (한글 번역)

2. **DL02: HTML 생성** (`/generate-html`)
   - 통합 JSON → 100x Daily Wrap HTML 변환
   - 템플릿 기반 Section 1-11 정확 매핑
   - 키워드 강조 + 스타일링 적용
   - 데이터 완전성 검증

3. **DL03: 품질 검토** (`/review-html`)
   - 5대 원칙 기반 HTML 검토
   - 데이터 무결성, 구조, 가독성, 시각 계층, 컨텍스트 스타일링
   - Before/After 코드로 개선안 제시

4. **DL04: 인덱스 업데이트** (`/update-index`)
   - 메타데이터 추출 (날짜, 요약, 하이라이트)
   - 신규 메타데이터 JSON 생성
   - 인덱스 JSON 업데이트 (맨 앞에 추가)

**소요 시간**:
- **사용자 작업**: ~30분 (품질 선택 지시 + 검토 개선안 적용)
- **자동 처리**: ~10분 (DL01-DL04 실행)
- **총 소요**: ~40분 (기존 GEMINI 2시간 30분 → 70% 단축)

**워크플로우 모드**:
- **Semi-Automated**: 사용자가 품질 선택 → Claude가 통합/검토/인덱싱 자동화
- **Quality-Driven**: GEMINI 수준 품질 유지하면서 속도 향상

**입력 요구사항**:
- Part1 JSON 파일 3개 (part1_01.json, part1_02.json, part1_03.json)
- Part2 JSON 파일 3개 (part2_01.json, part2_02.json, part2_03.json)
- 일반 HTML 파일 6개 (선택 사항)
- 사용자 품질 선택 지시 (출처 지정 형식)

**출력 결과물**:
1. 섹션별 출처 요약 리포트 (Markdown)
2. 통합 JSON 파일
3. 100x Daily Wrap HTML 파일
4. 품질 검토 결과 (개선 제안)
5. 메타데이터 JSON 파일
6. 업데이트된 인덱스 JSON 파일

**사용 예시**:
```
사용자: /full-workflow

[DL01 시작]
사용자: 출처 지정 문서를 첨부하세요.
[사용자가 품질 선택 지시 제공]

[DL01 완료] → [DL02 시작]
[통합 JSON → HTML 변환 중...]

[DL02 완료] → [DL03 시작]
[품질 검토 중... 개선안 3개 발견]

[사용자가 개선안 검토 및 적용]

[DL03 완료] → [DL04 시작]
[메타데이터 추출 및 인덱스 업데이트 중...]

[DL04 완료]
✅ 전체 워크플로우 완료!
```

**참고**:
- 각 단계의 룰북은 `Feno_Docs/Claude_Integration/` 디렉토리 참조
- 개별 단계 실행도 가능 (`/integrate-json`, `/generate-html`, `/review-html`, `/update-index`)
- GEMINI 병렬 검증 권장 (첫 2주간 품질 확인용)
