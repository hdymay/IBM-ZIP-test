#!/bin/bash

# Airflow 3.1.0 및 의존성 패키지 수집 스크립트
# 폐쇄망 환경에서 사용하기 위한 whl 파일 다운로드

echo "=========================================="
echo "Airflow 3.1.0 의존성 패키지 수집"
echo "=========================================="

# 출력 디렉토리 생성
OUTPUT_DIR="airflow_3.1.0_wheels"
mkdir -p $OUTPUT_DIR

# Python 버전 확인
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "Python 버전: $PYTHON_VERSION"

# 플랫폼 확인
PLATFORM=$(python -c "import platform; print(platform.system().lower())")
echo "플랫폼: $PLATFORM"

# 아키텍처 확인
ARCH=$(python -c "import platform; print(platform.machine())")
echo "아키텍처: $ARCH"

echo ""
echo "=========================================="
echo "1. Airflow 3.1.0 다운로드 중..."
echo "=========================================="

pip download \
    --dest $OUTPUT_DIR \
    --python-version $PYTHON_VERSION \
    --platform manylinux2014_x86_64 \
    --platform manylinux_2_17_x86_64 \
    --platform win_amd64 \
    --only-binary=:all: \
    apache-airflow==3.1.0

echo ""
echo "=========================================="
echo "2. 핵심 의존성 다운로드 중..."
echo "=========================================="

# Airflow 핵심 의존성
pip download \
    --dest $OUTPUT_DIR \
    --python-version $PYTHON_VERSION \
    --platform manylinux2014_x86_64 \
    --platform manylinux_2_17_x86_64 \
    --platform win_amd64 \
    --only-binary=:all: \
    alembic \
    argcomplete \
    asgiref \
    attrs \
    blinker \
    colorlog \
    configupdater \
    connexion \
    cron-descriptor \
    croniter \
    cryptography \
    deprecated \
    dill \
    flask \
    flask-appbuilder \
    flask-caching \
    flask-login \
    flask-session \
    flask-wtf \
    graphviz \
    gunicorn \
    httpx \
    importlib-metadata \
    importlib-resources \
    itsdangerous \
    jinja2 \
    jsonschema \
    lazy-object-proxy \
    linkify-it-py \
    lockfile \
    markdown \
    markdown-it-py \
    markupsafe \
    marshmallow \
    marshmallow-oneofschema \
    mdit-py-plugins \
    methodtools \
    opentelemetry-api \
    opentelemetry-exporter-otlp \
    packaging \
    pathspec \
    pendulum \
    pluggy \
    psutil \
    pygments \
    pyjwt \
    python-daemon \
    python-dateutil \
    python-nvd3 \
    python-slugify \
    pytz \
    pyyaml \
    requests \
    rfc3339-validator \
    rich \
    rich-argparse \
    setproctitle \
    sqlalchemy \
    sqlalchemy-jsonfield \
    tabulate \
    tenacity \
    termcolor \
    typing-extensions \
    unicodecsv \
    werkzeug \
    wtforms

echo ""
echo "=========================================="
echo "3. 데이터베이스 드라이버 다운로드 중..."
echo "=========================================="

# PostgreSQL
pip download \
    --dest $OUTPUT_DIR \
    --python-version $PYTHON_VERSION \
    --platform manylinux2014_x86_64 \
    --platform manylinux_2_17_x86_64 \
    --platform win_amd64 \
    --only-binary=:all: \
    psycopg2-binary

# MySQL
pip download \
    --dest $OUTPUT_DIR \
    --python-version $PYTHON_VERSION \
    --platform manylinux2014_x86_64 \
    --platform manylinux_2_17_x86_64 \
    --platform win_amd64 \
    --only-binary=:all: \
    mysqlclient

echo ""
echo "=========================================="
echo "4. Airflow Providers 다운로드 중..."
echo "=========================================="

# 주요 Providers
pip download \
    --dest $OUTPUT_DIR \
    --python-version $PYTHON_VERSION \
    --platform manylinux2014_x86_64 \
    --platform manylinux_2_17_x86_64 \
    --platform win_amd64 \
    --only-binary=:all: \
    apache-airflow-providers-http \
    apache-airflow-providers-postgres \
    apache-airflow-providers-mysql \
    apache-airflow-providers-amazon \
    apache-airflow-providers-google \
    apache-airflow-providers-slack \
    apache-airflow-providers-email \
    apache-airflow-providers-ftp \
    apache-airflow-providers-ssh

echo ""
echo "=========================================="
echo "5. 추가 유틸리티 다운로드 중..."
echo "=========================================="

pip download \
    --dest $OUTPUT_DIR \
    --python-version $PYTHON_VERSION \
    --platform manylinux2014_x86_64 \
    --platform manylinux_2_17_x86_64 \
    --platform win_amd64 \
    --only-binary=:all: \
    celery \
    redis \
    flower

echo ""
echo "=========================================="
echo "6. C to Java 프로젝트 의존성 다운로드 중..."
echo "=========================================="

pip download \
    --dest $OUTPUT_DIR \
    --python-version $PYTHON_VERSION \
    --platform manylinux2014_x86_64 \
    --platform manylinux_2_17_x86_64 \
    --platform win_amd64 \
    --only-binary=:all: \
    requests \
    python-dotenv

echo ""
echo "=========================================="
echo "완료!"
echo "=========================================="
echo ""
echo "다운로드된 패키지 위치: $OUTPUT_DIR"
echo "파일 개수: $(ls -1 $OUTPUT_DIR | wc -l)"
echo "총 크기: $(du -sh $OUTPUT_DIR | cut -f1)"
echo ""
echo "폐쇄망 환경에서 설치 방법:"
echo "  pip install --no-index --find-links=$OUTPUT_DIR apache-airflow==3.1.0"
