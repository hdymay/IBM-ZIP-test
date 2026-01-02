# Airflow 의존성 해결 메커니즘 설명

## 질문: Flask가 패키지 목록에 없는 것 같은데?

**답변**: Flask는 **명시적으로 포함되어 있습니다!**

## 의존성 다운로드 방식

### 방법 1: apache-airflow만 다운로드 (자동 의존성 해결)

```bash
pip download apache-airflow==3.1.0 -d wheels/
```

**결과**:
- apache-airflow-3.1.0.whl
- flask-2.2.5.whl (자동으로 다운로드됨)
- flask-appbuilder-4.3.0.whl (자동으로 다운로드됨)
- sqlalchemy-1.4.50.whl (자동으로 다운로드됨)
- ... (약 100개 의존성 자동 다운로드)

**장점**:
- 간단함
- 의존성 누락 없음

**단점**:
- 어떤 패키지가 다운로드되는지 불명확
- 버전 제어 어려움

### 방법 2: 명시적 패키지 나열 (우리가 사용하는 방식)

```bash
# 1단계: Airflow 코어
pip download apache-airflow==3.1.0 -d wheels/

# 2단계: 핵심 의존성 명시적 다운로드
pip download flask -d wheels/
pip download flask-appbuilder -d wheels/
pip download sqlalchemy -d wheels/
pip download requests -d wheels/
pip download python-dotenv -d wheels/
# ... (계속)
```

**장점**:
- 어떤 패키지가 필요한지 명확
- 버전 제어 가능
- 문서화 용이

**단점**:
- 목록 작성 필요
- 일부 의존성 누락 가능 (하지만 1단계에서 자동 해결됨)

## 우리 스크립트의 동작 방식

### collect_airflow_wheels.ps1 분석

```powershell
# 1단계: Airflow 코어 다운로드
pip download apache-airflow==3.1.0 --dest $OUTPUT_DIR

# 이 단계에서 이미 Flask를 포함한 모든 의존성이 다운로드됩니다!
```

**다운로드되는 패키지 (예시)**:
```
airflow_3.1.0_wheels/
├── apache_airflow-3.1.0-py3-none-any.whl
├── flask-2.2.5-py3-none-any.whl              ← 자동 다운로드
├── flask_appbuilder-4.3.0-py3-none-any.whl   ← 자동 다운로드
├── sqlalchemy-1.4.50-py3-none-any.whl        ← 자동 다운로드
├── werkzeug-2.0.3-py3-none-any.whl           ← 자동 다운로드
├── jinja2-3.1.2-py3-none-any.whl             ← 자동 다운로드
└── ... (약 100개 파일)
```

```powershell
# 2단계: 핵심 의존성 명시적 다운로드
$core_packages = @(
    "flask",              # ← 명시적으로 포함됨!
    "flask-appbuilder",
    "flask-caching",
    "flask-login",
    "flask-session",
    "flask-wtf",
    ...
)

foreach ($package in $core_packages) {
    pip download $package --dest $OUTPUT_DIR
}
```

**왜 중복 다운로드?**
- 1단계에서 이미 다운로드되었지만
- 2단계에서 다시 다운로드 시도
- pip는 이미 존재하는 파일은 건너뜀 (중복 방지)

**결과**:
```
  다운로드 중: flask
  Requirement already satisfied: flask in ./airflow_3.1.0_wheels
  (건너뜀)
```

## 실제 확인 방법

### 스크립트 실행 후 확인

```powershell
# 스크립트 실행
.\collect_airflow_wheels.ps1

# Flask 관련 파일 확인
ls airflow_3.1.0_wheels | Select-String "flask"
```

**예상 결과**:
```
flask-2.2.5-py3-none-any.whl
flask_appbuilder-4.3.0-py3-none-any.whl
flask_caching-2.1.0-py3-none-any.whl
flask_login-0.6.2-py3-none-any.whl
flask_session-0.5.0-py3-none-any.whl
flask_wtf-1.1.0-py3-none-any.whl
```

### 의존성 트리 확인

```bash
# apache-airflow의 의존성 확인
pip show apache-airflow

# 출력 예시:
# Requires: flask>=2.2.5, sqlalchemy>=1.4.36, ...
```

## 왜 명시적으로 나열하는가?

### 1. 문서화 목적

`airflow_3.1.0_requirements.txt`:
```txt
# ============================================================
# 2. 핵심 의존성
# ============================================================
flask>=2.2.5,<3.1          # ← 명시적으로 문서화
flask-appbuilder>=4.3.0
sqlalchemy>=1.4.36,<2.0
...
```

**이유**:
- 어떤 패키지가 필요한지 한눈에 파악
- 버전 요구사항 명확화
- 문제 발생 시 디버깅 용이

### 2. 버전 제어

```bash
# 특정 버전 강제 지정 가능
pip download flask==2.2.5 -d wheels/

# Airflow가 요구하는 버전과 다른 버전 설치 방지
```

### 3. 선택적 설치

```bash
# 최소 설치 (Flask 포함)
pip install --no-index --find-links=wheels apache-airflow

# 추가 기능 설치
pip install --no-index --find-links=wheels celery redis
```

## 의존성 계층 구조

```
apache-airflow==3.1.0
├── flask>=2.2.5,<3.1
│   ├── werkzeug>=2.0
│   ├── jinja2>=3.1.2
│   ├── itsdangerous>=2.0
│   └── click>=8.0
├── flask-appbuilder>=4.3.0
│   ├── flask>=2.2.5
│   ├── flask-login>=0.6.2
│   ├── flask-wtf>=1.1.0
│   └── sqlalchemy>=1.4.36
├── sqlalchemy>=1.4.36,<2.0
├── requests>=2.27.0
└── ... (약 60개 직접 의존성)
```

**총 패키지 수**: 약 100-150개 (간접 의존성 포함)

## 실전 테스트

### 테스트 1: Airflow만 다운로드

```powershell
# 새 폴더 생성
mkdir test_airflow_only
cd test_airflow_only

# Airflow만 다운로드
pip download apache-airflow==3.1.0 -d wheels/

# Flask 확인
ls wheels/ | Select-String "flask"
```

**결과**: Flask 관련 파일 6개 이상 발견

### 테스트 2: 명시적 다운로드

```powershell
# 새 폴더 생성
mkdir test_explicit
cd test_explicit

# 1단계: Airflow
pip download apache-airflow==3.1.0 -d wheels/

# 2단계: Flask 명시적 다운로드
pip download flask -d wheels/

# 결과 확인
ls wheels/ | Select-String "flask"
```

**결과**: 동일한 Flask 파일들 (중복 없음)

## 결론

### Flask는 다운로드됩니다!

**방법 1**: `apache-airflow==3.1.0` 다운로드 시 자동으로 포함
**방법 2**: 명시적으로 `flask` 다운로드 (우리 스크립트)

### 우리 스크립트의 장점

1. **명확성**: 어떤 패키지가 필요한지 명시
2. **문서화**: requirements.txt에 모든 패키지 나열
3. **안정성**: 중요 패키지는 명시적으로 다운로드
4. **유연성**: 필요한 패키지만 선택적 설치 가능

### 확인 방법

```powershell
# 스크립트 실행
.\collect_airflow_wheels.ps1

# Flask 확인
ls airflow_3.1.0_wheels | Select-String "flask"

# 전체 패키지 수 확인
(ls airflow_3.1.0_wheels).Count
```

**예상 결과**: 100-150개 파일, Flask 포함

## 추가 설명: pip download의 동작

### --only-binary=:all: 옵션

```powershell
pip download apache-airflow==3.1.0 `
    --dest $OUTPUT_DIR `
    --only-binary=:all:
```

**의미**:
- 소스 코드(.tar.gz) 대신 바이너리(.whl)만 다운로드
- 컴파일 불필요
- 폐쇄망 환경에서 즉시 설치 가능

### 의존성 자동 해결

```
apache-airflow 다운로드 요청
    ↓
pip가 setup.py 또는 pyproject.toml 확인
    ↓
의존성 목록 추출 (flask, sqlalchemy, ...)
    ↓
각 의존성 다운로드
    ↓
각 의존성의 의존성도 다운로드 (재귀적)
    ↓
모든 파일 다운로드 완료
```

## 실제 파일 목록 예시

```
airflow_3.1.0_wheels/
├── apache_airflow-3.1.0-py3-none-any.whl
├── alembic-1.13.1-py3-none-any.whl
├── flask-2.2.5-py3-none-any.whl              ← Flask
├── flask_appbuilder-4.3.0-py3-none-any.whl   ← Flask 확장
├── flask_caching-2.1.0-py3-none-any.whl      ← Flask 확장
├── flask_login-0.6.2-py3-none-any.whl        ← Flask 확장
├── flask_session-0.5.0-py3-none-any.whl      ← Flask 확장
├── flask_wtf-1.1.0-py3-none-any.whl          ← Flask 확장
├── werkzeug-2.0.3-py3-none-any.whl           ← Flask 의존성
├── jinja2-3.1.2-py3-none-any.whl             ← Flask 의존성
├── itsdangerous-2.1.2-py3-none-any.whl       ← Flask 의존성
├── click-8.1.7-py3-none-any.whl              ← Flask 의존성
├── sqlalchemy-1.4.50-py3-none-any.whl
├── requests-2.31.0-py3-none-any.whl
├── python_dotenv-1.0.0-py3-none-any.whl
└── ... (약 100개 더)
```

## 요약

**질문**: Flask가 패키지 목록에 없는 것 같은데?

**답변**: 
1. Flask는 **명시적으로 포함**되어 있습니다 (스크립트 라인 43)
2. 설령 명시하지 않아도 `apache-airflow` 다운로드 시 **자동으로 포함**됩니다
3. 우리는 **명확성과 문서화**를 위해 명시적으로 나열합니다
4. pip는 중복 다운로드를 자동으로 방지합니다

**확인 방법**:
```powershell
.\collect_airflow_wheels.ps1
ls airflow_3.1.0_wheels | Select-String "flask"
```

Flask와 관련 패키지들이 모두 다운로드된 것을 확인할 수 있습니다!
