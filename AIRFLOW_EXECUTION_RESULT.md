# Airflow DAG 실행 결과

## 실행 완료!

`conditional_pipeline` DAG가 성공적으로 실행되었습니다!

### 실행 정보
- **DAG ID**: conditional_pipeline
- **실행 시간**: 2026-01-02 00:31:08
- **상태**: SUCCESS (성공)
- **소요 시간**: 약 2초

### 실행된 Task 목록
1. `check_quality` - 데이터 품질 검사 (조건 분기)
2. `high_quality_process` / `medium_quality_process` / `low_quality_alert` 중 하나

## 웹 UI에서 확인하기

### 1. Airflow 웹 UI 접속
```
http://localhost:8080
Username: airflow
Password: airflow
```

### 2. DAG 찾기
- 메인 페이지에서 `conditional_pipeline` 검색
- 또는 목록에서 찾기

### 3. 실행 결과 확인
1. DAG 이름 클릭
2. **Grid View** 탭에서 실행 이력 확인
3. 초록색 박스 = 성공한 Task

### 4. 상세 로그 확인
1. Task 박스 클릭 (예: `check_quality`)
2. **Log** 버튼 클릭
3. 실행 로그 확인:
   - 데이터 품질 점수
   - 어떤 분기로 갔는지
   - 실행 결과

### 5. Graph View로 흐름 확인
1. **Graph** 탭 클릭
2. Task 의존성 시각화
3. 어떤 경로로 실행되었는지 확인

## 다른 DAG 실행해보기

### 사용 가능한 DAG 목록

#### 1. conditional_pipeline (방금 실행함)
- 조건부 분기 (if-else)
- 데이터 품질에 따라 다른 처리

#### 2. dynamic_tasks_pipeline
- 동적 Task 생성 (for loop)
- 여러 파일 병렬 처리

#### 3. error_handling_pipeline
- 재시도 및 에러 처리
- 콜백 함수 테스트

#### 4. complex_dependency_pipeline
- 복잡한 의존성 (다이아몬드 패턴)
- 병렬 실행 후 병합

#### 5. time_based_pipeline
- 시간대별 다른 처리
- 야간/주간/저녁 분기

#### 6. full_integration_pipeline
- 전체 통합 파이프라인
- 데이터 수집 → 검증 → 처리 → 저장 → 알림

### DAG 실행 방법

#### 웹 UI에서 (권장)
1. DAG 목록에서 원하는 DAG 찾기
2. 왼쪽 토글 스위치 켜기 (활성화)
3. 오른쪽 ▶ 버튼 클릭 → **Trigger DAG**

#### CLI에서
```bash
# DAG 활성화
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow dags unpause dynamic_tasks_pipeline

# DAG 실행
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow dags trigger dynamic_tasks_pipeline

# 실행 결과 확인
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  airflow dags list-runs -d dynamic_tasks_pipeline --no-backfill
```

## 실행 결과 해석

### 상태 코드
- **success**: 성공
- **failed**: 실패
- **running**: 실행 중
- **queued**: 대기 중
- **skipped**: 건너뜀 (조건부 분기에서)

### 조건부 분기 결과 확인
`conditional_pipeline`의 경우:
- `check_quality`가 실행됨
- 품질 점수에 따라 3개 중 1개만 실행됨:
  - 80점 이상 → `high_quality_process`
  - 50-79점 → `medium_quality_process`
  - 50점 미만 → `low_quality_alert`

웹 UI의 Graph View에서 실행된 경로가 초록색으로 표시됩니다!

## 커스텀 DAG 수정하기

### 1. DAG 파일 수정
```bash
# dags/custom_pipeline_examples.py 파일 편집
# 예: 품질 점수 기준 변경
```

### 2. Airflow가 자동으로 감지
- 약 30초 후 자동으로 새로고침
- 또는 Scheduler 재시작:
```bash
docker-compose -f docker-compose.airflow.yml restart airflow-scheduler
```

### 3. 수정된 DAG 재실행
- 웹 UI에서 다시 Trigger

## 문제 해결

### DAG가 목록에 안 보이는 경우
```bash
# DAG 파일 구문 검사
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
  python /opt/airflow/dags/custom_pipeline_examples.py
```

### Task가 실패하는 경우
1. 웹 UI에서 실패한 Task 클릭
2. **Log** 버튼으로 에러 메시지 확인
3. **Clear** 버튼으로 재실행

### Airflow 재시작
```bash
docker-compose -f docker-compose.airflow.yml restart
```

## 다음 단계

### 1. 다른 예시 DAG 실행해보기
- `dynamic_tasks_pipeline` - 반복문 예시
- `full_integration_pipeline` - 전체 파이프라인

### 2. 커스텀 DAG 만들기
- `dags/` 폴더에 새 Python 파일 생성
- 예시 코드 참고하여 작성

### 3. watsonx Notebook Job 연동
- `watsonx_notebook_job_pipeline` DAG 활성화
- 환경 변수 설정 후 실행

## 요약

Airflow DAG 실행이 성공적으로 완료되었습니다!

- 웹 UI: http://localhost:8080
- 10개의 예시 DAG 사용 가능
- Python 코드로 완전히 커스터마이징 가능
- 조건부 분기, 반복문, 병렬 실행 모두 지원

이제 원하는 대로 파이프라인을 구현할 수 있습니다!
