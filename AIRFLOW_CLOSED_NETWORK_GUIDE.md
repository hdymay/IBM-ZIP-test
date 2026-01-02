# Airflow 폐쇄망 환경 구축 가이드

## 개요

이 문서는 인터넷 연결이 없는 폐쇄망 환경에서 C to Java 프로젝트의 Airflow 파이프라인을 구축하는 방법을 설명합니다.

## 폐쇄망 환경 특징

### 제약사항
- 외부 인터넷 연결 불가
- PyPI, GitHub 등 외부 저장소 접근 불가
- 패키지 설치는 USB 등 물리적 매체를 통해서만 가능

### 필요한 준비물
1. **Python 패키지** (whl 파일)
2. **Git CLI** (설치 파일)
3. **프로젝트 소스 코드**
4. **환경 설정 파일**

---

## 1단계: 인터넷 환경에서 준비

### 1.1 Python 패키지 수집

```powershell
# Windows에서 실행
.\collect_airflow_wheels.ps1
```

수집되는 패키지:
- Airflow 3.1.0 + 모든 의존성
- PostgreSQL 드라이버
- Celery, Redis, Flower
- **requests** (watsonx.ai, GitHub API)
- **python-dotenv** (환경 변수 관리)

결과: `airflow_3.1.0_wheels/` 폴더 (약 450MB)

### 1.2 Git 설치 파일 다운로드

```
Windows: https://git-scm.com/download/win
Linux: Git 패키지 파일 (rpm, deb)
```

### 1.3 프로젝트 소스 코드 준비

```bash
# 프로젝트 전체를 압축
tar -czf c-to-java-project.tar.gz \
    dags/ \
    src/ \
    samples/ \
    config/ \
    .env.example \
    requirements.txt \
    README.md
```

### 1.4 Docker 이미지 준비 (선택)

```bash
# Airflow 이미지
docker pull apache/airflow:3.1.0
docker save apache/airflow:3.1.0 -o airflow_3.1.0_image.tar

# PostgreSQL 이미지
docker pull postgres:13
docker save postgres:13 -o postgres_13_image.tar

# Redis 이미지
docker pull redis:7
docker save redis:7 -o redis_7_image.tar
```

### 1.5 USB로 전송할 파일 목록

```
폐쇄망_설치_패키지/
├── airflow_3.1.0_wheels/          # Python 패키지 (450MB)
├── c-to-java-project.tar.gz       # 프로젝트 소스
├── git_installer/                 # Git 설치 파일
│   ├── Git-2.43.0-64-bit.exe     # Windows
│   └── git-2.43.0.rpm            # Linux
├── docker_images/                 # Docker 이미지 (선택)
│   ├── airflow_3.1.0_image.tar
│   ├── postgres_13_image.tar
│   └── redis_7_image.tar
├── docker-compose.airflow.yml     # Docker Compose 설정
└── 설치_가이드.txt                # 이 문서
```

---

## 2단계: 폐쇄망 환경에서 설치

### 2.1 Git 설치

#### Windows
```powershell
# Git 설치 파일 실행
.\Git-2.43.0-64-bit.exe

# 설치 확인
git --version
```

#### Linux
```bash
# RPM 기반 (CentOS, RHEL)
sudo rpm -ivh git-2.43.0.rpm

# DEB 기반 (Ubuntu, Debian)
sudo dpkg -i git_2.43.0_amd64.deb

# 설치 확인
git --version
```

### 2.2 프로젝트 소스 압축 해제

```bash
# 프로젝트 디렉토리 생성
mkdir -p ~/c-to-java-project
cd ~/c-to-java-project

# 압축 해제
tar -xzf /path/to/c-to-java-project.tar.gz
```

### 2.3 Python 가상환경 생성

```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화
# Windows
.venv\Scripts\activate

# Linux
source .venv/bin/activate
```

### 2.4 Airflow 및 의존성 설치

```bash
# 로컬 패키지에서 설치
pip install \
    --no-index \
    --find-links=/path/to/airflow_3.1.0_wheels \
    apache-airflow==3.1.0 \
    requests \
    python-dotenv \
    celery \
    redis \
    psycopg2-binary

# 설치 확인
pip list | grep airflow
```

### 2.5 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# 환경 변수 편집
nano .env
```

`.env` 파일 내용:
```bash
# watsonx.ai 설정 (내부 인스턴스 또는 프록시)
WATSONX_API_KEY=your_api_key
WATSONX_ENDPOINT=https://internal-watsonx.company.com
WATSONX_PROJECT_ID=your_project_id

# GitHub 설정 (내부 GitHub Enterprise 또는 GitLab)
GITHUB_TOKEN=your_token
GITHUB_REPO_URL=https://internal-git.company.com/your-org/your-repo.git

# Airflow 설정
AIRFLOW_HOME=/home/user/airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@localhost/airflow
```

### 2.6 Airflow 초기화

```bash
# 환경 변수 설정
export AIRFLOW_HOME=~/airflow

# 데이터베이스 초기화
airflow db migrate

# 관리자 계정 생성
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@company.com \
    --password admin123
```

### 2.7 DAG 및 소스 코드 배포

```bash
# DAG 디렉토리 생성
mkdir -p $AIRFLOW_HOME/dags
mkdir -p $AIRFLOW_HOME/src
mkdir -p $AIRFLOW_HOME/samples
mkdir -p $AIRFLOW_HOME/config

# 파일 복사
cp -r dags/* $AIRFLOW_HOME/dags/
cp -r src/* $AIRFLOW_HOME/src/
cp -r samples/* $AIRFLOW_HOME/samples/
cp -r config/* $AIRFLOW_HOME/config/
cp .env $AIRFLOW_HOME/.env
```

### 2.8 Airflow 실행

```bash
# Standalone 모드 (개발/테스트)
airflow standalone

# 또는 개별 서비스 실행 (프로덕션)
# Terminal 1: Webserver
airflow webserver --port 8080

# Terminal 2: Scheduler
airflow scheduler
```

---

## 3단계: Docker 환경 구축 (선택)

### 3.1 Docker 이미지 로드

```bash
# 이미지 로드
docker load -i airflow_3.1.0_image.tar
docker load -i postgres_13_image.tar
docker load -i redis_7_image.tar

# 이미지 확인
docker images
```

### 3.2 Docker Compose 실행

```bash
# docker-compose.airflow.yml 수정
# image: apache/airflow:3.1.0 (이미 로드됨)

# 환경 변수 설정
export AIRFLOW_UID=$(id -u)

# 컨테이너 실행
docker-compose -f docker-compose.airflow.yml up -d

# 로그 확인
docker-compose -f docker-compose.airflow.yml logs -f
```

---

## 4단계: Git 저장소 설정

### 4.1 내부 Git 서버 연동

폐쇄망 환경에서는 내부 Git 서버를 사용해야 합니다:

- **GitHub Enterprise Server**
- **GitLab (Self-hosted)**
- **Bitbucket Server**
- **Gitea**

### 4.2 Git 저장소 초기화

```bash
cd ~/c-to-java-project

# Git 초기화
git init

# 원격 저장소 추가 (내부 Git 서버)
git remote add origin https://internal-git.company.com/your-org/c-to-java.git

# 초기 커밋
git add .
git commit -m "Initial commit"

# 푸시
git push -u origin main
```

### 4.3 Git 자동화 테스트

```bash
# Git 자동화 스크립트 실행
python test_git_automation.py
```

---

## 5단계: watsonx.ai 연동 설정

### 5.1 내부 watsonx.ai 인스턴스

폐쇄망에서 watsonx.ai를 사용하려면:

1. **내부 watsonx.ai 인스턴스 구축**
   - IBM Cloud Pak for Data 설치
   - watsonx.ai 서비스 활성화

2. **프록시 서버 설정**
   - 외부 IBM Cloud 접근을 위한 프록시
   - 보안 정책에 따라 허용 여부 결정

### 5.2 API 엔드포인트 수정

내부 인스턴스를 사용하는 경우:

```python
# src/core/watsonx_uploader.py 수정
IAM_TOKEN_URL = "https://internal-iam.company.com/identity/token"

# .env 파일 수정
WATSONX_ENDPOINT=https://internal-watsonx.company.com
```

### 5.3 연결 테스트

```bash
# watsonx 연결 테스트
python test_connection.py
```

---

## 6단계: Airflow DAG 실행

### 6.1 DAG 활성화

```bash
# Airflow UI 접속
http://localhost:8080

# 로그인: admin / admin123

# DAG 목록에서 활성화:
# - c_to_java_pipeline
# - c_to_java_samples_pipeline
# - watsonx_notebook_job_pipeline
```

### 6.2 수동 실행

```bash
# CLI에서 DAG 실행
airflow dags test c_to_java_pipeline 2025-01-02

# 특정 Task 실행
airflow tasks test c_to_java_pipeline select_files 2025-01-02
```

### 6.3 결과 확인

```bash
# 로그 확인
tail -f $AIRFLOW_HOME/logs/dag_id=c_to_java_pipeline/run_id=manual__2025-01-02/task_id=select_files/attempt=1.log

# 출력 파일 확인
ls -lh output/
```

---

## 문제 해결

### Git 관련 문제

#### 문제: Git 명령어를 찾을 수 없음
```bash
# 해결: Git 설치 확인
git --version

# PATH 환경 변수 확인
echo $PATH

# Git 경로 추가 (필요시)
export PATH=$PATH:/usr/local/git/bin
```

#### 문제: Git push 인증 실패
```bash
# 해결: 자격 증명 저장
git config --global credential.helper store

# 또는 SSH 키 사용
ssh-keygen -t rsa -b 4096 -C "your_email@company.com"
cat ~/.ssh/id_rsa.pub  # 내부 Git 서버에 등록
```

### watsonx.ai 관련 문제

#### 문제: IAM 토큰 획득 실패
```bash
# 해결: 엔드포인트 확인
curl -X POST https://internal-iam.company.com/identity/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=YOUR_API_KEY"
```

#### 문제: 프록시 설정 필요
```bash
# 해결: 프록시 환경 변수 설정
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1,internal-git.company.com
```

### Airflow 관련 문제

#### 문제: DAG 파일을 찾을 수 없음
```bash
# 해결: DAG 경로 확인
airflow config get-value core dags_folder

# DAG 파일 복사
cp -r dags/* $(airflow config get-value core dags_folder)/
```

#### 문제: 모듈을 찾을 수 없음 (ModuleNotFoundError)
```bash
# 해결: PYTHONPATH 설정
export PYTHONPATH=$AIRFLOW_HOME:$PYTHONPATH

# 또는 airflow.cfg 수정
# [core]
# dags_folder = /home/user/airflow/dags
```

---

## 보안 고려사항

### 1. 자격 증명 관리

```bash
# .env 파일 권한 설정
chmod 600 .env

# Git에서 제외
echo ".env" >> .gitignore
```

### 2. Airflow Connections

```bash
# Airflow UI에서 Connections 설정
# Admin > Connections > Add

# 또는 CLI로 설정
airflow connections add 'watsonx_default' \
    --conn-type 'http' \
    --conn-host 'internal-watsonx.company.com' \
    --conn-password 'your_api_key'
```

### 3. 네트워크 격리

```bash
# Docker 네트워크 생성
docker network create --internal airflow-internal

# docker-compose.yml에 네트워크 추가
networks:
  airflow-internal:
    external: true
```

---

## 성능 최적화

### 1. Celery Executor 사용

```bash
# .env 파일 수정
AIRFLOW__CORE__EXECUTOR=CeleryExecutor
AIRFLOW__CELERY__BROKER_URL=redis://localhost:6379/0
AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:airflow@localhost/airflow

# Celery Worker 실행
airflow celery worker
```

### 2. 병렬 처리 설정

```python
# DAG 파일에서 설정
default_args = {
    'max_active_runs': 3,
    'max_active_tasks': 10,
}
```

### 3. 로그 정리

```bash
# 오래된 로그 삭제
airflow db clean --clean-before-timestamp "2024-12-01"
```

---

## 백업 및 복구

### 백업

```bash
# 데이터베이스 백업
pg_dump airflow > airflow_backup_$(date +%Y%m%d).sql

# DAG 및 설정 백업
tar -czf airflow_config_backup_$(date +%Y%m%d).tar.gz \
    $AIRFLOW_HOME/dags \
    $AIRFLOW_HOME/config \
    $AIRFLOW_HOME/.env
```

### 복구

```bash
# 데이터베이스 복구
psql airflow < airflow_backup_20250102.sql

# 설정 복구
tar -xzf airflow_config_backup_20250102.tar.gz -C $AIRFLOW_HOME
```

---

## 요약

### 폐쇄망 환경 구축 체크리스트

- [ ] Python 패키지 수집 (450MB)
- [ ] Git 설치 파일 준비
- [ ] 프로젝트 소스 코드 압축
- [ ] Docker 이미지 저장 (선택)
- [ ] USB로 폐쇄망 환경에 전송
- [ ] Git 설치 및 설정
- [ ] Python 가상환경 생성
- [ ] Airflow 및 의존성 설치
- [ ] 환경 변수 설정 (.env)
- [ ] Airflow 초기화 (DB, 사용자)
- [ ] DAG 및 소스 코드 배포
- [ ] 내부 Git 저장소 연동
- [ ] 내부 watsonx.ai 연동
- [ ] Airflow 실행 및 테스트
- [ ] DAG 활성화 및 실행

### 예상 소요 시간

- 패키지 수집 (인터넷 환경): 20-30분
- 폐쇄망 설치: 30-60분
- 설정 및 테스트: 30-60분
- **총 소요 시간**: 약 2-3시간

---

## 추가 리소스

### 문서
- `AIRFLOW_OFFLINE_INSTALLATION_GUIDE.md` - 상세 설치 가이드
- `AIRFLOW_DEPENDENCIES_USAGE.md` - 의존성 패키지 사용처 가이드 ⭐
- `AIRFLOW_QUICKSTART.md` - Airflow 빠른 시작
- `AIRFLOW_CUSTOM_PIPELINE_GUIDE.md` - 커스텀 파이프라인 작성
- `WATSONX_NOTEBOOK_JOB_GUIDE.md` - watsonx Job 연동

### 스크립트
- `collect_airflow_wheels.ps1` - Windows 패키지 수집
- `collect_airflow_wheels.sh` - Linux 패키지 수집
- `test_git_automation.py` - Git 자동화 테스트
- `test_connection.py` - watsonx 연결 테스트

### 문의
폐쇄망 환경 구축 중 문제가 발생하면:
1. 로그 파일 확인 (`$AIRFLOW_HOME/logs/`)
2. 환경 변수 확인 (`.env`)
3. 네트워크 연결 확인 (내부 Git, watsonx)
4. 패키지 버전 확인 (`pip list`)
