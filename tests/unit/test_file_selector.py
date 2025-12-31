"""Unit tests for FileSelector class."""

import os
import tempfile
import pytest
from pathlib import Path
from src.core.file_selector import FileSelector
from src.models.data_models import FileSelection


class TestFileSelector:
    """FileSelector 클래스 단위 테스트."""
    
    @pytest.fixture
    def temp_dir(self):
        """임시 디렉토리 생성."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_files(self, temp_dir):
        """테스트용 샘플 Python 파일 생성."""
        files = []
        
        # 루트 레벨 파일
        file1 = Path(temp_dir) / "test1.py"
        file1.write_text("# Test file 1")
        files.append(str(file1))
        
        # 서브디렉토리 파일
        subdir = Path(temp_dir) / "subdir"
        subdir.mkdir()
        file2 = subdir / "test2.py"
        file2.write_text("# Test file 2")
        files.append(str(file2))
        
        # 비Python 파일 (필터링되어야 함)
        txt_file = Path(temp_dir) / "readme.txt"
        txt_file.write_text("Not a Python file")
        
        return files
    
    @pytest.fixture
    def file_selector(self):
        """FileSelector 인스턴스 생성."""
        return FileSelector()
    
    def test_scan_directory_finds_python_files(self, temp_dir, sample_files, file_selector):
        """디렉토리 스캔이 Python 파일을 찾는지 테스트."""
        found_files = file_selector.scan_directory(temp_dir)
        
        assert len(found_files) == 2
        assert all(f.endswith('.py') for f in found_files)
    
    def test_scan_directory_invalid_path(self, file_selector):
        """존재하지 않는 경로 스캔 시 에러 발생 테스트."""
        with pytest.raises(ValueError, match="경로가 존재하지 않습니다"):
            file_selector.scan_directory("/nonexistent/path")
    
    def test_scan_directory_not_a_directory(self, temp_dir, file_selector):
        """파일 경로를 디렉토리로 스캔 시 에러 발생 테스트."""
        file_path = Path(temp_dir) / "test.py"
        file_path.write_text("# Test")
        
        with pytest.raises(ValueError, match="디렉토리가 아닙니다"):
            file_selector.scan_directory(str(file_path))
    
    def test_select_file_adds_to_selection(self, sample_files, file_selector):
        """파일 선택이 선택 목록에 추가되는지 테스트."""
        file_selector.select_file(sample_files[0])
        
        selected = file_selector.get_selected_files()
        assert len(selected) == 1
        assert sample_files[0] in selected[0]
    
    def test_select_file_invalid_file(self, file_selector):
        """존재하지 않는 파일 선택 시 에러 발생 테스트."""
        with pytest.raises(ValueError, match="파일이 존재하지 않습니다"):
            file_selector.select_file("/nonexistent/file.py")
    
    def test_select_file_non_python(self, temp_dir, file_selector):
        """Python이 아닌 파일 선택 시 에러 발생 테스트."""
        txt_file = Path(temp_dir) / "test.txt"
        txt_file.write_text("Not Python")
        
        with pytest.raises(ValueError, match="Python 파일이 아닙니다"):
            file_selector.select_file(str(txt_file))
    
    def test_deselect_file_removes_from_selection(self, sample_files, file_selector):
        """파일 선택 해제가 목록에서 제거하는지 테스트."""
        file_selector.select_file(sample_files[0])
        file_selector.deselect_file(sample_files[0])
        
        selected = file_selector.get_selected_files()
        assert len(selected) == 0
    
    def test_select_multiple_files(self, sample_files, file_selector):
        """여러 파일 선택 테스트."""
        selected = file_selector.select_files(sample_files)
        
        assert len(selected) == 2
        assert len(file_selector.get_selected_files()) == 2
    
    def test_clear_selection(self, sample_files, file_selector):
        """선택 초기화 테스트."""
        file_selector.select_files(sample_files)
        file_selector.clear_selection()
        
        assert len(file_selector.get_selected_files()) == 0
    
    def test_validate_selection_with_files(self, sample_files, file_selector):
        """파일이 선택된 경우 검증 성공 테스트 (Requirements 1.5)."""
        file_selector.select_file(sample_files[0])
        
        assert file_selector.validate_selection() is True
    
    def test_validate_selection_without_files(self, file_selector):
        """파일이 선택되지 않은 경우 검증 실패 테스트 (Requirements 1.5)."""
        assert file_selector.validate_selection() is False
    
    def test_validate_selection_with_explicit_list(self, sample_files):
        """명시적 파일 목록 검증 테스트."""
        file_selector = FileSelector()
        
        # 빈 목록
        assert file_selector.validate_selection([]) is False
        
        # 파일이 있는 목록
        assert file_selector.validate_selection(sample_files) is True
    
    def test_get_file_selections(self, temp_dir, sample_files, file_selector):
        """FileSelection 객체 목록 반환 테스트."""
        file_selector.select_files(sample_files)
        
        selections = file_selector.get_file_selections(temp_dir)
        
        assert len(selections) == 2
        assert all(isinstance(s, FileSelection) for s in selections)
        assert all(s.selected is True for s in selections)
        assert all(s.size > 0 for s in selections)
    
    def test_select_sample_mode_selects_all_samples(self, temp_dir, file_selector):
        """샘플 모드가 모든 샘플 파일을 자동 선택하는지 테스트 (Requirements 5.3)."""
        # 샘플 디렉토리 생성
        samples_dir = Path(temp_dir) / "samples"
        samples_dir.mkdir()
        
        # 7개 샘플 파일 생성
        sample_names = ["ingest.py", "parse.py", "extract.py", "transform.py", 
                       "generate.py", "validate.py", "report.py"]
        
        for name in sample_names:
            sample_file = samples_dir / name
            sample_file.write_text(f"# Sample file: {name}")
        
        # 샘플 모드 활성화
        selected = file_selector.select_sample_mode(str(samples_dir))
        
        # 모든 샘플 파일이 선택되었는지 확인
        assert len(selected) == 7
        assert len(file_selector.get_selected_files()) == 7
        
        # 파일명 확인
        selected_names = [Path(f).name for f in selected]
        for name in sample_names:
            assert name in selected_names
    
    def test_select_sample_mode_clears_previous_selection(self, temp_dir, sample_files, file_selector):
        """샘플 모드가 이전 선택을 초기화하는지 테스트."""
        # 먼저 다른 파일 선택
        file_selector.select_file(sample_files[0])
        assert len(file_selector.get_selected_files()) == 1
        
        # 샘플 디렉토리 생성
        samples_dir = Path(temp_dir) / "samples"
        samples_dir.mkdir()
        
        sample_file = samples_dir / "test_sample.py"
        sample_file.write_text("# Sample")
        
        # 샘플 모드 활성화
        file_selector.select_sample_mode(str(samples_dir))
        
        # 이전 선택이 초기화되고 샘플만 선택되었는지 확인
        selected = file_selector.get_selected_files()
        assert len(selected) == 1
        assert "test_sample.py" in selected[0]
        assert sample_files[0] not in selected[0]
    
    def test_select_sample_mode_invalid_directory(self, file_selector):
        """존재하지 않는 샘플 디렉토리 선택 시 에러 발생 테스트."""
        with pytest.raises(ValueError, match="샘플 디렉토리가 존재하지 않습니다"):
            file_selector.select_sample_mode("/nonexistent/samples")
    
    def test_select_sample_mode_empty_directory(self, temp_dir, file_selector):
        """샘플 파일이 없는 디렉토리 선택 시 에러 발생 테스트."""
        empty_dir = Path(temp_dir) / "empty_samples"
        empty_dir.mkdir()
        
        with pytest.raises(ValueError, match="샘플 디렉토리에 Python 파일이 없습니다"):
            file_selector.select_sample_mode(str(empty_dir))
    
    def test_select_sample_mode_with_default_path(self, file_selector):
        """기본 샘플 경로로 샘플 모드 테스트."""
        # 실제 samples 디렉토리가 있는 경우에만 테스트
        if Path("samples").exists():
            selected = file_selector.select_sample_mode()
            
            # 최소 7개 샘플 파일이 선택되어야 함 (Requirements 5.1)
            assert len(selected) >= 7
            
            # 필수 샘플 파일명 확인
            selected_names = [Path(f).name for f in selected]
            required_samples = ["ingest.py", "parse.py", "extract.py", "transform.py",
                              "generate.py", "validate.py", "report.py"]
            
            for sample in required_samples:
                assert sample in selected_names
