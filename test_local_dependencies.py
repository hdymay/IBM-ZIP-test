"""
로컬 환경 의존성 테스트 스크립트

회사 Airflow 서버에 업로드하기 전에 로컬에서 테스트할 수 있습니다.
"""

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


def test_python_version():
    """Python 버전 확인"""
    print("=" * 60)
    print("Python 환경 정보")
    print("=" * 60)
    
    import sys
    import platform
    
    print(f"Python 버전: {sys.version}")
    print(f"Python 경로: {sys.executable}")
    print(f"플랫폼: {platform.platform()}")
    print(f"아키텍처: {platform.machine()}")
    print()


def test_requests():
    """requests 패키지 테스트"""
    print("=" * 60)
    print("requests 패키지 테스트")
    print("=" * 60)
    
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
    
    print()
    return success


def test_dotenv():
    """python-dotenv 패키지 테스트"""
    print("=" * 60)
    print("python-dotenv 패키지 테스트")
    print("=" * 60)
    
    success, version = check_package('python-dotenv', 'dotenv')
    
    if success:
        # 간단한 기능 테스트
        try:
            from dotenv import load_dotenv
            print(f"  - load_dotenv 함수: OK")
        except Exception as e:
            print(f"  - 기능 테스트 실패: {e}")
    
    print()
    return success


def test_cryptography():
    """cryptography 패키지 테스트"""
    print("=" * 60)
    print("cryptography 패키지 테스트")
    print("=" * 60)
    
    success, version = check_package('cryptography')
    
    if success:
        # 간단한 기능 테스트
        try:
            from cryptography.fernet import Fernet
            key = Fernet.generate_key()
            print(f"  - Fernet 암호화: OK")
        except Exception as e:
            print(f"  - 기능 테스트 실패: {e}")
    
    print()
    return success


def test_git():
    """Git CLI 설치 확인"""
    print("=" * 60)
    print("Git CLI 설치 확인")
    print("=" * 60)
    
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
        
        print()
        return True
    except FileNotFoundError:
        print(f"✗ Git: NOT INSTALLED (명령어를 찾을 수 없음)")
        print()
        return False
    except Exception as e:
        print(f"✗ Git: ERROR - {e}")
        print()
        return False


def test_airflow():
    """Airflow 설치 확인 (선택적)"""
    print("=" * 60)
    print("Airflow 설치 확인 (선택적)")
    print("=" * 60)
    
    success, version = check_package('airflow')
    
    if not success:
        print("  (로컬 환경에서는 Airflow가 없어도 됩니다)")
    
    print()
    return success


def test_all_packages():
    """모든 패키지 종합 테스트"""
    print("\n" + "=" * 60)
    print("의존성 패키지 종합 테스트 결과")
    print("=" * 60)
    
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
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    for name, success, version in results:
        status = "✓" if success else "✗"
        version_str = f"({version})" if version else "(미설치)"
        print(f"{status} {name}: {version_str}")
    
    print(f"\n총 {success_count}/{total_count} 패키지 설치됨")
    
    if success_count == total_count:
        print("\n모든 의존성이 설치되어 있습니다!")
        print("C to Java 프로젝트를 실행할 수 있습니다.")
    else:
        print(f"\n{total_count - success_count}개 패키지가 누락되었습니다.")
        print("\n누락된 패키지 설치 방법:")
        for name, success, _ in results:
            if not success:
                if name == 'Git CLI':
                    print(f"  - {name}:")
                    print(f"    Windows: https://git-scm.com/download/win")
                    print(f"    Linux: sudo apt-get install git")
                else:
                    print(f"  - {name}: pip install {name}")
    
    print("\n" + "=" * 60)
    print("회사 Airflow 서버 테스트 방법")
    print("=" * 60)
    print("1. dags/test_dependencies.py 파일을 회사 Airflow에 업로드")
    print("2. Airflow UI에서 'test_dependencies' DAG 실행")
    print("3. 로그에서 누락된 패키지 확인")
    print("4. collect_c_to_java_packages.ps1 실행하여 패키지 수집")
    print("5. USB로 전송 및 설치")
    
    return results


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("C to Java 프로젝트 의존성 테스트")
    print("=" * 60)
    print()
    
    # 테스트 실행
    test_python_version()
    test_requests()
    test_dotenv()
    test_cryptography()
    test_git()
    test_airflow()
    
    # 종합 결과
    test_all_packages()
    
    print("\n테스트 완료!")
