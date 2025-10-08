HTML 품질 검토 및 개선안 제시를 수행합니다.

**사용법**:
```
/review-html
```

**실행 내용**:
1. `Feno_Docs/Claude_Integration/quality_reviewer.md` 룰북 적용
2. 1차 생성 HTML 파일 로드 (DL02 결과물)
3. 5대 원칙 기반 검토:
   - 원칙 1: 데이터 무결성 (누락 확인)
   - 원칙 2: 구조적 일관성 (의도된 생략 존중)
   - 원칙 3: 가독성 극대화 (줄글 재구성)
   - 원칙 4: 시각적 계층 (핵심 강조)
   - 원칙 5: 컨텍스트 스타일링 (의미 추가)
4. Before/After 코드 조각으로 개선안 제시

**출력**:
- 검토 요약 (데이터 무결성, 구조, 가독성, 시각, 스타일링)
- 개선 제안 목록 (Before/After 코드 포함)
- 검증 완료 체크리스트

**참고**: `Feno_Docs/Claude_Integration/quality_reviewer.md` 파일의 모든 규칙을 엄격히 따릅니다.
