"""
회사 Airflow 서버에 DAG 파일 업로드 스크립트

여러 방법을 제공합니다:
1. SCP (SSH 접근 가능한 경우)
2. HTTP API (Airflow REST API)
3. 수동 업로드 가이드
"""

import os
import subprocess
from pathlib import Path


def upload_via_scp(host, username, dag_folder_path, password=None):
    """
    SCP를 사용하여 DAG 파일 업로드
    
    Args:
        host: 서버 주소 (예: 125.7.235.90)
        username: SSH 사용자명
        dag_folder_path: 서버의 DAG 폴더 경로 (예: /opt/airflow/dags)
        password: SSH 비밀번호 (선택적, 없으면 키 인증 사용)
    """
    print("=" * 60)
    print("SCP를 사용한 DAG 파일 업로드")
    print("=" * 60)
    
    # 업로드할 파일 목록
    dag_files = [
        "dags/test_network_access.py",
        "dags/test_dependencies.py",
        "dags/test_filesystem.py",
    ]
    
    for dag_file in dag_files:
        if not os.path.exists(dag_file):
            print(f"✗ 파일을 찾을 수 없음: {dag_file}")
            continue
        
        # SCP 명령어
        remote_path = f"{username}@{host}:{dag_folder_path}/"
        
        try:
            if password:
                # sshpass 사용 (Linux/Mac)
                cmd = f"sshpass -p '{password}' scp {dag_file} {remote_path}"
            else:
                # 키 인증 사용
                cmd = f"scp {dag_file} {remote_path}"
            
            print(f"업로드 중: {dag_file}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ 업로드 완료: {dag_file}")
            else:
                print(f"✗ 업로드 실패: {dag_file}")
                print(f"  에러: {result.stderr}")
        
        except Exception as e:
            print(f"✗ 업로드 중 오류: {e}")
    
    print("\n업로드 완료!")
    print(f"Airflow UI에서 확인: http://{host}:8181/")


def check_airflow_api(host, port=8181):
    """
    Airflow REST API 접근 가능 여부 확인
    
    Args:
        host: 서버 주소
        port: Airflow 포트 (기본값: 8181)
    """
    print("=" * 60)
    print("Airflow REST API 확인")
    print("=" * 60)
    
    try:
        import requests
        
        # API 버전 확인
        url = f"http://{host}:{port}/api/v1/version"
        print(f"API 엔드포인트: {url}")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            version_info = response.json()
            print(f"✓ Airflow 버전: {version_info.get('version', 'unknown')}")
            print(f"✓ Git 버전: {version_info.get('git_version', 'unknown')}")
            return True
        elif response.status_code == 401:
            print("✗ 인증 필요 (401 Unauthorized)")
            print("  username과 password가 필요합니다")
            return False
        else:
            print(f"✗ API 접근 실패: HTTP {response.status_code}")
            return False
    
    except ImportError:
        print("✗ requests 패키지가 설치되지 않았습니다")
        print("  설치: pip install requests")
        return False
    except Exception as e:
        print(f"✗ API 확인 중 오류: {e}")
        return False


def manual_upload_guide(host):
    """
    수동 업로드 가이드 출력
    """
    print("\n" + "=" * 60)
    print("수동 업로드 가이드")
    print("=" * 60)
    
    print("\n방법 1: 웹 UI를 통한 업로드 (가능한 경우)")
    print("-" * 60)
    print("1. Airflow UI 접속: http://{host}:8181/")
    print("2. Admin > Browse > DAG Files 메뉴 확인")
    print("3. 파일 업로드 기능이 있으면 사용")
    print("   (일부 Airflow 버전에서는 지원하지 않음)")
    
    print("\n방법 2: 서버 직접 접근")
    print("-" * 60)
    print("1. 서버 관리자에게 SSH 접근 권한 요청")
    print("2. SSH로 서버 접속:")
    print(f"   ssh username@{host}")
    print("3. DAG 폴더로 이동:")
    print("   cd /opt/airflow/dags  # 또는 실제 DAG 폴더 경로")
    print("4. 파일 복사:")
    print("   - 로컬에서 파일 내용 복사")
    print("   - 서버에서 vi 또는 nano로 파일 생성")
    print("   - 붙여넣기")
    
    print("\n방법 3: Git 저장소 사용 (권장)")
    print("-" * 60)
    print("1. 내부 Git 저장소에 DAG 파일 푸시")
    print("2. 서버에서 Git pull")
    print("3. Airflow가 자동으로 DAG 감지")
    
    print("\n방법 4: 관리자에게 요청")
    print("-" * 60)
    print("1. DAG 파일을 이메일 또는 메신저로 전달")
    print("2. 관리자가 서버에 업로드")
    
    print("\n업로드할 파일:")
    print("-" * 60)
    dag_files = [
        "dags/test_network_access.py",
        "dags/test_dependencies.py",
        "dags/test_filesystem.py",
    ]
    for f in dag_files:
        if os.path.exists(f):
            size = os.path.getsize(f)
            print(f"  ✓ {f} ({size} bytes)")
        else:
            print(f"  ✗ {f} (파일 없음)")


def create_upload_package():
    """
    업로드용 패키지 생성 (ZIP)
    """
    print("\n" + "=" * 60)
    print("업로드 패키지 생성")
    print("=" * 60)
    
    import zipfile
    from datetime import datetime
    
    # ZIP 파일명
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"airflow_test_dags_{timestamp}.zip"
    
    # 업로드할 파일 목록
    files_to_upload = [
        "dags/test_network_access.py",
        "dags/test_dependencies.py",
        "dags/test_filesystem.py",
        "src/core/file_selector.py",
        "src/core/zip_builder.py",
        "src/core/watsonx_uploader.py",
        "src/core/github_uploader.py",
        "src/core/git_manager.py",
        "src/config/config_manager.py",
        "src/models/data_models.py",
    ]
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_upload:
                if os.path.exists(file_path):
                    zipf.write(file_path)
                    print(f"  추가: {file_path}")
                else:
                    print(f"  건너뜀: {file_path} (파일 없음)")
        
        print(f"\n✓ 패키지 생성 완료: {zip_filename}")
        print(f"  크기: {os.path.getsize(zip_filename)} bytes")
        print(f"\n이 파일을 관리자에게 전달하거나 서버에 업로드하세요.")
        
        return zip_filename
    
    except Exception as e:
        print(f"✗ 패키지 생성 실패: {e}")
        return None


def main():
    """메인 함수"""
    print("\n" + "=" * 60)
    print("회사 Airflow 서버 DAG 업로드 도구")
    print("=" * 60)
    
    host = "125.7.235.90"
    port = 8181
    
    print(f"\n대상 서버: http://{host}:{port}/")
    print()
    
    # 1. API 확인
    api_available = check_airflow_api(host, port)
    
    # 2. 업로드 패키지 생성
    zip_file = create_upload_package()
    
    # 3. 수동 업로드 가이드
    manual_upload_guide(host)
    
    # 4. SCP 사용 가능 여부 확인
    print("\n" + "=" * 60)
    print("SCP 업로드 (SSH 접근 가능한 경우)")
    print("=" * 60)
    print("\nSSH 접근이 가능하다면 다음 명령어를 사용하세요:")
    print(f"  scp dags/test_*.py username@{host}:/opt/airflow/dags/")
    print("\n또는 이 스크립트의 upload_via_scp() 함수를 사용하세요.")
    
    print("\n" + "=" * 60)
    print("다음 단계")
    print("=" * 60)
    print("1. 위 방법 중 하나를 선택하여 DAG 파일 업로드")
    print("2. Airflow UI에서 DAG 목록 확인")
    print("3. test_dependencies DAG 실행")
    print("4. 로그에서 누락된 패키지 확인")
    print("5. collect_c_to_java_packages.ps1 실행")
    print("6. 패키지 설치 및 C to Java 파이프라인 실행")


if __name__ == "__main__":
    main()
