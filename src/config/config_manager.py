"""
설정 관리자 모듈

이 모듈은 watsonx.ai 연결 설정을 관리합니다.
Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv
from cryptography.fernet import Fernet

from src.models.data_models import Configuration


class ConfigManager:
    """설정 파일 및 환경 변수 관리 클래스
    
    Requirements: 7.1, 7.2, 7.3, 7.4
    """
    
    def __init__(self, config_file: str = "config/settings.json", 
                 key_file: str = "config/.key"):
        """ConfigManager 초기화
        
        Args:
            config_file: 설정 파일 경로
            key_file: 암호화 키 파일 경로
        """
        self.config_file = Path(config_file)
        self.key_file = Path(key_file)
        self._cipher = None
        
        # 설정 디렉토리 생성
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 암호화 키 로드 또는 생성
        self._load_or_create_key()
    
    def _load_or_create_key(self) -> None:
        """암호화 키 로드 또는 생성
        
        Requirements: 7.4
        """
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        self._cipher = Fernet(key)
    
    def _encrypt(self, value: str) -> str:
        """문자열 암호화
        
        Args:
            value: 암호화할 문자열
            
        Returns:
            암호화된 문자열
            
        Requirements: 7.4
        """
        return self._cipher.encrypt(value.encode()).decode()
    
    def _decrypt(self, encrypted_value: str) -> str:
        """문자열 복호화
        
        Args:
            encrypted_value: 복호화할 문자열
            
        Returns:
            복호화된 문자열
            
        Requirements: 7.4
        """
        return self._cipher.decrypt(encrypted_value.encode()).decode()

    
    def load_config(self) -> Configuration:
        """설정 파일 로드
        
        환경 변수를 먼저 확인하고, 없으면 설정 파일에서 로드합니다.
        
        Returns:
            Configuration 객체
            
        Raises:
            FileNotFoundError: 설정 파일이 없고 환경 변수도 설정되지 않은 경우
            ValueError: 설정 값이 유효하지 않은 경우
            
        Requirements: 7.1, 7.2
        """
        # .env 파일 로드
        load_dotenv()
        
        # 환경 변수에서 먼저 읽기 시도
        config_dict = self._load_from_env()
        
        # 환경 변수에 없으면 설정 파일에서 읽기
        if not config_dict:
            if not self.config_file.exists():
                raise FileNotFoundError(
                    f"설정 파일이 없습니다: {self.config_file}. "
                    "환경 변수를 설정하거나 save_config()를 사용하여 설정을 저장하세요."
                )
            config_dict = self._load_from_file()
        
        # Configuration 객체 생성
        return Configuration(**config_dict)
    
    def _load_from_env(self) -> Dict[str, any]:
        """환경 변수에서 설정 로드
        
        Returns:
            설정 딕셔너리 (환경 변수가 없으면 빈 딕셔너리)
            
        Requirements: 7.2
        """
        watsonx_api_key = os.getenv('WATSONX_API_KEY')
        
        # 필수 환경 변수가 없으면 빈 딕셔너리 반환
        if not watsonx_api_key:
            return {}
        
        return {
            'watsonx_api_key': watsonx_api_key,
            'watsonx_endpoint': os.getenv('WATSONX_ENDPOINT', ''),
            'watsonx_project_id': os.getenv('WATSONX_PROJECT_ID', ''),
            'output_directory': os.getenv('OUTPUT_DIRECTORY', './output'),
            'max_retries': int(os.getenv('MAX_RETRIES', '3')),
            'timeout': int(os.getenv('TIMEOUT', '300')),
            # GitHub 설정 (선택적)
            'github_token': os.getenv('GITHUB_TOKEN'),
            'github_repo_url': os.getenv('GITHUB_REPO_URL'),
            'github_upload_enabled': os.getenv('GITHUB_UPLOAD_ENABLED', 'false').lower() == 'true'
        }
    
    def _load_from_file(self) -> Dict[str, any]:
        """설정 파일에서 설정 로드
        
        Returns:
            설정 딕셔너리
            
        Requirements: 7.1
        """
        with open(self.config_file, 'r', encoding='utf-8') as f:
            encrypted_config = json.load(f)
        
        # API 키 복호화
        config_dict = encrypted_config.copy()
        config_dict['watsonx_api_key'] = self._decrypt(
            encrypted_config['watsonx_api_key']
        )
        
        # GitHub 토큰 복호화 (있는 경우)
        if encrypted_config.get('github_token'):
            config_dict['github_token'] = self._decrypt(
                encrypted_config['github_token']
            )
        
        return config_dict
    
    def save_config(self, config: Configuration) -> None:
        """설정 파일 저장
        
        Args:
            config: 저장할 Configuration 객체
            
        Requirements: 7.1, 7.4
        """
        # API 키 암호화
        config_dict = {
            'watsonx_api_key': self._encrypt(config.watsonx_api_key),
            'watsonx_endpoint': config.watsonx_endpoint,
            'watsonx_project_id': config.watsonx_project_id,
            'output_directory': config.output_directory,
            'max_retries': config.max_retries,
            'timeout': config.timeout,
            # GitHub 설정 (선택적)
            'github_token': self._encrypt(config.github_token) if config.github_token else None,
            'github_repo_url': config.github_repo_url,
            'github_upload_enabled': config.github_upload_enabled
        }
        
        # 파일에 저장
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)

    
    def validate_config(self, config: Configuration) -> bool:
        """설정 검증
        
        Args:
            config: 검증할 Configuration 객체
            
        Returns:
            설정이 유효하면 True, 아니면 False
            
        Raises:
            ValueError: 설정 값이 유효하지 않은 경우
            
        Requirements: 7.3
        """
        errors = []
        
        # API 키 검증
        if not config.watsonx_api_key or len(config.watsonx_api_key.strip()) == 0:
            errors.append("watsonx_api_key는 필수입니다")
        
        # 엔드포인트 검증
        if not config.watsonx_endpoint or len(config.watsonx_endpoint.strip()) == 0:
            errors.append("watsonx_endpoint는 필수입니다")
        elif not config.watsonx_endpoint.startswith(('http://', 'https://')):
            errors.append("watsonx_endpoint는 http:// 또는 https://로 시작해야 합니다")
        
        # 프로젝트 ID 검증
        if not config.watsonx_project_id or len(config.watsonx_project_id.strip()) == 0:
            errors.append("watsonx_project_id는 필수입니다")
        
        # 출력 디렉토리 검증
        if not config.output_directory or len(config.output_directory.strip()) == 0:
            errors.append("output_directory는 필수입니다")
        
        # 재시도 횟수 검증
        if config.max_retries < 0:
            errors.append("max_retries는 0 이상이어야 합니다")
        
        # 타임아웃 검증
        if config.timeout <= 0:
            errors.append("timeout은 0보다 커야 합니다")
        
        if errors:
            raise ValueError("설정 검증 실패:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True
    
    def test_connection(self, config: Configuration) -> tuple[bool, Optional[str]]:
        """watsonx.ai API 연결 테스트
        
        Args:
            config: 테스트할 Configuration 객체
            
        Returns:
            (성공 여부, 에러 메시지) 튜플
            
        Requirements: 7.5
        """
        import requests
        
        try:
            # 설정 검증
            self.validate_config(config)
            
            # API 엔드포인트 구성
            # watsonx.ai의 실제 API 엔드포인트는 프로젝트에 따라 다를 수 있음
            # 여기서는 기본적인 연결 테스트를 수행
            url = f"{config.watsonx_endpoint.rstrip('/')}/v1/projects/{config.watsonx_project_id}"
            
            headers = {
                'Authorization': f'Bearer {config.watsonx_api_key}',
                'Content-Type': 'application/json'
            }
            
            # 연결 테스트 (timeout 적용)
            response = requests.get(
                url,
                headers=headers,
                timeout=min(config.timeout, 10)  # 연결 테스트는 최대 10초
            )
            
            if response.status_code == 200:
                return True, None
            elif response.status_code == 401:
                return False, "인증 실패: API 키가 유효하지 않습니다"
            elif response.status_code == 404:
                return False, "프로젝트를 찾을 수 없습니다: 프로젝트 ID를 확인하세요"
            else:
                return False, f"연결 실패: HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "연결 시간 초과: 엔드포인트를 확인하세요"
        except requests.exceptions.ConnectionError:
            return False, "연결 실패: 네트워크 연결 또는 엔드포인트를 확인하세요"
        except ValueError as e:
            return False, f"설정 오류: {str(e)}"
        except Exception as e:
            return False, f"예상치 못한 오류: {str(e)}"
