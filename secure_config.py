"""
Secure Configuration Management
환경 변수 기반 보안 크레덴셜 관리 시스템
"""

import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv


class SecureConfig:
    """
    환경 변수에서 보안 크레덴셜을 안전하게 로드

    Usage:
        config = SecureConfig()
        email = config.get('TERMINALX_EMAIL')
        password = config.get('TERMINALX_PASSWORD')
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        환경 변수 로드

        Args:
            env_file: .env 파일 경로 (기본값: 프로젝트 루트의 .env)
        """
        if env_file is None:
            # 프로젝트 루트 찾기
            current_dir = Path(__file__).resolve().parent
            env_file = current_dir / '.env'

        # .env 파일 로드
        if Path(env_file).exists():
            load_dotenv(env_file)
            print(f"✅ Loaded environment variables from: {env_file}")
        else:
            print(f"⚠️  Warning: .env file not found at {env_file}")
            print(f"   Please copy .env.example to .env and fill in your credentials")

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        환경 변수 값 가져오기

        Args:
            key: 환경 변수 이름
            default: 기본값 (없으면 None)

        Returns:
            환경 변수 값 또는 기본값

        Raises:
            ValueError: 필수 값이 없고 기본값도 없는 경우
        """
        value = os.environ.get(key, default)

        if value is None:
            raise ValueError(
                f"Required environment variable '{key}' not found. "
                f"Please set it in your .env file or system environment."
            )

        return value

    def get_all(self) -> Dict[str, str]:
        """
        모든 환경 변수 반환 (디버깅용, 프로덕션에서는 사용하지 말 것)

        Returns:
            환경 변수 딕셔너리
        """
        return dict(os.environ)

    @property
    def terminalx_email(self) -> str:
        """TerminalX 이메일"""
        return self.get('TERMINALX_EMAIL')

    @property
    def terminalx_password(self) -> str:
        """TerminalX 비밀번호"""
        return self.get('TERMINALX_PASSWORD')

    @property
    def openai_api_key(self) -> Optional[str]:
        """OpenAI API 키 (선택사항)"""
        return self.get('OPENAI_API_KEY', default='')

    @property
    def anthropic_api_key(self) -> Optional[str]:
        """Anthropic API 키 (선택사항)"""
        return self.get('ANTHROPIC_API_KEY', default='')

    @property
    def google_api_key(self) -> Optional[str]:
        """Google API 키 (선택사항)"""
        return self.get('GOOGLE_API_KEY', default='')


# 전역 인스턴스 (싱글톤 패턴)
_config: Optional[SecureConfig] = None


def get_config() -> SecureConfig:
    """
    전역 설정 인스턴스 반환 (싱글톤)

    Returns:
        SecureConfig 인스턴스
    """
    global _config
    if _config is None:
        _config = SecureConfig()
    return _config


# 편의 함수들
def get_terminalx_credentials() -> tuple[str, str]:
    """
    TerminalX 크레덴셜 반환

    Returns:
        (email, password) 튜플
    """
    config = get_config()
    return config.terminalx_email, config.terminalx_password


def get_api_key(service: str) -> Optional[str]:
    """
    특정 서비스의 API 키 반환

    Args:
        service: 'openai', 'anthropic', 'google' 등

    Returns:
        API 키 또는 None
    """
    config = get_config()
    key_name = f"{service.upper()}_API_KEY"
    return config.get(key_name, default='')


if __name__ == '__main__':
    # 테스트 코드
    print("=== Secure Config Test ===\n")

    try:
        config = SecureConfig()

        print("✅ Configuration loaded successfully\n")

        # TerminalX 크레덴셜 테스트 (실제 값은 마스킹)
        try:
            email = config.terminalx_email
            password = config.terminalx_password
            print(f"TerminalX Email: {email[:5]}***@{email.split('@')[1] if '@' in email else '***'}")
            print(f"TerminalX Password: {'*' * len(password)}")
        except ValueError as e:
            print(f"❌ TerminalX credentials error: {e}")

        print()

        # API 키 테스트 (실제 값은 마스킹)
        for service in ['openai', 'anthropic', 'google']:
            key = get_api_key(service)
            if key:
                masked = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
                print(f"✅ {service.capitalize()} API Key: {masked}")
            else:
                print(f"⚠️  {service.capitalize()} API Key: Not set")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease ensure:")
        print("1. .env file exists in project root")
        print("2. .env contains required variables (see .env.example)")
        print("3. python-dotenv is installed: pip install python-dotenv")
