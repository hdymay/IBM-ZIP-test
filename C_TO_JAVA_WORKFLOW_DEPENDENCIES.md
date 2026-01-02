# C to Java Airflow 워크플로우 의존성 분석

## 워크플로우 개요

```
┌─────────────────────────────────────────────────────────────┐
│                    Airflow Orchestration                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   ┌────────┐           ┌────────┐           ┌────────┐
   │ Job A  │  ──────>  │ Job B  │  ──────>  │ Job C  │
   │Git Clone│          │C to Java│          │Git Push │
   └────────┘           └────────┘           │BXM Upload│
                                              └────────┘
```

---

## Job A: Git Clone (소스 가져오기)

### 작업 내용
- Git 저장소에서 소스 코드 Clone
- 특정 브랜치 또는 커밋 체크아웃

### 필요한 의존성

#### 1. Git CLI (필수)
```bash
# 시스템 레벨 설치
# Windows: Git-2.43.0-64-bit.exe
# Linux: yum install git 또는 apt-get install git
```

**사용 예시**:
```python
from airflow.operators.bash import BashOperator

git_clone_task = BashOperator(
    task_id='git_clone',
    bash_command='git clone https://github.com/user/repo.git /tmp/source'
)
```

#### 2. GitPython (선택적, Python에서 Git 제어)
```bash
pip install GitPython
```

**사용 예시**:
```python
from airflow.operators.python import PythonOperator
import git

def clone_repo():
    repo = git.Repo.clone_from(
        'https://github.com/user/repo.git',
        '/tmp/source'
    )
    return repo.head.commit.hexsha

git_clone_task = PythonOperator(
    task_id='git_clone',
    python_callable=clone_repo
)
```

---

## Job B: C to Java 변환 (다른 개발자 담당)

### 작업 내용
- C 소스 코드를 Java로 변환
- 변환 도구 실행 (다른 팀이 개발)

### 필요한 의존성

#### 1. subprocess (Python 내장)
```python
from airflow.operators.python import PythonOperator
import subprocess

def run_c_to_java_converter():
    result = subprocess.run(
        ['python', '/path/to/converter.py', '--input', '/tmp/source'],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

convert_task = PythonOperator(
    task_id='c_to_java_convert',
    python_callable=run_c_to_java_converter
)
```

#### 2. 변환 도구 의존성 (다른 팀 제공)
- 변환 도구가 필요로 하는 패키지
- 예: `tree-sitter`, `libclang` 등 (변환 도구에 따라 다름)

---

## Job C: 결과 처리 및 업로드

### 작업 내용
1. Git Pull (최신 상태 동기화)
2. Git Push (변환 결과 푸시)
3. Transform/복사 작업
4. Git Push (최종 결과)
5. BXM 업로드

### 필요한 의존성

#### 1. Git CLI (필수)
```python
from airflow.operators.bash import BashOperator

git_push_task = BashOperator(
    task_id='git_push',
    bash_command='''
        cd /tmp/source
        git add .
        git commit -m "C to Java conversion results"
        git push origin main
    '''
)
```

#### 2. GitPython (선택적)
```python
def git_push_results():
    import git
    repo = git.Repo('/tmp/source')
    repo.git.add('.')
    repo.index.commit('C to Java conversion results')
    origin = repo.remote('origin')
    origin.push()
```

#### 3. requests (BXM 업로드용)
```bash
pip install requests
```

**사용 예시**:
```python
import requests

def upload_to_bxm():
    with open('/tmp/result.zip', 'rb') as f:
        response = requests.post(
            'https://bxm.company.com/api/upload',
            files={'file': f},
            headers={'Authorization': 'Bearer token'}
        )
    return response.status_code == 200
```

#### 4. python-dotenv (환경 변수 관리)
```bash
pip install python-dotenv
```

**사용 예시**:
```python
from dotenv import load_dotenv
import os

load_dotenv()
bxm_token = os.getenv('BXM_TOKEN')
git_token = os.getenv('GIT_TOKEN')
```

---

## 전체 워크플로우 의존성 요약

### 필수 패키지

| 패키지 | 용도 | 설치 방법 |
|--------|------|----------|
| **Git CLI** | Git clone, push, pull | 시스템 설치 |
| **requests** | BXM API 호출 | pip install requests |
| **python-dotenv** | 환경 변수 관리 | pip install python-dotenv |

### 선택적 패키지

| 패키지 | 용도 | 설치 방법 |
|--------|------|----------|
| **GitPython** | Python에서 Git 제어 | pip install GitPython |
| **paramiko** | SSH/SFTP 접근 | pip install paramiko |

### Airflow 기본 제공 (이미 설치됨)

| 패키지 | 용도 |
|--------|------|
| **subprocess** | 외부 명령어 실행 (Python 내장) |
| **os, shutil** | 파일 시스템 작업 (Python 내장) |
| **BashOperator** | Bash 명령어 실행 (Airflow 내장) |
| **PythonOperator** | Python 함수 실행 (Airflow 내장) |

---

## 실제 DAG 예시

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import os

def upload_to_bxm(**context):
    """BXM에 결과 업로드"""
    import requests
    from dotenv import load_dotenv
    
    load_dotenv()
    
    bxm_url = os.getenv('BXM_URL')
    bxm_token = os.getenv('BXM_TOKEN')
    
    with open('/tmp/result.zip', 'rb') as f:
        response = requests.post(
            f'{bxm_url}/api/upload',
            files={'file': f},
            headers={'Authorization': f'Bearer {bxm_token}'}
        )
    
    return response.status_code == 200

with DAG(
    'c_to_java_pipeline',
    start_date=datetime(2025, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:
    
    # Job A: Git Clone
    git_clone = BashOperator(
        task_id='git_clone',
        bash_command='''
            rm -rf /tmp/c_source
            git clone https://github.com/company/c-source.git /tmp/c_source
        '''
    )
    
    # Job B: C to Java 변환 (다른 팀 도구 호출)
    c_to_java_convert = BashOperator(
        task_id='c_to_java_convert',
        bash_command='''
            python /opt/converter/c_to_java.py \
                --input /tmp/c_source \
                --output /tmp/java_output
        '''
    )
    
    # Job C-1: Git Pull (최신 상태 동기화)
    git_pull = BashOperator(
        task_id='git_pull',
        bash_command='''
            cd /tmp/java_output
            git pull origin main
        '''
    )
    
    # Job C-2: Transform/복사
    transform = BashOperator(
        task_id='transform',
        bash_command='''
            cp -r /tmp/java_output/* /tmp/final_output/
            # 추가 변환 작업
        '''
    )
    
    # Job C-3: Git Push
    git_push = BashOperator(
        task_id='git_push',
        bash_command='''
            cd /tmp/final_output
            git add .
            git commit -m "C to Java conversion $(date +%Y%m%d)"
            git push origin main
        '''
    )
    
    # Job C-4: BXM 업로드
    bxm_upload = PythonOperator(
        task_id='bxm_upload',
        python_callable=upload_to_bxm
    )
    
    # 워크플로우 정의
    git_clone >> c_to_java_convert >> git_pull >> transform >> git_push >> bxm_upload
```

---

## 환경 변수 설정

### .env 파일
```bash
# Git 설정
GIT_USERNAME=your_username
GIT_TOKEN=your_git_token
GIT_REPO_URL=https://github.com/company/repo.git

# BXM 설정
BXM_URL=https://bxm.company.com
BXM_TOKEN=your_bxm_token
BXM_PROJECT_ID=your_project_id

# 변환 도구 설정
CONVERTER_PATH=/opt/converter/c_to_java.py
```

### Airflow Variables (권장)
```python
# Airflow UI > Admin > Variables
GIT_REPO_URL = https://github.com/company/repo.git
BXM_URL = https://bxm.company.com
```

### Airflow Connections (권장)
```python
# Airflow UI > Admin > Connections

# Git Connection
Connection ID: git_default
Connection Type: HTTP
Host: github.com
Login: your_username
Password: your_token

# BXM Connection
Connection ID: bxm_default
Connection Type: HTTP
Host: bxm.company.com
Password: your_bxm_token
```

---

## 폐쇄망 환경 패키지 수집

### 최소 패키지 (5MB)
```bash
# collect_c_to_java_packages.ps1 실행
requests
python-dotenv
```

### 권장 패키지 (10MB)
```bash
requests
python-dotenv
GitPython  # Python에서 Git 제어
```

### 전체 패키지 (20MB)
```bash
requests
python-dotenv
GitPython
paramiko  # SSH/SFTP
cryptography  # 암호화
```

---

## Git 인증 방법

### 방법 1: HTTPS + Token
```bash
git clone https://username:token@github.com/company/repo.git
```

### 방법 2: SSH Key
```bash
# SSH 키 생성
ssh-keygen -t rsa -b 4096 -C "airflow@company.com"

# 공개 키를 Git 서버에 등록
cat ~/.ssh/id_rsa.pub

# Git clone
git clone git@github.com:company/repo.git
```

### 방법 3: Git Credential Helper
```bash
# 자격 증명 저장
git config --global credential.helper store

# 첫 번째 push 시 자격 증명 입력
# 이후 자동으로 사용됨
```

---

## BXM 업로드 방법

### 방법 1: REST API
```python
import requests

def upload_to_bxm(file_path, bxm_url, token):
    with open(file_path, 'rb') as f:
        response = requests.post(
            f'{bxm_url}/api/upload',
            files={'file': f},
            headers={'Authorization': f'Bearer {token}'}
        )
    return response.json()
```

### 방법 2: SDK (BXM 제공)
```python
from bxm_sdk import BXMClient

client = BXMClient(api_key='your_key')
result = client.upload_file('/tmp/result.zip')
```

---

## 문제 해결

### Git 인증 실패
```bash
# 토큰 확인
echo $GIT_TOKEN

# SSH 키 확인
ssh -T git@github.com

# Git 설정 확인
git config --list
```

### BXM 업로드 실패
```python
# 연결 테스트
import requests
response = requests.get(f'{bxm_url}/api/health')
print(response.status_code)

# 토큰 확인
print(f'Token: {bxm_token[:10]}...')
```

### 파일 권한 문제
```bash
# 디렉토리 권한 확인
ls -la /tmp/

# 권한 변경
chmod 755 /tmp/c_source
chown airflow:airflow /tmp/c_source
```

---

## 요약

### 필수 의존성 (회사 Airflow에 추가 필요)
1. **Git CLI** - 시스템 설치
2. **requests** - BXM API 호출
3. **python-dotenv** - 환경 변수 관리

### 선택적 의존성
4. **GitPython** - Python에서 Git 제어 (BashOperator 대신)

### 이미 설치되어 있음 (Airflow 기본)
- subprocess, os, shutil (Python 내장)
- BashOperator, PythonOperator (Airflow 내장)
- Flask, SQLAlchemy 등 (Airflow 의존성)

### 다음 단계
1. 회사 Airflow에서 `test_dependencies.py` 실행
2. 누락된 패키지 확인
3. `collect_c_to_java_packages.ps1` 실행
4. USB로 전송 및 설치
5. 실제 DAG 작성 및 테스트
