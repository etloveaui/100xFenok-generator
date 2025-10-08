JSON 파일 통합을 수행합니다.

**사용법**:
```
/integrate-json
```

**실행 내용**:
1. `Feno_Docs/Claude_Integration/integration_agent.md` 룰북 적용
2. 사용자가 제공한 Part1×3, Part2×3, 일반×6 파일들을 읽기
3. 사용자가 지정한 출처 요약에 따라 섹션별 최우수 답변 선택
4. 오류 데이터 보정 + 인용 제거 + 표준화
5. 통합 JSON 생성 (한글 번역 포함)

**출력**:
- 섹션별 출처 요약 리포트 (Markdown)
- 최종 통합 JSON 파일

**참고**: `Feno_Docs/Claude_Integration/integration_agent.md` 파일의 모든 규칙을 엄격히 따릅니다.
