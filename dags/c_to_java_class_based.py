"""
C to Java 변환 파이프라인 DAG - 클래스 기반 예제

재사용 가능한 클래스 구조로 Task를 정의합니다.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys

sys.path.insert(0, '/opt/airflow/samples')

import ingest
import parse
import extract
import transform
import generate
import validate
import report


class PipelineStepOperator:
    """파이프라인 단계를 실행하는 재사용 가능한 클래스"""
    
    def __init__(self, step_name, step_module, step_number):
        self.step_name = step_name
        self.step_module = step_module
        self.step_number = step_number
    
    def execute(self, **context):
        """단계 실행"""
        print("=" * 60)
        print(f"[단계 {self.step_number}/7] {self.step_name}")
        print("=" * 60)
        
        try:
            result = self.step_module.main()
            context['ti'].xcom_push(
                key=f'{self.step_name.lower()}_result',
                value=result
            )
            print(f"✓ {self.step_name} 완료")
            return result
        except Exception as e:
            print(f"✗ {self.step_name} 실패: {e}")
            raise


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
    'c_to_java_class_based',
    default_args=default_args,
    description='C to Java 변환 파이프라인 (클래스 기반)',
    schedule_interval=None,
    catchup=False,
    tags=['conversion', 'c-to-java', 'class-based'],
)

# 파이프라인 단계 정의
pipeline_steps = [
    ('Ingest', ingest, 1),
    ('Parse', parse, 2),
    ('Extract', extract, 3),
    ('Transform', transform, 4),
    ('Generate', generate, 5),
    ('Validate', validate, 6),
    ('Report', report, 7),
]

# Task 생성
tasks = []
for step_name, step_module, step_number in pipeline_steps:
    operator = PipelineStepOperator(step_name, step_module, step_number)
    
    task = PythonOperator(
        task_id=f'step_{step_number}_{step_name.lower()}',
        python_callable=operator.execute,
        dag=dag,
    )
    tasks.append(task)

# Task 의존성 설정 (순차 실행)
for i in range(len(tasks) - 1):
    tasks[i] >> tasks[i + 1]
