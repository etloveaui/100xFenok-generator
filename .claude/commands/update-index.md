인덱스 업데이트를 수행합니다.

**사용법**:
```
/update-index
```

**실행 내용**:
1. `Feno_Docs/Claude_Integration/index_manager.md` 룰북 적용
2. 최종 완성 HTML 파일 로드 (DL03 결과물)
3. 메타데이터 추출:
   - 날짜 (YYYY-MM-DD)
   - 제목
   - 요약 (200자 이내)
   - 주요 하이라이트 (3-5개)
   - 섹션 개수
   - 생성 시각
4. 신규 메타데이터 JSON 생성
5. 기존 인덱스 JSON 업데이트 (맨 앞에 추가)

**출력**:
- 신규 메타데이터 JSON 파일 (`Feno_Docs/index/YYYYMMDD_metadata.json`)
- 업데이트된 인덱스 JSON 파일 (`Feno_Docs/index/daily_wrap_index.json`)
- [알림 발송X]

**참고**: `Feno_Docs/Claude_Integration/index_manager.md` 파일의 모든 규칙을 엄격히 따릅니다.
