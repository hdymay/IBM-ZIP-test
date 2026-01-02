# C to Java 변환 파이프라인 테스트 시스템

Python 소스 파일들을 자동으로 ZIP 아카이브로 패키징하고, watsonx.ai asset에 업로드하여 내부 파이프라인을 실행하는 시스템입니다.

## 주요 기능

- ✅ Python 소스 파일 선택 (디렉토리 스캔 또는 샘플 모드)
- ✅ 자동 ZIP 아카이브 생성 (타임스탬프 포함)
- ✅ watsonx.ai asset 자동 업로드
- ✅ GitHub 자동 업로드 (선택적)
- ✅ Git 자동화 (커밋, 푸시, 풀)
- ✅ 재시도 메커니즘 (최대 3회, 지수 백오프)
- ✅ 진행 상황 실시간 추적
- ✅ 샘플 파일 실행 및 결과 추적

## 설치 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 필요한 값을 입력하세요:

```bash
cp .env.example .env
```

`.env` 파일 내용:

```ini
# watsonx.ai API 설정
WATSONX_API_KEY=your_api_key_here
WATSONX_ENDPOINT=https://your-endpoint.watsonx.ai
WATSONX_PROJECT_ID=your_project_id

# 출력 디렉토리 설정
OUTPUT_DIRECTORY=./output

# 재시도 설정
MAX_RETRIES=3

# 타임아웃 설정 (초)
TIMEOUT=300

# GitHub 업로드 설정 (선택적)
GITHUB_TOKEN=your_github_token
GITHUB_REPO_URL=https://github.com/your-username/your-repo.git
GITHUB_UPLOAD_ENABLED=true
```

#### GitHub 업로드 설정 (선택적)

watsonx.ai 업로드와 함께 GitHub에도 ZIP 파일을 자동 업로드할 수 있습니다:

1. **GitHub Personal Access Token 생성**:
   - https://github.com/settings/tokens 에서 새 토큰 생성
   - `repo` 권한 (Contents: Write) 필요

2. **GitHub 저장소 준비**:
   - 새 저장소 생성 또는 기존 저장소 사용
   - 저장소 URL을 `GITHUB_REPO_URL`에 설정

3. **환경 변수 설정**:
   ```ini
   GITHUB_TOKEN=ghp_your_token_here
   GITHUB_REPO_URL=https://github.com/hdymay/IBM-ZIP-test.git
   GITHUB_UPLOAD_ENABLED=true
   ```

## 사용 방법

### 기본 실행

```bash
python main.py
```

### 워크플로우

1. **설정 로드**: 환경 변수 또는 설정 파일에서 watsonx.ai 및 GitHub 연결 정보를 로드합니다.

2. **파일 선택**: 두 가지 모드 중 선택
   - **샘플 모드**: `samples/` 디렉토리의 모든 Python 파일 자동 선택
   - **디렉토리 지정**: 원하는 디렉토리를 지정하여 파일 선택

3. **ZIP 생성**: 선택된 파일들을 타임스탬프가 포함된 ZIP 파일로 압축

4. **업로드**: 
   - **watsonx.ai**: 기본 업로드 대상 (재시도 메커니즘 포함)
   - **GitHub**: 선택적 추가 업로드 (GitHub 설정이 활성화된 경우)

5. **완료**: Asset ID, URL 및 watsonx.ai 노트북에서 사용할 코드 예시 표시

## 프로젝트 구조

```
c-to-java-pipeline/
├── main.py                    # 메인 진입점
├── src/
│   ├── config/
│   │   └── config_manager.py  # 설정 관리
│   ├── core/
│   │   ├── file_selector.py   # 파일 선택
│   │   ├── zip_builder.py     # ZIP 생성
│   │   ├── watsonx_uploader.py # 업로드
│   │   └── sample_executor.py # 샘플 실행
│   └── models/
│       └── data_models.py     # 데이터 모델
├── samples/                   # 샘플 Python 파일
│   ├── ingest.py
│   ├── parse.py
│   ├── extract.py
│   ├── transform.py
│   ├── generate.py
│   ├── validate.py
│   └── report.py
├── tests/                     # 테스트
│   ├── unit/                  # 단위 테스트
│   └── integration/           # 통합 테스트
├── config/                    # 설정 파일 저장 위치
├── output/                    # ZIP 파일 출력 위치
└── requirements.txt           # Python 의존성
```

## 샘플 모드

시스템에는 7개의 샘플 Python 파일이 포함되어 있습니다:

1. **ingest.py**: 데이터 수집 단계
2. **parse.py**: 파싱 단계
3. **extract.py**: 추출 단계
4. **transform.py**: 변환 단계
5. **generate.py**: 생성 단계
6. **validate.py**: 검증 단계
7. **report.py**: 보고서 생성 단계

샘플 모드를 선택하면 이 파일들이 자동으로 실행되고 결과가 추적됩니다.

## 테스트 실행

### 단위 테스트

```bash
pytest tests/unit/ -v
```

### 통합 테스트

```bash
pytest tests/integration/ -v
```

### 전체 테스트

```bash
pytest tests/ -v
```

### 커버리지 포함

```bash
pytest --cov=src --cov-report=html
```

## 에러 처리

시스템은 다음과 같은 에러를 자동으로 처리합니다:

- **파일 시스템 에러**: 파일 읽기/쓰기 실패, 권한 문제
- **네트워크 에러**: watsonx.ai 연결 실패, 타임아웃
- **검증 에러**: 잘못된 파일 형식, 빈 파일 선택
- **업로드 에러**: 재시도 메커니즘 (최대 3회, 지수 백오프)

## 설정 가이드

### 설정 파일 사용

환경 변수 대신 설정 파일을 사용할 수 있습니다:

```python
from src.config.config_manager import ConfigManager
from src.models.data_models import Configuration

config_manager = ConfigManager()

# 설정 생성
config = Configuration(
    watsonx_api_key="your_api_key",
    watsonx_endpoint="https://your-endpoint.watsonx.ai",
    watsonx_project_id="your_project_id",
    output_directory="./output",
    max_retries=3,
    timeout=300
)

# 설정 저장 (암호화됨)
config_manager.save_config(config)

# 설정 로드
loaded_config = config_manager.load_config()

# 연결 테스트
success, error = config_manager.test_connection(loaded_config)
```

### 연결 테스트

watsonx.ai 연결을 테스트하려면:

```python
from src.config.config_manager import ConfigManager

config_manager = ConfigManager()
config = config_manager.load_config()

success, error_message = config_manager.test_connection(config)

if success:
    print("✓ 연결 성공")
else:
    print(f"❌ 연결 실패: {error_message}")
```

## 보안

- API 키는 자동으로 암호화되어 저장됩니다
- 설정 파일(`config/settings.json`)과 암호화 키(`config/.key`)는 `.gitignore`에 포함되어 있습니다
- 환경 변수를 사용하는 것을 권장합니다

## 요구사항

- Python 3.9 이상
- requests
- python-dotenv
- cryptography
- pytest (테스트용)
- hypothesis (Property-Based Testing용)

## 라이선스

이 프로젝트는 내부 테스트 목적으로 개발되었습니다.

## watsonx.ai 노트북에서 사용하기

업로드된 ZIP 파일을 watsonx.ai 노트북에서 자동으로 실행하는 방법입니다.

### 1. ZIP 파일 업로드

먼저 로컬에서 ZIP 파일을 생성하고 업로드합니다:

```bash
python main.py
```

업로드가 완료되면 Asset ID와 파일명이 표시됩니다 (예: `pipeline_20251230_091147.zip`).

### 2. 노트북 생성

watsonx.ai 프로젝트에서:
1. **Assets** 탭으로 이동
2. **New asset** → **Jupyter Notebook** 선택
3. 원하는 런타임 환경 선택 (Python 3.9 이상)

### 3. 노트북 초기화

**방법 1: 간단한 경로 확인 (권장)**

노트북의 **첫 번째 셀**에서 ZIP 파일 위치를 먼저 확인합니다:

```python
import os

# ZIP 파일 위치 확인
paths = ["/project_data/data_asset", "/project_data/assets", "/home/wsuser/work", "/userfs"]

for path in paths:
    if os.path.exists(path):
        files = [f for f in os.listdir(path) if f.endswith('.zip')]
        if files:
            print(f"✅ ZIP 파일 발견: {path}")
            for f in files:
                print(f"   - {f}")
                print(f"   전체 경로: {os.path.join(path, f)}")
```

**방법 2: 전체 초기화 코드**

ZIP 파일 경로를 확인한 후, **두 번째 셀**에서 다음 코드를 실행합니다:

```python
import zipfile
import sys
import os

# ============================================================
# 설정: 업로드한 ZIP 파일명을 여기에 입력하세요
# ============================================================
ZIP_FILE_NAME = "pipeline_20251230_091147.zip"  # 실제 파일명으로 변경

# ============================================================
# 자동 설정
# ============================================================
zip_path = f"/project_data/data_asset/{ZIP_FILE_NAME}"

if os.path.exists(zip_path):
    # ZIP 압축 해제
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall("/tmp/pipeline")
    
    # Python 경로에 추가
    sys.path.insert(0, "/tmp/pipeline")
    
    print("✓ Pipeline 준비 완료!")
    print(f"  ZIP 파일: {ZIP_FILE_NAME}")
    print(f"  압축 해제: /tmp/pipeline")
else:
    print(f"❌ ZIP 파일을 찾을 수 없습니다: {zip_path}")
    print("\n사용 가능한 파일:")
    import os
    asset_dir = "/project_data/data_asset"
    if os.path.exists(asset_dir):
        for f in os.listdir(asset_dir):
            if f.endswith('.zip'):
                print(f"  - {f}")
```

### 4. 파이프라인 실행

**두 번째 셀**에서 파이프라인을 실행합니다:

```python
import main

# 전체 파이프라인 실행
result = main.run_pipeline()

if result == 0:
    print("\n✅ 파이프라인 실행 완료!")
else:
    print("\n⚠ 일부 단계가 실패했습니다")
```

### 5. 개별 단계 실행 (선택적)

특정 단계만 실행하려면:

```python
import ingest
import parse
import extract
import transform
import generate
import validate
import report

# 예: 파싱 단계만 실행
result = parse.main()
print(f"파싱 결과: {result}")
```

### 문제 해결

#### 자산 디렉토리를 찾을 수 없는 경우

watsonx.ai 환경마다 디렉토리 구조가 다를 수 있습니다. **진단 스크립트**를 실행하여 실제 경로를 확인하세요:

**노트북 첫 번째 셀에서 실행:**

```python
# samples/diagnose_environment.py의 전체 내용을 복사하여 실행
# 또는 GitHub에서 파일을 다운로드하여 실행

# 이 스크립트는 다음을 확인합니다:
# - Python 환경 정보
# - 가능한 모든 자산 디렉토리 경로
# - 업로드된 ZIP 파일 위치
# - 디렉토리 구조 및 권한
```

진단 스크립트 실행 후:
1. **ZIP 파일이 발견된 경로**를 확인
2. 해당 경로를 초기화 코드의 `zip_path`에 사용

#### ZIP 파일을 찾을 수 없는 경우

1. **파일명 확인**: 로컬에서 업로드할 때 표시된 파일명과 정확히 일치하는지 확인
2. **자산 확인**: watsonx.ai 프로젝트의 Assets 탭에서 ZIP 파일이 업로드되었는지 확인
3. **프로젝트 확인**: 노트북이 올바른 프로젝트에서 실행되고 있는지 확인

#### 대안 방법: Watson Studio Lib 사용

파일 시스템 접근이 안 되는 경우, `ibm_watson_studio_lib`를 사용할 수 있습니다:

```python
# samples/notebook_setup_alternative.py의 내용 사용
# API 키가 필요합니다

API_KEY = "your_ibm_cloud_api_key"  # IBM Cloud API 키
ZIP_FILE_NAME = "pipeline_20251230_091147.zip"

# 나머지 코드는 notebook_setup_alternative.py 참조
```

이 방법은:
- IBM Cloud API 키를 사용하여 프로젝트 자산에 접근
- ZIP 파일을 다운로드하여 압축 해제
- 파일 시스템 경로 문제를 우회

#### Import 오류가 발생하는 경우

1. **경로 확인**: `sys.path`에 `/tmp/pipeline`이 포함되어 있는지 확인

```python
import sys
print(sys.path)
```

2. **파일 확인**: 압축 해제된 파일 목록 확인

```python
import os
if os.path.exists("/tmp/pipeline"):
    print("압축 해제된 파일:")
    for f in os.listdir("/tmp/pipeline"):
        print(f"  - {f}")
```

### 노트북 템플릿 저장 (권장)

초기화 코드가 정상 작동하면 노트북을 템플릿으로 저장하여 재사용할 수 있습니다:

1. 노트북 상단의 **File** → **Save as template** 선택
2. 템플릿 이름 입력 (예: "C to Java Pipeline Runner")
3. 다음에 새 노트북을 만들 때 이 템플릿을 선택하면 초기화 코드가 자동으로 포함됩니다

### 자동화된 초기화 스크립트

더 자세한 진단 정보가 필요하면 `samples/notebook_setup.py`의 내용을 사용하세요. 이 스크립트는:
- ZIP 파일 자동 검색
- 압축 해제 및 검증
- 모듈 import 테스트
- 상세한 에러 메시지 제공

## Airflow 통합

### Airflow 파이프라인

C to Java 프로젝트는 Apache Airflow를 통해 자동화된 파이프라인을 실행할 수 있습니다.

#### 빠른 시작

```bash
# Airflow 실행 (Docker Compose)
docker-compose -f docker-compose.airflow.yml up -d

# Airflow UI 접속
http://localhost:8080
# 로그인: airflow / airflow
```

#### 사용 가능한 DAG

1. **c_to_java_pipeline.py** - 기본 파이프라인
2. **c_to_java_taskflow.py** - TaskFlow API 버전
3. **c_to_java_samples_pipeline.py** - 샘플 실행 파이프라인
4. **watsonx_notebook_job_pipeline.py** - watsonx Job 연동

#### 상세 가이드

- **AIRFLOW_QUICKSTART.md** - Airflow 빠른 시작
- **AIRFLOW_CUSTOM_PIPELINE_GUIDE.md** - 커스텀 파이프라인 작성
- **AIRFLOW_RESULT_GUIDE.md** - 결과 확인 방법
- **WATSONX_NOTEBOOK_JOB_GUIDE.md** - watsonx Job 연동

### 폐쇄망 환경 설치

인터넷 연결이 없는 폐쇄망 환경에서 Airflow를 설치하는 방법입니다.

#### 옵션 A: 회사 Airflow 서버에 추가 패키지만 설치 (권장)

회사에 이미 Airflow가 설치되어 있는 경우, C to Java 프로젝트에 필요한 패키지만 추가합니다.

```powershell
# Windows
.\collect_c_to_java_packages.ps1

# Linux/Mac
chmod +x collect_c_to_java_packages.sh
./collect_c_to_java_packages.sh
```

수집되는 패키지:
- **requests** (watsonx.ai, GitHub API)
- **python-dotenv** (환경 변수 관리)

**총 크기**: 약 5MB

**장점**:
- 용량 절약 (355MB → 5MB)
- 빠른 전송
- 명확한 목적

#### 옵션 B: Airflow 전체 설치 (새 서버)

Airflow가 설치되지 않은 새 서버에 전체 설치가 필요한 경우:

```powershell
# Windows
.\collect_airflow_wheels.ps1

# Linux/Mac
chmod +x collect_airflow_wheels.sh
./collect_airflow_wheels.sh
```

수집되는 패키지:
- Airflow 3.1.0 + 모든 의존성 (약 200MB)
- PostgreSQL 드라이버
- Celery, Redis, Flower
- **requests** (watsonx.ai, GitHub API)
- **python-dotenv** (환경 변수 관리)

**총 크기**: 약 355MB (Docker 이미지 제외)

#### 2단계: USB로 전송

```bash
# 패키지 압축
tar -czf airflow_3.1.0_wheels.tar.gz airflow_3.1.0_wheels/

# USB로 폐쇄망 환경에 전송
```

#### 3단계: 폐쇄망 환경에서 설치

```bash
# 압축 해제
tar -xzf airflow_3.1.0_wheels.tar.gz

# 가상환경 생성
python -m venv .venv
source .venv/bin/activate

# 로컬 패키지에서 설치
pip install \
    --no-index \
    --find-links=airflow_3.1.0_wheels \
    apache-airflow==3.1.0 \
    requests \
    python-dotenv

# Airflow 초기화
export AIRFLOW_HOME=~/airflow
airflow db migrate
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@company.com \
    --password admin123
```

#### 폐쇄망 환경 가이드

- **AIRFLOW_OFFLINE_INSTALLATION_GUIDE.md** - 상세 설치 가이드
- **AIRFLOW_CLOSED_NETWORK_GUIDE.md** - 폐쇄망 환경 구축 가이드
- **AIRFLOW_PACKAGE_SUMMARY.md** - 패키지 요약 및 체크리스트
- **AIRFLOW_DEPENDENCIES_USAGE.md** - 의존성 패키지 사용처 가이드 ⭐

#### 폐쇄망 환경 특화 요구사항

1. **Git CLI 필수**
   - Git push/pull 자동화에 사용
   - Windows: Git-2.43.0-64-bit.exe
   - Linux: git-2.43.0.rpm 또는 .deb

2. **내부 Git 서버**
   - GitHub Enterprise Server
   - GitLab Self-hosted
   - Bitbucket Server

3. **내부 watsonx.ai 인스턴스**
   - IBM Cloud Pak for Data
   - 또는 프록시 서버 설정

4. **환경 변수 설정**
   ```bash
   # 내부 서버 URL로 변경
   GITHUB_REPO_URL=https://internal-git.company.com/org/repo.git
   WATSONX_ENDPOINT=https://internal-watsonx.company.com
   ```

## Git 자동화

프로젝트는 Git push/pull 자동화 기능을 제공합니다.

### 사용 방법

```python
from src.core.git_manager import GitManager

# Git 관리자 초기화
git_manager = GitManager(repo_path=".")

# 자동 커밋 및 푸시
result = git_manager.auto_commit_and_push(
    commit_message="Update pipeline results",
    remote="origin",
    branch="main"
)

if result.success:
    print(f"✓ {result.message}")
else:
    print(f"✗ {result.error}")
```

### 테스트

```bash
# Git 자동화 테스트
python test_git_automation.py
```

### Airflow DAG에서 사용

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.core.git_manager import GitManager

def git_push_task():
    git_manager = GitManager()
    result = git_manager.auto_commit_and_push(
        commit_message="Airflow pipeline execution results"
    )
    if not result.success:
        raise Exception(f"Git push failed: {result.error}")

with DAG('git_automation_dag', ...) as dag:
    push_task = PythonOperator(
        task_id='git_push',
        python_callable=git_push_task
    )
```

## 문의

문제가 발생하거나 질문이 있으시면 이슈를 등록해주세요.
