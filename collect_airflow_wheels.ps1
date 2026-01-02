# Airflow 3.1.0 및 의존성 패키지 수집 스크립트 (Windows)
# 폐쇄망 환경에서 사용하기 위한 whl 파일 다운로드

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Airflow 3.1.0 의존성 패키지 수집" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# 출력 디렉토리 생성
$OUTPUT_DIR = "airflow_3.1.0_wheels"
New-Item -ItemType Directory -Force -Path $OUTPUT_DIR | Out-Null

# Python 버전 확인
$PYTHON_VERSION = python --version 2>&1 | Select-String -Pattern "\d+\.\d+" | ForEach-Object { $_.Matches.Value }
Write-Host "Python 버전: $PYTHON_VERSION" -ForegroundColor Cyan

# 플랫폼 확인
$PLATFORM = python -c "import platform; print(platform.system().lower())"
Write-Host "플랫폼: $PLATFORM" -ForegroundColor Cyan

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "1. Airflow 3.1.0 다운로드 중..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

pip download `
    --dest $OUTPUT_DIR `
    --python-version $PYTHON_VERSION `
    --platform win_amd64 `
    --only-binary=:all: `
    apache-airflow==3.1.0

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "2. 핵심 의존성 다운로드 중..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Airflow 핵심 의존성
$core_packages = @(
    "alembic",
    "argcomplete",
    "asgiref",
    "attrs",
    "blinker",
    "colorlog",
    "configupdater",
    "connexion",
    "cron-descriptor",
    "croniter",
    "cryptography",
    "deprecated",
    "dill",
    "flask",
    "flask-appbuilder",
    "flask-caching",
    "flask-login",
    "flask-session",
    "flask-wtf",
    "graphviz",
    "gunicorn",
    "httpx",
    "importlib-metadata",
    "importlib-resources",
    "itsdangerous",
    "jinja2",
    "jsonschema",
    "lazy-object-proxy",
    "linkify-it-py",
    "lockfile",
    "markdown",
    "markdown-it-py",
    "markupsafe",
    "marshmallow",
    "marshmallow-oneofschema",
    "mdit-py-plugins",
    "methodtools",
    "opentelemetry-api",
    "opentelemetry-exporter-otlp",
    "packaging",
    "pathspec",
    "pendulum",
    "pluggy",
    "psutil",
    "pygments",
    "pyjwt",
    "python-daemon",
    "python-dateutil",
    "python-nvd3",
    "python-slugify",
    "pytz",
    "pyyaml",
    "requests",
    "rfc3339-validator",
    "rich",
    "rich-argparse",
    "setproctitle",
    "sqlalchemy",
    "sqlalchemy-jsonfield",
    "tabulate",
    "tenacity",
    "termcolor",
    "typing-extensions",
    "unicodecsv",
    "werkzeug",
    "wtforms"
)

foreach ($package in $core_packages) {
    Write-Host "  다운로드 중: $package" -ForegroundColor Yellow
    pip download `
        --dest $OUTPUT_DIR `
        --python-version $PYTHON_VERSION `
        --platform win_amd64 `
        --only-binary=:all: `
        $package 2>&1 | Out-Null
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "3. 데이터베이스 드라이버 다운로드 중..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# PostgreSQL
Write-Host "  다운로드 중: psycopg2-binary" -ForegroundColor Yellow
pip download `
    --dest $OUTPUT_DIR `
    --python-version $PYTHON_VERSION `
    --platform win_amd64 `
    --only-binary=:all: `
    psycopg2-binary

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "4. Airflow Providers 다운로드 중..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

$providers = @(
    "apache-airflow-providers-http",
    "apache-airflow-providers-postgres",
    "apache-airflow-providers-amazon",
    "apache-airflow-providers-google",
    "apache-airflow-providers-slack",
    "apache-airflow-providers-email",
    "apache-airflow-providers-ftp",
    "apache-airflow-providers-ssh"
)

foreach ($provider in $providers) {
    Write-Host "  다운로드 중: $provider" -ForegroundColor Yellow
    pip download `
        --dest $OUTPUT_DIR `
        --python-version $PYTHON_VERSION `
        --platform win_amd64 `
        --only-binary=:all: `
        $provider 2>&1 | Out-Null
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "5. 추가 유틸리티 다운로드 중..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

$utilities = @("celery", "redis", "flower")

foreach ($util in $utilities) {
    Write-Host "  다운로드 중: $util" -ForegroundColor Yellow
    pip download `
        --dest $OUTPUT_DIR `
        --python-version $PYTHON_VERSION `
        --platform win_amd64 `
        --only-binary=:all: `
        $util 2>&1 | Out-Null
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "6. C to Java 프로젝트 의존성 다운로드 중..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# C to Java 프로젝트에서 사용하는 패키지들
$project_packages = @(
    "requests",
    "python-dotenv"
)

foreach ($package in $project_packages) {
    Write-Host "  다운로드 중: $package" -ForegroundColor Yellow
    pip download `
        --dest $OUTPUT_DIR `
        --python-version $PYTHON_VERSION `
        --platform win_amd64 `
        --only-binary=:all: `
        $package 2>&1 | Out-Null
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "완료!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

$file_count = (Get-ChildItem $OUTPUT_DIR).Count
$total_size = (Get-ChildItem $OUTPUT_DIR | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host "다운로드된 패키지 위치: $OUTPUT_DIR" -ForegroundColor Cyan
Write-Host "파일 개수: $file_count" -ForegroundColor Cyan
Write-Host "총 크기: $([math]::Round($total_size, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "폐쇄망 환경에서 설치 방법:" -ForegroundColor Yellow
Write-Host "  pip install --no-index --find-links=$OUTPUT_DIR apache-airflow==3.1.0" -ForegroundColor White
