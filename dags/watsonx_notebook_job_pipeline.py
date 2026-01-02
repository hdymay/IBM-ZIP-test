"""
watsonx.ai Notebook Job 기반 Airflow DAG

이 DAG는 watsonx.ai의 Notebook Job API를 사용하여
노트북을 자동으로 실행합니다.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
import json
import os


# 기본 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}


def prepare_notebook_job_payload(**context):
    """
    watsonx Notebook Job 실행을 위한 페이로드 준비
    
    Returns:
        dict: Notebook Job API 요청 페이로드
    """
    # 환경 변수에서 설정 로드
    project_id = os.getenv('WATSONX_PROJECT_ID')
    notebook_asset_id = os.getenv('WATSONX_NOTEBOOK_ASSET_ID')
    
    # Notebook Job 실행 페이로드
    payload = {
        "job_run": {
            "configuration": {
                "env_variables": {
                    "PIPELINE_RUN_ID": context['run_id'],
                    "EXECUTION_DATE": context['ds'],
                }
            }
        }
    }
    
    # XCom에 저장
    context['ti'].xcom_push(key='notebook_job_payload', value=payload)
    context['ti'].xcom_push(key='project_id', value=project_id)
    context['ti'].xcom_push(key='notebook_asset_id', value=notebook_asset_id)
    
    return payload


def get_iam_token(**context):
    """
    IBM Cloud IAM 토큰 획득
    
    Returns:
        str: IAM 액세스 토큰
    """
    import requests
    
    api_key = os.getenv('WATSONX_API_KEY')
    
    response = requests.post(
        'https://iam.cloud.ibm.com/identity/token',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
            'apikey': api_key
        }
    )
    
    if response.status_code == 200:
        token = response.json()['access_token']
        context['ti'].xcom_push(key='iam_token', value=token)
        return token
    else:
        raise Exception(f"IAM 토큰 획득 실패: {response.text}")


def create_notebook_job(**context):
    """
    watsonx Notebook Job 생성 및 실행
    
    Returns:
        str: Job Run ID
    """
    import requests
    
    # XCom에서 데이터 가져오기
    ti = context['ti']
    token = ti.xcom_pull(key='iam_token', task_ids='get_iam_token')
    project_id = ti.xcom_pull(key='project_id', task_ids='prepare_payload')
    notebook_asset_id = ti.xcom_pull(key='notebook_asset_id', task_ids='prepare_payload')
    payload = ti.xcom_pull(key='notebook_job_payload', task_ids='prepare_payload')
    
    # watsonx API 엔드포인트
    endpoint = os.getenv('WATSONX_ENDPOINT', 'https://api.dataplatform.cloud.ibm.com')
    url = f"{endpoint}/v2/jobs"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Job 생성 요청
    job_payload = {
        "project_id": project_id,
        "asset_ref": notebook_asset_id,
        "configuration": payload['job_run']['configuration']
    }
    
    response = requests.post(url, headers=headers, json=job_payload)
    
    if response.status_code in [200, 201]:
        job_run_id = response.json()['metadata']['asset_id']
        ti.xcom_push(key='job_run_id', value=job_run_id)
        print(f"✓ Notebook Job 생성 완료: {job_run_id}")
        return job_run_id
    else:
        raise Exception(f"Notebook Job 생성 실패: {response.text}")


def check_job_status(**context):
    """
    Notebook Job 실행 상태 확인
    
    Returns:
        str: Job 상태 (completed, failed, running)
    """
    import requests
    import time
    
    ti = context['ti']
    token = ti.xcom_pull(key='iam_token', task_ids='get_iam_token')
    job_run_id = ti.xcom_pull(key='job_run_id', task_ids='create_job')
    project_id = ti.xcom_pull(key='project_id', task_ids='prepare_payload')
    
    endpoint = os.getenv('WATSONX_ENDPOINT', 'https://api.dataplatform.cloud.ibm.com')
    url = f"{endpoint}/v2/jobs/{job_run_id}"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    params = {'project_id': project_id}
    
    # 최대 30분 대기 (30초마다 확인)
    max_attempts = 60
    attempt = 0
    
    while attempt < max_attempts:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            status = response.json()['entity']['job_run']['state']
            print(f"Job 상태: {status} (시도 {attempt + 1}/{max_attempts})")
            
            if status == 'completed':
                print("✓ Notebook Job 실행 완료")
                return 'completed'
            elif status == 'failed':
                raise Exception("Notebook Job 실행 실패")
            elif status in ['running', 'queued', 'starting']:
                time.sleep(30)
                attempt += 1
            else:
                raise Exception(f"알 수 없는 상태: {status}")
        else:
            raise Exception(f"상태 확인 실패: {response.text}")
    
    raise Exception("Job 실행 시간 초과 (30분)")


def get_job_results(**context):
    """
    Notebook Job 실행 결과 가져오기
    
    Returns:
        dict: Job 실행 결과
    """
    import requests
    
    ti = context['ti']
    token = ti.xcom_pull(key='iam_token', task_ids='get_iam_token')
    job_run_id = ti.xcom_pull(key='job_run_id', task_ids='create_job')
    project_id = ti.xcom_pull(key='project_id', task_ids='prepare_payload')
    
    endpoint = os.getenv('WATSONX_ENDPOINT', 'https://api.dataplatform.cloud.ibm.com')
    url = f"{endpoint}/v2/jobs/{job_run_id}/runs"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    params = {'project_id': project_id}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        results = response.json()
        print("✓ Job 결과 조회 완료")
        print(json.dumps(results, indent=2))
        return results
    else:
        raise Exception(f"결과 조회 실패: {response.text}")


# DAG 정의
with DAG(
    'watsonx_notebook_job_pipeline',
    default_args=default_args,
    description='watsonx.ai Notebook Job을 실행하는 Airflow DAG',
    schedule_interval='@daily',
    catchup=False,
    tags=['watsonx', 'notebook', 'c-to-java'],
) as dag:
    
    # Task 1: 페이로드 준비
    prepare_payload = PythonOperator(
        task_id='prepare_payload',
        python_callable=prepare_notebook_job_payload,
        provide_context=True,
    )
    
    # Task 2: IAM 토큰 획득
    get_token = PythonOperator(
        task_id='get_iam_token',
        python_callable=get_iam_token,
        provide_context=True,
    )
    
    # Task 3: Notebook Job 생성 및 실행
    create_job = PythonOperator(
        task_id='create_job',
        python_callable=create_notebook_job,
        provide_context=True,
    )
    
    # Task 4: Job 상태 확인 (완료될 때까지 대기)
    check_status = PythonOperator(
        task_id='check_job_status',
        python_callable=check_job_status,
        provide_context=True,
    )
    
    # Task 5: Job 결과 가져오기
    get_results = PythonOperator(
        task_id='get_job_results',
        python_callable=get_job_results,
        provide_context=True,
    )
    
    # Task 의존성 설정
    prepare_payload >> get_token >> create_job >> check_status >> get_results
