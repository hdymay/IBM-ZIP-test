# Airflow 3.1.0 의존성 패키지 사용처 가이드

## 개요

이 문서는 Airflow 3.1.0 폐쇄망 설치 시 수집되는 모든 패키지가 어디에서 어떻게 사용되는지 설명합니다.

---

## 1. Airflow 코어 패키지

### apache-airflow==3.1.0
**사용처**: Airflow 전체 시스템
**용도**: 
- 워크플로우 스케줄링 및 실행
- DAG 관리
- Task 오케스트레이션
- 웹 UI 제공

**C to Java 프로젝트에서의 역할**:
```python
# dags/c_to_java_pipeline.py
from airflow import DAG
from airflow.operators.python import PythonOperator

# DAG 정의 및 Task 실행
```

---

## 2. 웹 프레임워크 및 API

### flask>=2.2.5,<3.1
**사용처**: Airflow 웹 서버
**용도**:
- Airflow UI 백엔드
- REST API 엔드포인트
- 사용자 인증 및 세션 관리

**실제 사용**:
- `http://localhost:8080` - Airflow 웹 UI
- DAG 목록, Task 상태, 로그 확인

### flask-appbuilder>=4.3.0
**사용처**: Airflow UI 컴포넌트
**용도**:
- 관리자 페이지 구성
- 사용자 권한 관리
- 메뉴 및 뷰 생성

### connexion[flask]>=3.0.0
**사용처**: Airflow REST API
**용도**:
- OpenAPI 스펙 기반 API 자동 생성
- API 문서화
- 요청 검증

**C to Java 프로젝트에서의 활용**:
```bash
# Airflow REST API를 통한 DAG 트리거
curl -X POST http://localhost:8080/api/v1/dags/c_to_java_pipeline/dagRuns \
  -H "Content-Type: application/json" \
  -d '{"conf": {}}'
```

### gunicorn>=20.1.0
**사용처**: Airflow 웹 서버 프로세스 관리
**용도**:
- WSGI HTTP 서버
- 멀티 워커 프로세스 관리
- 프로덕션 환경 배포

---

## 3. 데이터베이스 관련

### sqlalchemy>=1.4.36,<2.0
**사용처**: Airflow 메타데이터 저장소
**용도**:
- DAG 실행 이력 저장
- Task 상태 추적
- 사용자 정보 관리
- Connection 정보 저장

**데이터베이스 테이블**:
- `dag_run` - DAG 실행 기록
- `task_instance` - Task 실행 상태
- `xcom` - Task 간 데이터 전달
- `connection` - 외부 시스템 연결 정보

### alembic>=1.13.1
**사용처**: 데이터베이스 마이그레이션
**용도**:
- 스키마 버전 관리
- 업그레이드/다운그레이드 스크립트 실행

**실제 사용**:
```bash
# Airflow 초기화 시 자동 실행
airflow db migrate
```

### psycopg2-binary
**사용처**: PostgreSQL 데이터베이스 드라이버
**용도**:
- PostgreSQL 연결
- SQL 쿼리 실행

**설정 예시**:
```bash
# .env 또는 airflow.cfg
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@localhost/airflow
```

---

## 4. 스케줄링 및 시간 관리

### croniter>=2.0.2
**사용처**: DAG 스케줄 파싱
**용도**:
- Cron 표현식 해석
- 다음 실행 시간 계산

**C to Java 프로젝트 예시**:
```python
# dags/c_to_java_pipeline.py
dag = DAG(
    'c_to_java_pipeline',
    schedule_interval='0 2 * * *',  # 매일 새벽 2시 실행 (croniter가 파싱)
    ...
)
```

### cron-descriptor>=1.2.24
**사용처**: Cron 표현식 설명
**용도**:
- Cron 표현식을 사람이 읽을 수 있는 문자열로 변환
- UI에서 스케줄 설명 표시

**예시**:
- `0 2 * * *` → "매일 오전 2시에 실행"

### pendulum>=3.0.0
**사용처**: 날짜/시간 처리
**용도**:
- 타임존 처리
- 날짜 계산
- 실행 시간 관리

**C to Java 프로젝트 예시**:
```python
from pendulum import datetime

default_args = {
    'start_date': datetime(2025, 1, 1, tz='Asia/Seoul'),
}
```

### python-dateutil>=2.3
**사용처**: 날짜 파싱 및 계산
**용도**:
- 상대적 날짜 계산
- 날짜 문자열 파싱

---

## 5. 템플릿 엔진

### jinja2>=3.1.2
**사용처**: DAG 템플릿 렌더링
**용도**:
- Task 파라미터 템플릿화
- 동적 값 주입

**C to Java 프로젝트 예시**:
```python
# dags/c_to_java_pipeline.py
PythonOperator(
    task_id='process_file',
    op_kwargs={
        'date': '{{ ds }}',  # Jinja2 템플릿 (실행 날짜)
        'run_id': '{{ run_id }}',  # 실행 ID
    }
)
```

### markupsafe>=2.1.2
**사용처**: Jinja2 보안
**용도**:
- HTML 이스케이프
- XSS 공격 방지

---

## 6. 직렬화 및 데이터 처리

### dill>=0.3.2
**사용처**: Python 객체 직렬화
**용도**:
- Task 간 데이터 전달 (XCom)
- 복잡한 객체 저장

**C to Java 프로젝트 예시**:
```python
# Task 1에서 데이터 반환
def select_files(**context):
    files = ['file1.py', 'file2.py']
    return files  # dill로 직렬화되어 XCom에 저장

# Task 2에서 데이터 가져오기
def build_zip(**context):
    ti = context['ti']
    files = ti.xcom_pull(task_ids='select_files')  # dill로 역직렬화
```

### marshmallow>=3.19.0
**사용처**: 데이터 검증 및 직렬화
**용도**:
- API 요청/응답 검증
- 스키마 정의

### jsonschema>=4.18.0
**사용처**: JSON 스키마 검증
**용도**:
- DAG 설정 검증
- API 페이로드 검증

---

## 7. 비동기 작업 처리

### celery>=5.3.0
**사용처**: CeleryExecutor (선택적)
**용도**:
- 분산 Task 실행
- 워커 프로세스 관리
- 대규모 병렬 처리

**설정 예시**:
```bash
# .env
AIRFLOW__CORE__EXECUTOR=CeleryExecutor
AIRFLOW__CELERY__BROKER_URL=redis://localhost:6379/0
```

**C to Java 프로젝트에서의 활용**:
- 여러 파일을 병렬로 처리
- 대용량 ZIP 파일 생성 시 워커 분산

### redis>=4.5.0
**사용처**: Celery 메시지 브로커
**용도**:
- Task 큐 관리
- 워커 간 통신
- 결과 백엔드

### flower>=2.0.0
**사용처**: Celery 모니터링
**용도**:
- 워커 상태 확인
- Task 진행 상황 모니터링
- 성능 메트릭 수집

**실행 방법**:
```bash
celery -A airflow.executors.celery_executor flower
# http://localhost:5555 접속
```

---

## 8. HTTP 클라이언트

### requests>=2.27.0
**사용처**: 
1. **Airflow 내부**: HTTP 연결 테스트, Provider 통신
2. **C to Java 프로젝트**: watsonx.ai, GitHub API 호출

**C to Java 프로젝트 사용처**:

#### watsonx.ai 업로드 (`src/core/watsonx_uploader.py`)
```python
import requests

# IAM 토큰 획득
response = requests.post(
    "https://iam.cloud.ibm.com/identity/token",
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
    data={'grant_type': 'urn:ibm:params:oauth:grant-type:apikey', 'apikey': api_key}
)

# 자산 업로드
response = requests.post(
    f"{endpoint}/v2/assets",
    headers={'Authorization': f'Bearer {token}'},
    json=asset_metadata
)
```

#### GitHub 업로드 (`src/core/github_uploader.py`)
```python
import requests

# 파일 업로드
response = requests.put(
    f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
    headers={'Authorization': f'token {github_token}'},
    json={'message': commit_message, 'content': content_base64}
)
```

### httpx>=0.25.0
**사용처**: Airflow 내부 HTTP 클라이언트
**용도**:
- 비동기 HTTP 요청
- HTTP/2 지원
- 최신 HTTP 기능

---

## 9. 환경 변수 관리

### python-dotenv>=1.0.0
**사용처**: C to Java 프로젝트
**용도**:
- `.env` 파일 로드
- 환경 변수 관리

**C to Java 프로젝트 사용처** (`src/config/config_manager.py`):
```python
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 읽기
watsonx_api_key = os.getenv('WATSONX_API_KEY')
github_token = os.getenv('GITHUB_TOKEN')
```

**`.env` 파일 예시**:
```bash
WATSONX_API_KEY=your_api_key
WATSONX_ENDPOINT=https://api.dataplatform.cloud.ibm.com
WATSONX_PROJECT_ID=your_project_id
GITHUB_TOKEN=ghp_your_token
GITHUB_REPO_URL=https://github.com/user/repo.git
```

---

## 10. 암호화 및 보안

### cryptography>=41.0.0
**사용처**: 
1. **Airflow**: Connection 암호화, Fernet 키
2. **C to Java 프로젝트**: 설정 파일 암호화

**Airflow 사용**:
```bash
# Fernet 키 생성
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# .env 설정
AIRFLOW__CORE__FERNET_KEY=your_fernet_key
```

**C to Java 프로젝트 사용** (`src/config/config_manager.py`):
```python
from cryptography.fernet import Fernet

# API 키 암호화 저장
cipher = Fernet(key)
encrypted_api_key = cipher.encrypt(api_key.encode())
```

### pyjwt>=2.4.0
**사용처**: Airflow 인증
**용도**:
- JWT 토큰 생성/검증
- API 인증

---

## 11. 로깅 및 모니터링

### colorlog>=6.7.0
**사용처**: Airflow 로그 출력
**용도**:
- 컬러 로그 출력
- 로그 레벨별 색상 구분

**실제 출력**:
```
[2025-01-02 10:00:00,000] {taskinstance.py:1234} INFO - Task started
[2025-01-02 10:00:01,000] {taskinstance.py:1235} ERROR - Task failed
```

### rich>=13.0.0
**사용처**: CLI 출력 포맷팅
**용도**:
- 테이블 출력
- 진행 바 표시
- 마크다운 렌더링

**예시**:
```bash
airflow dags list  # rich로 포맷된 테이블 출력
```

### opentelemetry-api>=1.15.0
**사용처**: 분산 추적
**용도**:
- Task 실행 추적
- 성능 모니터링
- 메트릭 수집

---

## 12. Airflow Providers

### apache-airflow-providers-http
**사용처**: HTTP Operator
**용도**:
- HTTP API 호출
- Webhook 트리거

**C to Java 프로젝트 활용 예시**:
```python
from airflow.providers.http.operators.http import SimpleHttpOperator

# watsonx.ai API 호출
http_task = SimpleHttpOperator(
    task_id='call_watsonx_api',
    http_conn_id='watsonx_default',
    endpoint='/v2/assets',
    method='POST',
    data=json.dumps(payload),
)
```

### apache-airflow-providers-postgres
**사용처**: PostgreSQL Operator
**용도**:
- SQL 쿼리 실행
- 데이터베이스 작업

### apache-airflow-providers-amazon
**사용처**: AWS 서비스 연동 (선택적)
**용도**:
- S3 파일 업로드/다운로드
- EMR 작업 실행

**C to Java 프로젝트 활용 가능**:
```python
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator

# ZIP 파일을 S3에 업로드
upload_to_s3 = LocalFilesystemToS3Operator(
    task_id='upload_to_s3',
    filename='/tmp/pipeline.zip',
    dest_key='pipelines/pipeline.zip',
    dest_bucket='my-bucket',
)
```

---

## 13. Git 작업 (별도 설치 필요)

### Git CLI
**사용처**: C to Java 프로젝트 Git 자동화
**용도**:
- Git push/pull 자동화
- 커밋 생성

**C to Java 프로젝트 사용** (`src/core/git_manager.py`):
```python
import subprocess

# Git 명령어 실행 (subprocess 사용)
result = subprocess.run(
    ['git', 'add', '.'],
    cwd=repo_path,
    capture_output=True,
    text=True
)

result = subprocess.run(
    ['git', 'commit', '-m', message],
    cwd=repo_path,
    capture_output=True,
    text=True
)

result = subprocess.run(
    ['git', 'push', 'origin', 'main'],
    cwd=repo_path,
    capture_output=True,
    text=True
)
```

**주의**: Git은 Python 패키지가 아니라 시스템 레벨 도구입니다.
- Windows: Git-2.43.0-64-bit.exe 설치
- Linux: `sudo apt-get install git` 또는 rpm 설치

---

## 14. 기타 유틸리티

### packaging>=23.0
**사용처**: 버전 비교 및 파싱
**용도**:
- 패키지 버전 검증
- 의존성 해결

### tenacity>=8.0.0
**사용처**: 재시도 로직
**용도**:
- Task 실패 시 자동 재시도
- 지수 백오프

**C to Java 프로젝트 활용**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def upload_to_watsonx():
    # 실패 시 최대 3회 재시도
    pass
```

### tabulate>=0.7.5
**사용처**: 테이블 출력
**용도**:
- CLI 테이블 포맷팅
- 데이터 시각화

---

## C to Java 프로젝트 의존성 맵

### 직접 사용하는 패키지

| 패키지 | 사용 모듈 | 용도 |
|--------|----------|------|
| **requests** | `src/core/watsonx_uploader.py` | watsonx.ai API 호출 |
| **requests** | `src/core/github_uploader.py` | GitHub API 호출 |
| **python-dotenv** | `src/config/config_manager.py` | 환경 변수 로드 |
| **cryptography** | `src/config/config_manager.py` | API 키 암호화 |
| **Git CLI** | `src/core/git_manager.py` | Git 자동화 (subprocess) |

### Airflow DAG에서 사용

| 패키지 | DAG 파일 | 용도 |
|--------|---------|------|
| **airflow** | 모든 DAG 파일 | DAG 정의, Task 실행 |
| **pendulum** | `dags/c_to_java_pipeline.py` | 날짜/시간 처리 |
| **jinja2** | 모든 DAG 파일 | 템플릿 변수 ({{ ds }}) |

---

## 패키지 크기 및 우선순위

### 필수 패키지 (약 250MB)
1. **apache-airflow** (100MB) - 핵심 시스템
2. **sqlalchemy** (5MB) - 데이터베이스
3. **flask** (3MB) - 웹 서버
4. **requests** (1MB) - HTTP 클라이언트 ⭐ C to Java 필수
5. **python-dotenv** (0.1MB) - 환경 변수 ⭐ C to Java 필수
6. **cryptography** (5MB) - 암호화 ⭐ C to Java 필수

### 선택 패키지 (약 100MB)
7. **celery** (10MB) - 분산 실행 (대규모 처리 시)
8. **redis** (5MB) - 메시지 큐 (Celery 사용 시)
9. **flower** (3MB) - 모니터링 (Celery 사용 시)
10. **Providers** (50MB) - 외부 시스템 연동

---

## 폐쇄망 환경 최소 설치

### 최소 구성 (약 250MB)
```bash
pip install \
    --no-index \
    --find-links=airflow_3.1.0_wheels \
    apache-airflow==3.1.0 \
    requests \
    python-dotenv \
    psycopg2-binary
```

이 구성으로 다음이 가능합니다:
- Airflow 웹 UI 실행
- DAG 스케줄링 및 실행
- watsonx.ai 업로드
- GitHub 업로드
- Git 자동화 (Git CLI 별도 설치 필요)

### 전체 구성 (약 355MB)
```bash
pip install \
    --no-index \
    --find-links=airflow_3.1.0_wheels \
    apache-airflow==3.1.0 \
    requests \
    python-dotenv \
    psycopg2-binary \
    celery \
    redis \
    flower \
    apache-airflow-providers-http \
    apache-airflow-providers-postgres
```

추가 기능:
- 분산 Task 실행 (Celery)
- 워커 모니터링 (Flower)
- HTTP Operator
- PostgreSQL Operator

---

## 문제 해결

### 패키지를 찾을 수 없는 경우

```bash
# 특정 패키지만 다시 다운로드
pip download --dest airflow_3.1.0_wheels requests python-dotenv

# 설치 시 패키지 확인
ls airflow_3.1.0_wheels/ | grep requests
```

### 의존성 충돌

```bash
# 의존성 트리 확인
pip install pipdeptree
pipdeptree -p apache-airflow

# 특정 버전 강제 설치
pip install --no-index --find-links=airflow_3.1.0_wheels requests==2.31.0
```

### 사용하지 않는 패키지 제거

```bash
# 최소 설치 후 필요한 패키지만 추가 설치
pip install --no-index --find-links=airflow_3.1.0_wheels celery
```

---

## 요약

### C to Java 프로젝트 핵심 의존성

1. **requests** - watsonx.ai, GitHub API 호출 (필수)
2. **python-dotenv** - 환경 변수 관리 (필수)
3. **cryptography** - API 키 암호화 (권장)
4. **Git CLI** - Git 자동화 (필수, 별도 설치)

### Airflow 핵심 의존성

1. **apache-airflow** - 워크플로우 엔진
2. **sqlalchemy** - 메타데이터 저장
3. **flask** - 웹 UI
4. **celery** - 분산 실행 (선택)
5. **redis** - 메시지 큐 (선택)

### 설치 우선순위

1. **1순위**: Airflow 코어 + requests + python-dotenv
2. **2순위**: Git CLI 설치
3. **3순위**: Celery + Redis (대규모 처리 시)
4. **4순위**: Providers (외부 시스템 연동 시)

이 가이드를 참고하여 필요한 패키지만 선택적으로 설치할 수 있습니다!
