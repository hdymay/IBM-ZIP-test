# watsonx.ai Notebook Job + Airflow 통합 가이드

이 가이드는 Airflow에서 watsonx.ai Notebook Job을 자동으로 실행하는 방법을 설명합니다.

## 아키텍처 비교

### 기존 방식 (수동)
```
로컬 PC
  ↓ (ZIP 생성)
  ↓ (업로드)
watsonx.ai Asset
  ↓ (수동 실행)
Notebook 실행
```

### Airflow + Notebook Job 방식 (자동)
```
Airflow DAG (스케줄)
  ↓ (API 호출)
watsonx Notebook Job API
  ↓ (자동 실행)
Notebook 실행
  ↓ (결과 반환)
Airflow (결과 처리)
```

## 설정 방법

### 1. watsonx.ai에서 Notebook 준비

#### 1.1 Notebook 생성
1. watsonx.ai 프로젝트에서 **Assets** 탭으로 이동
2. **New asset** → **Jupyter Notebook** 선택
3. 노트북 이름 입력 (예: `c_to_java_pipeline`)
4. 런타임 환경 선택 (Python 3.9 이상)

#### 1.2 Notebook에 코드 작성
```python
# Cell 1: 환경 변수 확인
import os
print("Pipeline Run ID:", os.getenv('PIPELINE_RUN_ID'))
print("Execution Date:", os.getenv('EXECUTION_DATE'))

# Cell 2: GitHub에서 코드 가져오기
import urllib.request
import zipfile
import sys

# GitHub에서 최신 ZIP 다운로드
urllib.request.urlretrieve(
    "https://github.com/hdymay/IBM-ZIP-test/raw/main/pipeline_latest.zip",
    "/tmp/pipeline.zip"
)

# 압축 해제
with zipfile.ZipFile("/tmp/pipeline.zip", "r") as z:
    z.extractall("/tmp/pipeline")

# Python 경로 추가
sys.path.insert(0, "/tmp/pipeline")

# Cell 3: 파이프라인 실행
import main
result = main.run_pipeline()

print(f"Pipeline 실행 결과: {result}")
```

#### 1.3 Notebook Asset ID 확인
1. 노트북 저장 후 **Asset details** 클릭
2. **Asset ID** 복사 (예: `abc123-def456-ghi789`)
3. `.env` 파일의 `WATSONX_NOTEBOOK_ASSET_ID`에 설정

### 2. Airflow 설정

#### 2.1 환경 변수 설정
`.env.watsonx.example`을 `.env`로 복사하고 값 입력:

```bash
cp .env.watsonx.example .env
```

```ini
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_ENDPOINT=https://api.dataplatform.cloud.ibm.com
WATSONX_PROJECT_ID=your_project_id
WATSONX_NOTEBOOK_ASSET_ID=your_notebook_asset_id
```

#### 2.2 Airflow 실행
```bash
# Docker Compose로 Airflow 시작
docker-compose -f docker-compose.airflow.yml up -d

# 웹 UI 접속
# http://localhost:8080
# 기본 계정: airflow / airflow
```

#### 2.3 DAG 활성화
1. Airflow 웹 UI에서 `watsonx_notebook_job_pipeline` DAG 찾기
2. 토글 스위치를 켜서 활성화
3. **Trigger DAG** 버튼으로 수동 실행 또는 스케줄 대기

## watsonx Notebook Job API 구조

### API 엔드포인트

#### 1. Job 생성 및 실행
```
POST https://api.dataplatform.cloud.ibm.com/v2/jobs
```

**요청 헤더:**
```json
{
  "Authorization": "Bearer {IAM_TOKEN}",
  "Content-Type": "application/json"
}
```

**요청 본문:**
```json
{
  "project_id": "your_project_id",
  "asset_ref": "notebook_asset_id",
  "configuration": {
    "env_variables": {
      "PIPELINE_RUN_ID": "airflow_run_123",
      "EXECUTION_DATE": "2025-01-01"
    }
  }
}
```

**응답:**
```json
{
  "metadata": {
    "asset_id": "job_run_id_xyz"
  }
}
```

#### 2. Job 상태 확인
```
GET https://api.dataplatform.cloud.ibm.com/v2/jobs/{job_run_id}?project_id={project_id}
```

**응답:**
```json
{
  "entity": {
    "job_run": {
      "state": "completed",  // completed, failed, running, queued
      "started_at": "2025-01-01T10:00:00Z",
      "completed_at": "2025-01-01T10:05:00Z"
    }
  }
}
```

#### 3. Job 결과 조회
```
GET https://api.dataplatform.cloud.ibm.com/v2/jobs/{job_run_id}/runs?project_id={project_id}
```

## Airflow DAG 구조

### Task 흐름
```
prepare_payload
    ↓
get_iam_token
    ↓
create_job (Notebook Job 생성 및 실행)
    ↓
check_job_status (완료될 때까지 폴링)
    ↓
get_job_results (결과 조회)
```

### Task 설명

#### 1. prepare_payload
- Notebook Job 실행에 필요한 페이로드 준비
- 환경 변수 설정 (PIPELINE_RUN_ID, EXECUTION_DATE 등)
- XCom에 데이터 저장

#### 2. get_iam_token
- IBM Cloud API 키로 IAM 토큰 획득
- 토큰은 1시간 유효
- XCom에 토큰 저장

#### 3. create_job
- watsonx Notebook Job API 호출
- Notebook 실행 시작
- Job Run ID 반환

#### 4. check_job_status
- 30초마다 Job 상태 확인
- 최대 30분 대기
- 상태: queued → starting → running → completed/failed

#### 5. get_job_results
- Job 실행 결과 조회
- 로그 및 출력 확인

## 스케줄링 옵션

### 1. 일일 실행
```python
schedule_interval='@daily'  # 매일 자정
```

### 2. 시간별 실행
```python
schedule_interval='@hourly'  # 매시간
```

### 3. Cron 표현식
```python
schedule_interval='0 9 * * *'  # 매일 오전 9시
```

### 4. 수동 실행만
```python
schedule_interval=None  # 수동 트리거만
```

## 에러 처리

### 재시도 설정
```python
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}
```

### 타임아웃 설정
```python
# check_job_status에서 최대 30분 대기
max_attempts = 60  # 30초 × 60 = 30분
```

### 실패 알림
```python
default_args = {
    'email_on_failure': True,
    'email': ['your-email@example.com'],
}
```

## 모니터링

### Airflow 웹 UI
- **DAG 실행 이력**: http://localhost:8080/dags/watsonx_notebook_job_pipeline/grid
- **Task 로그**: 각 Task 클릭 → Logs 탭
- **XCom 데이터**: Admin → XCom

### watsonx.ai 웹 UI
- **Jobs 탭**: 프로젝트 → Jobs → 실행 이력 확인
- **Notebook 출력**: Job 클릭 → Output 확인

## 장점

### Airflow + Notebook Job 방식
1. **완전 자동화**: 스케줄에 따라 자동 실행
2. **재시도 메커니즘**: 실패 시 자동 재시도
3. **모니터링**: Airflow UI에서 전체 파이프라인 모니터링
4. **의존성 관리**: Task 간 의존성 명확히 정의
5. **확장성**: 여러 Notebook을 순차/병렬 실행 가능

### 기존 수동 방식
1. **간단함**: 설정이 단순
2. **디버깅 용이**: 노트북에서 직접 실행 및 확인
3. **유연성**: 즉시 코드 수정 및 재실행

## 권장 사항

### 개발 단계
- 기존 수동 방식 사용
- 노트북에서 직접 코드 작성 및 테스트

### 운영 단계
- Airflow + Notebook Job 방식 사용
- 스케줄 기반 자동 실행
- 모니터링 및 알림 설정

## 문제 해결

### IAM 토큰 오류
```
Error: 401 Unauthorized
```
**해결**: API 키 확인 및 재발급

### Notebook Asset ID 오류
```
Error: Asset not found
```
**해결**: watsonx.ai에서 Notebook Asset ID 재확인

### Job 타임아웃
```
Error: Job 실행 시간 초과 (30분)
```
**해결**: `max_attempts` 값 증가 또는 Notebook 코드 최적화

### 환경 변수 미전달
```
Error: PIPELINE_RUN_ID not found
```
**해결**: `prepare_payload`에서 환경 변수 설정 확인

## 참고 자료

- [watsonx.ai API 문서](https://cloud.ibm.com/apidocs/watson-data-api)
- [Airflow 공식 문서](https://airflow.apache.org/docs/)
- [IBM Cloud IAM 문서](https://cloud.ibm.com/docs/account?topic=account-iamoverview)
