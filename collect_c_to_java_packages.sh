#!/bin/bash

# C to Java 프로젝트 전용 패키지 수집 스크립트
# 회사 Airflow 서버에 추가로 필요한 패키지만 다운로드

echo "=========================================="
echo "C to Java 프로젝트 패키지 수집"
echo "=========================================="
echo ""
echo "이 스크립트는 회사 Airflow 서버에 추가로 필요한"
echo "C to Java 프로젝트 전용 패키지만 다운로드합니다."
echo ""
echo "회사 Airflow에 이미 설치된 패키지는 제외됩니다:"
echo "  - Flask (Airflow UI용)"
echo "  - SQLAlchemy (Airflow 메타데이터용)"
echo "  - Jinja2, Pendulum 등 Airflow 기본 패키지"
echo ""

# 출력 디렉토리 생성
OUTPUT_DIR="c_to_java_wheels"
mkdir -p $OUTPUT_DIR

# Python 버전 확인
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "Python 버전: $PYTHON_VERSION"
echo ""

echo "=========================================="
echo "C to Java 프로젝트 전용 패키지 다운로드"
echo "=========================================="

# C to Java 프로젝트에서 사용하는 패키지 (Airflow 기본 패키지 제외)
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
echo "다운로드된 패키지:"
ls -1 $OUTPUT_DIR | sed 's/^/  - /'
echo ""
echo "회사 Airflow 서버에서 설치 방법:"
echo "  pip install --no-index --find-links=$OUTPUT_DIR requests python-dotenv"
echo ""
echo "USB로 전송:"
echo "  tar -czf c_to_java_wheels.tar.gz $OUTPUT_DIR"
