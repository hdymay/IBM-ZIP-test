"""
ConfigManager 단위 테스트

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.config.config_manager import ConfigManager
from src.models.data_models import Configuration


@pytest.fixture
def temp_config_dir(tmp_path):
    """임시 설정 디렉토리 생성"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def config_manager(temp_config_dir):
    """ConfigManager 인스턴스 생성"""
    config_file = temp_config_dir / "settings.json"
    key_file = temp_config_dir / ".key"
    return ConfigManager(str(config_file), str(key_file))


@pytest.fixture
def sample_config():
    """샘플 Configuration 객체"""
    return Configuration(
        watsonx_api_key="test_api_key_12345",
        watsonx_endpoint="https://test.watsonx.ai",
        watsonx_project_id="test_project_123",
        output_directory="./output",
        max_retries=3,
        timeout=300
    )


class TestConfigManager:
    """ConfigManager 테스트 클래스"""
    
    def test_init_creates_key_file(self, config_manager):
        """초기화 시 암호화 키 파일 생성 확인"""
        assert config_manager.key_file.exists()
        assert config_manager._cipher is not None
    
    def test_save_and_load_config(self, config_manager, sample_config):
        """설정 저장 및 로드 테스트"""
        # 설정 저장
        config_manager.save_config(sample_config)
        assert config_manager.config_file.exists()
        
        # 설정 로드
        loaded_config = config_manager.load_config()
        
        # 검증
        assert loaded_config.watsonx_api_key == sample_config.watsonx_api_key
        assert loaded_config.watsonx_endpoint == sample_config.watsonx_endpoint
        assert loaded_config.watsonx_project_id == sample_config.watsonx_project_id
        assert loaded_config.output_directory == sample_config.output_directory
        assert loaded_config.max_retries == sample_config.max_retries
        assert loaded_config.timeout == sample_config.timeout
    
    def test_encrypt_decrypt(self, config_manager):
        """암호화 및 복호화 테스트"""
        original = "test_secret_value"
        encrypted = config_manager._encrypt(original)
        decrypted = config_manager._decrypt(encrypted)
        
        assert encrypted != original
        assert decrypted == original
    
    def test_load_from_env(self, config_manager, monkeypatch):
        """환경 변수에서 설정 로드 테스트"""
        # 환경 변수 설정
        monkeypatch.setenv('WATSONX_API_KEY', 'env_api_key')
        monkeypatch.setenv('WATSONX_ENDPOINT', 'https://env.watsonx.ai')
        monkeypatch.setenv('WATSONX_PROJECT_ID', 'env_project_id')
        monkeypatch.setenv('OUTPUT_DIRECTORY', './env_output')
        monkeypatch.setenv('MAX_RETRIES', '5')
        monkeypatch.setenv('TIMEOUT', '600')
        
        # 환경 변수에서 로드
        config_dict = config_manager._load_from_env()
        
        # 검증
        assert config_dict['watsonx_api_key'] == 'env_api_key'
        assert config_dict['watsonx_endpoint'] == 'https://env.watsonx.ai'
        assert config_dict['watsonx_project_id'] == 'env_project_id'
        assert config_dict['output_directory'] == './env_output'
        assert config_dict['max_retries'] == 5
        assert config_dict['timeout'] == 600

    
    def test_validate_config_success(self, config_manager, sample_config):
        """유효한 설정 검증 테스트"""
        assert config_manager.validate_config(sample_config) is True
    
    def test_validate_config_missing_api_key(self, config_manager):
        """API 키 누락 시 검증 실패 테스트"""
        invalid_config = Configuration(
            watsonx_api_key="",
            watsonx_endpoint="https://test.watsonx.ai",
            watsonx_project_id="test_project",
            output_directory="./output"
        )
        
        with pytest.raises(ValueError, match="watsonx_api_key는 필수입니다"):
            config_manager.validate_config(invalid_config)
    
    def test_validate_config_invalid_endpoint(self, config_manager):
        """잘못된 엔드포인트 형식 검증 실패 테스트"""
        invalid_config = Configuration(
            watsonx_api_key="test_key",
            watsonx_endpoint="invalid_endpoint",
            watsonx_project_id="test_project",
            output_directory="./output"
        )
        
        with pytest.raises(ValueError, match="http:// 또는 https://로 시작해야 합니다"):
            config_manager.validate_config(invalid_config)
    
    def test_validate_config_negative_retries(self, config_manager):
        """음수 재시도 횟수 검증 실패 테스트"""
        invalid_config = Configuration(
            watsonx_api_key="test_key",
            watsonx_endpoint="https://test.watsonx.ai",
            watsonx_project_id="test_project",
            output_directory="./output",
            max_retries=-1
        )
        
        with pytest.raises(ValueError, match="max_retries는 0 이상이어야 합니다"):
            config_manager.validate_config(invalid_config)
    
    def test_validate_config_zero_timeout(self, config_manager):
        """0 이하 타임아웃 검증 실패 테스트"""
        invalid_config = Configuration(
            watsonx_api_key="test_key",
            watsonx_endpoint="https://test.watsonx.ai",
            watsonx_project_id="test_project",
            output_directory="./output",
            timeout=0
        )
        
        with pytest.raises(ValueError, match="timeout은 0보다 커야 합니다"):
            config_manager.validate_config(invalid_config)
    
    def test_load_config_file_not_found(self, config_manager):
        """설정 파일이 없을 때 예외 발생 테스트"""
        with pytest.raises(FileNotFoundError, match="설정 파일이 없습니다"):
            config_manager.load_config()
    
    @patch('requests.get')
    def test_connection_success(self, mock_get, config_manager, sample_config):
        """연결 테스트 성공"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        success, error = config_manager.test_connection(sample_config)
        
        assert success is True
        assert error is None
    
    @patch('requests.get')
    def test_connection_auth_failure(self, mock_get, config_manager, sample_config):
        """인증 실패 테스트"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        success, error = config_manager.test_connection(sample_config)
        
        assert success is False
        assert "인증 실패" in error
    
    @patch('requests.get')
    def test_connection_not_found(self, mock_get, config_manager, sample_config):
        """프로젝트를 찾을 수 없음 테스트"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        success, error = config_manager.test_connection(sample_config)
        
        assert success is False
        assert "프로젝트를 찾을 수 없습니다" in error
    
    @patch('requests.get')
    def test_connection_timeout(self, mock_get, config_manager, sample_config):
        """연결 시간 초과 테스트"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        success, error = config_manager.test_connection(sample_config)
        
        assert success is False
        assert "연결 시간 초과" in error
    
    @patch('requests.get')
    def test_connection_error(self, mock_get, config_manager, sample_config):
        """연결 오류 테스트"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        success, error = config_manager.test_connection(sample_config)
        
        assert success is False
        assert "연결 실패" in error
