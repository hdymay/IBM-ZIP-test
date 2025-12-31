"""
C to Java 변환 파이프라인 DAG
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, '/opt/airflow')

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
    'c_to_java_pipeline',
    default_args=default_args,
    description='C 코드를 Java로 변환하는 파이프라인',
    schedule_interval=None,  # 수동 실행
    catchup=False,
    tags=['conversion', 'c-to-java'],
)

def select_files_task(**context):
    """파일 선택 작업"""
    from src.core.file_selector import FileSelector
    
    selector = FileSelector()
    selected_files = selector.select_files()
    
    print(f"선택된 파일: {selected_files}")
    context['ti'].xcom_push(key='selected_files', value=selected_files)
    return selected_files

def build_zip_task(**context):
    """ZIP 파일 생성 작업"""
    from src.core.zip_builder import ZipBuilder
    
    ti = context['ti']
    selected_files = ti.xcom_pull(key='selected_files', task_ids='select_files')
    
    builder = ZipBuilder()
    zip_path = builder.build_zip(selected_files)
    
    print(f"생성된 ZIP: {zip_path}")
    ti.xcom_push(key='zip_path', value=zip_path)
    return zip_path

def execute_samples_task(**context):
    """샘플 실행 작업"""
    from src.core.sample_executor import SampleExecutor
    
    ti = context['ti']
    zip_path = ti.xcom_pull(key='zip_path', task_ids='build_zip')
    
    executor = SampleExecutor()
    results = executor.execute_all_samples(zip_path)
    
    print(f"샘플 실행 결과: {results}")
    ti.xcom_push(key='sample_results', value=results)
    return results

def upload_to_github_task(**context):
    """GitHub 업로드 작업"""
    from src.core.github_uploader import GitHubUploader
    
    ti = context['ti']
    zip_path = ti.xcom_pull(key='zip_path', task_ids='build_zip')
    
    uploader = GitHubUploader()
    result = uploader.upload(zip_path)
    
    print(f"GitHub 업로드 결과: {result}")
    return result

def upload_to_watsonx_task(**context):
    """WatsonX 업로드 작업"""
    from src.core.watsonx_uploader import WatsonXUploader
    
    ti = context['ti']
    zip_path = ti.xcom_pull(key='zip_path', task_ids='build_zip')
    
    uploader = WatsonXUploader()
    result = uploader.upload(zip_path)
    
    print(f"WatsonX 업로드 결과: {result}")
    return result

# Task 정의
select_files = PythonOperator(
    task_id='select_files',
    python_callable=select_files_task,
    dag=dag,
)

build_zip = PythonOperator(
    task_id='build_zip',
    python_callable=build_zip_task,
    dag=dag,
)

execute_samples = PythonOperator(
    task_id='execute_samples',
    python_callable=execute_samples_task,
    dag=dag,
)

upload_github = PythonOperator(
    task_id='upload_github',
    python_callable=upload_to_github_task,
    dag=dag,
)

upload_watsonx = PythonOperator(
    task_id='upload_watsonx',
    python_callable=upload_to_watsonx_task,
    dag=dag,
)

# Task 의존성 설정
select_files >> build_zip >> execute_samples >> [upload_github, upload_watsonx]
