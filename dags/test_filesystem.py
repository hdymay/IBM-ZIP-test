"""
파일시스템 권한 테스트 DAG

회사 Airflow 환경에서 파일 생성, 읽기, 쓰기 권한을 테스트합니다.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import tempfile


def test_temp_dir():
    """임시 디렉토리 쓰기 테스트"""
    print("=" * 50)
    print("임시 디렉토리 쓰기 테스트")
    print("=" * 50)
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('test content')
            temp_path = f.name
        
        print(f"✓ 임시 파일 생성 성공: {temp_path}")
        
        # 파일 읽기 테스트
        with open(temp_path, 'r') as f:
            content = f.read()
            print(f"✓ 파일 읽기 성공: {content}")
        
        # 파일 삭제
        os.remove(temp_path)
        print(f"✓ 파일 삭제 성공")
        
        return True
    except Exception as e:
        print(f"✗ 임시 파일 생성 실패: {e}")
        return False


def test_output_dir():
    """출력 디렉토리 생성 테스트"""
    print("=" * 50)
    print("출력 디렉토리 생성 테스트")
    print("=" * 50)
    
    try:
        output_dir = '/tmp/c_to_java_output'
        os.makedirs(output_dir, exist_ok=True)
        print(f"✓ 디렉토리 생성 성공: {output_dir}")
        
        # 테스트 파일 생성
        test_file = os.path.join(output_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
        print(f"✓ 파일 생성 성공: {test_file}")
        
        # 파일 크기 확인
        file_size = os.path.getsize(test_file)
        print(f"✓ 파일 크기: {file_size} bytes")
        
        # 파일 삭제
        os.remove(test_file)
        print(f"✓ 파일 삭제 성공")
        
        return True
    except Exception as e:
        print(f"✗ 출력 디렉토리 사용 불가: {e}")
        return False


def test_zip_creation():
    """ZIP 파일 생성 테스트"""
    print("=" * 50)
    print("ZIP 파일 생성 테스트")
    print("=" * 50)
    
    try:
        import zipfile
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            zip_path = f.name
        
        # ZIP 파일 생성
        with zipfile.ZipFile(zip_path, 'w') as z:
            z.writestr('test1.txt', 'content 1')
            z.writestr('test2.txt', 'content 2')
            z.writestr('folder/test3.txt', 'content 3')
        
        print(f"✓ ZIP 파일 생성 성공: {zip_path}")
        
        # ZIP 파일 크기 확인
        zip_size = os.path.getsize(zip_path)
        print(f"✓ ZIP 파일 크기: {zip_size} bytes")
        
        # ZIP 파일 내용 확인
        with zipfile.ZipFile(zip_path, 'r') as z:
            file_list = z.namelist()
            print(f"✓ ZIP 파일 내용: {file_list}")
        
        # 파일 삭제
        os.remove(zip_path)
        print(f"✓ ZIP 파일 삭제 성공")
        
        return True
    except Exception as e:
        print(f"✗ ZIP 파일 생성 실패: {e}")
        return False


def test_large_file():
    """대용량 파일 생성 테스트"""
    print("=" * 50)
    print("대용량 파일 생성 테스트 (10MB)")
    print("=" * 50)
    
    try:
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            # 10MB 파일 생성
            data = b'x' * (10 * 1024 * 1024)
            f.write(data)
            large_file_path = f.name
        
        file_size = os.path.getsize(large_file_path)
        print(f"✓ 대용량 파일 생성 성공: {file_size / (1024*1024):.2f} MB")
        
        # 파일 삭제
        os.remove(large_file_path)
        print(f"✓ 파일 삭제 성공")
        
        return True
    except Exception as e:
        print(f"✗ 대용량 파일 생성 실패: {e}")
        return False


def test_disk_space():
    """디스크 공간 확인"""
    print("=" * 50)
    print("디스크 공간 확인")
    print("=" * 50)
    
    try:
        import shutil
        
        # /tmp 디렉토리 공간 확인
        stat = shutil.disk_usage('/tmp')
        
        total_gb = stat.total / (1024**3)
        used_gb = stat.used / (1024**3)
        free_gb = stat.free / (1024**3)
        
        print(f"총 용량: {total_gb:.2f} GB")
        print(f"사용 중: {used_gb:.2f} GB")
        print(f"사용 가능: {free_gb:.2f} GB")
        print(f"사용률: {(used_gb/total_gb)*100:.1f}%")
        
        if free_gb < 1:
            print(f"⚠ 경고: 사용 가능한 공간이 1GB 미만입니다!")
        else:
            print(f"✓ 충분한 디스크 공간 확보")
        
        return True
    except Exception as e:
        print(f"✗ 디스크 공간 확인 실패: {e}")
        return False


def test_permissions():
    """파일 권한 테스트"""
    print("=" * 50)
    print("파일 권한 테스트")
    print("=" * 50)
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('test')
            test_file = f.name
        
        # 파일 권한 확인
        import stat
        file_stat = os.stat(test_file)
        mode = file_stat.st_mode
        
        print(f"파일 권한: {oct(mode)}")
        print(f"읽기 권한: {bool(mode & stat.S_IRUSR)}")
        print(f"쓰기 권한: {bool(mode & stat.S_IWUSR)}")
        print(f"실행 권한: {bool(mode & stat.S_IXUSR)}")
        
        # 파일 소유자 확인
        print(f"UID: {file_stat.st_uid}")
        print(f"GID: {file_stat.st_gid}")
        
        # 현재 사용자 확인
        import pwd
        current_user = pwd.getpwuid(os.getuid()).pw_name
        print(f"현재 사용자: {current_user}")
        
        os.remove(test_file)
        
        return True
    except Exception as e:
        print(f"✗ 권한 테스트 실패: {e}")
        return False


with DAG(
    'test_filesystem',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['test', 'filesystem', 'company'],
    description='회사 Airflow 환경 파일시스템 권한 테스트'
) as dag:
    
    test_temp_task = PythonOperator(
        task_id='test_temp_dir',
        python_callable=test_temp_dir
    )
    
    test_output_task = PythonOperator(
        task_id='test_output_dir',
        python_callable=test_output_dir
    )
    
    test_zip_task = PythonOperator(
        task_id='test_zip_creation',
        python_callable=test_zip_creation
    )
    
    test_large_task = PythonOperator(
        task_id='test_large_file',
        python_callable=test_large_file
    )
    
    test_disk_task = PythonOperator(
        task_id='test_disk_space',
        python_callable=test_disk_space
    )
    
    test_permissions_task = PythonOperator(
        task_id='test_permissions',
        python_callable=test_permissions
    )
    
    # 순차 실행
    [test_temp_task, test_output_task] >> test_zip_task >> test_large_task >> [test_disk_task, test_permissions_task]
