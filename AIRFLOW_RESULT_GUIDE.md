# Airflow 파이프라인 결과 확인 가이드

## 결과를 확인하는 5가지 방법

### 1. 웹 UI - Log 탭 (가장 쉬움)

**단계:**
1. http://localhost:8080 접속
2. DAG 클릭 (예: `result_demo_pipeline`)
3. **Grid View**에서 Task 클릭
4. **Log** 버튼 클릭
5. `print()` 출력 확인

**장점:**
- 실시간 로그 확인
- 에러 메시지 확인
- 실행 과정 추적

**예시:**
```
[2026-01-02 00:31:10] INFO - ============================================================
[2026-01-02 00:31:10] INFO - 처리 결과:
[2026-01-02 00:31:10] INFO - {
[2026-01-02 00:31:10] INFO -   "status": "success",
[2026-01-02 00:31:10] INFO -   "processed_records": 1234
[2026-01-02 00:31:10] INFO - }
```

---

### 2. 웹 UI - XCom 탭 (구조화된 데이터)

**단계:**
1. http://localhost:8080 접속
2. **Admin** → **XCom** 메뉴
3. DAG ID, Task ID로 필터링
4. Value 컬럼에서 JSON 데이터 확인

**장점:**
- 구조화된 데이터 저장
- Task 간 데이터 전달 확인
- JSON 형식으로 저장

**코드 예시:**
```python
def my_task(**context):
    result = {"status": "success", "count": 100}
    
    # XCom에 저장
    context['ti'].xcom_push(key='result', value=result)
    
    # 또는 return (자동으로 XCom에 저장)
    return result

def next_task(**context):
    # XCom에서 가져오기
    result = context['ti'].xcom_pull(
        key='result',
        task_ids='my_task'
    )
    print(f"이전 결과: {result}")
```

**웹 UI에서 확인:**
```
DAG ID: result_demo_pipeline
Task ID: process
Key: result
Value: {"status": "success", "processed_records": 1234, ...}
```

---

### 3. 데이터베이스에 저장

**PostgreSQL 예시:**
```python
from airflow.providers.postgres.hooks.postgres import PostgresHook

def save_result(**context):
    result = context['ti'].xcom_pull(task_ids='process')
    
    # PostgreSQL 연결
    hook = PostgresHook(postgres_conn_id='my_postgres')
    
    # 결과 저장
    hook.run("""
        INSERT INTO pipeline_results 
        (dag_id, run_id, status, records, created_at)
        VALUES (%s, %s, %s, %s, NOW())
    """, parameters=(
        context['dag'].dag_id,
        context['run_id'],
        result['status'],
        result['processed_records']
    ))
```

**확인:**
```sql
SELECT * FROM pipeline_results 
WHERE dag_id = 'result_demo_pipeline'
ORDER BY created_at DESC;
```

---

### 4. 파일로 저장 (S3, GCS, 로컬)

**S3 예시:**
```python
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import json

def save_to_s3(**context):
    result = context['ti'].xcom_pull(task_ids='process')
    
    # S3 Hook
    s3 = S3Hook(aws_conn_id='my_aws')
    
    # JSON 파일로 저장
    filename = f"results/{context['run_id']}.json"
    s3.load_string(
        string_data=json.dumps(result),
        key=filename,
        bucket_name='my-pipeline-results'
    )
    
    print(f"S3에 저장: s3://my-pipeline-results/{filename}")
```

**로컬 파일 예시:**
```python
def save_to_file(**context):
    result = context['ti'].xcom_pull(task_ids='process')
    
    filename = f"/tmp/result_{context['run_id']}.json"
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"파일 저장: {filename}")
```

---

### 5. 외부 시스템에 전송 (Slack, Email)

**Slack 예시:**
```python
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

send_slack = SlackWebhookOperator(
    task_id='send_slack',
    slack_webhook_conn_id='slack_webhook',
    message="""
    파이프라인 실행 완료!
    - DAG: {{ dag.dag_id }}
    - 상태: SUCCESS
    - 레코드: {{ ti.xcom_pull(task_ids='process')['processed_records'] }}
    """,
)
```

**Email 예시:**
```python
from airflow.operators.email import EmailOperator

send_email = EmailOperator(
    task_id='send_email',
    to='team@example.com',
    subject='파이프라인 실행 완료',
    html_content="""
    <h2>실행 결과</h2>
    <p>상태: SUCCESS</p>
    <p>처리 레코드: {{ ti.xcom_pull(task_ids='process')['processed_records'] }}</p>
    """,
)
```

---

## 실전 예시: 전체 결과 파이프라인

### DAG 구조
```
process (데이터 처리)
  ↓
validate (결과 검증)
  ↓
report (보고서 생성)
  ↓
├─ save_db (DB 저장)
├─ send_slack (Slack 알림)
└─ save_file (파일 저장)
```

### 실행 및 확인

#### 1. DAG 실행
```bash
# 웹 UI에서 또는
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow dags trigger result_demo_pipeline
```

#### 2. 로그 확인 (웹 UI)
- `process` Task → Log 탭
- 출력 예시:
```
============================================================
처리 결과:
{
  "status": "success",
  "processed_records": 1234,
  "errors": 0,
  "warnings": 5,
  "execution_time": "2.5 seconds"
}
============================================================
```

#### 3. XCom 확인 (웹 UI)
- Admin → XCom
- Task: `process`, Key: `result`
- Value: JSON 데이터 확인

#### 4. 최종 보고서 확인
- `report` Task → Log 탭
- 전체 보고서 JSON 확인

---

## 결과 확인 Best Practices

### 개발 단계
1. **Log 사용**: `print()` 문으로 디버깅
2. **XCom 사용**: Task 간 데이터 전달 확인

### 프로덕션 단계
1. **데이터베이스**: 영구 저장 및 쿼리
2. **파일 저장**: S3, GCS 등에 백업
3. **알림**: Slack, Email로 실시간 알림
4. **모니터링**: Grafana, Prometheus 연동

---

## 실습: result_demo_pipeline 실행

### 1. DAG 활성화 및 실행
```bash
# 활성화
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow dags unpause result_demo_pipeline

# 실행
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow dags trigger result_demo_pipeline
```

### 2. 웹 UI에서 확인
1. http://localhost:8080 접속
2. `result_demo_pipeline` 클릭
3. Grid View에서 각 Task 클릭
4. Log 탭에서 결과 확인:
   - `process`: 처리 결과
   - `validate`: 검증 결과
   - `report`: 최종 보고서

### 3. XCom 확인
1. Admin → XCom
2. DAG ID: `result_demo_pipeline`
3. 각 Task의 결과 확인

---

## 결과 데이터 구조 예시

### process Task 결과
```json
{
  "status": "success",
  "processed_records": 1234,
  "errors": 0,
  "warnings": 5,
  "execution_time": "2.5 seconds",
  "output_file": "/tmp/result.csv"
}
```

### validate Task 결과
```json
{
  "is_valid": true,
  "quality_score": 95.5,
  "recommendation": "프로덕션 배포 가능"
}
```

### report Task 결과
```json
{
  "title": "파이프라인 실행 보고서",
  "execution_date": "2026-01-02T00:31:08+00:00",
  "dag_id": "result_demo_pipeline",
  "run_id": "manual__2026-01-02T00:31:08+00:00",
  "summary": {
    "total_records": 1234,
    "success_rate": "100%",
    "quality_score": 95.5,
    "status": "SUCCESS"
  },
  "details": {
    "processing": {...},
    "validation": {...}
  }
}
```

---

## 문제 해결

### 로그가 안 보이는 경우
- Task가 실행되었는지 확인 (Grid View에서 초록색)
- Scheduler 로그 확인:
```bash
docker-compose -f docker-compose.airflow.yml logs airflow-scheduler
```

### XCom 데이터가 없는 경우
- Task가 성공했는지 확인
- `xcom_push()` 또는 `return` 사용했는지 확인

### 한글이 깨지는 경우
- `ensure_ascii=False` 사용:
```python
print(json.dumps(result, indent=2, ensure_ascii=False))
```

---

## 요약

**결과 확인 방법:**
1. **Log** - 실시간 출력 확인
2. **XCom** - 구조화된 데이터 확인
3. **Database** - 영구 저장
4. **File** - S3, GCS 등에 저장
5. **Notification** - Slack, Email 알림

**권장 조합:**
- 개발: Log + XCom
- 프로덕션: Database + File + Notification

이제 `result_demo_pipeline`을 실행해서 직접 확인해보세요!
