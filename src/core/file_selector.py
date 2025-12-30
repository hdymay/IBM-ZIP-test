"""File selector module for selecting Python source files."""

import os
from pathlib import Path
from typing import List, Set
from src.models.data_models import FileSelection


class FileSelector:
    """
    파일 선택기 클래스.
    
    사용자가 처리할 Python 파일을 선택하는 기능을 제공합니다.
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
    """
    
    def __init__(self):
        """FileSelector 초기화."""
        self._selected_files: Set[str] = set()
    
    def scan_directory(self, path: str) -> List[str]:
        """
        디렉토리에서 Python 파일을 스캔합니다.
        
        Args:
            path: 스캔할 디렉토리 경로
            
        Returns:
            발견된 Python 파일 경로 목록
            
        Raises:
            ValueError: 경로가 존재하지 않거나 디렉토리가 아닌 경우
        """
        directory = Path(path)
        
        if not directory.exists():
            raise ValueError(f"경로가 존재하지 않습니다: {path}")
        
        if not directory.is_dir():
            raise ValueError(f"디렉토리가 아닙니다: {path}")
        
        python_files = []
        
        # 디렉토리를 재귀적으로 탐색하여 .py 파일 찾기
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
        
        return sorted(python_files)
    
    def select_file(self, file_path: str) -> None:
        """
        파일을 선택 목록에 추가합니다.
        
        Args:
            file_path: 선택할 파일 경로
            
        Raises:
            ValueError: 파일이 존재하지 않거나 Python 파일이 아닌 경우
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ValueError(f"파일이 존재하지 않습니다: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"파일이 아닙니다: {file_path}")
        
        if not file_path.endswith('.py'):
            raise ValueError(f"Python 파일이 아닙니다: {file_path}")
        
        self._selected_files.add(str(path.absolute()))
    
    def deselect_file(self, file_path: str) -> None:
        """
        파일을 선택 목록에서 제거합니다.
        
        Args:
            file_path: 제거할 파일 경로
        """
        abs_path = str(Path(file_path).absolute())
        self._selected_files.discard(abs_path)
    
    def get_selected_files(self) -> List[str]:
        """
        현재 선택된 파일 목록을 반환합니다.
        
        Returns:
            선택된 파일 경로 목록 (정렬됨)
        """
        return sorted(list(self._selected_files))
    
    def clear_selection(self) -> None:
        """모든 선택을 초기화합니다."""
        self._selected_files.clear()
    
    def select_files(self, files: List[str]) -> List[str]:
        """
        여러 파일을 한 번에 선택합니다.
        
        Args:
            files: 선택할 파일 경로 목록
            
        Returns:
            성공적으로 선택된 파일 목록
            
        Raises:
            ValueError: 유효하지 않은 파일이 포함된 경우
        """
        selected = []
        
        for file_path in files:
            try:
                self.select_file(file_path)
                selected.append(file_path)
            except ValueError as e:
                # 유효하지 않은 파일은 건너뛰고 계속 진행
                continue
        
        return selected
    
    def validate_selection(self, files: List[str] = None) -> bool:
        """
        선택된 파일을 검증합니다.
        
        Args:
            files: 검증할 파일 목록 (None이면 현재 선택된 파일 사용)
            
        Returns:
            최소 1개 이상의 파일이 선택되었으면 True, 아니면 False
        """
        if files is None:
            files = self.get_selected_files()
        
        return len(files) >= 1
    
    def get_file_selections(self, base_path: str = None) -> List[FileSelection]:
        """
        선택된 파일들의 상세 정보를 FileSelection 객체 목록으로 반환합니다.
        
        Args:
            base_path: 상대 경로 계산을 위한 기준 경로
            
        Returns:
            FileSelection 객체 목록
        """
        selections = []
        
        for file_path in self.get_selected_files():
            path = Path(file_path)
            
            # 상대 경로 계산
            if base_path:
                try:
                    relative_path = str(path.relative_to(base_path))
                except ValueError:
                    # 상대 경로를 계산할 수 없으면 파일명만 사용
                    relative_path = path.name
            else:
                relative_path = path.name
            
            # 파일 크기 가져오기
            size = path.stat().st_size if path.exists() else 0
            
            selection = FileSelection(
                file_path=str(path.absolute()),
                relative_path=relative_path,
                size=size,
                selected=True
            )
            selections.append(selection)
        
        return selections
    
    def select_sample_mode(self, samples_directory: str = "samples") -> List[str]:
        """
        샘플 모드를 활성화하여 모든 샘플 파일을 자동으로 선택합니다.
        
        Requirements: 5.3
        
        Args:
            samples_directory: 샘플 파일이 있는 디렉토리 경로 (기본값: "samples")
            
        Returns:
            선택된 샘플 파일 경로 목록
            
        Raises:
            ValueError: 샘플 디렉토리가 존재하지 않거나 샘플 파일이 없는 경우
        """
        samples_path = Path(samples_directory)
        
        if not samples_path.exists():
            raise ValueError(f"샘플 디렉토리가 존재하지 않습니다: {samples_directory}")
        
        if not samples_path.is_dir():
            raise ValueError(f"샘플 경로가 디렉토리가 아닙니다: {samples_directory}")
        
        # 기존 선택 초기화
        self.clear_selection()
        
        # 샘플 디렉토리의 모든 Python 파일 스캔
        sample_files = self.scan_directory(samples_directory)
        
        if not sample_files:
            raise ValueError(f"샘플 디렉토리에 Python 파일이 없습니다: {samples_directory}")
        
        # 모든 샘플 파일 선택
        selected_files = self.select_files(sample_files)
        
        return selected_files
