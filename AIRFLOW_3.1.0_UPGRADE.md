# Airflow 3.1.0 업그레이드 완료

## 변경 사항

### 버전
- **이전**: Apache Airflow 2.8.1
- **현재**: Apache Airflow 3.1.0

### 주요 변경사항

#### 1. 명령어 변경
```yaml
# 이전 (2.x)
command: webserver

# 현재 (3.x)
command: api-server
```

Airflow 3.x에서는 `webserver` 명령어가 `api-server`로 변경되었습니다.

#### 2. Docker Compose 설정
```yaml
x-airflow-common:
  &airflow-common
  image: apache/airflow:3.1.0  # 2.8.1 → 3.1.0
```

## 확인 방법

### 1. 버전 확인
```bash
docker-compose -f docker-compose.airflow.yml exec airflow-scheduler airflow version
```

**출력:**
```
3.1.0
```

### 2. 서비스 상태 확인
```bash
docker-compose -f docker-compose.airflow.yml ps
```

**예상 출력:**
```
NAME                          STATUS
ctojava-airflow-scheduler-1   Up (healthy)
ctojava-airflow-webserver-1   Up (healthy)
ctojava-postgres-1            Up (healthy)
```

### 3. 웹 UI 접속
```
http://localhost:8080
Username: airflow
Password: airflow
```

## Airflow 3.x 주요 신기능

### 1. 개선된 UI
- 더 빠른 렌더링
- 향상된 사용자 경험
- 새로운 디자인

### 2. 성능 향상
- 더 빠른 DAG 파싱
- 개선된 스케줄러 성능
- 메모리 사용량 최적화

### 3. API 개선
- RESTful API 개선
- 더 나은 인증 메커니즘
- 향상된 에러 처리

### 4. TaskFlow API 개선
- 더 간단한 구문
- 향상된 타입 힌팅
- 더 나은 디버깅

## 호환성 확인

### 기존 DAG 호환성
대부분의 Airflow 2.x DAG는 3.x에서도 동작합니다. 하지만 일부 변경사항이 있을 수 있습니다:

#### 1. Deprecated 기능 제거
```python
# 2.x에서 deprecated된 기능들이 3.x에서 제거됨
# 예: 일부 오래된 Operator
```

#### 2. Import 경로 변경
```python
# 일부 import 경로가 변경되었을 수 있음
# 예시:
# 이전: from airflow.operators.python_operator import PythonOperator
# 현재: from airflow.operators.python import PythonOperator
```

### 테스트 권장사항
1. 모든 DAG가 정상적으로 로드되는지 확인
2. 각 DAG를 수동으로 실행하여 테스트
3. 로그에서 경고 메시지 확인

## 문제 해결

### DAG가 로드되지 않는 경우

#### 1. DAG 파일 구문 검사
```bash
docker-compose -f docker-compose.airflow.yml exec airflow-scheduler \
  python /opt/airflow/dags/your_dag.py
```

#### 2. Scheduler 로그 확인
```bash
docker-compose -f docker-compose.airflow.yml logs airflow-scheduler --tail=100
```

#### 3. DAG 파일 권한 확인
```bash
ls -la dags/
```

### Webserver가 시작되지 않는 경우

#### 1. 로그 확인
```bash
docker-compose -f docker-compose.airflow.yml logs airflow-webserver --tail=100
```

#### 2. 데이터베이스 마이그레이션 확인
```bash
docker-compose -f docker-compose.airflow.yml exec airflow-scheduler \
  airflow db check
```

#### 3. 재시작
```bash
docker-compose -f docker-compose.airflow.yml restart airflow-webserver
```

### 이전 버전으로 롤백

필요한 경우 이전 버전으로 롤백할 수 있습니다:

```bash
# 1. 서비스 중지
docker-compose -f docker-compose.airflow.yml down

# 2. docker-compose.airflow.yml 수정
# image: apache/airflow:3.1.0 → image: apache/airflow:2.8.1
# command: api-server → command: webserver

# 3. 재시작
docker-compose -f docker-compose.airflow.yml up -d
```

## 마이그레이션 체크리스트

- [x] Docker Compose 파일 업데이트
- [x] 명령어 변경 (webserver → api-server)
- [x] 서비스 재시작
- [x] 버전 확인
- [ ] 웹 UI 접속 확인
- [ ] DAG 목록 확인
- [ ] 샘플 DAG 실행 테스트
- [ ] 로그 확인
- [ ] 성능 모니터링

## 다음 단계

### 1. 웹 UI 확인
```
http://localhost:8080
```

### 2. DAG 테스트
```bash
# DAG 목록 확인
docker-compose -f docker-compose.airflow.yml exec airflow-scheduler \
  airflow dags list

# 샘플 DAG 실행
docker-compose -f docker-compose.airflow.yml exec airflow-scheduler \
  airflow dags trigger result_demo_pipeline
```

### 3. 모니터링
- CPU 사용량
- 메모리 사용량
- DAG 실행 시간
- 에러 로그

## 참고 자료

- [Airflow 3.0 Release Notes](https://airflow.apache.org/docs/apache-airflow/3.0.0/release_notes.html)
- [Migration Guide](https://airflow.apache.org/docs/apache-airflow/3.0.0/migration-guide.html)
- [Breaking Changes](https://airflow.apache.org/docs/apache-airflow/3.0.0/breaking-changes.html)

## 요약

Airflow 3.1.0 업그레이드가 완료되었습니다!

- 버전: 2.8.1 → 3.1.0
- 명령어: webserver → api-server
- 상태: 실행 중
- 다음: 웹 UI 접속 및 DAG 테스트

웹 UI가 완전히 시작되면 (약 1-2분 소요) http://localhost:8080 에서 확인할 수 있습니다.
