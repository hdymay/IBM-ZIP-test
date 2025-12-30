"""
ZIP 빌더 모듈

이 모듈은 선택된 파일들을 ZIP 아카이브로 압축하는 기능을 제공합니다.
Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
"""

import os
import zipfile
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from src.models.data_models import ZIPArchiveInfo, FileSelection


class ZIPBuilder:
    """ZIP 아카이브 생성 및 관리 클래스
    
    선택된 파일들을 ZIP 아카이브로 압축하고, 디렉토리 구조를 보존하며,
    타임스탬프가 포함된 파일명을 생성합니다.
    
    Requirements: 2.1, 2.2, 2.3
    """
    
    def __init__(self, output_directory: str = "./output"):
        """ZIPBuilder 초기화
        
        Args:
            output_directory: ZIP 파일을 저장할 디렉토리 경로
        """
        self.output_directory = output_directory
        os.makedirs(output_directory, exist_ok=True)
    
    def create_archive(
        self, 
        files: List[FileSelection], 
        base_path: Optional[str] = None
    ) -> ZIPArchiveInfo:
        """ZIP 아카이브 생성
        
        선택된 파일들을 ZIP 아카이브로 압축합니다.
        타임스탬프가 포함된 파일명을 자동으로 생성합니다.
        
        Args:
            files: 압축할 파일 목록 (FileSelection 객체 리스트)
            base_path: 상대 경로 계산을 위한 기준 경로
        
        Returns:
            ZIPArchiveInfo: 생성된 ZIP 아카이브 정보
            
        Raises:
            ValueError: 파일 목록이 비어있는 경우
            FileNotFoundError: 파일을 찾을 수 없는 경우
            IOError: ZIP 생성 중 오류 발생 시
            
        Requirements: 2.1, 2.2, 2.3
        """
        if not files:
            raise ValueError("압축할 파일 목록이 비어있습니다.")
        
        # 타임스탬프 포함 파일명 생성 (Requirement 2.3)
        archive_filename = self._generate_timestamped_filename()
        archive_path = os.path.join(self.output_directory, archive_filename)
        
        created_at = datetime.now()
        total_size = 0
        file_count = 0
        
        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_selection in files:
                    if not file_selection.selected:
                        continue
                    
                    file_path = file_selection.file_path
                    
                    # 파일 존재 확인
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
                    
                    # 디렉토리 구조 보존 (Requirement 2.2)
                    arcname = file_selection.relative_path
                    
                    # 파일을 아카이브에 추가
                    self.add_file(zipf, file_path, arcname)
                    
                    total_size += file_selection.size
                    file_count += 1
            
            # 체크섬 계산
            checksum = self._calculate_checksum(archive_path)
            
            # ZIP 아카이브 정보 생성
            archive_info = ZIPArchiveInfo(
                archive_path=archive_path,
                file_count=file_count,
                total_size=total_size,
                created_at=created_at,
                checksum=checksum
            )
            
            return archive_info
            
        except Exception as e:
            # 실패 시 생성된 파일 정리
            if os.path.exists(archive_path):
                os.remove(archive_path)
            raise IOError(f"ZIP 아카이브 생성 중 오류 발생: {str(e)}") from e
    
    def add_file(
        self, 
        zipf: zipfile.ZipFile, 
        file_path: str, 
        archive_path: str
    ) -> None:
        """파일을 아카이브에 추가
        
        Args:
            zipf: ZipFile 객체
            file_path: 추가할 파일의 실제 경로
            archive_path: 아카이브 내에서의 경로
            
        Requirements: 2.1, 2.2
        """
        zipf.write(file_path, archive_path)
    
    def validate_archive(self, archive_path: str) -> bool:
        """생성된 아카이브 검증
        
        ZIP 파일이 올바르게 생성되었는지 검증합니다.
        
        Args:
            archive_path: 검증할 ZIP 파일 경로
            
        Returns:
            bool: 검증 성공 여부
            
        Requirements: 2.4
        """
        try:
            if not os.path.exists(archive_path):
                return False
            
            # ZIP 파일 무결성 검사
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                # testzip()은 손상된 파일이 있으면 해당 파일명을 반환
                bad_file = zipf.testzip()
                if bad_file is not None:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _generate_timestamped_filename(self) -> str:
        """타임스탬프 포함 파일명 생성
        
        현재 시간을 기반으로 고유한 파일명을 생성합니다.
        형식: pipeline_YYYYMMDD_HHMMSS.zip
        
        Returns:
            str: 타임스탬프가 포함된 파일명
            
        Requirements: 2.3
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"pipeline_{timestamp}.zip"
    
    def _calculate_checksum(self, file_path: str) -> str:
        """파일의 체크섬 계산
        
        SHA256 해시를 사용하여 파일의 체크섬을 계산합니다.
        
        Args:
            file_path: 체크섬을 계산할 파일 경로
            
        Returns:
            str: 16진수 형식의 체크섬
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # 대용량 파일을 위해 청크 단위로 읽기
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def get_archive_info(self, archive_path: str) -> dict:
        """ZIP 아카이브 정보 조회
        
        생성된 ZIP 파일의 상세 정보를 반환합니다.
        
        Args:
            archive_path: ZIP 파일 경로
            
        Returns:
            dict: 아카이브 정보 (경로, 크기, 파일 개수 등)
            
        Requirements: 2.5
        """
        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"ZIP 파일을 찾을 수 없습니다: {archive_path}")
        
        file_size = os.path.getsize(archive_path)
        
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            file_list = zipf.namelist()
            file_count = len(file_list)
        
        return {
            "archive_path": archive_path,
            "file_size": file_size,
            "file_count": file_count,
            "files": file_list
        }

    def display_archive_info(self, archive_info: ZIPArchiveInfo) -> str:
        """생성된 ZIP 정보를 사용자 친화적 형식으로 표시
        
        Args:
            archive_info: ZIP 아카이브 정보
            
        Returns:
            str: 포맷된 정보 문자열
            
        Requirements: 2.5
        """
        size_mb = archive_info.total_size / (1024 * 1024)
        
        info_text = f"""
ZIP 아카이브 생성 완료
{'=' * 50}
파일 경로: {archive_info.archive_path}
파일 개수: {archive_info.file_count}개
전체 크기: {size_mb:.2f} MB
생성 시간: {archive_info.created_at.strftime('%Y-%m-%d %H:%M:%S')}
체크섬: {archive_info.checksum[:16]}...
{'=' * 50}
"""
        return info_text.strip()
    
    def handle_compression_error(self, error: Exception) -> str:
        """압축 실패 시 에러 메시지 생성
        
        Args:
            error: 발생한 예외
            
        Returns:
            str: 사용자 친화적 에러 메시지
            
        Requirements: 2.4
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        if isinstance(error, FileNotFoundError):
            return f"❌ 파일을 찾을 수 없습니다: {error_msg}"
        elif isinstance(error, PermissionError):
            return f"❌ 파일 접근 권한이 없습니다: {error_msg}"
        elif isinstance(error, IOError):
            return f"❌ ZIP 압축 중 오류가 발생했습니다: {error_msg}"
        elif isinstance(error, ValueError):
            return f"❌ 잘못된 입력값: {error_msg}"
        else:
            return f"❌ 예상치 못한 오류 발생 ({error_type}): {error_msg}"
