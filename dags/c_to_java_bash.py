"""
C to Java 변환 파이프라인 DAG - BashOperator 예제

Python 함수 대신 Bash 명령어로 직접 실행합니다.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'c_to_java_bash',
    default_args=default_args,
    description='C to Java 변환 파이프라인 (Bash 명령어)',
    schedule_interval=None,
    catchup=False,
    tags=['conversion', 'c-to-java', 'bash'],
)

# Bash 명령어로 Python 스크립트 직접 실행
task_1_ingest = BashOperator(
    task_id='step_1_ingest',
    bash_command='cd /opt/airflow/samples && python ingest.py',
    dag=dag,
)

task_2_parse = BashOperator(
    task_id='step_2_parse',
    bash_command='cd /opt/airflow/samples && python parse.py',
    dag=dag,
)

task_3_extract = BashOperator(
    task_id='step_3_extract',
    bash_command='cd /opt/airflow/samples && python extract.py',
    dag=dag,
)

task_4_transform = BashOperator(
    task_id='step_4_transform',
    bash_command='cd /opt/airflow/samples && python transform.py',
    dag=dag,
)

task_5_generate = BashOperator(
    task_id='step_5_generate',
    bash_command='cd /opt/airflow/samples && python generate.py',
    dag=dag,
)

task_6_validate = BashOperator(
    task_id='step_6_validate',
    bash_command='cd /opt/airflow/samples && python validate.py',
    dag=dag,
)

task_7_report = BashOperator(
    task_id='step_7_report',
    bash_command='cd /opt/airflow/samples && python report.py',
    dag=dag,
)

# Task 의존성 설정
task_1_ingest >> task_2_parse >> task_3_extract >> task_4_transform >> task_5_generate >> task_6_validate >> task_7_report
