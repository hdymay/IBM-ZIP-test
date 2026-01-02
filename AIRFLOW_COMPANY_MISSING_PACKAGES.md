# 회사 Airflow 서버 누락 패키지 분석

## 상황 이해

### 회사 폐쇄망 Airflow 서버
- **URL**: http://125.7.235.90:8181/
- **상태**: Airflow 이미 설치 및 실행 중
- **의미**: Flask, SQLAlchemy 등 Airflow 기본 패키지는 **이미 설치되어 있음**

### 문제
회사 Airflow에는 **Airflow 자체 실행에 필요한 패키지**만 있고,
**C to Java 프로젝트 실행에 필요한 추가 패키지**가 없을 수 있음

---

## 이미 설치되어 있을 패키지 (Airflow 기본)

### Airflow 코어 패키지
```
✓ apache-airflow (당연히 설치됨)
✓ flask (Airflow UI용)
✓ flask-appbuilder (Airflow UI용)
✓ sqlalchemy (Airflow 메타데이터용)
✓ jinja2 (템플릿용)
✓ pendulum (날짜/시간용)
✓ croniter (스케줄용)
✓ gunicorn (웹서버용)
✓ celery (Executor가 CeleryExecutor인 경우)
✓ redis (Celery 사용 시)
```

**이유**: Airflow가 실행되고 있다는 것은 이 패키지들이 이미 설치되어 있다는 의미

---

## 누락되었을 가능성이 높은 패키지 (C to Java 프로젝트용)

### 1. requests (필수)
**용도**: watsonx.ai API, GitHub API 호출
**사용처**: 
- `src/core/watsonx_uploader.py`
- `src/core/github_uploader.py`

**누락 가능성**: 높음
**이유**: Airflow 자체는 requests를 필수로 요구하지 않음 (httpx 사용)

### 2. python-dotenv (필수)
**용도**: `.env` 파일에서 환경 변수 로드
**사용처**: `src/config/config_manager.py`

**누락 가능성**: 매우 높음
**이유**: Airflow는 환경 변수를 직접 읽거나 airflow.cfg 사용

### 3. cryptography (권장)
**용도**: API 키 암호화
**사용처**: `src/config/config_manager.py`

**누락 가능성**: 낮음
**이유**: Airflow Fernet 키 암호화에 사용 (아마 설치되어 있을 것)

### 4. Git CLI (필수)
**용도**: Git push/pull 자동화
**사용처**: `src/core/git_manager.py`

**누락 가능성**: 중간
**이유**: 시스템 레벨 도구, Airflow와 무관

---

## 테스트 결과 예상

### 시나리오 1: 최소 설치 (가장 가능성 높음)
```bash
# test_dependencies DAG 실행 결과
✓ Python 3.9+
✓ flask (Airflow 기본)
✓ sqlalchemy (Airflow 기본)
✓ jinja2 (Airflow 기본)
✓ cryptography (Airflow Fernet용)
✗ requests (미설치)
✗ python-dotenv (미설치)
? Git CLI (확인 필요)
```

**필요한 조치**:
- requests 설치
- python-dotenv 설치
- Git CLI 설치 (없는 경우)

### 시나리오 2: 일부 설치됨
```bash
✓ requests (다른 DAG에서 사용 중)
✗ python-dotenv (미설치)
✓ Git CLI (시스템에 설치됨)
```

**필요한 조치**:
- python-dotenv만 설치

### 시나리오 3: 모두 설치됨 (이상적, 가능성 낮음)
```bash
✓ requests
✓ python-dotenv
✓ cryptography
✓ Git CLI
```

**필요한 조치**: 없음, 바로 실행 가능

---

## 왜 Flask는 확인하지 않는가?

### 질문
"Flask는 Airflow UI에 필요한데 왜 폐쇄망 패키지에 넣지 않았나?"

### 답변
**회사 Airflow 서버에는 이미 Flask가 설치되어 있습니다!**

**증거**:
1. Airflow UI가 실행 중 (http://125.7.235.90:8181/)
2. Airflow UI는 Flask로 만들어짐
3. Flask 없이는 Airflow UI가 작동 불가능

**따라서**:
- Flask 설치 여부 확인 불필요
- Flask는 이미 있음이 확실
- 우리는 **추가로 필요한 패키지**만 확인하면 됨

---

## 실제 확인 방법

### 1단계: test_dependencies DAG 실행

```python
# dags/test_dependencies.py 실행
# 결과 확인:
✓ requests: 2.31.0
✗ python-dotenv: NOT INSTALLED
✓ cryptography: 41.0.0
✓ Git: git version 2.39.0
```

### 2단계: 누락된 패키지 목록 작성

```markdown
## 회사 Airflow 누락 패키지

| 패키지 | 필요 여부 | 설치 방법 |
|--------|----------|----------|
| python-dotenv | 필수 | pip install python-dotenv |
```

### 3단계: 패키지 설치 요청

**옵션 A: IT 팀에 요청**
```
IT 팀님께,

C to Java 프로젝트 실행을 위해 다음 패키지 설치를 요청드립니다:
- python-dotenv==1.0.0

설치 명령어:
pip install python-dotenv==1.0.0

감사합니다.
```

**옵션 B: whl 파일 제공**
```
USB에 담아서 전달:
- python_dotenv-1.0.0-py3-none-any.whl

설치 방법:
pip install python_dotenv-1.0.0-py3-none-any.whl
```

---

## 폐쇄망 패키지 수집 전략 수정

### 현재 전략 (불필요한 패키지 포함)
```bash
# Airflow 전체 + 의존성 다운로드
pip download apache-airflow==3.1.0
# → Flask, SQLAlchemy 등 이미 설치된 패키지도 다운로드
```

**문제**: 
- 불필요한 패키지 다운로드 (이미 설치되어 있음)
- 용량 낭비 (약 200MB)

### 개선된 전략 (필요한 패키지만)
```bash
# C to Java 프로젝트 전용 패키지만 다운로드
pip download requests python-dotenv -d c_to_java_wheels/
# → 약 5MB만 다운로드
```

**장점**:
- 용량 절약
- 명확한 목적
- 빠른 전송

---

## 새로운 수집 스크립트

### collect_c_to_java_packages.ps1 (신규)

```powershell
# C to Java 프로젝트 전용 패키지 수집
# 회사 Airflow에 추가로 필요한 패키지만 다운로드

Write-Host "==========================================" -ForegroundColor Green
Write-Host "C to Java 프로젝트 패키지 수집" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

$OUTPUT_DIR = "c_to_java_wheels"
New-Item -ItemType Directory -Force -Path $OUTPUT_DIR | Out-Null

# C to Java 프로젝트 전용 패키지
$packages = @(
    "requests",        # watsonx.ai, GitHub API
    "python-dotenv"    # 환경 변수 관리
)

foreach ($package in $packages) {
    Write-Host "다운로드 중: $package" -ForegroundColor Yellow
    pip download --dest $OUTPUT_DIR $package
}

Write-Host ""
Write-Host "완료!" -ForegroundColor Green
Write-Host "다운로드 위치: $OUTPUT_DIR" -ForegroundColor Cyan
Write-Host "파일 개수: $((Get-ChildItem $OUTPUT_DIR).Count)" -ForegroundColor Cyan
```

**결과**:
```
c_to_java_wheels/
├── requests-2.31.0-py3-none-any.whl
├── python_dotenv-1.0.0-py3-none-any.whl
├── urllib3-2.1.0-py3-none-any.whl (requests 의존성)
├── certifi-2023.11.17-py3-none-any.whl (requests 의존성)
├── charset_normalizer-3.3.2-py3-none-any.whl (requests 의존성)
└── idna-3.6-py3-none-any.whl (requests 의존성)
```

**총 크기**: 약 5MB (기존 355MB 대비 98% 감소)

---

## 실전 가이드

### 1단계: 회사 Airflow 테스트
```bash
# test_dependencies.py 실행
# 누락된 패키지 확인
```

### 2단계: 필요한 패키지만 수집
```powershell
# 새 스크립트 실행
.\collect_c_to_java_packages.ps1
```

### 3단계: USB로 전송
```bash
# 압축
Compress-Archive -Path c_to_java_wheels -DestinationPath c_to_java_wheels.zip
# USB로 복사
```

### 4단계: 회사 서버에 설치
```bash
# 압축 해제
unzip c_to_java_wheels.zip

# 설치
pip install --no-index --find-links=c_to_java_wheels requests python-dotenv
```

---

## 요약

### 오해
"Flask가 폐쇄망 패키지에 없다"

### 진실
1. **회사 Airflow에는 Flask가 이미 설치되어 있음** (Airflow UI가 작동 중)
2. **우리가 준비한 패키지는 Airflow 전체 재설치용**이 아니라 **C to Java 프로젝트 추가 패키지용**
3. **실제로 필요한 것**: requests, python-dotenv (약 5MB)
4. **불필요한 것**: Flask, SQLAlchemy 등 Airflow 기본 패키지 (이미 설치됨)

### 다음 단계
1. `test_dependencies.py` 실행하여 실제 누락 패키지 확인
2. 누락된 패키지만 수집 (새 스크립트 사용)
3. USB로 전송 및 설치
4. C to Java 파이프라인 실행

이제 명확해졌나요?
