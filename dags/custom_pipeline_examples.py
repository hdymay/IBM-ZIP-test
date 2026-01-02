"""
Airflow 커스텀 파이프라인 예시 모음

Python 코드로 원하는 대로 파이프라인을 구현할 수 있습니다.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.sensors.filesystem import FileSensor
import random


# ============================================================
# 예시 1: 조건부 분기 (if-else 로직)
# ============================================================

def check_data_quality(**context):
    """데이터 품질 검사"""
    # 실제로는 데이터베이스나 파일을 검사
    data_quality_score = random.randint(0, 100)
    
    print(f"데이터 품질 점수: {data_quality_score}")
    
    # XCom에 저장 (다른 Task에서 사용 가능)
    context['ti'].xcom_push(key='quality_score', value=data_quality_score)
    
    # 조건부 분기
    if data_quality_score >= 80:
        return 'high_quality_process'
    elif data_quality_score >= 50:
        return 'medium_quality_process'
    else:
        return 'low_quality_alert'


def high_quality_process(**context):
    """고품질 데이터 처리"""
    print("고품질 데이터 → 전체 파이프라인 실행")
    # watsonx Notebook Job 실행
    # ML 모델 학습
    # 결과 배포


def medium_quality_process(**context):
    """중품질 데이터 처리"""
    print("중품질 데이터 → 데이터 정제 후 처리")
    # 데이터 정제
    # 간단한 처리만 수행


def low_quality_alert(**context):
    """저품질 데이터 알림"""
    score = context['ti'].xcom_pull(key='quality_score', task_ids='check_quality')
    print(f"저품질 데이터 감지! 점수: {score}")
    # Slack 알림
    # 담당자에게 이메일


with DAG(
    'conditional_pipeline',
    default_args={'start_date': datetime(2025, 1, 1)},
    schedule_interval='@daily',
    catchup=False,
) as dag1:
    
    check = BranchPythonOperator(
        task_id='check_quality',
        python_callable=check_data_quality,
    )
    
    high = PythonOperator(
        task_id='high_quality_process',
        python_callable=high_quality_process,
    )
    
    medium = PythonOperator(
        task_id='medium_quality_process',
        python_callable=medium_quality_process,
    )
    
    low = PythonOperator(
        task_id='low_quality_alert',
        python_callable=low_quality_alert,
    )
    
    # 조건부 분기
    check >> [high, medium, low]


# ============================================================
# 예시 2: 동적 Task 생성 (반복문)
# ============================================================

def process_file(file_name, **context):
    """개별 파일 처리"""
    print(f"파일 처리 중: {file_name}")
    # 실제 처리 로직
    return f"{file_name} 처리 완료"


with DAG(
    'dynamic_tasks_pipeline',
    default_args={'start_date': datetime(2025, 1, 1)},
    schedule_interval='@daily',
    catchup=False,
) as dag2:
    
    # 처리할 파일 목록 (실제로는 S3나 데이터베이스에서 가져옴)
    files = ['file1.csv', 'file2.csv', 'file3.csv', 'file4.csv', 'file5.csv']
    
    # 동적으로 Task 생성
    tasks = []
    for file_name in files:
        task = PythonOperator(
            task_id=f'process_{file_name.replace(".", "_")}',
            python_callable=process_file,
            op_kwargs={'file_name': file_name},
        )
        tasks.append(task)
    
    # 모든 파일 처리 후 실행할 Task
    summary = PythonOperator(
        task_id='summary',
        python_callable=lambda: print("모든 파일 처리 완료!"),
    )
    
    # 병렬 실행 후 summary
    tasks >> summary


# ============================================================
# 예시 3: 재시도 및 에러 처리 커스터마이징
# ============================================================

def unstable_task(**context):
    """불안정한 작업 (가끔 실패)"""
    if random.random() < 0.3:  # 30% 확률로 실패
        raise Exception("일시적 오류 발생!")
    print("작업 성공!")


def on_failure_callback(context):
    """실패 시 실행되는 콜백"""
    task_instance = context['task_instance']
    print(f"Task 실패: {task_instance.task_id}")
    print(f"시도 횟수: {task_instance.try_number}")
    # Slack 알림, 이메일 전송 등


def on_retry_callback(context):
    """재시도 시 실행되는 콜백"""
    task_instance = context['task_instance']
    print(f"Task 재시도: {task_instance.task_id}")
    print(f"재시도 횟수: {task_instance.try_number}")


def on_success_callback(context):
    """성공 시 실행되는 콜백"""
    print("Task 성공!")


with DAG(
    'error_handling_pipeline',
    default_args={
        'start_date': datetime(2025, 1, 1),
        'retries': 3,  # 최대 3회 재시도
        'retry_delay': timedelta(minutes=5),  # 5분 후 재시도
        'retry_exponential_backoff': True,  # 지수 백오프
        'max_retry_delay': timedelta(minutes=30),  # 최대 30분
    },
    schedule_interval='@daily',
    catchup=False,
) as dag3:
    
    task = PythonOperator(
        task_id='unstable_task',
        python_callable=unstable_task,
        on_failure_callback=on_failure_callback,
        on_retry_callback=on_retry_callback,
        on_success_callback=on_success_callback,
    )


# ============================================================
# 예시 4: 복잡한 의존성 (다이아몬드 패턴)
# ============================================================

with DAG(
    'complex_dependency_pipeline',
    default_args={'start_date': datetime(2025, 1, 1)},
    schedule_interval='@daily',
    catchup=False,
) as dag4:
    
    start = PythonOperator(
        task_id='start',
        python_callable=lambda: print("파이프라인 시작"),
    )
    
    # 병렬 처리
    process_a = PythonOperator(
        task_id='process_a',
        python_callable=lambda: print("처리 A"),
    )
    
    process_b = PythonOperator(
        task_id='process_b',
        python_callable=lambda: print("처리 B"),
    )
    
    process_c = PythonOperator(
        task_id='process_c',
        python_callable=lambda: print("처리 C"),
    )
    
    # 병합
    merge = PythonOperator(
        task_id='merge',
        python_callable=lambda: print("결과 병합"),
    )
    
    end = PythonOperator(
        task_id='end',
        python_callable=lambda: print("파이프라인 완료"),
    )
    
    # 다이아몬드 패턴
    start >> [process_a, process_b, process_c] >> merge >> end


# ============================================================
# 예시 5: 외부 시스템 연동 (API, 데이터베이스)
# ============================================================

def fetch_from_api(**context):
    """외부 API에서 데이터 가져오기"""
    import requests
    
    response = requests.get('https://api.example.com/data')
    data = response.json()
    
    # XCom에 저장
    context['ti'].xcom_push(key='api_data', value=data)
    return data


def save_to_database(**context):
    """데이터베이스에 저장"""
    # XCom에서 데이터 가져오기
    data = context['ti'].xcom_pull(key='api_data', task_ids='fetch_api')
    
    # 데이터베이스 연결 (실제로는 Connection 사용)
    print(f"데이터베이스에 저장: {len(data)} 레코드")


with DAG(
    'external_integration_pipeline',
    default_args={'start_date': datetime(2025, 1, 1)},
    schedule_interval='@hourly',
    catchup=False,
) as dag5:
    
    fetch = PythonOperator(
        task_id='fetch_api',
        python_callable=fetch_from_api,
    )
    
    save = PythonOperator(
        task_id='save_db',
        python_callable=save_to_database,
    )
    
    # HTTP Operator 사용 (더 간단)
    call_webhook = SimpleHttpOperator(
        task_id='call_webhook',
        http_conn_id='my_webhook',
        endpoint='/notify',
        method='POST',
        data='{"status": "completed"}',
        headers={'Content-Type': 'application/json'},
    )
    
    fetch >> save >> call_webhook


# ============================================================
# 예시 6: 센서를 사용한 대기 (파일 생성 대기)
# ============================================================

with DAG(
    'sensor_pipeline',
    default_args={'start_date': datetime(2025, 1, 1)},
    schedule_interval='@daily',
    catchup=False,
) as dag6:
    
    # 파일이 생성될 때까지 대기
    wait_for_file = FileSensor(
        task_id='wait_for_file',
        filepath='/tmp/data.csv',
        poke_interval=30,  # 30초마다 확인
        timeout=3600,  # 최대 1시간 대기
    )
    
    process = PythonOperator(
        task_id='process_file',
        python_callable=lambda: print("파일 처리 시작"),
    )
    
    wait_for_file >> process


# ============================================================
# 예시 7: 커스텀 Operator 생성
# ============================================================

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class WatsonxNotebookOperator(BaseOperator):
    """커스텀 Operator: watsonx Notebook 실행"""
    
    @apply_defaults
    def __init__(
        self,
        notebook_id: str,
        project_id: str,
        api_key: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.notebook_id = notebook_id
        self.project_id = project_id
        self.api_key = api_key
    
    def execute(self, context):
        """Notebook 실행"""
        print(f"watsonx Notebook 실행: {self.notebook_id}")
        
        # 1. IAM 토큰 획득
        # 2. Notebook Job 생성
        # 3. 상태 확인
        # 4. 결과 반환
        
        return {"status": "completed", "notebook_id": self.notebook_id}


with DAG(
    'custom_operator_pipeline',
    default_args={'start_date': datetime(2025, 1, 1)},
    schedule_interval='@daily',
    catchup=False,
) as dag7:
    
    # 커스텀 Operator 사용
    run_notebook = WatsonxNotebookOperator(
        task_id='run_notebook',
        notebook_id='abc123',
        project_id='project123',
        api_key='{{ var.value.watsonx_api_key }}',  # Airflow Variable 사용
    )


# ============================================================
# 예시 8: 데이터 기반 동적 파이프라인
# ============================================================

def get_tasks_from_database(**context):
    """데이터베이스에서 실행할 작업 목록 가져오기"""
    # 실제로는 데이터베이스 쿼리
    tasks = [
        {'id': 1, 'type': 'transform', 'priority': 'high'},
        {'id': 2, 'type': 'validate', 'priority': 'medium'},
        {'id': 3, 'type': 'export', 'priority': 'low'},
    ]
    
    # XCom에 저장
    context['ti'].xcom_push(key='task_list', value=tasks)
    return tasks


def execute_task(task_info, **context):
    """개별 작업 실행"""
    print(f"작업 실행: {task_info}")
    # 작업 타입에 따라 다른 처리
    if task_info['type'] == 'transform':
        print("데이터 변환 중...")
    elif task_info['type'] == 'validate':
        print("데이터 검증 중...")
    elif task_info['type'] == 'export':
        print("데이터 내보내기 중...")


with DAG(
    'data_driven_pipeline',
    default_args={'start_date': datetime(2025, 1, 1)},
    schedule_interval='@daily',
    catchup=False,
) as dag8:
    
    get_tasks = PythonOperator(
        task_id='get_tasks',
        python_callable=get_tasks_from_database,
    )
    
    # 실제로는 TaskFlow API나 Dynamic Task Mapping 사용
    # (Airflow 2.3+)


# ============================================================
# 예시 9: 시간 기반 조건부 실행
# ============================================================

def check_time_window(**context):
    """시간대에 따라 다른 처리"""
    execution_date = context['execution_date']
    hour = execution_date.hour
    
    if 0 <= hour < 6:
        return 'night_process'
    elif 6 <= hour < 18:
        return 'day_process'
    else:
        return 'evening_process'


with DAG(
    'time_based_pipeline',
    default_args={'start_date': datetime(2025, 1, 1)},
    schedule_interval='@hourly',
    catchup=False,
) as dag9:
    
    check_time = BranchPythonOperator(
        task_id='check_time',
        python_callable=check_time_window,
    )
    
    night = PythonOperator(
        task_id='night_process',
        python_callable=lambda: print("야간 처리 (대용량 배치)"),
    )
    
    day = PythonOperator(
        task_id='day_process',
        python_callable=lambda: print("주간 처리 (실시간 처리)"),
    )
    
    evening = PythonOperator(
        task_id='evening_process',
        python_callable=lambda: print("저녁 처리 (보고서 생성)"),
    )
    
    check_time >> [night, day, evening]


# ============================================================
# 예시 10: 전체 통합 파이프라인
# ============================================================

with DAG(
    'full_integration_pipeline',
    default_args={
        'start_date': datetime(2025, 1, 1),
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
    schedule_interval='0 9 * * *',  # 매일 오전 9시
    catchup=False,
    tags=['production', 'c-to-java'],
) as dag10:
    
    # 1. 데이터 수집
    collect = PythonOperator(
        task_id='collect_data',
        python_callable=lambda: print("S3에서 데이터 수집"),
    )
    
    # 2. 데이터 검증
    validate = PythonOperator(
        task_id='validate_data',
        python_callable=lambda: print("데이터 품질 검증"),
    )
    
    # 3. 조건부 분기
    def decide_process(**context):
        # 데이터 크기 확인
        data_size = random.randint(100, 10000)
        if data_size > 5000:
            return 'large_data_process'
        else:
            return 'small_data_process'
    
    branch = BranchPythonOperator(
        task_id='branch',
        python_callable=decide_process,
    )
    
    # 4a. 대용량 처리
    large = PythonOperator(
        task_id='large_data_process',
        python_callable=lambda: print("대용량 데이터 처리 (분산 처리)"),
    )
    
    # 4b. 소용량 처리
    small = PythonOperator(
        task_id='small_data_process',
        python_callable=lambda: print("소용량 데이터 처리 (단일 처리)"),
    )
    
    # 5. watsonx Notebook Job 실행 (여기서는 시뮬레이션)
    notebook = PythonOperator(
        task_id='run_watsonx_notebook',
        python_callable=lambda: print("watsonx Notebook Job 실행"),
        trigger_rule='none_failed',  # 이전 Task 중 하나라도 성공하면 실행
    )
    
    # 6. 결과 저장
    save = PythonOperator(
        task_id='save_results',
        python_callable=lambda: print("결과를 데이터베이스에 저장"),
    )
    
    # 7. 알림
    notify = PythonOperator(
        task_id='send_notification',
        python_callable=lambda: print("Slack 알림 전송"),
    )
    
    # 의존성 정의
    collect >> validate >> branch
    branch >> [large, small]
    [large, small] >> notebook >> save >> notify
