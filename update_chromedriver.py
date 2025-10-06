"""
ChromeDriver 자동 업데이트 스크립트
Chrome 브라우저 버전에 맞는 ChromeDriver 다운로드
"""
import os
import sys
import zipfile
import requests
import subprocess
from pathlib import Path

def get_chrome_version():
    """설치된 Chrome 버전 확인"""
    try:
        # Windows에서 Chrome 버전 확인
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(chrome_path):
            chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

        result = subprocess.run(
            ['powershell', '-Command', f'(Get-Item "{chrome_path}").VersionInfo.ProductVersion'],
            capture_output=True,
            text=True
        )
        version = result.stdout.strip()
        print(f"[OK] Chrome 버전: {version}")
        return version
    except Exception as e:
        print(f"[ERROR] Chrome 버전 확인 실패: {e}")
        return None

def download_chromedriver(chrome_version):
    """ChromeDriver 다운로드"""
    try:
        # Chrome 버전에서 메이저 버전만 추출
        major_version = chrome_version.split('.')[0]
        print(f"[INFO] Chrome 메이저 버전: {major_version}")

        # ChromeDriver 다운로드 URL (Chrome for Testing)
        url = f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}/win64/chromedriver-win64.zip"

        print(f"[DOWNLOAD] 다운로드 URL: {url}")

        # 다운로드
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            # 정확한 버전이 없으면 메이저 버전으로 시도
            print(f"[WARNING] 정확한 버전 없음, 메이저 버전으로 재시도...")
            # 최신 버전 확인 API 사용
            latest_url = f"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{major_version}"
            latest_response = requests.get(latest_url)
            if latest_response.status_code == 200:
                latest_version = latest_response.text.strip()
                url = f"https://storage.googleapis.com/chrome-for-testing-public/{latest_version}/win64/chromedriver-win64.zip"
                print(f"[INFO] 최신 버전 사용: {latest_version}")
                response = requests.get(url, stream=True)

        if response.status_code != 200:
            print(f"[ERROR] 다운로드 실패: HTTP {response.status_code}")
            return False

        # 임시 파일로 저장
        zip_path = "chromedriver_temp.zip"
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[OK] 다운로드 완료: {zip_path}")

        # 압축 해제
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("chromedriver_temp")

        print(f"[OK] 압축 해제 완료")

        # chromedriver.exe 찾기 및 이동
        chromedriver_exe = None
        for root, dirs, files in os.walk("chromedriver_temp"):
            if "chromedriver.exe" in files:
                chromedriver_exe = os.path.join(root, "chromedriver.exe")
                break

        if not chromedriver_exe:
            print(f"[ERROR] chromedriver.exe를 찾을 수 없습니다")
            return False

        # 기존 파일 백업
        if os.path.exists("chromedriver.exe"):
            os.rename("chromedriver.exe", "chromedriver.exe.backup")
            print(f"[BACKUP] 기존 파일 백업: chromedriver.exe.backup")

        # 새 파일 복사
        import shutil
        shutil.copy2(chromedriver_exe, "chromedriver.exe")
        print(f"[OK] 새 ChromeDriver 설치 완료")

        # 임시 파일 정리
        os.remove(zip_path)
        shutil.rmtree("chromedriver_temp")
        print(f"[CLEANUP] 임시 파일 정리 완료")

        return True

    except Exception as e:
        print(f"[ERROR] ChromeDriver 다운로드 실패: {e}")
        return False

def main():
    print("=" * 60)
    print("ChromeDriver 자동 업데이트")
    print("=" * 60)

    # Chrome 버전 확인
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("\n[ERROR] Chrome 버전을 확인할 수 없습니다")
        return False

    # ChromeDriver 다운로드
    print(f"\n[START] ChromeDriver 다운로드 중...")
    success = download_chromedriver(chrome_version)

    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] ChromeDriver 업데이트 완료!")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("[FAILED] ChromeDriver 업데이트 실패")
        print("=" * 60)
        print("\n수동 다운로드 방법:")
        print("1. https://googlechromelabs.github.io/chrome-for-testing/ 방문")
        print(f"2. Chrome {chrome_version} 버전용 ChromeDriver 다운로드")
        print("3. chromedriver.exe를 프로젝트 폴더에 복사")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
