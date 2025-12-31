# Airflow로 Samples 실행하기

## 동작 방식 설명

### 1. 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    Airflow 웹 UI                             │
│                  (http://localhost:8080)                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Airflow Scheduler                           │
│              (DAG 파일 읽고 Task 스케줄링)                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    DAG 파일                                  │
│        dags/c_to_java_samples_pipeline.py                   │
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│  │ Task 1   │──▶│ Task 2   │──▶│ Task 3   │──▶ ...        │
│  │ Ingest   │   │ Parse    │   │ Extract  │               │
│  └──────────┘   └──────────┘   └──────────┘               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Samples 폴더                                │
│              (Docker 볼륨으로 마운트됨)                       │
│                                                              │
│  samples/ingest.py    ──▶  실제 실행되는 Python 스크립트     │
│  samples/parse.py                                            │
│  samples/extract.py                                          │
│  ...                                                         │
└─────────────────────────────────────────────────────────────┘
```

### 2. 실행 흐름

#### Step 1: DAG 파일 감지
```
1. Airflow Scheduler가 dags/ 폴더를 주기적으로 스캔
2. c_to_java_samples_pipeline.py 파일 발견
3. DAG 정의를 파싱하여 메타데이터 DB에 저장
```

#### Step 2: 사용자가 DAG 실행
```
1. 웹 UI에서 "Trigger DAG" 버튼 클릭
2. Scheduler가 첫 번째 Task (step_1_ingest) 실행 시작
```

#### Step 3: Task 실행
```
Task: step_1_ingest
  ↓
PythonOperator가 run_ingest() 함수 호출
  ↓
run_ingest()가 samples/ingest.py의 main() 함수 호출
  ↓
ingest.main() 실행 (C 파일 수집 시뮬레이션)
  ↓
결과를 XCom에 저장 (다른 Task에서 사용 가능)
  ↓
Task 완료
```

#### Step 4: 다음 Task로 진행
```
step_1_ingest 완료
  ↓
step_2_parse 시작
  ↓
step_3_extract 시작
  ↓
... (순차적으로 모든 Task 실행)
  ↓
step_7_report 완료
  ↓
전체 DAG 실행 완료
```

### 3. 파일 구조

```
프로젝트 루트/
├── dags/                                    # Airflow DAG 정의
│   ├── c_to_java_pipeline.py               # 기존 DAG (src/ 폴더 사용)
│   └── c_to_java_samples_pipeline.py       # 새 DAG (samples/ 폴더 사용)
│
├── samples/                                 # 실제 실행될 Python 스크립트
│   ├── main.py                             # 로컬에서 직접 실행용
│   ├── ingest.py                           # 1단계: 데이터 수집
│   ├── parse.py                            # 2단계: 파싱
│   ├── extract.py                          # 3단계: 추출
│   ├── transform.py                        # 4단계: 변환
│   ├── generate.py                         # 5단계: 생성
│   ├── validate.py                         # 6단계: 검증
│   └── report.py                           # 7단계: 보고서
│
└── docker-compose.airflow.yml              # Docker 설정
    volumes:
      - ./samples:/opt/airflow/samples      # samples 폴더 마운트
```

### 4. 실행 방법 비교

#### 방법 1: 로컬에서 직접 실행
```bash
cd samples
python main.py
```
- 장점: 간단하고 빠름
- 단점: 스케줄링 불가, 모니터링 어려움, 재실행 어려움

#### 방법 2: Airflow로 실행 (권장)
```bash
# 웹 UI에서 "Trigger DAG" 클릭
```
- 장점:
  - 각 단계별 실행 상태 시각화
  - 실패한 단계만 재실행 가능
  - 로그 관리 용이
  - 스케줄링 가능 (매일, 매주 등)
  - 병렬 실행 가능 (의존성 없는 Task)
  - 알림 설정 가능 (실패 시 이메일 등)

## 실습 가이드

### 1. DAG 확인
```bash
# Scheduler 재시작 (새 DAG 파일 인식)
docker-compose -f docker-compose.airflow.yml restart airflow-scheduler

# 약 30초 후 웹 UI에서 확인
# http://localhost:8080
```

### 2. DAG 실행
1. 웹 UI에서 `c_to_java_samples_pipeline` 찾기
2. 왼쪽 토글 버튼 클릭하여 활성화
3. 우측 "▶" (Trigger DAG) 버튼 클릭

### 3. 실행 모니터링

#### Graph View (그래프 뷰)
```
[step_1_ingest] → [step_2_parse] → [step_3_extract] → [step_4_transform]
                                                              ↓
                                    [step_7_report] ← [step_6_validate] ← [step_5_generate]
```
- 각 Task의 상태를 색상으로 표시
  - 초록색: 성공
  - 빨간색: 실패
  - 노란색: 실행 중
  - 회색: 대기 중

#### Grid View (그리드 뷰)
```
DAG Run │ step_1 │ step_2 │ step_3 │ ...
────────┼────────┼────────┼────────┼────
Run 1   │   ✓    │   ✓    │   ✓    │ ...
Run 2   │   ✓    │   ✗    │   -    │ ...
```
- 여러 실행의 이력을 한눈에 확인

#### Logs (로그)
```
[2025-12-31 16:30:00] INFO: Starting data ingestion phase
[2025-12-31 16:30:01] INFO: Scanning for C source files...
[2025-12-31 16:30:02] INFO: Found 15 C source files
...
```
- 각 Task의 상세 실행 로그 확인

### 4. 고급 기능

#### 특정 Task만 재실행
1. Grid View에서 실패한 Task 클릭
2. "Clear" 버튼 클릭
3. 해당 Task부터 다시 실행

#### 병렬 실행 설정
DAG 파일 수정:
```python
# 의존성 없는 Task는 병렬 실행 가능
task_5_generate >> [task_6_validate, task_upload_github]
```

#### 스케줄링 설정
```python
# 매일 오전 9시 자동 실행
schedule_interval='0 9 * * *'

# 매주 월요일 실행
schedule_interval='0 0 * * 1'

# Cron 표현식 사용
schedule_interval='*/30 * * * *'  # 30분마다
```

#### 조건부 실행
```python
from airflow.operators.python import BranchPythonOperator

def decide_branch(**context):
    # 조건에 따라 다른 Task 실행
    if some_condition:
        return 'task_a'
    else:
        return 'task_b'

branch_task = BranchPythonOperator(
    task_id='branch',
    python_callable=decide_branch,
)
```

## 주요 차이점

### samples/main.py vs Airflow DAG

| 특징 | samples/main.py | Airflow DAG |
|------|----------------|-------------|
| 실행 방식 | 순차 실행 (한 번에) | Task 단위 실행 |
| 실패 처리 | 전체 중단 | 실패한 Task만 재실행 |
| 모니터링 | 콘솔 출력만 | 웹 UI + 로그 + 메트릭 |
| 스케줄링 | 수동 실행만 | Cron 기반 자동 실행 |
| 병렬 처리 | 불가능 | 가능 |
| 알림 | 없음 | 이메일, Slack 등 |
| 재시도 | 수동 | 자동 재시도 설정 |

## 트러블슈팅

### DAG가 보이지 않음
```bash
# Scheduler 로그 확인
docker-compose -f docker-compose.airflow.yml logs airflow-scheduler

# Python 문법 오류 확인
docker-compose -f docker-compose.airflow.yml exec airflow-webserver python /opt/airflow/dags/c_to_java_samples_pipeline.py
```

### Import 오류
```python
# DAG 파일에서 경로 확인
sys.path.insert(0, '/opt/airflow/samples')  # Docker 내부 경로
```

### Task 실패
1. Grid View에서 실패한 Task 클릭
2. "Log" 버튼으로 상세 로그 확인
3. 오류 수정 후 "Clear" → 재실행

## 다음 단계

1. [ ] 기본 DAG 실행 및 모니터링
2. [ ] samples 파일 수정하여 실제 로직 구현
3. [ ] 병렬 실행 구조로 최적화
4. [ ] 스케줄링 설정
5. [ ] 알림 설정 (실패 시 이메일)
6. [ ] 외부 시스템 연동 (GitHub, WatsonX)
