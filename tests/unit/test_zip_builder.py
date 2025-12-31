"""
ZIPBuilder 단위 테스트

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
"""

import os
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
import pytest

from src.core.zip_builder import ZIPBuilder
from src.models.data_models import FileSelection, ZIPArchiveInfo


class TestZIPBuilder:
    """ZIPBuilder 클래스 테스트"""
    
    @pytest.fixture
    def temp_dir(self):
        """임시 디렉토리 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_files(self, temp_dir):
        """테스트용 샘플 파일 생성"""
        files = []
        base_path = Path(temp_dir)
        
        # 샘플 파일 3개 생성
        for i in range(3):
            file_path = base_path / f"test_file_{i}.py"
            content = f"# Test file {i}\nprint('Hello from file {i}')\n"
            file_path.write_text(content)
            
            files.append(FileSelection(
                file_path=str(file_path),
                relative_path=f"test_file_{i}.py",
                size=len(content),
                selected=True
            ))
        
        return files
    
    @pytest.fixture
    def zip_builder(self, temp_dir):
        """ZIPBuilder 인스턴스 생성"""
        output_dir = os.path.join(temp_dir, "output")
        return ZIPBuilder(output_directory=output_dir)
    
    def test_create_archive_success(self, zip_builder, sample_files):
        """ZIP 아카이브 생성 성공 테스트 (Requirement 2.1)"""
        archive_info = zip_builder.create_archive(sample_files)
        
        assert isinstance(archive_info, ZIPArchiveInfo)
        assert os.path.exists(archive_info.archive_path)
        assert archive_info.file_count == 3
        assert archive_info.total_size > 0
    
    def test_directory_structure_preserved(self, zip_builder, temp_dir):
        """디렉토리 구조 보존 테스트 (Requirement 2.2)"""
        base_path = Path(temp_dir)
        
        # 중첩된 디렉토리 구조 생성
        subdir = base_path / "subdir"
        subdir.mkdir()
        
        file1 = base_path / "root_file.py"
        file2 = subdir / "sub_file.py"
        
        file1.write_text("# Root file")
        file2.write_text("# Sub file")
        
        files = [
            FileSelection(
                file_path=str(file1),
                relative_path="root_file.py",
                size=len("# Root file"),
                selected=True
            ),
            FileSelection(
                file_path=str(file2),
                relative_path="subdir/sub_file.py",
                size=len("# Sub file"),
                selected=True
            )
        ]
        
        archive_info = zip_builder.create_archive(files)
        
        # ZIP 내부 구조 확인
        with zipfile.ZipFile(archive_info.archive_path, 'r') as zipf:
            namelist = zipf.namelist()
            assert "root_file.py" in namelist
            assert "subdir/sub_file.py" in namelist
    
    def test_timestamped_filename(self, zip_builder, sample_files):
        """타임스탬프 파일명 생성 테스트 (Requirement 2.3)"""
        archive_info = zip_builder.create_archive(sample_files)
        
        filename = os.path.basename(archive_info.archive_path)
        
        # 파일명 형식 확인: pipeline_YYYYMMDD_HHMMSS.zip
        assert filename.startswith("pipeline_")
        assert filename.endswith(".zip")
        assert len(filename) == len("pipeline_20231225_123456.zip")
    
    def test_validate_archive_success(self, zip_builder, sample_files):
        """ZIP 검증 성공 테스트 (Requirement 2.4)"""
        archive_info = zip_builder.create_archive(sample_files)
        
        is_valid = zip_builder.validate_archive(archive_info.archive_path)
        assert is_valid is True
    
    def test_validate_archive_nonexistent(self, zip_builder):
        """존재하지 않는 ZIP 검증 테스트 (Requirement 2.4)"""
        is_valid = zip_builder.validate_archive("/nonexistent/path.zip")
        assert is_valid is False
    
    def test_get_archive_info(self, zip_builder, sample_files):
        """ZIP 정보 조회 테스트 (Requirement 2.5)"""
        archive_info = zip_builder.create_archive(sample_files)
        
        info = zip_builder.get_archive_info(archive_info.archive_path)
        
        assert "archive_path" in info
        assert "file_size" in info
        assert "file_count" in info
        assert "files" in info
        assert info["file_count"] == 3
    
    def test_display_archive_info(self, zip_builder, sample_files):
        """ZIP 정보 표시 테스트 (Requirement 2.5)"""
        archive_info = zip_builder.create_archive(sample_files)
        
        display_text = zip_builder.display_archive_info(archive_info)
        
        assert "ZIP 아카이브 생성 완료" in display_text
        assert "파일 경로:" in display_text
        assert "파일 개수:" in display_text
        assert "전체 크기:" in display_text
    
    def test_create_archive_empty_list(self, zip_builder):
        """빈 파일 목록으로 아카이브 생성 시 에러 (Requirement 2.4)"""
        with pytest.raises(ValueError, match="압축할 파일 목록이 비어있습니다"):
            zip_builder.create_archive([])
    
    def test_create_archive_nonexistent_file(self, zip_builder):
        """존재하지 않는 파일로 아카이브 생성 시 에러 (Requirement 2.4)"""
        files = [
            FileSelection(
                file_path="/nonexistent/file.py",
                relative_path="file.py",
                size=100,
                selected=True
            )
        ]
        
        with pytest.raises(IOError):
            zip_builder.create_archive(files)
    
    def test_handle_compression_error(self, zip_builder):
        """압축 에러 처리 테스트 (Requirement 2.4)"""
        error = FileNotFoundError("test.py")
        msg = zip_builder.handle_compression_error(error)
        
        assert "파일을 찾을 수 없습니다" in msg
    
    def test_checksum_calculation(self, zip_builder, sample_files):
        """체크섬 계산 테스트"""
        archive_info = zip_builder.create_archive(sample_files)
        
        # 체크섬이 생성되었는지 확인
        assert archive_info.checksum is not None
        assert len(archive_info.checksum) == 64  # SHA256 해시 길이
    
    def test_selected_files_only(self, zip_builder, temp_dir):
        """선택된 파일만 압축되는지 테스트"""
        base_path = Path(temp_dir)
        
        file1 = base_path / "selected.py"
        file2 = base_path / "not_selected.py"
        
        file1.write_text("# Selected")
        file2.write_text("# Not selected")
        
        files = [
            FileSelection(
                file_path=str(file1),
                relative_path="selected.py",
                size=len("# Selected"),
                selected=True
            ),
            FileSelection(
                file_path=str(file2),
                relative_path="not_selected.py",
                size=len("# Not selected"),
                selected=False  # 선택되지 않음
            )
        ]
        
        archive_info = zip_builder.create_archive(files)
        
        # ZIP 내부에 선택된 파일만 있는지 확인
        with zipfile.ZipFile(archive_info.archive_path, 'r') as zipf:
            namelist = zipf.namelist()
            assert "selected.py" in namelist
            assert "not_selected.py" not in namelist
            assert len(namelist) == 1
