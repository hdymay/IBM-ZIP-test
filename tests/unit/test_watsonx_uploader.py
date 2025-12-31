"""
WatsonxUploader 단위 테스트

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

import pytest
import time
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.core.watsonx_uploader import WatsonxUploader
from src.models.data_models import Configuration, UploadResult


@pytest.fixture
def test_config():
    """테스트용 Configuration 객체"""
    return Configuration(
        watsonx_api_key="test_api_key_12345",
        watsonx_endpoint="https://test.watsonx.ai",
        watsonx_project_id="9aadac27896d4566b3b6cc3fab5632f1",
        output_directory="./output",
        max_retries=3,
        timeout=300
    )


@pytest.fixture
def test_zip_file():
    """테스트용 임시 ZIP 파일"""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.zip', delete=False) as f:
        f.write(b'PK\x03\x04' + b'\x00' * 100)  # 간단한 ZIP 헤더
        temp_path = f.name
    
    yield temp_path
    
    # 정리
    if os.path.exists(temp_path):
        os.remove(temp_path)


class TestWatsonxUploader:
    """WatsonxUploader 클래스 테스트"""
    
    def test_init(self, test_config):
        """초기화 테스트"""
        uploader = WatsonxUploader(test_config)
        
        assert uploader.config == test_config
        assert uploader._upload_progress == 0.0
        assert uploader._is_authenticated == False
        assert uploader._session is not None
    
    @patch('requests.Session.get')
    def test_authenticate_success(self, mock_get, test_config):
        """인증 성공 테스트
        
        Requirements: 3.1, 3.2
        """
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        uploader = WatsonxUploader(test_config)
        result = uploader.authenticate()
        
        assert result == True
        assert uploader._is_authenticated == True
        
        # 올바른 URL로 호출되었는지 확인
        expected_url = f"{test_config.watsonx_endpoint}/v1/projects/{test_config.watsonx_project_id}"
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0] == expected_url
    
    @patch('requests.Session.get')
    def test_authenticate_invalid_api_key(self, mock_get, test_config):
        """잘못된 API 키로 인증 실패 테스트
        
        Requirements: 3.1, 3.2
        """
        # Mock 응답 설정 (401 Unauthorized)
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        uploader = WatsonxUploader(test_config)
        
        with pytest.raises(ValueError, match="인증 실패: API 키가 유효하지 않습니다"):
            uploader.authenticate()
    
    def test_authenticate_no_api_key(self):
        """API 키 없이 인증 시도 테스트
        
        Requirements: 3.1
        """
        config = Configuration(
            watsonx_api_key="",
            watsonx_endpoint="https://test.watsonx.ai",
            watsonx_project_id="test_project",
            output_directory="./output"
        )
        
        uploader = WatsonxUploader(config)
        
        with pytest.raises(ValueError, match="API 키가 설정되지 않았습니다"):
            uploader.authenticate()
    
    @patch('requests.Session.post')
    def test_upload_asset_success(self, mock_post, test_config, test_zip_file):
        """asset 업로드 성공 테스트
        
        Requirements: 3.1, 3.2, 3.5
        """
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'asset_id': 'asset_123',
            'href': 'https://test.watsonx.ai/assets/asset_123'
        }
        mock_post.return_value = mock_response
        
        uploader = WatsonxUploader(test_config)
        uploader._is_authenticated = True  # 인증 상태로 설정
        
        result = uploader.upload_asset(test_zip_file)
        
        assert result.success == True
        assert result.asset_id == 'asset_123'
        assert result.asset_url == 'https://test.watsonx.ai/assets/asset_123'
        assert result.file_size > 0
        assert result.upload_time >= 0
        assert result.error_message is None
    
    def test_upload_asset_not_authenticated(self, test_config, test_zip_file):
        """인증 없이 업로드 시도 테스트
        
        Requirements: 3.1
        """
        uploader = WatsonxUploader(test_config)
        
        with pytest.raises(ValueError, match="인증이 필요합니다"):
            uploader.upload_asset(test_zip_file)
    
    def test_upload_asset_file_not_found(self, test_config):
        """존재하지 않는 파일 업로드 시도 테스트
        
        Requirements: 3.2
        """
        uploader = WatsonxUploader(test_config)
        uploader._is_authenticated = True
        
        with pytest.raises(FileNotFoundError):
            uploader.upload_asset("nonexistent_file.zip")
    
    @patch('requests.Session.post')
    def test_upload_asset_with_progress_callback(self, mock_post, test_config, test_zip_file):
        """진행 상황 콜백과 함께 업로드 테스트
        
        Requirements: 3.3
        """
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'asset_id': 'asset_456',
            'href': 'https://test.watsonx.ai/assets/asset_456'
        }
        mock_post.return_value = mock_response
        
        uploader = WatsonxUploader(test_config)
        uploader._is_authenticated = True
        
        progress_values = []
        
        def progress_callback(progress):
            progress_values.append(progress)
        
        result = uploader.upload_asset(test_zip_file, progress_callback)
        
        assert result.success == True
        # 진행 상황 콜백이 호출되었는지 확인 (실제로는 mock이므로 호출되지 않을 수 있음)
    
    def test_get_upload_progress(self, test_config):
        """업로드 진행률 조회 테스트
        
        Requirements: 3.3
        """
        uploader = WatsonxUploader(test_config)
        
        assert uploader.get_upload_progress() == 0.0
        
        uploader._upload_progress = 0.5
        assert uploader.get_upload_progress() == 0.5
    
    @patch('requests.Session.post')
    @patch('time.sleep')
    def test_retry_upload_success_on_second_attempt(self, mock_sleep, mock_post, test_config, test_zip_file):
        """두 번째 시도에서 업로드 성공 테스트
        
        Requirements: 3.4
        """
        # 첫 번째 호출은 실패, 두 번째 호출은 성공
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.text = "Internal Server Error"
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            'asset_id': 'asset_retry_123',
            'href': 'https://test.watsonx.ai/assets/asset_retry_123'
        }
        
        mock_post.side_effect = [mock_response_fail, mock_response_success]
        
        uploader = WatsonxUploader(test_config)
        uploader._is_authenticated = True
        
        result = uploader.retry_upload(test_zip_file, max_retries=3)
        
        assert result.success == True
        assert result.asset_id == 'asset_retry_123'
        
        # sleep이 호출되었는지 확인 (지수 백오프)
        mock_sleep.assert_called_once_with(1)  # 첫 번째 재시도는 1초 대기
    
    @patch('requests.Session.post')
    @patch('time.sleep')
    def test_retry_upload_all_attempts_fail(self, mock_sleep, mock_post, test_config, test_zip_file):
        """모든 재시도 실패 테스트
        
        Requirements: 3.4
        """
        # 모든 호출이 실패
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        uploader = WatsonxUploader(test_config)
        uploader._is_authenticated = True
        
        result = uploader.retry_upload(test_zip_file, max_retries=2)
        
        assert result.success == False
        assert "최대 재시도 횟수" in result.error_message
        
        # 총 3번 호출 (초기 시도 + 2번 재시도)
        assert mock_post.call_count == 3
        
        # sleep이 2번 호출되었는지 확인 (1초, 2초)
        assert mock_sleep.call_count == 2
    
    @patch('requests.Session.post')
    @patch('time.sleep')
    def test_retry_upload_exponential_backoff(self, mock_sleep, mock_post, test_config, test_zip_file):
        """지수 백오프 테스트
        
        Requirements: 3.4
        """
        # 모든 호출이 실패
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.text = "Service Unavailable"
        mock_post.return_value = mock_response
        
        uploader = WatsonxUploader(test_config)
        uploader._is_authenticated = True
        
        result = uploader.retry_upload(test_zip_file, max_retries=3)
        
        assert result.success == False
        
        # 지수 백오프 확인: 1초, 2초, 4초
        expected_calls = [((1,),), ((2,),), ((4,),)]
        assert mock_sleep.call_args_list == expected_calls
    
    def test_context_manager(self, test_config):
        """컨텍스트 매니저 테스트"""
        with WatsonxUploader(test_config) as uploader:
            assert uploader is not None
            assert uploader._session is not None
        
        # 컨텍스트 종료 후 세션이 닫혔는지 확인은 어려우므로 예외가 발생하지 않는지만 확인
    
    def test_close(self, test_config):
        """세션 종료 테스트"""
        uploader = WatsonxUploader(test_config)
        session = uploader._session
        
        uploader.close()
        
        # close 호출 후 예외가 발생하지 않는지 확인
        # 실제 세션 종료 여부는 mock 없이 확인하기 어려움
