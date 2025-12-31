"""
C to Java 변환 파이프라인 DAG - Samples 폴더 실행

samples/ 폴더의 각 단계를 Airflow Task로 실행합니다.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# samples 폴더를 Python 경로에 추가
sys.path.insert(0, '/opt/airflow/samples')

# 각 단계 모듈 import
import ingest
import parse
import extract
import transform
import generate
import validate
import report

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
    'c_to_java_samples_pipeline',
    default_args=default_args,
    description='C to Java 변환 파이프라인 (samples 폴더 실행)',
    schedule_interval=None,  # 수동 실행
    catchup=False,
    tags=['conversion', 'c-to-java', 'samples'],
)

def run_ingest(**context):
    """1단계: 데이터 수집"""
    print("=" * 60)
    print("[단계 1/7] 데이터 수집 (Ingest)")
    print("=" * 60)
    result = ingest.main()
    context['ti'].xcom_push(key='ingest_result', value=result)
    return result

def run_parse(**context):
    """2단계: 파싱"""
    print("=" * 60)
    print("[단계 2/7] 파싱 (Parse)")
    print("=" * 60)
    result = parse.main()
    context['ti'].xcom_push(key='parse_result', value=result)
    return result

def run_extract(**context):
    """3단계: 추출"""
    print("=" * 60)
    print("[단계 3/7] 추출 (Extract)")
    print("=" * 60)
    result = extract.main()
    context['ti'].xcom_push(key='extract_result', value=result)
    return result

def run_transform(**context):
    """4단계: 변환"""
    print("=" * 60)
    print("[단계 4/7] 변환 (Transform)")
    print("=" * 60)
    result = transform.main()
    context['ti'].xcom_push(key='transform_result', value=result)
    return result

def run_generate(**context):
    """5단계: 생성"""
    print("=" * 60)
    print("[단계 5/7] 생성 (Generate)")
    print("=" * 60)
    result = generate.main()
    context['ti'].xcom_push(key='generate_result', value=result)
    return result

def run_validate(**context):
    """6단계: 검증"""
    print("=" * 60)
    print("[단계 6/7] 검증 (Validate)")
    print("=" * 60)
    result = validate.main()
    context['ti'].xcom_push(key='validate_result', value=result)
    return result

def run_report(**context):
    """7단계: 보고서 생성"""
    print("=" * 60)
    print("[단계 7/7] 보고서 생성 (Report)")
    print("=" * 60)
    
    # 이전 단계들의 결과 수집
    ti = context['ti']
    results = {
        'ingest': ti.xcom_pull(key='ingest_result', task_ids='step_1_ingest'),
        'parse': ti.xcom_pull(key='parse_result', task_ids='step_2_parse'),
        'extract': ti.xcom_pull(key='extract_result', task_ids='step_3_extract'),
        'transform': ti.xcom_pull(key='transform_result', task_ids='step_4_transform'),
        'generate': ti.xcom_pull(key='generate_result', task_ids='step_5_generate'),
        'validate': ti.xcom_pull(key='validate_result', task_ids='step_6_validate'),
    }
    
    print("\n전체 파이프라인 결과:")
    for step, result in results.items():
        status = "✓ 성공" if result == 0 else "✗ 실패"
        print(f"  {step}: {status}")
    
    result = report.main()
    context['ti'].xcom_push(key='report_result', value=result)
    return result

# Task 정의
task_1_ingest = PythonOperator(
    task_id='step_1_ingest',
    python_callable=run_ingest,
    dag=dag,
)

task_2_parse = PythonOperator(
    task_id='step_2_parse',
    python_callable=run_parse,
    dag=dag,
)

task_3_extract = PythonOperator(
    task_id='step_3_extract',
    python_callable=run_extract,
    dag=dag,
)

task_4_transform = PythonOperator(
    task_id='step_4_transform',
    python_callable=run_transform,
    dag=dag,
)

task_5_generate = PythonOperator(
    task_id='step_5_generate',
    python_callable=run_generate,
    dag=dag,
)

task_6_validate = PythonOperator(
    task_id='step_6_validate',
    python_callable=run_validate,
    dag=dag,
)

task_7_report = PythonOperator(
    task_id='step_7_report',
    python_callable=run_report,
    dag=dag,
)

# Task 의존성 설정 (순차 실행)
task_1_ingest >> task_2_parse >> task_3_extract >> task_4_transform >> task_5_generate >> task_6_validate >> task_7_report
