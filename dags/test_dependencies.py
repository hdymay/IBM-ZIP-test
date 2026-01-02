"""
의존성 패키지 테스트 DAG

회사 Airflow 환경에 필요한 Python 패키지가 설치되어 있는지 확인합니다.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def check_package(package_name, import_name=None):
    """패키지 설치 여부 및 버전 확인"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✓ {package_name}: {version}")
        return True, version
    except ImportError as e:
        print(f"✗ {package_name}: NOT INSTALLED - {e}")
        return False, None


def test_requests():
    """requests 패키지 테스트"""
    print("=" * 50)
    print("requests 패키지 테스트")
    print("=" * 50)
    
    success, version = check_package('requests')
    
    if success:
        # 간단한 기능 테스트
        try:
            import requests
            print(f"  - Session 생성: OK")
            session = requests.Session()
            print(f"  - 기본 기능: OK")
        except Exception as e:
            print(f"  - 기능 테스트 실패: {e}")
    
    return success


def test_dotenv():
    """python-dotenv 패키지 테스트"""
    print("=" * 50)
    print("python-dotenv 패키지 테스트")
    print("=" * 50)
    
    success, version = check_package('python-dotenv', 'dotenv')
    
    if success:
        # 간단한 기능 테스트
        try:
            from dotenv import load_dotenv
            print(f"  - load_dotenv 함수: OK")
        except Exception as e:
            print(f"  - 기능 테스트 실패: {e}")
    
    return success


def test_cryptography():
    """cryptography 패키지 테스트"""
    print("=" * 50)
    print("cryptography 패키지 테스트")
    print("=" * 50)
    
    success, version = check_package('cryptography')
    
    if success:
        # 간단한 기능 테스트
        try:
            from cryptography.fernet import Fernet
            key = Fernet.generate_key()
            print(f"  - Fernet 암호화: OK")
        except Exception as e:
            print(f"  - 기능 테스트 실패: {e}")
    
    return success


def test_git():
    """Git CLI 설치 확인"""
    print("=" * 50)
    print("Git CLI 설치 확인")
    print("=" * 50)
    
    import subprocess
    try:
        result = subprocess.run(
            ['git', '--version'], 
            capture_output=True, 
            text=True,
            timeout=5
        )
        print(f"✓ Git: {result.stdout.strip()}")
        
        # Git 설정 확인
        try:
            config_result = subprocess.run(
                ['git', 'config', '--list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"  - Git 설정: OK")
        except Exception as e:
            print(f"  - Git 설정 확인 실패: {e}")
        
        return True
    except FileNotFoundError:
        print(f"✗ Git: NOT INSTALLED (명령어를 찾을 수 없음)")
        return False
    except Exception as e:
        print(f"✗ Git: ERROR - {e}")
        return False


def test_python_version():
    """Python 버전 확인"""
    print("=" * 50)
    print("Python 환경 정보")
    print("=" * 50)
    
    import sys
    import platform
    
    print(f"Python 버전: {sys.version}")
    print(f"Python 경로: {sys.executable}")
    print(f"플랫폼: {platform.platform()}")
    print(f"아키텍처: {platform.machine()}")
    
    return True


def test_all_packages():
    """모든 패키지 종합 테스트"""
    print("=" * 50)
    print("의존성 패키지 종합 테스트")
    print("=" * 50)
    
    packages = [
        ('requests', 'requests'),
        ('python-dotenv', 'dotenv'),
        ('cryptography', 'cryptography'),
    ]
    
    results = []
    for package_name, import_name in packages:
        success, version = check_package(package_name, import_name)
        results.append((package_name, success, version))
    
    # Git 확인
    import subprocess
    try:
        subprocess.run(['git', '--version'], capture_output=True, timeout=5)
        results.append(('Git CLI', True, 'installed'))
    except:
        results.append(('Git CLI', False, None))
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("테스트 결과 요약")
    print("=" * 50)
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    for name, success, version in results:
        status = "✓" if success else "✗"
        version_str = f"({version})" if version else "(미설치)"
        print(f"{status} {name}: {version_str}")
    
    print(f"\n총 {success_count}/{total_count} 패키지 설치됨")
    
    if success_count == total_count:
        print("\n모든 의존성이 설치되어 있습니다!")
    else:
        print(f"\n{total_count - success_count}개 패키지가 누락되었습니다.")
        print("\n누락된 패키지 설치 방법:")
        for name, success, _ in results:
            if not success:
                if name == 'Git CLI':
                    print(f"  - {name}: yum install git 또는 apt-get install git")
                else:
                    print(f"  - {name}: pip install {name}")
    
    return results


with DAG(
    'test_dependencies',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['test', 'dependencies', 'company'],
    description='회사 Airflow 환경 의존성 패키지 테스트'
) as dag:
    
    test_python_task = PythonOperator(
        task_id='test_python_version',
        python_callable=test_python_version
    )
    
    test_requests_task = PythonOperator(
        task_id='test_requests',
        python_callable=test_requests
    )
    
    test_dotenv_task = PythonOperator(
        task_id='test_dotenv',
        python_callable=test_dotenv
    )
    
    test_cryptography_task = PythonOperator(
        task_id='test_cryptography',
        python_callable=test_cryptography
    )
    
    test_git_task = PythonOperator(
        task_id='test_git',
        python_callable=test_git
    )
    
    test_all_task = PythonOperator(
        task_id='test_all_packages',
        python_callable=test_all_packages
    )
    
    # 순차 실행
    test_python_task >> [test_requests_task, test_dotenv_task, test_cryptography_task, test_git_task] >> test_all_task
