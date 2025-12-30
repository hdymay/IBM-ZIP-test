"""
데이터 모델 정의

이 모듈은 C to Java 변환 파이프라인 테스트 시스템의 모든 데이터 클래스를 정의합니다.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class FileSelection:
    """선택된 파일 정보
    
    Requirements: 1.3
    """
    file_path: str
    relative_path: str
    size: int
    selected: bool


@dataclass
class ZIPArchiveInfo:
    """ZIP 아카이브 정보
    
    Requirements: 2.1
    """
    archive_path: str
    file_count: int
    total_size: int
    created_at: datetime
    checksum: str


@dataclass
class UploadResult:
    """업로드 결과
    
    Requirements: 3.5
    """
    asset_id: str
    asset_url: str
    upload_time: float
    file_size: int
    success: bool
    error_message: Optional[str] = None


@dataclass
class ExecutionStatus:
    """파이프라인 실행 상태
    
    Requirements: 4.3, 6.1, 6.2
    """
    execution_id: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    progress: float
    current_step: str
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class LogEntry:
    """로그 엔트리
    
    Requirements: 4.3, 4.5
    """
    timestamp: datetime
    level: str  # 'INFO', 'WARNING', 'ERROR'
    message: str
    step: str


@dataclass
class Configuration:
    """시스템 설정
    
    Requirements: 7.1, 7.2, 7.3, 7.4
    """
    watsonx_api_key: str
    watsonx_endpoint: str
    watsonx_project_id: str
    output_directory: str
    max_retries: int = 3
    timeout: int = 300
    # GitHub 설정 (선택적)
    github_token: Optional[str] = None
    github_repo_url: Optional[str] = None
    github_upload_enabled: bool = False


@dataclass
class SampleExecutionResult:
    """샘플 파일 실행 결과
    
    Requirements: 5.4, 5.5
    """
    sample_name: str
    file_path: str
    success: bool
    execution_time: float
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None


@dataclass
class SampleExecutionSummary:
    """샘플 실행 요약
    
    Requirements: 5.4, 5.5
    """
    total_samples: int
    successful_samples: int
    failed_samples: int
    success_rate: float
    failed_sample_names: List[str]
    execution_results: List[SampleExecutionResult]
    total_execution_time: float
