# Design Document

## Overview

C to Java 변환 파이프라인 테스트 시스템은 사용자가 선택한 Python 소스 파일들을 ZIP으로 패키징하고, watsonx.ai asset에 자동으로 업로드하는 워크플로우 자동화 도구입니다.

**핵심 목표**:
1. 사용자가 원하는 파일만 선택하여 ZIP 파일로 만드는 자동화
2. 생성된 ZIP 파일을 watsonx.ai asset에 업로드하는 자동화

시스템은 CLI 기반 인터페이스를 제공하며, 파일 선택, ZIP 생성, watsonx.ai 업로드의 3단계로 구성됩니다. 샘플 파일들은 간단한 로그만 출력하여 파이프라인 동작을 검증합니다.

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   CLI Interface │
└────────┬────────┘
         │
         ├──> File Selector
         │
         ├──> ZIP Builder
         │
         ├──> watsonx.ai Uploader
         │
         ├──> Pipeline Executor
         │
         └──> Log Collector
```

### Component Interaction Flow

```
User Input
    │
    ▼
File Selector ──> Selected Files List
    │
    ▼
ZIP Builder ──> ZIP Archive
    │
    ▼
watsonx.ai Uploader ──> Asset ID
    │
    ▼
Pipeline Executor ──> Execution Status
    │
    ▼
Log Collector ──> Execution Logs
    │
    ▼
Display Results
```

## Components and Interfaces

### 1. CLI Interface

**책임**: 사용자와의 상호작용 및 전체 워크플로우 조율

**주요 기능**:
- 명령줄 인자 파싱
- 대화형 메뉴 제공
- 진행 상황 표시
- 에러 메시지 출력

**인터페이스**:
```python
class CLIInterface:
    def run(self) -> None:
        """메인 실행 루프"""
        
    def display_menu(self) -> str:
        """메뉴 옵션 표시 및 선택 받기"""
        
    def display_progress(self, step: str, progress: float) -> None:
        """진행 상황 표시"""
        
    def display_error(self, error: str) -> None:
        """에러 메시지 표시"""
```

### 2. File Selector

**책임**: 사용자가 처리할 Python 파일 선택

**주요 기능**:
- 디렉토리 탐색
- Python 파일 필터링
- 파일 선택/해제
- 선택 목록 검증

**인터페이스**:
```python
class FileSelector:
    def scan_directory(self, path: str) -> List[str]:
        """디렉토리에서 Python 파일 스캔"""
        
    def select_files(self, files: List[str]) -> List[str]:
        """사용자가 파일 선택"""
        
    def validate_selection(self, files: List[str]) -> bool:
        """선택된 파일 검증"""
```

### 3. ZIP Builder

**책임**: 선택된 파일들을 ZIP 아카이브로 압축

**주요 기능**:
- 디렉토리 구조 보존
- 타임스탬프 포함 파일명 생성
- 압축 진행 상황 추적
- 압축 파일 검증

**인터페이스**:
```python
class ZIPBuilder:
    def create_archive(self, files: List[str], output_path: str) -> str:
        """ZIP 아카이브 생성"""
        
    def add_file(self, file_path: str, archive_path: str) -> None:
        """파일을 아카이브에 추가"""
        
    def validate_archive(self, archive_path: str) -> bool:
        """생성된 아카이브 검증"""
```

### 4. watsonx.ai Uploader

**책임**: ZIP 파일을 watsonx.ai asset에 업로드

**주요 기능**:
- watsonx.ai API 인증
- 파일 업로드
- 재시도 메커니즘
- 업로드 진행 상황 추적

**인터페이스**:
```python
class WatsonxUploader:
    def authenticate(self, api_key: str, endpoint: str) -> bool:
        """watsonx.ai 인증"""
        
    def upload_asset(self, file_path: str) -> str:
        """asset 업로드 및 asset ID 반환"""
        
    def get_upload_progress(self) -> float:
        """업로드 진행률 반환"""
        
    def retry_upload(self, file_path: str, max_retries: int) -> str:
        """재시도 로직 포함 업로드"""
```

### 5. Pipeline Executor

**책임**: watsonx.ai에서 파이프라인 실행 트리거 및 모니터링

**주요 기능**:
- 파이프라인 실행 트리거
- 실행 상태 모니터링
- 로그 스트리밍
- 실행 완료 감지

**인터페이스**:
```python
class PipelineExecutor:
    def trigger_pipeline(self, asset_id: str) -> str:
        """파이프라인 실행 트리거 및 실행 ID 반환"""
        
    def monitor_execution(self, execution_id: str) -> ExecutionStatus:
        """실행 상태 모니터링"""
        
    def get_logs(self, execution_id: str) -> List[str]:
        """실행 로그 가져오기"""
```

### 6. Log Collector

**책임**: 파이프라인 실행 로그 수집 및 저장

**주요 기능**:
- 로그 다운로드
- 로그 파싱
- 로그 파일 저장
- 로그 요약 생성

**인터페이스**:
```python
class LogCollector:
    def collect_logs(self, execution_id: str) -> List[str]:
        """로그 수집"""
        
    def save_logs(self, logs: List[str], output_path: str) -> None:
        """로그 파일 저장"""
        
    def generate_summary(self, logs: List[str]) -> str:
        """로그 요약 생성"""
```

### 7. Configuration Manager

**책임**: watsonx.ai 연결 설정 관리

**주요 기능**:
- 설정 파일 읽기/쓰기
- 설정 검증
- 자격 증명 암호화
- 연결 테스트

**인터페이스**:
```python
class ConfigManager:
    def load_config(self) -> Dict[str, str]:
        """설정 파일 로드"""
        
    def save_config(self, config: Dict[str, str]) -> None:
        """설정 파일 저장"""
        
    def validate_config(self, config: Dict[str, str]) -> bool:
        """설정 검증"""
        
    def test_connection(self, config: Dict[str, str]) -> bool:
        """연결 테스트"""
```

## Data Models

### File Selection

```python
@dataclass
class FileSelection:
    """선택된 파일 정보"""
    file_path: str
    relative_path: str
    size: int
    selected: bool
```

### ZIP Archive Info

```python
@dataclass
class ZIPArchiveInfo:
    """ZIP 아카이브 정보"""
    archive_path: str
    file_count: int
    total_size: int
    created_at: datetime
    checksum: str
```

### Upload Result

```python
@dataclass
class UploadResult:
    """업로드 결과"""
    asset_id: str
    asset_url: str
    upload_time: float
    file_size: int
    success: bool
    error_message: Optional[str] = None
```

### Execution Status

```python
@dataclass
class ExecutionStatus:
    """파이프라인 실행 상태"""
    execution_id: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    progress: float
    current_step: str
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
```

### Log Entry

```python
@dataclass
class LogEntry:
    """로그 엔트리"""
    timestamp: datetime
    level: str  # 'INFO', 'WARNING', 'ERROR'
    message: str
    step: str
```

### Configuration

```python
@dataclass
class Configuration:
    """시스템 설정"""
    watsonx_api_key: str
    watsonx_endpoint: str
    watsonx_project_id: str
    output_directory: str
    max_retries: int = 3
    timeout: int = 300
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: File selection validation

*For any* file selection operation, if the user completes the selection, then the selected file list must contain at least one valid Python file.

**Validates: Requirements 1.5**

### Property 2: ZIP archive integrity

*For any* ZIP archive created by the system, extracting and re-listing the files should produce the same file list as the original selection.

**Validates: Requirements 2.2**

### Property 3: Upload retry consistency

*For any* failed upload attempt, if retries are available (count < max_retries), then the system should attempt upload again with the same file.

**Validates: Requirements 3.4**

### Property 4: Pipeline execution monitoring

*For any* pipeline execution, the system should continuously monitor the status until it reaches a terminal state ('completed' or 'failed').

**Validates: Requirements 4.3**

### Property 5: Log completeness

*For any* completed pipeline execution, the collected logs should contain entries for all processing steps that were executed.

**Validates: Requirements 4.5**

### Property 6: Progress tracking monotonicity

*For any* workflow execution, the progress percentage should never decrease (monotonically increasing).

**Validates: Requirements 6.2**

### Property 7: Configuration validation

*For any* configuration input, if all required fields are present and valid, then the connection test should succeed or fail deterministically based on the credentials.

**Validates: Requirements 7.3**

### Property 8: Log file naming uniqueness

*For any* two log files saved by the system, their filenames should be different due to timestamp and execution ID inclusion.

**Validates: Requirements 8.3**

## Error Handling

### Error Categories

1. **File System Errors**
   - 파일 읽기/쓰기 실패
   - 디렉토리 접근 권한 없음
   - 디스크 공간 부족

2. **Network Errors**
   - watsonx.ai 연결 실패
   - 업로드 타임아웃
   - API 인증 실패

3. **Validation Errors**
   - 잘못된 파일 형식
   - 빈 파일 선택
   - 잘못된 설정 값

4. **Pipeline Errors**
   - 파이프라인 실행 실패
   - 로그 수집 실패
   - 타임아웃

### Error Handling Strategy

```python
class ErrorHandler:
    def handle_error(self, error: Exception, context: str) -> None:
        """에러 처리 및 로깅"""
        
    def should_retry(self, error: Exception) -> bool:
        """재시도 가능 여부 판단"""
        
    def get_user_message(self, error: Exception) -> str:
        """사용자 친화적 에러 메시지 생성"""
```

### Retry Logic

- **Network Errors**: 최대 3회 재시도, 지수 백오프 (1s, 2s, 4s)
- **Transient Errors**: 즉시 재시도
- **Permanent Errors**: 재시도 없이 즉시 실패

### Logging Strategy

- 모든 에러는 로그 파일에 기록
- 사용자에게는 간결한 메시지 표시
- 디버그 모드에서 상세 스택 트레이스 출력

## Testing Strategy

### Unit Tests

각 컴포넌트의 개별 기능을 테스트합니다:

- **FileSelector**: 디렉토리 스캔, 파일 필터링, 선택 검증
- **ZIPBuilder**: 아카이브 생성, 파일 추가, 검증
- **WatsonxUploader**: 인증, 업로드, 재시도 로직
- **PipelineExecutor**: 실행 트리거, 상태 모니터링
- **LogCollector**: 로그 수집, 파싱, 저장
- **ConfigManager**: 설정 로드/저장, 검증

### Property-Based Tests

Property-based testing 라이브러리로 **Hypothesis**를 사용합니다. 각 테스트는 최소 100회 반복 실행됩니다.

각 correctness property는 다음과 같이 구현됩니다:

1. **Property 1 테스트**: 랜덤 파일 목록 생성 → 선택 완료 → 최소 1개 Python 파일 확인
2. **Property 2 테스트**: 랜덤 파일 생성 → ZIP 압축 → 압축 해제 → 파일 목록 비교
3. **Property 3 테스트**: 업로드 실패 시뮬레이션 → 재시도 카운트 확인
4. **Property 4 테스트**: 파이프라인 실행 → 상태 변화 추적 → 터미널 상태 도달 확인
5. **Property 5 테스트**: 파이프라인 실행 → 로그 수집 → 모든 단계 로그 존재 확인
6. **Property 6 테스트**: 워크플로우 실행 → 진행률 변화 추적 → 단조 증가 확인
7. **Property 7 테스트**: 랜덤 설정 생성 → 검증 → 연결 테스트 결과 일관성 확인
8. **Property 8 테스트**: 여러 로그 파일 생성 → 파일명 중복 확인

### Integration Tests

전체 워크플로우를 테스트합니다:

- 파일 선택 → ZIP 생성 → 업로드 → 파이프라인 실행 → 로그 수집
- 에러 시나리오: 네트워크 실패, 인증 실패, 파이프라인 실패
- 샘플 파일 모드 전체 실행

### Test Data

시스템에 포함될 샘플 Python 파일들 (각 파일은 간단한 로그만 출력):

1. **ingest.py**: 데이터 수집 단계 로그
2. **parse.py**: 파싱 단계 로그
3. **extract.py**: 추출 단계 로그
4. **transform.py**: 변환 단계 로그
5. **generate.py**: 생성 단계 로그
6. **validate.py**: 검증 단계 로그
7. **report.py**: 보고서 생성 단계 로그

### Mocking Strategy

- watsonx.ai API 호출은 mock 객체로 대체
- 파일 시스템 작업은 임시 디렉토리 사용
- 네트워크 에러는 mock으로 시뮬레이션

## Implementation Notes

### Technology Stack

- **Language**: Python 3.9+
- **CLI Framework**: Click 또는 argparse
- **HTTP Client**: requests
- **ZIP Library**: zipfile (표준 라이브러리)
- **Testing**: pytest, hypothesis
- **Configuration**: python-dotenv, cryptography

### Directory Structure

```
c-to-java-pipeline/
├── src/
│   ├── cli/
│   │   └── interface.py
│   ├── core/
│   │   ├── file_selector.py
│   │   ├── zip_builder.py
│   │   ├── watsonx_uploader.py
│   │   ├── pipeline_executor.py
│   │   └── log_collector.py
│   ├── config/
│   │   └── config_manager.py
│   ├── models/
│   │   └── data_models.py
│   └── utils/
│       ├── error_handler.py
│       └── logger.py
├── samples/
│   ├── ingest.py
│   ├── parse.py
│   ├── extract.py
│   ├── transform.py
│   ├── generate.py
│   ├── validate.py
│   └── report.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── property/
├── config/
│   └── .env.example
└── main.py
```

### Configuration File Format

```ini
# .env
WATSONX_API_KEY=your_api_key_here
WATSONX_ENDPOINT=https://your-endpoint.watsonx.ai
WATSONX_PROJECT_ID=your_project_id
OUTPUT_DIRECTORY=./output
MAX_RETRIES=3
TIMEOUT=300
```

### Security Considerations

- API 키는 환경 변수 또는 암호화된 설정 파일에 저장
- 설정 파일은 .gitignore에 추가
- 로그에 민감한 정보 출력 금지
- HTTPS를 통한 안전한 통신

### Performance Considerations

- 대용량 파일 업로드 시 청크 단위 전송
- 비동기 업로드 지원 (선택적)
- 로그 스트리밍으로 메모리 사용량 최소화
- 진행 상황 표시로 사용자 경험 향상
