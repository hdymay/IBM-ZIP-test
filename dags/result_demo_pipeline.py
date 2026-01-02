"""
파이프라인 결과 확인 데모

이 DAG는 결과를 확인하는 다양한 방법을 보여줍니다.
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import json


# ============================================================
# 방법 1: XCom으로 결과 저장 (웹 UI에서 확인 가능)
# ============================================================

def process_data(**context):
    """데이터 처리 및 결과 생성"""
    # 실제 처리 로직
    result = {
        "status": "success",
        "processed_records": 1234,
        "errors": 0,
        "warnings": 5,
        "execution_time": "2.5 seconds",
        "output_file": "/tmp/result.csv"
    }
    
    # 로그에 출력 (웹 UI Log에서 확인)
    print("=" * 60)
    print("처리 결과:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 60)
    
    # XCom에 저장 (웹 UI XCom에서 확인)
    context['ti'].xcom_push(key='result', value=result)
    
    # Return 값도 자동으로 XCom에 저장됨
    return result


def validate_result(**context):
    """결과 검증"""
    # XCom에서 결과 가져오기
    result = context['ti'].xcom_pull(key='result', task_ids='process')
    
    print("=" * 60)
    print("검증 중...")
    print(f"처리된 레코드: {result['processed_records']}")
    print(f"에러: {result['errors']}")
    print(f"경고: {result['warnings']}")
    print("=" * 60)
    
    # 검증 결과
    validation = {
        "is_valid": result['errors'] == 0,
        "quality_score": 95.5,
        "recommendation": "프로덕션 배포 가능"
    }
    
    print("검증 결과:")
    print(json.dumps(validation, indent=2, ensure_ascii=False))
    
    return validation


def generate_report(**context):
    """최종 보고서 생성"""
    # 이전 Task들의 결과 가져오기
    process_result = context['ti'].xcom_pull(key='result', task_ids='process')
    validation_result = context['ti'].xcom_pull(task_ids='validate')
    
    # 보고서 생성
    report = {
        "title": "파이프라인 실행 보고서",
        "execution_date": str(context['execution_date']),
        "dag_id": context['dag'].dag_id,
        "run_id": context['run_id'],
        "summary": {
            "total_records": process_result['processed_records'],
            "success_rate": "100%",
            "quality_score": validation_result['quality_score'],
            "status": "SUCCESS"
        },
        "details": {
            "processing": process_result,
            "validation": validation_result
        }
    }
    
    print("=" * 60)
    print("최종 보고서:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("=" * 60)
    
    # 파일로 저장 (실제로는 S3, 데이터베이스 등에 저장)
    report_file = f"/tmp/report_{context['run_id']}.json"
    print(f"\n보고서 저장 위치: {report_file}")
    
    return report


with DAG(
    'result_demo_pipeline',
    default_args={'start_date': datetime(2025, 1, 1)},
    schedule_interval=None,  # 수동 실행만
    catchup=False,
    tags=['demo', 'result'],
) as dag:
    
    process = PythonOperator(
        task_id='process',
        python_callable=process_data,
    )
    
    validate = PythonOperator(
        task_id='validate',
        python_callable=validate_result,
    )
    
    report = PythonOperator(
        task_id='report',
        python_callable=generate_report,
    )
    
    process >> validate >> report


# ============================================================
# 방법 2: 데이터베이스에 결과 저장
# ============================================================

def save_to_database(**context):
    """결과를 데이터베이스에 저장"""
    result = context['ti'].xcom_pull(task_ids='process')
    
    # 실제로는 PostgreSQL, MySQL 등에 저장
    print("데이터베이스에 저장 중...")
    print(f"INSERT INTO pipeline_results VALUES ({result})")
    
    return {"db_id": 12345, "saved_at": str(datetime.now())}


# ============================================================
# 방법 3: 외부 시스템에 결과 전송
# ============================================================

def send_to_slack(**context):
    """Slack으로 결과 전송"""
    report = context['ti'].xcom_pull(task_ids='report')
    
    # 실제로는 Slack API 호출
    message = f"""
    파이프라인 실행 완료!
    
    - DAG: {context['dag'].dag_id}
    - 상태: SUCCESS
    - 처리 레코드: {report['summary']['total_records']}
    - 품질 점수: {report['summary']['quality_score']}
    """
    
    print("=" * 60)
    print("Slack 메시지:")
    print(message)
    print("=" * 60)
    
    return {"slack_sent": True, "channel": "#data-pipeline"}


# ============================================================
# 방법 4: 파일로 결과 저장
# ============================================================

def save_to_file(**context):
    """결과를 파일로 저장"""
    report = context['ti'].xcom_pull(task_ids='report')
    
    # JSON 파일로 저장
    filename = f"/tmp/pipeline_result_{context['run_id']}.json"
    
    print(f"파일 저장: {filename}")
    print(f"내용: {json.dumps(report, indent=2, ensure_ascii=False)}")
    
    # 실제로는 S3, GCS 등에 업로드
    return {"file_path": filename, "file_size": "2.5 KB"}


# ============================================================
# 전체 통합 DAG
# ============================================================

with DAG(
    'full_result_pipeline',
    default_args={'start_date': datetime(2025, 1, 1)},
    schedule_interval=None,
    catchup=False,
    tags=['demo', 'result', 'full'],
) as dag2:
    
    process = PythonOperator(
        task_id='process',
        python_callable=process_data,
    )
    
    validate = PythonOperator(
        task_id='validate',
        python_callable=validate_result,
    )
    
    report = PythonOperator(
        task_id='report',
        python_callable=generate_report,
    )
    
    # 결과를 여러 곳에 저장 (병렬)
    save_db = PythonOperator(
        task_id='save_db',
        python_callable=save_to_database,
    )
    
    send_slack = PythonOperator(
        task_id='send_slack',
        python_callable=send_to_slack,
    )
    
    save_file = PythonOperator(
        task_id='save_file',
        python_callable=save_to_file,
    )
    
    # 의존성
    process >> validate >> report >> [save_db, send_slack, save_file]
