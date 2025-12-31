"""
GitHub 업로더 단위 테스트

이 모듈은 GitHubUploader 클래스의 단위 테스트를 제공합니다.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.core.github_uploader import GitHubUploader
from src.models.data_models import UploadResult


class TestGitHubUploader:
    """GitHubUploader 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.repo_url = "https://github.com/test-user/test-repo.git"
        self.github_token = "test_token_123"
        self.uploader = GitHubUploader(self.repo_url, self.github_token)
    
    def test_init_valid_repo_url(self):
        """유효한 저장소 URL로 초기화 테스트"""
        assert self.uploader.owner == "test-user"
        assert self.uploader.repo == "test-repo"
        assert self.uploader.github_token == self.github_token
        assert self.uploader.repo_url == "https://github.com/test-user/test-repo"
    
    def test_init_invalid_repo_url(self):
        """잘못된 저장소 URL로 초기화 테스트"""
        with pytest.raises(ValueError, match="잘못된 GitHub URL 형식"):
            GitHubUploader("invalid-url")
    
    def test_init_without_git_extension(self):
        """.git 확장자 없는 URL 테스트"""
        uploader = GitHubUploader("https://github.com/user/repo")
        assert uploader.owner == "user"
        assert uploader.repo == "repo"
    
    @patch('requests.get')
    @patch('requests.put')
    def test_upload_file_success_new_file(self, mock_put, mock_get):
        """새 파일 업로드 성공 테스트"""
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            # Mock 설정
            mock_get.return_value.status_code = 404  # 파일이 존재하지 않음
            mock_put.return_value.status_code = 201
            mock_put.return_value.json.return_value = {
                'content': {'sha': 'test_sha_123'}
            }
            
            # 업로드 실행
            result = self.uploader.upload_file(temp_file)
            
            # 결과 검증
            assert result.success is True
            assert result.asset_id == 'test_sha_123'
            assert 'github.com/test-user/test-repo/blob/main' in result.asset_url
            assert 'github.com/test-user/test-repo/raw/main' in result.error_message
            
        finally:
            os.unlink(temp_file)
    
    @patch('requests.get')
    @patch('requests.put')
    def test_upload_file_success_update_existing(self, mock_put, mock_get):
        """기존 파일 업데이트 성공 테스트"""
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as f:
            f.write("updated content")
            temp_file = f.name
        
        try:
            # Mock 설정 - 기존 파일 존재
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                'sha': 'existing_sha_456'
            }
            mock_put.return_value.status_code = 200
            mock_put.return_value.json.return_value = {
                'content': {'sha': 'updated_sha_789'}
            }
            
            # 업로드 실행
            result = self.uploader.upload_file(temp_file)
            
            # 결과 검증
            assert result.success is True
            assert result.asset_id == 'updated_sha_789'
            
            # PUT 요청에 기존 SHA가 포함되었는지 확인
            put_call_args = mock_put.call_args
            assert put_call_args[1]['json']['sha'] == 'existing_sha_456'
            
        finally:
            os.unlink(temp_file)
    
    def test_upload_file_not_found(self):
        """존재하지 않는 파일 업로드 테스트"""
        result = self.uploader.upload_file("nonexistent_file.zip")
        
        assert result.success is False
        assert "파일을 찾을 수 없습니다" in result.error_message
    
    @patch('requests.get')
    @patch('requests.put')
    def test_upload_file_api_error(self, mock_put, mock_get):
        """GitHub API 오류 테스트"""
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            # Mock 설정
            mock_get.return_value.status_code = 404
            mock_put.return_value.status_code = 403  # Forbidden
            mock_put.return_value.json.return_value = {
                'message': 'Forbidden'
            }
            
            # 업로드 실행
            result = self.uploader.upload_file(temp_file)
            
            # 결과 검증
            assert result.success is False
            assert "GitHub API 오류: HTTP 403" in result.error_message
            assert "Forbidden" in result.error_message
            
        finally:
            os.unlink(temp_file)
    
    @patch('src.core.github_uploader.GitHubUploader.upload_file')
    def test_retry_upload_success_first_try(self, mock_upload):
        """첫 번째 시도에서 성공하는 재시도 테스트"""
        # Mock 설정
        success_result = UploadResult(
            asset_id='test_id',
            asset_url='test_url',
            upload_time=1.0,
            file_size=100,
            success=True
        )
        mock_upload.return_value = success_result
        
        # 재시도 업로드 실행
        result = self.uploader.retry_upload("test_file.zip", max_retries=3)
        
        # 결과 검증
        assert result.success is True
        assert result.asset_id == 'test_id'
        assert mock_upload.call_count == 1
    
    @patch('src.core.github_uploader.GitHubUploader.upload_file')
    @patch('time.sleep')
    def test_retry_upload_success_after_retries(self, mock_sleep, mock_upload):
        """재시도 후 성공하는 테스트"""
        # Mock 설정 - 처음 두 번은 실패, 세 번째는 성공
        fail_result = UploadResult(
            asset_id='',
            asset_url='',
            upload_time=0.0,
            file_size=0,
            success=False,
            error_message="Network error"
        )
        success_result = UploadResult(
            asset_id='test_id',
            asset_url='test_url',
            upload_time=1.0,
            file_size=100,
            success=True
        )
        mock_upload.side_effect = [fail_result, fail_result, success_result]
        
        # 재시도 업로드 실행
        result = self.uploader.retry_upload("test_file.zip", max_retries=3)
        
        # 결과 검증
        assert result.success is True
        assert result.asset_id == 'test_id'
        assert mock_upload.call_count == 3
        assert mock_sleep.call_count == 2  # 두 번의 재시도 대기
    
    @patch('src.core.github_uploader.GitHubUploader.upload_file')
    @patch('time.sleep')
    def test_retry_upload_max_retries_exceeded(self, mock_sleep, mock_upload):
        """최대 재시도 횟수 초과 테스트"""
        # Mock 설정 - 모든 시도 실패
        fail_result = UploadResult(
            asset_id='',
            asset_url='',
            upload_time=0.0,
            file_size=0,
            success=False,
            error_message="Persistent error"
        )
        mock_upload.return_value = fail_result
        
        # 재시도 업로드 실행
        result = self.uploader.retry_upload("test_file.zip", max_retries=2)
        
        # 결과 검증
        assert result.success is False
        assert "최대 재시도 횟수(2)를 초과했습니다" in result.error_message
        assert mock_upload.call_count == 3  # 초기 시도 + 2번 재시도
        assert mock_sleep.call_count == 2
    
    def test_get_upload_progress_initial(self):
        """초기 업로드 진행률 테스트"""
        progress = self.uploader.get_upload_progress()
        assert progress == 0.0
    
    @patch('requests.get')
    @patch('requests.put')
    def test_upload_with_progress_callback(self, mock_put, mock_get):
        """진행 상황 콜백 테스트"""
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            # Mock 설정
            mock_get.return_value.status_code = 404
            mock_put.return_value.status_code = 201
            mock_put.return_value.json.return_value = {
                'content': {'sha': 'test_sha'}
            }
            
            # 진행 상황 콜백 Mock
            progress_callback = Mock()
            
            # 업로드 실행
            result = self.uploader.upload_file(temp_file, progress_callback=progress_callback)
            
            # 결과 검증
            assert result.success is True
            assert progress_callback.call_count > 0
            
            # 진행률이 0.0에서 1.0 사이인지 확인
            for call in progress_callback.call_args_list:
                progress_value = call[0][0]
                assert 0.0 <= progress_value <= 1.0
            
        finally:
            os.unlink(temp_file)
    
    def test_upload_with_custom_target_path(self):
        """사용자 지정 대상 경로 테스트"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            with patch('requests.get') as mock_get, \
                 patch('requests.put') as mock_put:
                
                mock_get.return_value.status_code = 404
                mock_put.return_value.status_code = 201
                mock_put.return_value.json.return_value = {
                    'content': {'sha': 'test_sha'}
                }
                
                # 사용자 지정 경로로 업로드
                custom_path = "custom/path/my_file.zip"
                result = self.uploader.upload_file(temp_file, target_path=custom_path)
                
                # PUT 요청 URL에 사용자 지정 경로가 포함되었는지 확인
                put_call_args = mock_put.call_args
                assert custom_path in put_call_args[0][0]  # URL에 포함
                
        finally:
            os.unlink(temp_file)
    
    def test_upload_with_custom_commit_message(self):
        """사용자 지정 커밋 메시지 테스트"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            with patch('requests.get') as mock_get, \
                 patch('requests.put') as mock_put:
                
                mock_get.return_value.status_code = 404
                mock_put.return_value.status_code = 201
                mock_put.return_value.json.return_value = {
                    'content': {'sha': 'test_sha'}
                }
                
                # 사용자 지정 커밋 메시지로 업로드
                custom_message = "Custom commit message for testing"
                result = self.uploader.upload_file(
                    temp_file, 
                    commit_message=custom_message
                )
                
                # PUT 요청 데이터에 사용자 지정 메시지가 포함되었는지 확인
                put_call_args = mock_put.call_args
                assert put_call_args[1]['json']['message'] == custom_message
                
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__])