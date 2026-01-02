# Airflow vs watsonx Job 비교

## 시나리오별 비교

### 시나리오 1: 단순 Notebook 실행

**요구사항:**
- 매일 오전 9시에 Notebook 1개 실행
- 실패 시 재시도

**watsonx Job만 사용:**
```
✓ 충분함
- watsonx Job 스케줄 설정
- 재시도 설정
```

**결론:** watsonx Job만으로 충분

---

### 시나리오 2: 복잡한 파이프라인

**요구사항:**
- 데이터 수집 → 전처리 → 변환 → 검증 → 저장
- 각 단계가 다른 환경에서 실행
- 실패 시 특정 단계만 재실행

**watsonx Job만 사용:**
```
✗ 어려움
- 모든 로직을 하나의 Notebook에 넣어야 함
- 외부 시스템 연동 복잡
- 부분 재실행 불가능
```

**Airflow 사용:**
```
✓ 적합
- 각 단계를 독립적인 Task로 분리
- 실패한 Task만 재실행
- 외부 시스템 쉽게 연동
```

**결론:** Airflow 필요

---

### 시나리오 3: 여러 Notebook 조율

**요구사항:**
- Notebook A 실행 → 성공 시 Notebook B, C 병렬 실행
- B, C 완료 후 Notebook D 실행
- 조건부 실행 (데이터 크기에 따라 다른 Notebook 실행)

**watsonx Job만 사용:**
```
✗ 불가능
- 병렬 실행 어려움
- 조건부 로직 구현 불가능
- Notebook 간 의존성 관리 어려움
```

**Airflow 사용:**
```
✓ 완벽
- Task 의존성 명확히 정의
- 병렬 실행 지원
- 조건부 분기 (BranchOperator)
```

**결론:** Airflow 필수

---

## 실제 사용 패턴

### 패턴 1: watsonx Job만 사용 (단순)

```
watsonx Job (스케줄: 매일 9시)
└── Notebook: C to Java 변환
    ├── Git에서 코드 가져오기
    ├── 변환 실행
    └── 결과 저장
```

**적합한 경우:**
- 단일 Notebook 실행
- 외부 시스템 연동 불필요
- 간단한 스케줄

---

### 패턴 2: Airflow + watsonx Job (복잡)

```
Airflow DAG (스케줄: 매일 9시)
├── Task 1: S3에서 데이터 다운로드
├── Task 2: 데이터 검증
├── Task 3: watsonx Notebook Job 실행
│   └── Notebook: C to Java 변환
├── Task 4: 결과 검증
├── Task 5: 결과를 PostgreSQL에 저장
└── Task 6: Slack 알림
```

**적합한 경우:**
- 여러 단계의 파이프라인
- 외부 시스템 연동 필요
- 복잡한 에러 처리
- 통합 모니터링 필요

---

## 구체적인 장점 비교

### 1. 워크플로우 관리

**watsonx Job:**
```python
# 모든 로직을 하나의 Notebook에
# Cell 1: 데이터 수집
# Cell 2: 전처리
# Cell 3: 변환
# Cell 4: 저장
# → 실패 시 전체 재실행
```

**Airflow:**
```python
# 각 단계를 독립적인 Task로
collect_data >> preprocess >> transform >> save
# → 실패한 Task만 재실행
```

---

### 2. 외부 시스템 연동

**watsonx Job:**
```python
# Notebook 내에서 직접 구현
import requests
response = requests.post("https://api.example.com/data")
# → 인증, 재시도 등 모두 직접 구현
```

**Airflow:**
```python
# 검증된 Operator 사용
from airflow.providers.http.operators.http import SimpleHttpOperator

call_api = SimpleHttpOperator(
    task_id='call_api',
    http_conn_id='my_api',  # 연결 정보 중앙 관리
    endpoint='/data',
    method='POST',
    # 재시도, 타임아웃 등 자동 처리
)
```

---

### 3. 조건부 실행

**watsonx Job:**
```python
# Notebook 내에서 if-else
if data_size > 1000000:
    # 대용량 처리 로직
else:
    # 소용량 처리 로직
# → 하나의 Notebook에 모든 로직
```

**Airflow:**
```python
# 조건에 따라 다른 Task 실행
from airflow.operators.python import BranchPythonOperator

def choose_task(**context):
    if data_size > 1000000:
        return 'large_data_task'
    else:
        return 'small_data_task'

branch = BranchPythonOperator(
    task_id='branch',
    python_callable=choose_task
)

branch >> [large_data_task, small_data_task]
```

---

### 4. 병렬 실행

**watsonx Job:**
```python
# Notebook 내에서 순차 실행만 가능
process_type_a()  # 10분 소요
process_type_b()  # 10분 소요
process_type_c()  # 10분 소요
# → 총 30분
```

**Airflow:**
```python
# 병렬 실행
start >> [task_a, task_b, task_c] >> end
# → 총 10분 (병렬 실행)
```

---

### 5. 모니터링 및 알림

**watsonx Job:**
- watsonx 웹 UI에서만 확인
- 알림 설정 제한적
- 로그 검색 어려움

**Airflow:**
- 통합 대시보드
- 다양한 알림 채널 (Slack, Email, PagerDuty)
- 중앙화된 로그 관리
- 메트릭 수집 (Prometheus, Grafana)

---

## 실제 프로덕션 예시

### 예시 1: 데이터 파이프라인

```
Airflow DAG: daily_data_pipeline
├── 00:00 - S3에서 원본 데이터 다운로드
├── 00:10 - 데이터 품질 검증
├── 00:20 - watsonx Notebook Job 1 (데이터 변환)
├── 00:40 - watsonx Notebook Job 2 (ML 모델 학습)
├── 01:00 - 결과를 Snowflake에 저장
├── 01:10 - 대시보드 업데이트
└── 01:15 - Slack 알림
```

**왜 Airflow가 필요한가?**
- S3, Snowflake 연동 (Airflow Operator 사용)
- 데이터 검증 실패 시 알림만 보내고 중단
- 두 Notebook을 순차 실행하되, 각각 독립적으로 재시도
- 전체 파이프라인 모니터링

---

### 예시 2: ML 파이프라인

```
Airflow DAG: ml_training_pipeline
├── 데이터 준비 (로컬 Python)
├── 특징 추출 (watsonx Notebook)
├── 모델 학습 (watsonx Notebook)
│   ├── 성공 → 모델 배포
│   └── 실패 → 이전 모델 유지
├── A/B 테스트 설정
└── 모니터링 대시보드 업데이트
```

**왜 Airflow가 필요한가?**
- 조건부 배포 (성공 시에만)
- 여러 환경 조율 (로컬 + watsonx)
- 배포 자동화
- 롤백 메커니즘

---

## 비용 및 복잡도 고려

### watsonx Job만 사용

**비용:**
- watsonx 사용료만

**복잡도:**
- 낮음 (설정 간단)

**적합한 경우:**
- 프로토타입
- 단순 파이프라인
- 소규모 프로젝트

---

### Airflow + watsonx Job

**비용:**
- watsonx 사용료
- Airflow 인프라 비용 (서버, 데이터베이스)

**복잡도:**
- 높음 (Airflow 학습 필요)

**적합한 경우:**
- 프로덕션 환경
- 복잡한 파이프라인
- 여러 시스템 통합
- 엔터프라이즈 요구사항

---

## 결론 및 권장사항

### 단계별 접근

**1단계: 프로토타입 (watsonx Job만)**
```
watsonx Job
└── Notebook: 기본 변환 로직
```

**2단계: 검증 (Airflow 추가)**
```
Airflow
├── 데이터 검증
├── watsonx Job 실행
└── 결과 검증
```

**3단계: 프로덕션 (완전한 파이프라인)**
```
Airflow
├── 데이터 수집 (여러 소스)
├── 전처리 및 검증
├── watsonx Job 실행 (여러 Notebook)
├── 후처리
├── 저장 (여러 대상)
└── 모니터링 및 알림
```

---

## 의사결정 플로우차트

```
시작
 ↓
단일 Notebook만 실행? ─ Yes → watsonx Job만 사용
 ↓ No
외부 시스템 연동 필요? ─ Yes → Airflow 사용
 ↓ No
여러 Notebook 조율 필요? ─ Yes → Airflow 사용
 ↓ No
조건부 실행 필요? ─ Yes → Airflow 사용
 ↓ No
복잡한 에러 처리 필요? ─ Yes → Airflow 사용
 ↓ No
통합 모니터링 필요? ─ Yes → Airflow 사용
 ↓ No
watsonx Job만 사용
```

---

## 요약

**watsonx Job만 사용:**
- 단순한 경우
- 빠른 프로토타입
- 학습 곡선 낮음

**Airflow + watsonx Job:**
- 복잡한 파이프라인
- 여러 시스템 통합
- 엔터프라이즈 요구사항
- 완전한 자동화

**핵심:** 
watsonx Job은 "Notebook 실행"에 특화되어 있고,
Airflow는 "전체 워크플로우 오케스트레이션"에 특화되어 있습니다.

둘을 함께 사용하면 각각의 장점을 활용할 수 있습니다!
