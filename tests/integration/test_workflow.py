"""
전체 워크플로우 통합 테스트

Requirements: 10.2
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from main import PipelineWorkflow
from src.models.data_models import Configuration, UploadResult, ZIPArchiveInfo
from datetime import datetime


class TestWorkflowIntegration:
    """전체 워크플로우 통합 테스트"""
    
    def test_workflow_initialization(self):
        """워크플로우 초기화 테스트"""
        workflow = PipelineWorkflow()
        
        assert workflow.config_manager is not None
        assert workflow.file_selector is not None
        assert workflow.sample_executor is not None
    
    def test_load_configuration_with_env(self, monkeypatch, tmp_path):
        """환경 변수를 통한 설정 로드 테스트"""
        # 환경 변수 설정
        monkeypatch.setenv('WATSONX_API_KEY', 'test_api_key')
        monkeypatch.setenv('WATSONX_ENDPOINT', 'https://test.watsonx.ai')
        monkeypatch.setenv('WATSONX_PROJECT_ID', 'test_project_id')
        monkeypatch.setenv('OUTPUT_DIRECTORY', str(tmp_path))
        
        workflow = PipelineWorkflow()
        workflow._load_configuration()
        
        assert workflow.config is not None
        assert workflow.config.watsonx_api_key == 'test_api_key'
        assert workflow.config.watsonx_endpoint == 'https://test.watsonx.ai'
        assert workflow.config.watsonx_project_id == 'test_project_id'
        assert workflow.zip_builder is not None
    
    def test_file_selection_sample_mode(self, tmp_path):
        """샘플 모드 파일 선택 테스트"""
        # 임시 샘플 디렉토리 생성
        samples_dir = tmp_path / "samples"
        samples_dir.mkdir()
        
        # 샘플 파일 생성
        sample_files = ['ingest.py', 'parse.py', 'extract.py']
        for filename in sample_files:
            sample_file = samples_dir / filename
            sample_file.write_text('print("Sample file")')
        
        workflow = PipelineWorkflow()
        
        # 샘플 모드 선택
        with patch.object(workflow.sample_executor, 'execute_samples'):
            with patch.object(workflow.sample_executor, 'print_summary'):
                selected = workflow.file_selector.select_sample_mode(str(samples_dir))
        
        assert len(selected) == 3
    
    def test_zip_creation_workflow(self, tmp_path, monkeypatch):
        """ZIP 생성 워크플로우 테스트"""
        # 환경 변수 설정
        monkeypatch.setenv('WATSONX_API_KEY', 'test_key')
        monkeypatch.setenv('WATSONX_ENDPOINT', 'https://test.watsonx.ai')
        monkeypatch.setenv('WATSONX_PROJECT_ID', 'test_project')
        monkeypatch.setenv('OUTPUT_DIRECTORY', str(tmp_path))
        
        # 테스트 파일 생성
        test_file = tmp_path / "test.py"
        test_file.write_text('print("test")')
        
        workflow = PipelineWorkflow()
        workflow._load_configuration()
        
        # 파일 선택
        workflow.file_selector.select_file(str(test_file))
        file_selections = workflow.file_selector.get_file_selections(str(tmp_path))
        
        # ZIP 생성
        archive_info = workflow._create_zip_archive(file_selections)
        
        assert archive_info is not None
        assert Path(archive_info.archive_path).exists()
        assert archive_info.file_count == 1
    
    def test_upload_workflow_with_mock(self, tmp_path, monkeypatch):
        """업로드 워크플로우 테스트 (mock 사용)"""
        # 환경 변수 설정
        monkeypatch.setenv('WATSONX_API_KEY', 'test_key')
        monkeypatch.setenv('WATSONX_ENDPOINT', 'https://test.watsonx.ai')
        monkeypatch.setenv('WATSONX_PROJECT_ID', 'test_project')
        monkeypatch.setenv('OUTPUT_DIRECTORY', str(tmp_path))
        
        # 테스트 ZIP 파일 생성
        test_zip = tmp_path / "test.zip"
        test_zip.write_bytes(b'test zip content')
        
        workflow = PipelineWorkflow()
        workflow._load_configuration()
        
        # WatsonxUploader mock
        mock_uploader = Mock()
        mock_uploader.authenticate.return_value = True
        mock_uploader.retry_upload.return_value = UploadResult(
            asset_id='test_asset_id',
            asset_url='https://test.watsonx.ai/assets/test_asset_id',
            upload_time=1.5,
            file_size=100,
            success=True
        )
        
        with patch('main.WatsonxUploader', return_value=mock_uploader):
            result = workflow._upload_to_watsonx(str(test_zip))
        
        assert result is not None
        assert result.success is True
        assert result.asset_id == 'test_asset_id'
    
    def test_github_upload_workflow_with_mock(self, tmp_path, monkeypatch):
        """GitHub 업로드 워크플로우 테스트 (mock 사용)"""
        # 환경 변수 설정 (GitHub 업로드 활성화)
        monkeypatch.setenv('WATSONX_API_KEY', 'test_key')
        monkeypatch.setenv('WATSONX_ENDPOINT', 'https://test.watsonx.ai')
        monkeypatch.setenv('WATSONX_PROJECT_ID', 'test_project')
        monkeypatch.setenv('OUTPUT_DIRECTORY', str(tmp_path))
        monkeypatch.setenv('GITHUB_UPLOAD_ENABLED', 'true')
        monkeypatch.setenv('GITHUB_REPO_URL', 'https://github.com/test/repo.git')
        monkeypatch.setenv('GITHUB_TOKEN', 'test_token')
        
        # 테스트 ZIP 파일 생성
        test_zip = tmp_path / "test.zip"
        test_zip.write_bytes(b'test zip content')
        
        workflow = PipelineWorkflow()
        workflow._load_configuration()
        
        # GitHub 설정 확인
        assert workflow.config.github_upload_enabled is True
        assert workflow.config.github_repo_url == 'https://github.com/test/repo.git'
        
        # GitHubUploader mock
        mock_github_uploader = Mock()
        mock_github_uploader.retry_upload.return_value = UploadResult(
            asset_id='github_sha_123',
            asset_url='https://github.com/test/repo/blob/main/test.zip',
            upload_time=2.0,
            file_size=100,
            success=True,
            error_message='https://github.com/test/repo/raw/main/test.zip'  # Raw URL
        )
        
        with patch('main.GitHubUploader', return_value=mock_github_uploader):
            result = workflow._upload_to_github(str(test_zip))
        
        assert result is not None
        assert result.success is True
        assert result.asset_id == 'github_sha_123'
        assert 'github.com/test/repo/blob/main' in result.asset_url
        assert 'github.com/test/repo/raw/main' in result.error_message
    
    def test_github_upload_disabled(self, tmp_path, monkeypatch):
        """GitHub 업로드 비활성화 테스트"""
        # 환경 변수 설정 (GitHub 업로드 비활성화)
        monkeypatch.setenv('WATSONX_API_KEY', 'test_key')
        monkeypatch.setenv('WATSONX_ENDPOINT', 'https://test.watsonx.ai')
        monkeypatch.setenv('WATSONX_PROJECT_ID', 'test_project')
        monkeypatch.setenv('OUTPUT_DIRECTORY', str(tmp_path))
        monkeypatch.setenv('GITHUB_UPLOAD_ENABLED', 'false')
        
        workflow = PipelineWorkflow()
        workflow._load_configuration()
        
        # GitHub 업로드 시도
        result = workflow._upload_to_github("test.zip")
        
        assert result is None
    
    def test_github_upload_no_repo_url(self, tmp_path, monkeypatch):
        """GitHub 저장소 URL 없는 경우 테스트"""
        # 환경 변수 설정 (저장소 URL 없음)
        monkeypatch.setenv('WATSONX_API_KEY', 'test_key')
        monkeypatch.setenv('WATSONX_ENDPOINT', 'https://test.watsonx.ai')
        monkeypatch.setenv('WATSONX_PROJECT_ID', 'test_project')
        monkeypatch.setenv('OUTPUT_DIRECTORY', str(tmp_path))
        monkeypatch.setenv('GITHUB_UPLOAD_ENABLED', 'true')
        # GITHUB_REPO_URL 설정하지 않음
        
        workflow = PipelineWorkflow()
        workflow._load_configuration()
        
        # GitHub 업로드 시도
        result = workflow._upload_to_github("test.zip")
        
        assert result is None
    
    def test_complete_workflow_pipeline(self, tmp_path, monkeypatch):
        """완전한 파이프라인 워크플로우 테스트
        
        파일 선택 → ZIP 생성 → 업로드 전체 플로우
        Requirements: 1.1, 2.1, 3.1
        """
        # 환경 변수 설정
        monkeypatch.setenv('WATSONX_API_KEY', 'test_key')
        monkeypatch.setenv('WATSONX_ENDPOINT', 'https://test.watsonx.ai')
        monkeypatch.setenv('WATSONX_PROJECT_ID', 'test_project')
        monkeypatch.setenv('OUTPUT_DIRECTORY', str(tmp_path))
        
        # 테스트 파일 생성
        test_file = tmp_path / "test.py"
        test_file.write_text('print("test")')
        
        workflow = PipelineWorkflow()
        
        # 1. 설정 로드
        workflow._load_configuration()
        assert workflow.config is not None
        
        # 2. 파일 선택
        workflow.file_selector.select_file(str(test_file))
        file_selections = workflow.file_selector.get_file_selections(str(tmp_path))
        assert len(file_selections) == 1
        
        # 3. ZIP 생성
        archive_info = workflow._create_zip_archive(file_selections)
        assert archive_info is not None
        assert Path(archive_info.archive_path).exists()
        
        # 4. 업로드 (mock)
        mock_uploader = Mock()
        mock_uploader.authenticate.return_value = True
        mock_uploader.retry_upload.return_value = UploadResult(
            asset_id='test_asset_id',
            asset_url='https://test.watsonx.ai/assets/test_asset_id',
            upload_time=1.5,
            file_size=archive_info.total_size,
            success=True
        )
        mock_uploader.close.return_value = None
        
        with patch('main.WatsonxUploader', return_value=mock_uploader):
            upload_result = workflow._upload_to_watsonx(archive_info.archive_path)
        
        assert upload_result is not None
        assert upload_result.success is True
        
        # 5. 완료 메시지 (출력만 확인)
        workflow._display_completion(upload_result)
    
    def test_workflow_error_handling(self, monkeypatch):
        """워크플로우 에러 처리 테스트"""
        workflow = PipelineWorkflow()
        
        # 설정 파일이 없고 환경 변수도 없는 경우
        with pytest.raises(SystemExit):
            workflow._load_configuration()
    
    def test_workflow_file_validation(self, tmp_path, monkeypatch):
        """파일 선택 검증 테스트"""
        monkeypatch.setenv('WATSONX_API_KEY', 'test_key')
        monkeypatch.setenv('WATSONX_ENDPOINT', 'https://test.watsonx.ai')
        monkeypatch.setenv('WATSONX_PROJECT_ID', 'test_project')
        monkeypatch.setenv('OUTPUT_DIRECTORY', str(tmp_path))
        
        workflow = PipelineWorkflow()
        workflow._load_configuration()
        
        # 파일을 선택하지 않은 경우
        assert not workflow.file_selector.validate_selection()
        
        # 파일 선택 후
        test_file = tmp_path / "test.py"
        test_file.write_text('print("test")')
        workflow.file_selector.select_file(str(test_file))
        
        assert workflow.file_selector.validate_selection()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
