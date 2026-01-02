# Airflow 3.1.0 폐쇄망 환경 설치 가이드

## 개요

이 가이드는 인터넷이 연결되지 않은 폐쇄망 환경에서 Apache Airflow 3.1.0을 설치하는 방법을 설명합니다.

## 사전 준비 (인터넷 연결된 환경)

### 1단계: 패키지 수집

#### Windows 환경
```powershell
# PowerShell 스크립트 실행
.\collect_airflow_wheels.ps1
```

#### Linux/Mac 환경
```bash
# Bash 스크립트 실행 권한 부여
chmod +x collect_airflow_wheels.sh

# 스크립트 실행
./collect_airflow_wheels.sh
```

#### 수동 다운로드 (requirements.txt 사용)
```bash
# 모든 의존성 다운로드
pip download -r airflow_3.1.0_requirements.txt -d airflow_3.1.0_wheels

# 특정 플랫폼용 다운로드
pip download \
    -r airflow_3.1.0_requirements.txt \
    -d airflow_3.1.0_wheels \
    --python-version 3.10 \
    --platform win_amd64 \
    --only-binary=:all:
```

### 2단계: 패키지 압축

```bash
# Windows
Compress-Archive -Path airflow_3.1.0_wheels -DestinationPath airflow_3.1.0_wheels.zip

# Linux/Mac
tar -czf airflow_3.1.0_wheels.tar.gz airflow_3.1.0_wheels/
```

### 3단계: USB로 전송

압축 파일을 USB에 복사하여 폐쇄망 환경으로 이동합니다.

---

## 폐쇄망 환경 설치

### 1단계: 패키지 압축 해제

```bash
# Windows
Expand-Archive -Path airflow_3.1.0_wheels.zip -DestinationPath .

# Linux/Mac
tar -xzf airflow_3.1.0_wheels.tar.gz
```

### 2단계: Python 가상환경 생성

```bash
# 가상환경 생성
python -m venv airflow_venv

# 가상환경 활성화
# Windows
airflow_venv\Scripts\activate

# Linux/Mac
source airflow_venv/bin/activate
```

### 3단계: Airflow 설치

```bash
# 로컬 패키지에서 설치
pip install \
    --no-index \
    --find-links=airflow_3.1.0_wheels \
    apache-airflow==3.1.0

# 추가 Provider 설치 (선택)
pip install \
    --no-index \
    --find-links=airflow_3.1.0_wheels \
    apache-airflow-providers-http \
    apache-airflow-providers-postgres
```

### 4단계: Airflow 초기화

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
    --email admin@example.com \
    --password admin
```

### 5단계: Airflow 실행

```bash
# Standalone 모드 (개발용)
airflow standalone

# 또는 개별 서비스 실행 (프로덕션)
# Terminal 1: Webserver
airflow webserver --port 8080

# Terminal 2: Scheduler
airflow scheduler
```

---

## Docker 환경 (폐쇄망)

### 1단계: Docker 이미지 저장 (인터넷 환경)

```bash
# Airflow 이미지 다운로드
docker pull apache/airflow:3.1.0

# 이미지 저장
docker save apache/airflow:3.1.0 -o airflow_3.1.0_image.tar

# PostgreSQL 이미지 (선택)
docker pull postgres:13
docker save postgres:13 -o postgres_13_image.tar
```

### 2단계: 이미지 로드 (폐쇄망 환경)

```bash
# 이미지 로드
docker load -i airflow_3.1.0_image.tar
docker load -i postgres_13_image.tar

# 이미지 확인
docker images | grep airflow
```

### 3단계: Docker Compose 실행

```bash
# docker-compose.airflow.yml 사용
docker-compose -f docker-compose.airflow.yml up -d
```

---

## 패키지 목록

### 필수 패키지 (약 200MB)

1. **Airflow 코어**
   - apache-airflow==3.1.0

2. **핵심 의존성** (약 60개)
   - Flask, SQLAlchemy, Jinja2 등

3. **데이터베이스 드라이버**
   - psycopg2-binary (PostgreSQL)
   - mysqlclient (MySQL, 선택)

4. **C to Java 프로젝트 의존성**
   - requests (watsonx.ai, GitHub API 호출)
   - python-dotenv (환경 변수 관리)

### 선택 패키지

5. **Airflow Providers** (약 50MB)
   - HTTP, PostgreSQL, Amazon, Google, Slack 등

6. **추가 유틸리티**
   - Celery, Redis, Flower

### 전체 크기 예상

- **최소 설치**: 약 250MB
- **전체 설치**: 약 450MB (C to Java 의존성 포함)

---

## 플랫폼별 주의사항

### Windows

```powershell
# Python 버전 확인
python --version  # 3.9, 3.10, 3.11 권장

# 플랫폼 확인
python -c "import platform; print(platform.machine())"  # AMD64

# 다운로드 시 플랫폼 지정
--platform win_amd64
```

### Linux

```bash
# Python 버전 확인
python3 --version

# 플랫폼 확인
python3 -c "import platform; print(platform.machine())"  # x86_64

# 다운로드 시 플랫폼 지정
--platform manylinux2014_x86_64
--platform manylinux_2_17_x86_64
```

### Mac (Apple Silicon)

```bash
# M1/M2 칩
--platform macosx_11_0_arm64

# Intel 칩
--platform macosx_10_9_x86_64
```

---

## C to Java 프로젝트 특화 설정

### Git 설치 (필수)

프로젝트에서 Git push/pull 자동화를 사용하므로 Git CLI가 설치되어 있어야 합니다.

#### Windows
```powershell
# Git for Windows 다운로드 및 설치
# https://git-scm.com/download/win

# 설치 확인
git --version
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get install git

# CentOS/RHEL
sudo yum install git

# 설치 확인
git --version
```

### IBM watsonx.ai 연동

프로젝트에서 watsonx.ai API를 사용합니다. 폐쇄망 환경에서는:

1. **API 엔드포인트 설정**
   - 내부 watsonx.ai 인스턴스 URL 필요
   - 또는 프록시를 통한 외부 접근 설정

2. **환경 변수 설정**
   ```bash
   # .env 파일 생성
   WATSONX_API_KEY=your_api_key
   WATSONX_ENDPOINT=https://your-watsonx-instance.com
   WATSONX_PROJECT_ID=your_project_id
   ```

3. **네트워크 설정**
   - IAM 토큰 엔드포인트: `https://iam.cloud.ibm.com/identity/token`
   - Watson Data API: `https://api.dataplatform.cloud.ibm.com`
   - 폐쇄망에서는 프록시 또는 내부 인스턴스 필요

### GitHub 연동

프로젝트에서 GitHub API를 사용합니다.

1. **GitHub Token 생성**
   - https://github.com/settings/tokens
   - `repo` 권한 필요

2. **환경 변수 설정**
   ```bash
   GITHUB_TOKEN=your_github_token
   GITHUB_REPO_URL=https://github.com/your-org/your-repo.git
   ```

3. **폐쇄망 대안**
   - GitHub Enterprise Server 사용
   - GitLab, Bitbucket 등 내부 Git 서버 사용
   - 코드 수정 필요: `src/core/github_uploader.py`

### Airflow DAG 설정

C to Java 프로젝트의 DAG 파일들:

```bash
dags/
├── c_to_java_pipeline.py           # 기본 파이프라인
├── c_to_java_taskflow.py           # TaskFlow API 버전
├── c_to_java_class_based.py        # 클래스 기반 버전
├── c_to_java_samples_pipeline.py   # 샘플 실행 파이프라인
└── watsonx_notebook_job_pipeline.py # watsonx Job 연동
```

폐쇄망 환경에서 DAG 배포:

```bash
# DAG 파일 복사
cp -r dags/* $AIRFLOW_HOME/dags/

# 프로젝트 소스 복사
cp -r src/* $AIRFLOW_HOME/src/
cp -r samples/* $AIRFLOW_HOME/samples/

# 환경 변수 설정
cp .env $AIRFLOW_HOME/.env
```

---

## 문제 해결

### 의존성 충돌

```bash
# 의존성 트리 확인
pip install pipdeptree
pipdeptree

# 특정 버전 강제 설치
pip install --no-index --find-links=airflow_3.1.0_wheels package==version
```

### 바이너리 패키지 누락

일부 패키지는 소스 코드만 제공될 수 있습니다. 이 경우:

```bash
# 컴파일 도구 설치 (인터넷 환경)
# Windows: Visual Studio Build Tools
# Linux: gcc, python3-dev
# Mac: Xcode Command Line Tools

# 소스에서 빌드
pip wheel -r airflow_3.1.0_requirements.txt -w airflow_3.1.0_wheels
```

### Python 버전 불일치

```bash
# 다운로드 환경과 설치 환경의 Python 버전이 일치해야 함
# 예: 3.10에서 다운로드 → 3.10에서 설치

# 버전 확인
python --version
```

---

## 검증

### 설치 확인

```bash
# Airflow 버전 확인
airflow version

# 설치된 패키지 확인
pip list | grep airflow

# 설정 확인
airflow config list
```

### 테스트 DAG 실행

```bash
# DAG 목록 확인
airflow dags list

# 테스트 DAG 실행
airflow dags test example_dag 2025-01-01
```

---

## 추가 리소스

### 필요한 파일 목록

1. `airflow_3.1.0_wheels/` - 패키지 디렉토리
2. `airflow_3.1.0_requirements.txt` - 의존성 목록
3. `collect_airflow_wheels.ps1` - Windows 수집 스크립트
4. `collect_airflow_wheels.sh` - Linux/Mac 수집 스크립트
5. `docker-compose.airflow.yml` - Docker Compose 설정

### 권장 디렉토리 구조

```
폐쇄망_설치_패키지/
├── airflow_3.1.0_wheels/          # whl 파일들
├── airflow_3.1.0_requirements.txt # 의존성 목록
├── docker_images/                 # Docker 이미지 (선택)
│   ├── airflow_3.1.0_image.tar
│   └── postgres_13_image.tar
├── docker-compose.airflow.yml     # Docker Compose 설정
└── README.md                      # 이 가이드
```

---

## 요약

### 인터넷 환경에서

1. 스크립트 실행: `collect_airflow_wheels.ps1` 또는 `.sh`
2. 패키지 압축: `airflow_3.1.0_wheels.zip`
3. USB로 전송

### 폐쇄망 환경에서

1. 압축 해제
2. 가상환경 생성
3. 로컬 패키지 설치: `pip install --no-index --find-links=...`
4. Airflow 초기화 및 실행

### 예상 소요 시간

- 패키지 다운로드: 10-20분 (인터넷 속도에 따라)
- 설치: 5-10분
- 초기화: 2-3분

---

## 문의

문제가 발생하면 다음을 확인하세요:

1. Python 버전 일치 여부
2. 플랫폼 (Windows/Linux/Mac) 일치 여부
3. 모든 의존성 패키지 다운로드 완료 여부
4. 가상환경 활성화 여부
