"""
C to Java 변환 파이프라인 DAG - TaskFlow API 예제

Airflow 2.0+ TaskFlow API를 사용한 최신 방식입니다.
데코레이터를 사용하여 더 간결하게 작성할 수 있습니다.
"""
from datetime import datetime, timedelta
from airflow.decorators import dag, task
import sys

sys.path.insert(0, '/opt/airflow/samples')

import ingest
import parse
import extract
import transform
import generate
import validate
import report


@dag(
    dag_id='c_to_java_taskflow',
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='C to Java 변환 파이프라인 (TaskFlow API)',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['conversion', 'c-to-java', 'taskflow'],
)
def c_to_java_pipeline():
    """TaskFlow API를 사용한 파이프라인"""
    
    @task(task_id='step_1_ingest')
    def run_ingest():
        """1단계: 데이터 수집"""
        print("=" * 60)
        print("[단계 1/7] 데이터 수집 (Ingest)")
        print("=" * 60)
        result = ingest.main()
        return result
    
    @task(task_id='step_2_parse')
    def run_parse(ingest_result):
        """2단계: 파싱"""
        print("=" * 60)
        print("[단계 2/7] 파싱 (Parse)")
        print(f"이전 단계 결과: {ingest_result}")
        print("=" * 60)
        result = parse.main()
        return result
    
    @task(task_id='step_3_extract')
    def run_extract(parse_result):
        """3단계: 추출"""
        print("=" * 60)
        print("[단계 3/7] 추출 (Extract)")
        print("=" * 60)
        result = extract.main()
        return result
    
    @task(task_id='step_4_transform')
    def run_transform(extract_result):
        """4단계: 변환"""
        print("=" * 60)
        print("[단계 4/7] 변환 (Transform)")
        print("=" * 60)
        result = transform.main()
        return result
    
    @task(task_id='step_5_generate')
    def run_generate(transform_result):
        """5단계: 생성"""
        print("=" * 60)
        print("[단계 5/7] 생성 (Generate)")
        print("=" * 60)
        result = generate.main()
        return result
    
    @task(task_id='step_6_validate')
    def run_validate(generate_result):
        """6단계: 검증"""
        print("=" * 60)
        print("[단계 6/7] 검증 (Validate)")
        print("=" * 60)
        result = validate.main()
        return result
    
    @task(task_id='step_7_report')
    def run_report(validate_result):
        """7단계: 보고서 생성"""
        print("=" * 60)
        print("[단계 7/7] 보고서 생성 (Report)")
        print("=" * 60)
        result = report.main()
        return result
    
    # Task 의존성 자동 설정 (함수 호출 순서로)
    ingest_result = run_ingest()
    parse_result = run_parse(ingest_result)
    extract_result = run_extract(parse_result)
    transform_result = run_transform(extract_result)
    generate_result = run_generate(transform_result)
    validate_result = run_validate(generate_result)
    run_report(validate_result)


# DAG 인스턴스 생성
dag_instance = c_to_java_pipeline()
