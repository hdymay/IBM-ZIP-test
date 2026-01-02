# 회사 Airflow 환경 테스트 계획

## 테스트 환경 정보

- **Airflow URL**: http://125.7.235.90:8181/
- **환경 유형**: 회사 전용망 (폐쇄망 유사)
- **목적**: 의존성 검증 및 실제 환경 테스트

---

## 1단계: 환경 조사 (정찰)

### 1.1 Airflow 버전 확인

**목표**: 설치된 Airflow 버전 및 설정 확인

**방법**:
1. 웹 UI 접속: http://125.7.235.90:8181/
2. 우측 상단 또는 About 메뉴에서 버전 확인
3. 가능하면 CLI 접근: `airflow version`

**확인 사항**:
- [ ] Airflow 버전 (2.x? 3.x?)
- [ ] Python 버전
- [ ] Executor 타입 (LocalExecutor? CeleryExecutor?)
- [ ] 데이터베이스 (PostgreSQL? MySQL?)

### 1.2 DAG 폴더 위치 확인

**목표**: DAG 파일을 어디에 업로드해야 하는지 확인

**방법**:
1. 기존 DAG 예시 확인
2. 관리자에게 문의
3. 또는 테스트 DAG 업로드 시도

**확인 사항**:
- [ ] DAG 폴더 경로 (예: `/opt/airflow/dags`)
- [ ] 파일 업로드 방법 (FTP? SCP? 웹 UI?)
- [ ] 쓰기 권한 여부

### 1.3 네트워크 제약 확인

**목표**: 외부 API 접근 가능 여부 확인

**테스트 DAG 작성**:
```python
# dags/test_network_access.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import socket

def test_dns():
    """DNS 해석 테스트"""
    try:
        ip = socket.gethostbyname('google.com')
        print(f"✓ DNS 작동: google.com -> {ip}")
        return True
    except Exception as e:
        print(f"✗ DNS 실패: {e}")
        return False

def test_http():
    """HTTP 접근 테스트"""
    try:
        import urllib.request
        response = urllib.request.urlopen('http://www.google.com', timeout=5)
        print(f"✓ HTTP 접근 가능: {response.status}")
        return True
    except Exception as e:
        print(f"✗ HTTP 접근 불가: {e}")
        return False

def test_https():
    """HTTPS 접근 테스트"""
    try:
        import urllib.request
        response = urllib.request.urlopen('https://www.google.com', timeout=5)
        print(f"✓ HTTPS 접근 가능: {response.status}")
        return True
    except Exception as e:
        print(f"✗ HTTPS 접근 불가: {e}")
        return False

def test_watsonx():
    """watsonx.ai 접근 테스트"""
    try:
        import urllib.request
        response = urllib.request.urlopen('https://iam.cloud.ibm.com', timeout=5)
        print(f"✓ watsonx.ai 접근 가능: {response.status}")
        return True
    except Exception as e:
        print(f"✗ watsonx.ai 접근 불가: {e}")
        return False

def test_github():
    """GitHub 접근 테스트"""
    try:
        import urllib.request
        response = urllib.request.urlopen('https://api.github.com', timeout=5)
        print(f"✓ GitHub 접근 가능: {response.status}")
        return True
    except Exception as e:
        print(f"✗ GitHub 접근 불가: {e}")
        return False

with DAG(
    'test_network_access',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['test', 'network']
) as dag:
    
    test_dns_task = PythonOperator(
        task_id='test_dns',
        python_callable=test_dns
    )
    
    test_http_task = PythonOperator(
        task_id='test_http',
        python_callable=test_http
    )
    
    test_https_task = PythonOperator(
        task_id='test_https',
        python_callable=test_https
    )
    
    test_watsonx_task = PythonOperator(
        task_id='test_watsonx',
        python_callable=test_watsonx
    )
    
    test_github_task = PythonOperator(
        task_id='test_github',
        python_callable=test_github
    )
```

**확인 사항**:
- [ ] 외부 인터넷 접근 가능 여부
- [ ] watsonx.ai 접근 가능 여부
- [ ] GitHub 접근 가능 여부
- [ ] 프록시 설정 필요 여부

---

## 2단계: 의존성 테스트

### 2.1 기본 패키지 확인

**목표**: 필요한 Python 패키지가 설치되어 있는지 확인

**테스트 DAG 작성**:
```python
# dags/test_dependencies.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def check_package(package_name):
    """패키지 설치 여부 및 버전 확인"""
    try:
        module = __import__(package_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✓ {package_name}: {version}")
        return True
    except ImportError:
        print(f"✗ {package_name}: NOT INSTALLED")
        return False

def test_requests():
    return check_package('requests')

def test_dotenv():
    return check_package('dotenv')

def test_cryptography():
    return check_package('cryptography')

def test_git():
    """Git CLI 설치 확인"""
    import subprocess
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        print(f"✓ Git: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"✗ Git: NOT INSTALLED - {e}")
        return False

with DAG(
    'test_dependencies',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['test', 'dependencies']
) as dag:
    
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
```

**확인 사항**:
- [ ] requests 설치 여부
- [ ] python-dotenv 설치 여부
- [ ] cryptography 설치 여부
- [ ] Git CLI 설치 여부

### 2.2 파일 시스템 권한 테스트

**테스트 DAG 작성**:
```python
# dags/test_filesystem.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import tempfile

def test_temp_dir():
    """임시 디렉토리 쓰기 테스트"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('test')
            temp_path = f.name
        
        os.remove(temp_path)
        print(f"✓ 임시 파일 생성 가능: {temp_path}")
        return True
    except Exception as e:
        print(f"✗ 임시 파일 생성 실패: {e}")
        return False

def test_output_dir():
    """출력 디렉토리 생성 테스트"""
    try:
        output_dir = '/tmp/c_to_java_output'
        os.makedirs(output_dir, exist_ok=True)
        
        test_file = os.path.join(output_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        
        os.remove(test_file)
        print(f"✓ 출력 디렉토리 사용 가능: {output_dir}")
        return True
    except Exception as e:
        print(f"✗ 출력 디렉토리 사용 불가: {e}")
        return False

def test_zip_creation():
    """ZIP 파일 생성 테스트"""
    try:
        import zipfile
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            zip_path = f.name
        
        with zipfile.ZipFile(zip_path, 'w') as z:
            z.writestr('test.txt', 'test content')
        
        os.remove(zip_path)
        print(f"✓ ZIP 파일 생성 가능")
        return True
    except Exception as e:
        print(f"✗ ZIP 파일 생성 실패: {e}")
        return False

with DAG(
    'test_filesystem',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['test', 'filesystem']
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
```

**확인 사항**:
- [ ] 임시 파일 생성 권한
- [ ] 출력 디렉토리 생성 권한
- [ ] ZIP 파일 생성 가능 여부

---

## 3단계: C to Java 프로젝트 소스 업로드

### 3.1 소스 코드 준비

**필요한 파일**:
```
회사_airflow_업로드/
├── dags/
│   ├── test_network_access.py      # 네트워크 테스트
│   ├── test_dependencies.py        # 의존성 테스트
│   ├── test_filesystem.py          # 파일시스템 테스트
│   ├── c_to_java_pipeline.py       # 실제 파이프라인
│   └── c_to_java_samples_pipeline.py
├── src/
│   ├── core/
│   │   ├── file_selector.py
│   │   ├── zip_builder.py
│   │   ├── watsonx_uploader.py
│   │   ├── github_uploader.py
│   │   └── git_manager.py
│   ├── config/
│   │   └── config_manager.py
│   └── models/
│       └── data_models.py
├── samples/
│   └── (샘플 Python 파일들)
└── .env.example
```

### 3.2 업로드 방법

**옵션 1: 웹 UI 업로드** (가능한 경우)
- Airflow UI에서 파일 업로드 기능 확인

**옵션 2: SCP/SFTP**
```bash
# 서버 접근 가능한 경우
scp -r dags/* user@125.7.235.90:/opt/airflow/dags/
scp -r src/* user@125.7.235.90:/opt/airflow/src/
```

**옵션 3: Git 저장소**
```bash
# 내부 Git 서버 사용
git clone https://internal-git.company.com/c-to-java.git
cd c-to-java
# DAG 파일 자동 동기화
```

**옵션 4: 관리자 요청**
- IT 관리자에게 파일 업로드 요청

---

## 4단계: 단계별 테스트 실행

### 4.1 네트워크 테스트 실행

1. Airflow UI 접속
2. DAGs 메뉴에서 `test_network_access` 찾기
3. 우측 토글로 DAG 활성화
4. "Trigger DAG" 버튼 클릭
5. 실행 완료 후 로그 확인

**예상 결과**:
```
✓ DNS 작동: google.com -> 172.217.x.x
✗ HTTP 접근 불가: [Errno 111] Connection refused
✗ HTTPS 접근 불가: [Errno 111] Connection refused
✗ watsonx.ai 접근 불가: [Errno 111] Connection refused
✗ GitHub 접근 불가: [Errno 111] Connection refused
```

**대응 방안**:
- 외부 접근 불가 → 내부 서버 사용 필요
- 프록시 설정 필요 → IT 팀에 문의

### 4.2 의존성 테스트 실행

1. `test_dependencies` DAG 실행
2. 로그에서 설치된 패키지 확인

**예상 결과 (최악의 경우)**:
```
✗ requests: NOT INSTALLED
✗ dotenv: NOT INSTALLED
✗ cryptography: NOT INSTALLED
✗ Git: NOT INSTALLED
```

**대응 방안**:
- 패키지 설치 요청
- 또는 수집한 whl 파일 제공

### 4.3 파일시스템 테스트 실행

1. `test_filesystem` DAG 실행
2. 권한 문제 확인

**예상 결과**:
```
✓ 임시 파일 생성 가능: /tmp/tmpXXXXXX
✓ 출력 디렉토리 사용 가능: /tmp/c_to_java_output
✓ ZIP 파일 생성 가능
```

---

## 5단계: 실제 파이프라인 테스트

### 5.1 환경 변수 설정

**방법 1: Airflow Variables**
```
Airflow UI > Admin > Variables

WATSONX_API_KEY = your_api_key
WATSONX_ENDPOINT = https://internal-watsonx.company.com
WATSONX_PROJECT_ID = your_project_id
GITHUB_TOKEN = your_token
GITHUB_REPO_URL = https://internal-git.company.com/repo.git
```

**방법 2: Airflow Connections**
```
Airflow UI > Admin > Connections

Connection ID: watsonx_default
Connection Type: HTTP
Host: internal-watsonx.company.com
Password: your_api_key
```

### 5.2 간단한 파이프라인 실행

**테스트 DAG** (`dags/test_simple_pipeline.py`):
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def select_files():
    """파일 선택 테스트"""
    files = ['test1.py', 'test2.py']
    print(f"선택된 파일: {files}")
    return files

def build_zip(**context):
    """ZIP 생성 테스트"""
    import zipfile
    import tempfile
    
    ti = context['ti']
    files = ti.xcom_pull(task_ids='select_files')
    
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
        zip_path = f.name
    
    with zipfile.ZipFile(zip_path, 'w') as z:
        for file in files:
            z.writestr(file, f'content of {file}')
    
    print(f"ZIP 생성 완료: {zip_path}")
    return zip_path

def upload_mock(**context):
    """업로드 모의 테스트 (실제 API 호출 없음)"""
    ti = context['ti']
    zip_path = ti.xcom_pull(task_ids='build_zip')
    
    print(f"업로드할 파일: {zip_path}")
    print("✓ 업로드 성공 (모의)")
    return True

with DAG(
    'test_simple_pipeline',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['test', 'pipeline']
) as dag:
    
    select_task = PythonOperator(
        task_id='select_files',
        python_callable=select_files
    )
    
    build_task = PythonOperator(
        task_id='build_zip',
        python_callable=build_zip
    )
    
    upload_task = PythonOperator(
        task_id='upload_mock',
        python_callable=upload_mock
    )
    
    select_task >> build_task >> upload_task
```

### 5.3 실제 파이프라인 실행 (조건부)

**조건**:
- 모든 의존성 설치 완료
- 네트워크 접근 가능 (또는 내부 서버 설정 완료)
- 환경 변수 설정 완료

**실행**:
1. `c_to_java_pipeline` DAG 활성화
2. Trigger DAG
3. 각 Task 로그 확인
4. 실패 시 에러 메시지 수집

---

## 6단계: 문제 해결 및 문서화

### 6.1 발견된 문제 기록

**템플릿**:
```markdown
## 문제 1: [문제 제목]

**증상**:
- [구체적인 에러 메시지]

**원인**:
- [추정되는 원인]

**해결 방법**:
- [시도한 해결 방법]
- [최종 해결 방법]

**관련 로그**:
```
[로그 내용]
```
```

### 6.2 누락된 의존성 목록 작성

**템플릿**:
```markdown
## 회사 Airflow 환경 누락 패키지

| 패키지 | 필요 여부 | 설치 방법 |
|--------|----------|----------|
| requests | 필수 | pip install requests |
| python-dotenv | 필수 | pip install python-dotenv |
| Git CLI | 필수 | yum install git |
```

### 6.3 네트워크 제약 문서화

**템플릿**:
```markdown
## 네트워크 제약사항

### 접근 가능
- [ ] 내부 네트워크
- [ ] 특정 내부 서버

### 접근 불가
- [ ] 외부 인터넷
- [ ] watsonx.ai (외부)
- [ ] GitHub (외부)

### 대안
- watsonx.ai → 내부 인스턴스 사용
- GitHub → 내부 Git 서버 사용
```

---

## 체크리스트

### 사전 준비
- [ ] 회사 Airflow 접근 권한 확보
- [ ] 로그인 계정 확인
- [ ] 테스트 DAG 파일 준비
- [ ] 백업 계획 수립

### 1단계: 환경 조사
- [ ] Airflow 버전 확인
- [ ] DAG 폴더 위치 확인
- [ ] 네트워크 제약 확인
- [ ] 파일 업로드 방법 확인

### 2단계: 의존성 테스트
- [ ] requests 설치 확인
- [ ] python-dotenv 설치 확인
- [ ] cryptography 설치 확인
- [ ] Git CLI 설치 확인

### 3단계: 소스 업로드
- [ ] 테스트 DAG 업로드
- [ ] src/ 폴더 업로드
- [ ] samples/ 폴더 업로드
- [ ] 환경 변수 설정

### 4단계: 테스트 실행
- [ ] 네트워크 테스트 실행
- [ ] 의존성 테스트 실행
- [ ] 파일시스템 테스트 실행
- [ ] 간단한 파이프라인 실행

### 5단계: 문제 해결
- [ ] 발견된 문제 기록
- [ ] 누락된 패키지 목록 작성
- [ ] 네트워크 제약 문서화
- [ ] 해결 방법 문서화

---

## 예상 시나리오

### 시나리오 1: 모든 패키지 설치됨 (이상적)
```
✓ requests 설치됨
✓ python-dotenv 설치됨
✓ Git CLI 설치됨
→ 바로 파이프라인 실행 가능
```

### 시나리오 2: 일부 패키지 누락 (일반적)
```
✗ requests 미설치
✗ python-dotenv 미설치
✓ Git CLI 설치됨
→ whl 파일 제공 필요
```

### 시나리오 3: 외부 접근 차단 (폐쇄망)
```
✗ watsonx.ai 접근 불가
✗ GitHub 접근 불가
→ 내부 서버 설정 필요
```

### 시나리오 4: 권한 제한
```
✗ DAG 폴더 쓰기 불가
✗ 패키지 설치 불가
→ 관리자 권한 필요
```

---

## 다음 단계

### 테스트 성공 시
1. 실제 파이프라인 배포
2. 스케줄 설정
3. 모니터링 설정
4. 문서 업데이트

### 테스트 실패 시
1. 문제 목록 작성
2. IT 팀과 협의
3. 대안 방안 수립
4. 재테스트 계획

---

## 연락처 및 지원

### IT 팀 문의 사항
- [ ] DAG 폴더 쓰기 권한 요청
- [ ] 패키지 설치 요청 (requests, python-dotenv)
- [ ] Git CLI 설치 요청
- [ ] 내부 watsonx.ai 인스턴스 정보
- [ ] 내부 Git 서버 정보
- [ ] 프록시 설정 정보

### 필요한 정보
- Airflow 관리자 연락처
- 네트워크 팀 연락처
- 보안 정책 문서
- 내부 서버 목록
