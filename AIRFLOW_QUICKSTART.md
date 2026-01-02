# Airflow 빠른 시작 가이드

## 1. 초기 설정 (최초 1회만)

### 환경 변수 설정
```bash
# .env.airflow.example을 .env로 복사
cp .env.airflow.example .env

# .env 파일 편집 (필요한 값 입력)
# - WATSONX_API_KEY
# - WATSONX_PROJECT_ID
# - WATSONX_NOTEBOOK_ASSET_ID (Notebook Job 사용 시)
```

### Airflow 초기화
```bash
# Docker 이미지 빌드 및 초기화
docker-compose -f docker-compose.airflow.yml up airflow-init

# 완료 메시지 확인:
# "airflow-init_1 exited with code 0"
```

## 2. Airflow 시작

### 전체 서비스 시작
```bash
docker-compose -f docker-compose.airflow.yml up -d
```

**시작되는 서비스:**
- `postgres`: 메타데이터 데이터베이스
- `redis`: 메시지 브로커
- `airflow-webserver`: 웹 UI (포트 8080)
- `airflow-scheduler`: DAG 스케줄러
- `airflow-worker`: Task 실행 워커
- `airflow-triggerer`: 이벤트 트리거
- `flower`: Celery 모니터링 (포트 5555)

### 상태 확인
```bash
# 컨테이너 상태 확인
docker-compose -f docker-compose.airflow.yml ps

# 로그 확인 (실시간)
docker-compose -f docker-compose.airflow.yml logs -f

# 특정 서비스 로그만 확인
docker-compose -f docker-compose.airflow.yml logs -f airflow-webserver
docker-compose -f docker-compose.airflow.yml logs -f airflow-scheduler
```

## 3. 웹 UI 접속

### Airflow 웹 UI
```
URL: http://localhost:8080
Username: airflow
Password: airflow
```

### Flower (Celery 모니터링)
```
URL: http://localhost:5555
```

## 4. DAG 실행

### 방법 1: 웹 UI에서 실행 (권장)

1. **DAG 목록 확인**
   - 메인 페이지에서 DAG 목록 확인
   - 검색창에서 DAG 이름 검색

2. **DAG 활성화**
   - DAG 왼쪽의 토글 스위치 클릭 (OFF → ON)
   - 활성화하면 스케줄에 따라 자동 실행

3. **수동 실행**
   - DAG 오른쪽의 **▶ (Play)** 버튼 클릭
   - **Trigger DAG** 선택
   - (선택) Configuration JSON 입력 가능

4. **실행 확인**
   - DAG 이름 클릭 → **Grid View**
   - 각 Task의 상태 확인 (초록색: 성공, 빨간색: 실패)
   - Task 클릭 → **Logs** 탭에서 상세 로그 확인

### 방법 2: CLI에서 실행

```bash
# DAG 목록 확인
docker-compose -f docker-compose.airflow.yml exec airflow-webserver airflow dags list

# DAG 수동 실행
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow dags trigger watsonx_notebook_job_pipeline

# DAG 실행 이력 확인
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow dags list-runs -d watsonx_notebook_job_pipeline

# 특정 Task 로그 확인
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow tasks logs watsonx_notebook_job_pipeline create_job 2025-01-01
```

### 방법 3: Python API에서 실행

```python
from airflow.api.client.local_client import Client

client = Client(None, None)

# DAG 트리거
client.trigger_dag(
    dag_id='watsonx_notebook_job_pipeline',
    conf={'key': 'value'}  # 선택적 설정
)
```

## 5. DAG 개발 및 테스트

### DAG 파일 위치
```
dags/
├── watsonx_notebook_job_pipeline.py  # Notebook Job 실행
├── c_to_java_pipeline.py             # 기본 파이프라인
├── c_to_java_samples_pipeline.py     # 샘플 실행
├── c_to_java_taskflow.py             # TaskFlow API
└── c_to_java_class_based.py          # 클래스 기반
```

### DAG 파일 수정 후
```bash
# Airflow는 자동으로 DAG 파일 변경을 감지합니다 (약 30초 소요)
# 강제로 새로고침하려면:
docker-compose -f docker-compose.airflow.yml restart airflow-scheduler
```

### DAG 구문 검사
```bash
# DAG 파일 구문 오류 확인
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow dags test watsonx_notebook_job_pipeline 2025-01-01
```

### 특정 Task만 테스트
```bash
# 특정 Task만 실행 (디버깅용)
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow tasks test watsonx_notebook_job_pipeline get_iam_token 2025-01-01
```

## 6. 모니터링

### 웹 UI에서 확인

**DAG 실행 상태:**
- **Grid View**: 시간별 실행 이력
- **Graph View**: Task 의존성 그래프
- **Calendar View**: 월별 실행 성공/실패
- **Gantt View**: Task 실행 시간 분석

**Task 상태:**
- 🟢 **Success**: 성공
- 🔴 **Failed**: 실패
- 🟡 **Running**: 실행 중
- ⚪ **Queued**: 대기 중
- 🟠 **Upstream Failed**: 이전 Task 실패
- ⏭️ **Skipped**: 건너뜀

### 로그 확인

```bash
# Scheduler 로그 (DAG 스케줄링)
docker-compose -f docker-compose.airflow.yml logs -f airflow-scheduler

# Worker 로그 (Task 실행)
docker-compose -f docker-compose.airflow.yml logs -f airflow-worker

# Webserver 로그 (UI 접속)
docker-compose -f docker-compose.airflow.yml logs -f airflow-webserver
```

### Flower에서 Celery 모니터링
```
http://localhost:5555
```
- Worker 상태 확인
- Task 큐 상태
- Task 실행 통계

## 7. 문제 해결

### DAG가 목록에 안 보이는 경우

**원인 1: 구문 오류**
```bash
# DAG 파일 구문 검사
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  python /opt/airflow/dags/watsonx_notebook_job_pipeline.py
```

**원인 2: Import 오류**
```bash
# Python 패키지 설치
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  pip install requests
```

**원인 3: 파일 권한**
```bash
# DAG 파일 권한 확인
ls -la dags/

# 권한 수정 (필요시)
chmod 644 dags/*.py
```

### Task가 실패하는 경우

**로그 확인:**
1. 웹 UI에서 실패한 Task 클릭
2. **Logs** 탭에서 에러 메시지 확인
3. **Try Number** 선택하여 재시도 로그 확인

**재실행:**
1. Task 클릭 → **Clear** 버튼
2. 또는 DAG 전체 재실행: **Actions** → **Clear**

### 환경 변수가 안 읽히는 경우

```bash
# 컨테이너 내부에서 환경 변수 확인
docker-compose -f docker-compose.airflow.yml exec airflow-webserver env | grep WATSONX

# .env 파일 수정 후 재시작
docker-compose -f docker-compose.airflow.yml restart
```

### 데이터베이스 초기화 (주의: 모든 데이터 삭제)

```bash
# 모든 컨테이너 중지 및 삭제
docker-compose -f docker-compose.airflow.yml down -v

# 다시 초기화
docker-compose -f docker-compose.airflow.yml up airflow-init
docker-compose -f docker-compose.airflow.yml up -d
```

## 8. 중지 및 정리

### 일시 중지
```bash
# 컨테이너 중지 (데이터 유지)
docker-compose -f docker-compose.airflow.yml stop
```

### 재시작
```bash
# 중지된 컨테이너 재시작
docker-compose -f docker-compose.airflow.yml start
```

### 완전 종료
```bash
# 컨테이너 중지 및 삭제 (데이터 유지)
docker-compose -f docker-compose.airflow.yml down

# 컨테이너 및 볼륨 모두 삭제 (데이터 삭제)
docker-compose -f docker-compose.airflow.yml down -v
```

### 로그 정리
```bash
# 로그 파일 삭제
rm -rf logs/*
```

## 9. 유용한 명령어 모음

### 컨테이너 관리
```bash
# 상태 확인
docker-compose -f docker-compose.airflow.yml ps

# 특정 서비스 재시작
docker-compose -f docker-compose.airflow.yml restart airflow-scheduler

# 컨테이너 내부 접속
docker-compose -f docker-compose.airflow.yml exec airflow-webserver bash
```

### DAG 관리
```bash
# DAG 목록
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow dags list

# DAG 일시 중지
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow dags pause watsonx_notebook_job_pipeline

# DAG 재개
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow dags unpause watsonx_notebook_job_pipeline
```

### 사용자 관리
```bash
# 사용자 목록
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow users list

# 새 사용자 생성
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin123
```

## 10. 프로덕션 배포 시 고려사항

### 보안
- 기본 비밀번호 변경
- Fernet 키 재생성
- Secret Key 재생성
- HTTPS 설정

### 성능
- Worker 수 증가
- 데이터베이스 최적화 (PostgreSQL 튜닝)
- Redis 메모리 증가

### 모니터링
- 로그 수집 (ELK Stack, CloudWatch 등)
- 메트릭 수집 (Prometheus, Grafana)
- 알림 설정 (Slack, Email)

### 백업
- 메타데이터 데이터베이스 백업
- DAG 파일 버전 관리 (Git)
- 로그 아카이빙

## 참고 자료

- [Airflow 공식 문서](https://airflow.apache.org/docs/)
- [Docker Compose 가이드](https://docs.docker.com/compose/)
- [watsonx.ai API 문서](https://cloud.ibm.com/apidocs/watson-data-api)
