#!/bin/bash

# Airflow 시작 스크립트

echo "=========================================="
echo "Airflow 시작 중..."
echo "=========================================="

# 환경 변수 파일 확인
if [ ! -f .env ]; then
    echo "⚠ .env 파일이 없습니다."
    echo "📝 .env.airflow.example을 .env로 복사하고 값을 입력하세요."
    echo ""
    echo "cp .env.airflow.example .env"
    exit 1
fi

# Docker Compose 파일 확인
if [ ! -f docker-compose.airflow.yml ]; then
    echo "❌ docker-compose.airflow.yml 파일이 없습니다."
    exit 1
fi

# 초기화 여부 확인
if [ ! -d "logs" ]; then
    echo "📦 Airflow 초기화 중..."
    docker-compose -f docker-compose.airflow.yml up airflow-init
    echo ""
fi

# Airflow 시작
echo "🚀 Airflow 컨테이너 시작 중..."
docker-compose -f docker-compose.airflow.yml up -d

# 상태 확인
echo ""
echo "⏳ 서비스 시작 대기 중 (10초)..."
sleep 10

echo ""
echo "=========================================="
echo "✓ Airflow 시작 완료!"
echo "=========================================="
echo ""
echo "📊 웹 UI: http://localhost:8080"
echo "   Username: airflow"
echo "   Password: airflow"
echo ""
echo "🌸 Flower: http://localhost:5555"
echo ""
echo "📝 로그 확인:"
echo "   docker-compose -f docker-compose.airflow.yml logs -f"
echo ""
echo "🛑 중지:"
echo "   docker-compose -f docker-compose.airflow.yml down"
echo ""
echo "=========================================="
