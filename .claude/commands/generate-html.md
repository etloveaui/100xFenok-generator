HTML 리포트 생성을 수행합니다.

**사용법**:
```
/generate-html
```

**실행 내용**:
1. `Feno_Docs/Claude_Integration/html_generator.md` 룰북 적용
2. 통합 JSON 파일 로드 (DL01 결과물)
3. `100x-daily-wrap-template.html` 템플릿 로드
4. Section 1-11 모두 정확히 매핑
5. 키워드 강조 + 한글 번역 + 스타일링 적용
6. 데이터 완전성 검증 (항목 수 일치 확인)

**출력**:
- 완성된 100x Daily Wrap HTML 파일 (YYYYMMDD_100x_Daily_Wrap_Final.html)

**참고**: `Feno_Docs/Claude_Integration/html_generator.md` 파일의 모든 규칙을 엄격히 따릅니다.
