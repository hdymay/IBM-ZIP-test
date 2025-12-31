# Airflow 실습 가이드

## 1. 초기 설정

### 필요한 디렉토리 생성
```bash
mkdir -p dags logs plugins config
```

### 환경 변수 설정 (Windows)
```powershell
$env:AIRFLOW_UID=50000
```

## 2. Airflow 시작

### Docker Compose로 실행
```bash
docker-compose -f docker-compose.airflow.yml up -d
```

초기 실행 시 데이터베이스 초기화와 사용자 생성이 자동으로 진행됩니다 (약 1-2분 소요).

## 3. 웹 UI 접속

브라우저에서 접속:
```
http://localhost:8080
```

로그인 정보:
- Username: `airflow`
- Password: `airflow`

## 4. DAG 실행

1. 웹 UI에서 `c_to_java_pipeline` DAG 찾기
2. 토글 버튼으로 DAG 활성화
3. 우측 "Trigger DAG" 버튼 클릭하여 수동 실행

## 5. 실행 모니터링

- **Graph View**: Task 간 의존성 시각화
- **Grid View**: 실행 이력 및 상태 확인
- **Logs**: 각 Task의 상세 로그 확인

## 6. 주요 명령어

### 로그 확인
```bash
# 전체 로그
docker-compose -f docker-compose.airflow.yml logs

# 특정 서비스 로그
docker-compose -f docker-compose.airflow.yml logs airflow-webserver
docker-compose -f docker-compose.airflow.yml logs airflow-scheduler
```

### 중지 및 재시작
```bash
# 중지
docker-compose -f docker-compose.airflow.yml down

# 재시작
docker-compose -f docker-compose.airflow.yml restart

# 완전 삭제 (데이터베이스 포함)
docker-compose -f docker-compose.airflow.yml down -v
```

### DAG 새로고침
DAG 파일을 수정한 후:
```bash
# Scheduler가 자동으로 감지 (약 30초 소요)
# 또는 강제 재시작
docker-compose -f docker-compose.airflow.yml restart airflow-scheduler
```

## 7. 트러블슈팅

### 포트 충돌 (8080)
다른 서비스가 8080 포트를 사용 중이면:
```yaml
# docker-compose.airflow.yml 수정
airflow-webserver:
  ports:
    - "8081:8080"  # 8081로 변경
```

### 권한 오류
Windows에서 볼륨 마운트 권한 문제 발생 시:
```bash
# Docker Desktop 설정에서 해당 드라이브 공유 활성화
# Settings > Resources > File Sharing
```

### DAG가 보이지 않음
1. `dags/` 디렉토리에 파일이 있는지 확인
2. Python 문법 오류 확인
3. Scheduler 로그 확인:
   ```bash
   docker-compose -f docker-compose.airflow.yml logs airflow-scheduler
   ```

## 8. 파이프라인 구조

```
select_files → build_zip → execute_samples → [upload_github, upload_watsonx]
```

- **select_files**: 변환할 C 파일 선택
- **build_zip**: 선택된 파일을 ZIP으로 압축
- **execute_samples**: 샘플 코드 실행 (parse, generate 등)
- **upload_github**: GitHub에 결과 업로드
- **upload_watsonx**: WatsonX에 결과 업로드

## 9. 실습 시나리오

### 시나리오 1: 전체 파이프라인 실행
1. DAG 활성화
2. "Trigger DAG" 클릭
3. Graph View에서 각 Task 진행 상황 확인
4. 완료 후 Logs에서 결과 확인

### 시나리오 2: 특정 Task만 재실행
1. Grid View에서 실패한 Task 클릭
2. "Clear" 버튼으로 해당 Task만 재실행

### 시나리오 3: 스케줄링 설정
DAG 파일에서 `schedule_interval` 수정:
```python
# 매일 오전 9시 실행
schedule_interval='0 9 * * *'

# 매주 월요일 실행
schedule_interval='0 0 * * 1'
```

## 10. 다음 단계

- [ ] 실제 프로젝트 파일로 테스트
- [ ] 에러 핸들링 추가 (retry, alert)
- [ ] 파라미터화된 실행 (Airflow Variables)
- [ ] 센서 추가 (파일 감지, API 대기)
- [ ] 브랜칭 로직 (조건부 실행)
