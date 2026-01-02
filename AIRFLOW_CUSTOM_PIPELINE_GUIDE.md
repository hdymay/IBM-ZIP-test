# Airflow 커스텀 파이프라인 가이드

## 핵심 개념: "Configuration as Code"

Airflow는 **Python 코드로 모든 것을 정의**합니다.

```python
# 이것이 Airflow DAG입니다!
from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG('my_pipeline', ...) as dag:
    task1 = PythonOperator(...)
    task2 = PythonOperator(...)
    
    task1 >> task2  # task1 실행 후 task2 실행
```

---

## 1. 기본 구조

### 최소 DAG
```python
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def my_function():
    print("Hello Airflow!")

with DAG(
    'my_first_dag',
    start_date=datetime(2025, 1, 1),
    schedule_interval='@daily',
) as dag:
    
    task = PythonOperator(
        task_id='hello',
        python_callable=my_function,
    )
```

---

## 2. 조건부 실행 (if-else)

### Python의 if-else를 그대로 사용
```python
from airflow.operators.python import BranchPythonOperator

def decide():
    if condition:
        return 'task_a'  # task_a 실행
    else:
        return 'task_b'  # task_b 실행

branch = BranchPythonOperator(
    task_id='branch',
    python_callable=decide,
)

task_a = PythonOperator(task_id='task_a', ...)
task_b = PythonOperator(task_id='task_b', ...)

branch >> [task_a, task_b]
```

---

## 3. 반복문 (for loop)

### Python의 for문으로 Task 생성
```python
files = ['file1.csv', 'file2.csv', 'file3.csv']

tasks = []
for file in files:
    task = PythonOperator(
        task_id=f'process_{file}',
        python_callable=process_file,
        op_kwargs={'filename': file},
    )
    tasks.append(task)

# 모든 Task 병렬 실행
start >> tasks >> end
```

---

## 4. 데이터 전달 (XCom)

### Task 간 데이터 공유
```python
def task1(**context):
    result = {"data": [1, 2, 3]}
    # 데이터 저장
    context['ti'].xcom_push(key='my_data', value=result)
    return result

def task2(**context):
    # 데이터 가져오기
    data = context['ti'].xcom_pull(
        key='my_data',
        task_ids='task1'
    )
    print(f"받은 데이터: {data}")

task1 >> task2
```

---

## 5. 병렬 실행

### 여러 Task 동시 실행
```python
start = PythonOperator(...)

# 병렬 실행
task_a = PythonOperator(...)
task_b = PythonOperator(...)
task_c = PythonOperator(...)

end = PythonOperator(...)

# start 후 a, b, c 병렬 실행, 모두 완료 후 end
start >> [task_a, task_b, task_c] >> end
```

---

## 6. 에러 처리

### 재시도 설정
```python
task = PythonOperator(
    task_id='my_task',
    python_callable=my_function,
    retries=3,  # 3회 재시도
    retry_delay=timedelta(minutes=5),  # 5분 후 재시도
)
```

### 콜백 함수
```python
def on_failure(context):
    print("Task 실패!")
    # Slack 알림, 이메일 등

task = PythonOperator(
    task_id='my_task',
    python_callable=my_function,
    on_failure_callback=on_failure,
)
```

---

## 7. 외부 시스템 연동

### API 호출
```python
from airflow.providers.http.operators.http import SimpleHttpOperator

call_api = SimpleHttpOperator(
    task_id='call_api',
    http_conn_id='my_api',
    endpoint='/data',
    method='POST',
    data='{"key": "value"}',
)
```

### 데이터베이스
```python
from airflow.providers.postgres.operators.postgres import PostgresOperator

query = PostgresOperator(
    task_id='query_db',
    postgres_conn_id='my_db',
    sql='SELECT * FROM users WHERE active = true',
)
```

---

## 8. 센서 (대기)

### 파일 생성 대기
```python
from airflow.sensors.filesystem import FileSensor

wait = FileSensor(
    task_id='wait_for_file',
    filepath='/tmp/data.csv',
    poke_interval=30,  # 30초마다 확인
    timeout=3600,  # 최대 1시간
)
```

---

## 9. 동적 파이프라인

### 데이터베이스에서 Task 목록 가져오기
```python
def get_tasks():
    # 데이터베이스 쿼리
    return [
        {'id': 1, 'type': 'transform'},
        {'id': 2, 'type': 'validate'},
    ]

def create_tasks():
    tasks = get_tasks()
    
    for task_info in tasks:
        task = PythonOperator(
            task_id=f"task_{task_info['id']}",
            python_callable=process_task,
            op_kwargs={'task_info': task_info},
        )
```

---

## 10. 커스텀 Operator

### 재사용 가능한 Operator 생성
```python
from airflow.models import BaseOperator

class MyCustomOperator(BaseOperator):
    def __init__(self, my_param, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_param = my_param
    
    def execute(self, context):
        print(f"실행: {self.my_param}")
        # 실제 로직
        return "완료"

# 사용
task = MyCustomOperator(
    task_id='custom_task',
    my_param='value',
)
```

---

## 실전 예시: 복잡한 파이프라인

```python
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from datetime import datetime, timedelta

def collect_data(**context):
    """S3에서 데이터 수집"""
    data = fetch_from_s3()
    context['ti'].xcom_push(key='data', value=data)
    return len(data)

def validate_data(**context):
    """데이터 검증"""
    data = context['ti'].xcom_pull(key='data', task_ids='collect')
    is_valid = check_quality(data)
    context['ti'].xcom_push(key='is_valid', value=is_valid)
    return is_valid

def decide_process(**context):
    """처리 방법 결정"""
    is_valid = context['ti'].xcom_pull(key='is_valid', task_ids='validate')
    data_size = context['ti'].xcom_pull(task_ids='collect')
    
    if not is_valid:
        return 'alert'
    elif data_size > 10000:
        return 'large_process'
    else:
        return 'small_process'

def large_process():
    """대용량 처리"""
    print("분산 처리 시작")
    # Spark, Dask 등 사용

def small_process():
    """소용량 처리"""
    print("단일 처리 시작")
    # Pandas 등 사용

def alert():
    """알림"""
    send_slack_message("데이터 품질 문제!")

def run_watsonx_notebook(**context):
    """watsonx Notebook Job 실행"""
    # IAM 토큰 획득
    # Notebook Job 생성
    # 상태 확인
    pass

def save_results(**context):
    """결과 저장"""
    # PostgreSQL에 저장
    pass

with DAG(
    'production_pipeline',
    default_args={
        'start_date': datetime(2025, 1, 1),
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
    schedule_interval='0 9 * * *',  # 매일 오전 9시
    catchup=False,
) as dag:
    
    # Task 정의
    collect = PythonOperator(
        task_id='collect',
        python_callable=collect_data,
    )
    
    validate = PythonOperator(
        task_id='validate',
        python_callable=validate_data,
    )
    
    decide = BranchPythonOperator(
        task_id='decide',
        python_callable=decide_process,
    )
    
    large = PythonOperator(
        task_id='large_process',
        python_callable=large_process,
    )
    
    small = PythonOperator(
        task_id='small_process',
        python_callable=small_process,
    )
    
    alert_task = PythonOperator(
        task_id='alert',
        python_callable=alert,
    )
    
    notebook = PythonOperator(
        task_id='notebook',
        python_callable=run_watsonx_notebook,
        trigger_rule='none_failed',  # 이전 중 하나라도 성공하면 실행
    )
    
    save = PythonOperator(
        task_id='save',
        python_callable=save_results,
    )
    
    # 의존성 정의
    collect >> validate >> decide
    decide >> [large, small, alert_task]
    [large, small] >> notebook >> save
```

---

## 핵심 정리

### 1. Python 코드로 모든 것을 정의
```python
# if-else
if condition:
    return 'task_a'
else:
    return 'task_b'

# for loop
for item in items:
    create_task(item)

# 함수 호출
result = my_function()
```

### 2. Task 의존성은 >> 연산자
```python
task1 >> task2  # 순차
task1 >> [task2, task3]  # 병렬
[task1, task2] >> task3  # 병합
```

### 3. 데이터 전달은 XCom
```python
# 저장
context['ti'].xcom_push(key='data', value=data)

# 가져오기
data = context['ti'].xcom_pull(key='data', task_ids='task1')
```

### 4. 에러 처리는 콜백
```python
task = PythonOperator(
    ...,
    retries=3,
    on_failure_callback=send_alert,
)
```

---

## 장점

1. **완전한 유연성**: Python으로 원하는 대로 구현
2. **버전 관리**: Git으로 DAG 코드 관리
3. **테스트 가능**: 단위 테스트 작성 가능
4. **재사용성**: 함수, 클래스로 재사용
5. **확장성**: 커스텀 Operator, Hook 생성

---

## 결론

Airflow는 **"코드로 파이프라인을 정의"**합니다.

- UI 클릭이 아닌 **Python 코드 작성**
- 드래그 앤 드롭이 아닌 **코드 편집**
- 설정 파일이 아닌 **프로그래밍**

이것이 Airflow의 핵심 철학입니다!
