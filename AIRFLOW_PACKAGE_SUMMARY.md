# Airflow 3.1.0 폐쇄망 설치 패키지 요약

## 패키지 구성

### 1. Airflow 코어 및 의존성
- **apache-airflow==3.1.0**
- 핵심 의존성 약 60개 (Flask, SQLAlchemy, Jinja2 등)
- 총 크기: 약 200MB

### 2. 데이터베이스 드라이버
- **psycopg2-binary** (PostgreSQL)
- mysqlclient (MySQL, 선택)
- 총 크기: 약 20MB

### 3. Airflow Providers
- apache-airflow-providers-http
- apache-airflow-providers-postgres
- apache-airflow-providers-amazon
- apache-airflow-providers-google
- apache-airflow-providers-slack
- apache-airflow-providers-email
- apache-airflow-providers-ftp
- apache-airflow-providers-ssh
- 총 크기: 약 50MB

### 4. 추가 유틸리티
- **celery** (비동기 작업 처리)
- **redis** (메시지 큐)
- **flower** (Celery 모니터링)
- 총 크기: 약 30MB

### 5. C to Java 프로젝트 의존성
- **requests** (watsonx.ai, GitHub API 호출)
- **python-dotenv** (환경 변수 관리)
- 총 크기: 약 5MB

### 6. Git (별도 설치 필요)
- **Git CLI** (시스템 레벨 설치)
- Windows: Git-2.43.0-64-bit.exe
- Linux: git-2.43.0.rpm 또는 .deb
- 총 크기: 약 50MB

---

## 전체 패키지 크기

| 구성 요소 | 크기 |
|---------|------|
| Airflow 코어 + 의존성 | 200MB |
| 데이터베이스 드라이버 | 20MB |
| Airflow Providers | 50MB |
| 추가 유틸리티 | 30MB |
| C to Java 의존성 | 5MB |
| Git 설치 파일 | 50MB |
| Docker 이미지 (선택) | 1.5GB |
| **총 크기 (최소)** | **약 355MB** |
| **총 크기 (Docker 포함)** | **약 1.9GB** |

---

## 수집 방법

### Windows 환경
```powershell
# PowerShell 스크립트 실행
.\collect_airflow_wheels.ps1

# 결과: airflow_3.1.0_wheels/ 폴더 생성
```

### Linux/Mac 환경
```bash
# Bash 스크립트 실행
chmod +x collect_airflow_wheels.sh
./collect_airflow_wheels.sh

# 결과: airflow_3.1.0_wheels/ 폴더 생성
```

### 수동 다운로드
```bash
# requirements.txt 사용
pip download -r airflow_3.1.0_requirements.txt -d airflow_3.1.0_wheels
```

---

## 폐쇄망 설치 방법

### 1. 패키지 전송
```bash
# 압축
tar -czf airflow_3.1.0_wheels.tar.gz airflow_3.1.0_wheels/

# USB로 폐쇄망 환경에 전송
```

### 2. 설치
```bash
# 압축 해제
tar -xzf airflow_3.1.0_wheels.tar.gz

# 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 로컬 패키지에서 설치
pip install \
    --no-index \
    --find-links=airflow_3.1.0_wheels \
    apache-airflow==3.1.0 \
    requests \
    python-dotenv
```

---

## C to Java 프로젝트 특화 요구사항

### Git 작업
- **Git CLI 필수**: push/pull 자동화에 사용
- **GitManager 클래스**: `src/core/git_manager.py`
- subprocess를 통한 Git 명령어 실행
- **별도 Python 패키지 불필요**

### watsonx.ai 연동
- **requests 패키지**: HTTP API 호출
- **IAM 토큰 인증**: IBM Cloud IAM
- **Watson Data API v2**: 자산 업로드
- **엔드포인트**: 
  - IAM: `https://iam.cloud.ibm.com/identity/token`
  - Data API: `https://api.dataplatform.cloud.ibm.com`

### GitHub 연동
- **requests 패키지**: GitHub API 호출
- **GitHub Token**: repo 권한 필요
- **GitHubUploader 클래스**: `src/core/github_uploader.py`
- **대안**: 내부 Git 서버 (GitLab, Bitbucket)

---

## 폐쇄망 환경 고려사항

### 1. 네트워크 격리
- 외부 인터넷 연결 불가
- 내부 Git 서버 필요 (GitHub Enterprise, GitLab)
- 내부 watsonx.ai 인스턴스 또는 프록시 필요

### 2. 대안 솔루션

#### Git 서버
- **GitHub Enterprise Server** (권장)
- **GitLab Self-hosted**
- **Bitbucket Server**
- **Gitea** (경량)

#### watsonx.ai
- **IBM Cloud Pak for Data** (내부 인스턴스)
- **프록시 서버** (보안 정책 허용 시)
- **API 엔드포인트 수정** (코드 변경 필요)

### 3. 환경 변수 설정

```bash
# .env 파일
# Git 설정
GITHUB_TOKEN=your_token
GITHUB_REPO_URL=https://internal-git.company.com/org/repo.git

# watsonx.ai 설정
WATSONX_API_KEY=your_api_key
WATSONX_ENDPOINT=https://internal-watsonx.company.com
WATSONX_PROJECT_ID=your_project_id

# Airflow 설정
AIRFLOW_HOME=/home/user/airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor
```

---

## 설치 체크리스트

### 인터넷 환경 (준비)
- [ ] Python 패키지 수집 (`collect_airflow_wheels.ps1`)
- [ ] Git 설치 파일 다운로드
- [ ] 프로젝트 소스 코드 압축
- [ ] Docker 이미지 저장 (선택)
- [ ] 모든 파일을 USB에 복사

### 폐쇄망 환경 (설치)
- [ ] USB에서 파일 복사
- [ ] Git 설치 및 확인 (`git --version`)
- [ ] Python 가상환경 생성
- [ ] Airflow 및 의존성 설치
- [ ] 환경 변수 설정 (`.env`)
- [ ] Airflow 초기화 (`airflow db migrate`)
- [ ] 관리자 계정 생성
- [ ] DAG 및 소스 코드 배포
- [ ] 내부 Git 저장소 연동
- [ ] 내부 watsonx.ai 연동 (또는 프록시)
- [ ] Airflow 실행 및 테스트

---

## 예상 소요 시간

| 단계 | 소요 시간 |
|-----|---------|
| 패키지 수집 (인터넷) | 20-30분 |
| USB 전송 | 5-10분 |
| Git 설치 | 5분 |
| Python 환경 설정 | 10분 |
| Airflow 설치 | 15-20분 |
| 환경 설정 | 15-20분 |
| 테스트 및 검증 | 20-30분 |
| **총 소요 시간** | **약 2-3시간** |

---

## 관련 문서

### 설치 가이드
- **AIRFLOW_OFFLINE_INSTALLATION_GUIDE.md** - 상세 설치 가이드
- **AIRFLOW_CLOSED_NETWORK_GUIDE.md** - 폐쇄망 환경 구축 가이드
- **AIRFLOW_DEPENDENCIES_USAGE.md** - 의존성 패키지 사용처 가이드 ⭐
- **AIRFLOW_3.1.0_UPGRADE.md** - 2.8.1에서 3.1.0 업그레이드

### 사용 가이드
- **AIRFLOW_QUICKSTART.md** - Airflow 빠른 시작
- **AIRFLOW_CUSTOM_PIPELINE_GUIDE.md** - 커스텀 파이프라인 작성
- **AIRFLOW_RESULT_GUIDE.md** - 결과 확인 방법
- **WATSONX_NOTEBOOK_JOB_GUIDE.md** - watsonx Job 연동

### 스크립트
- **collect_airflow_wheels.ps1** - Windows 패키지 수집
- **collect_airflow_wheels.sh** - Linux 패키지 수집
- **test_git_automation.py** - Git 자동화 테스트
- **test_connection.py** - watsonx 연결 테스트

---

## 문제 해결

### 패키지 수집 실패
```powershell
# 특정 패키지만 다시 다운로드
pip download --dest airflow_3.1.0_wheels apache-airflow==3.1.0

# 플랫폼 지정
pip download --dest airflow_3.1.0_wheels --platform win_amd64 requests
```

### Git 명령어 실패
```bash
# Git 설치 확인
git --version

# PATH 환경 변수 확인
echo $PATH

# Git 경로 추가
export PATH=$PATH:/usr/local/git/bin
```

### watsonx.ai 연결 실패
```bash
# 엔드포인트 확인
curl -X POST https://iam.cloud.ibm.com/identity/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=YOUR_API_KEY"

# 프록시 설정
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### Airflow 실행 실패
```bash
# 로그 확인
tail -f $AIRFLOW_HOME/logs/scheduler/latest/*.log

# 데이터베이스 재초기화
airflow db reset
airflow db migrate
```

---

## 보안 권장사항

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

# 또는 환경 변수 사용
export AIRFLOW_CONN_WATSONX_DEFAULT='http://your_api_key@internal-watsonx.company.com'
```

### 3. 네트워크 격리
```bash
# Docker 네트워크 생성
docker network create --internal airflow-internal
```

---

## 요약

### 핵심 포인트
1. **총 패키지 크기**: 약 355MB (Docker 제외)
2. **Git CLI 필수**: push/pull 자동화
3. **requests 패키지**: watsonx.ai, GitHub API
4. **python-dotenv**: 환경 변수 관리
5. **내부 서버 필요**: Git, watsonx.ai (또는 프록시)

### 다음 단계
1. 인터넷 환경에서 `collect_airflow_wheels.ps1` 실행
2. Git 설치 파일 다운로드
3. 모든 파일을 USB에 복사
4. 폐쇄망 환경에서 설치 진행
5. 환경 변수 설정 및 테스트

### 성공 기준
- [ ] Airflow 웹 UI 접속 가능 (http://localhost:8080)
- [ ] DAG 목록 표시
- [ ] Git push/pull 자동화 동작
- [ ] watsonx.ai 업로드 성공
- [ ] 파이프라인 실행 완료
