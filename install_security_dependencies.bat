@echo off
echo ============================================================
echo 보안 시스템 종속성 설치
echo ============================================================
echo.

echo [1/2] python-dotenv 설치 중...
pip install python-dotenv
if errorlevel 1 (
    echo ERROR: python-dotenv 설치 실패
    pause
    exit /b 1
)
echo ✅ python-dotenv 설치 완료

echo.
echo [2/2] (선택사항) git-filter-repo 설치 중...
echo Git 히스토리 정리를 더 빠르고 안전하게 수행합니다.
pip install git-filter-repo
if errorlevel 1 (
    echo ⚠️  git-filter-repo 설치 실패 (선택사항이므로 계속 진행)
    echo    Git 히스토리 정리 시 git filter-branch가 대신 사용됩니다.
) else (
    echo ✅ git-filter-repo 설치 완료
)

echo.
echo ============================================================
echo ✅ 설치 완료!
echo ============================================================
echo.
echo 다음 단계:
echo 1. .env.example을 .env로 복사
echo 2. .env에 새로운 크레덴셜 입력
echo 3. python secure_config.py 로 설정 테스트
echo.
pause
