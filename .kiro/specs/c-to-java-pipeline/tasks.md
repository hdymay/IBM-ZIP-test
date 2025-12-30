# Implementation Plan

- [x] 1. 프로젝트 구조 및 기본 설정





  - 디렉토리 구조 생성 (src/, samples/, tests/, config/)
  - requirements.txt 작성 (requests, python-dotenv, cryptography, pytest, hypothesis)
  - .env.example 파일 생성
  - .gitignore 설정
  - _Requirements: 7.1_



- [x] 2. 데이터 모델 구현


  - [x] 2.1 데이터 클래스 정의


    - FileSelection, ZIPArchiveInfo, UploadResult, ExecutionStatus, LogEntry, Configuration 클래스 작성
    - _Requirements: 1.3, 2.1, 3.5_

- [ ]* 2.2 데이터 모델 property 테스트 작성
  - **Property 2: ZIP archive integrity**
  - **Validates: Requirements 2.2**

- [x] 3. 설정 관리자 구현






  - [x] 3.1 ConfigManager 클래스 구현

    - 설정 파일 로드/저장 기능
    - 환경 변수 읽기
    - 설정 검증 로직
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ]* 3.2 설정 검증 property 테스트 작성
  - **Property 7: Configuration validation**
  - **Validates: Requirements 7.3**


- [x] 3.3 연결 테스트 기능 구현

  - watsonx.ai API 연결 테스트
  - _Requirements: 7.5_

- [x] 4. 파일 선택기 구현






  - [x] 4.1 FileSelector 클래스 구현

    - 디렉토리 스캔 기능
    - Python 파일 필터링
    - 파일 선택/해제 로직
    - _Requirements: 1.1, 1.2, 1.3, 1.4_


- [x] 4.2 파일 선택 검증 구현

  - 최소 1개 파일 선택 확인
  - _Requirements: 1.5_

- [ ]* 4.3 파일 선택 property 테스트 작성
  - **Property 1: File selection validation**
  - **Validates: Requirements 1.5**


- [x] 5. ZIP 빌더 구현



  - [x] 5.1 ZIPBuilder 클래스 구현


    - ZIP 아카이브 생성 기능
    - 파일 추가 로직
    - 디렉토리 구조 보존
    - _Requirements: 2.1, 2.2_

- [x] 5.2 타임스탬프 파일명 생성

  - 현재 시간 기반 파일명 생성
  - _Requirements: 2.3_

- [x] 5.3 ZIP 검증 및 에러 처리


  - 압축 실패 시 에러 메시지 표시
  - 생성된 ZIP 정보 표시
  - _Requirements: 2.4, 2.5_

- [ ]* 5.4 ZIP 무결성 property 테스트 작성
  - **Property 2: ZIP archive integrity**
  - **Validates: Requirements 2.2**
- [x] 6. watsonx.ai 업로더 구현










  - [x] 6.1 WatsonxUploader 클래스 구현





    - API 인증 기능
    - 파일 업로드 로직
    - _Requirements: 3.1, 3.2_

- [x] 6.2 업로드 진행 상황 추적






  - 진행률 계산 및 표시
  - _Requirements: 3.3_



- [x] 6.3 재시도 메커니즘 구현


  - 최대 3회 재시도 로직


  - 지수 백오프 적용
  - _Requirements: 3.4_

- [x]* 6.4 업로드 재시도 property 테스트 작성


  - **Property 3: Upload retry consistency**
  - **Validates: Requirements 3.4**




- [x] 6.5 업로드 완료 처리







  - asset ID 및 URL 반환
  - _Requirements: 3.5_

- [ ] 7. 샘플 파일 생성

  - [x] 7.1 7개 샘플 Python 파일 작성





    - ingest.py: 데이터 수집 로그
    - parse.py: 파싱 로그
    - extract.py: 추출 로그
    - transform.py: 변환 로그
    - generate.py: 생성 로그
    - validate.py: 검증 로그
    - report.py: 보고서 생성 로그
    - _Requirements: 5.1, 5.2_

- [x] 7.2 샘플 모드 구현




  - 모든 샘플 파일 자동 선택 기능
  - _Requirements: 5.3_

- [x] 7.3 샘플 실행 결과 기록





  - 성공/실패 추적
  - 성공률 계산
  - _Requirements: 5.4, 5.5_

- [ ] 8. CLI 인터페이스 구현
  - [ ] 8.1 CLIInterface 클래스 구현
    - 명령줄 인자 파싱
    - 메인 실행 루프
    - _Requirements: 1.1_

- [ ] 8.2 대화형 메뉴 구현
  - 파일 선택 메뉴
  - 샘플 모드 선택
  - 설정 메뉴
  - _Requirements: 1.1, 5.3, 7.2_

- [ ] 8.3 진행 상황 표시 구현
  - 워크플로우 단계 표시
  - 진행률 업데이트
  - 현재 처리 파일 표시
  - _Requirements: 6.1, 6.2, 6.3_

- [ ]* 8.4 진행률 단조성 property 테스트 작성
  - **Property 6: Progress tracking monotonicity**
  - **Validates: Requirements 6.2**

- [ ] 8.4 에러 메시지 표시
  - 에러 발생 시 메시지 출력
  - 진행 일시 중지
  - _Requirements: 6.4_

- [ ] 8.5 요약 보고서 생성
  - 전체 프로세스 완료 후 요약 표시
  - _Requirements: 6.5_

- [ ] 9. 에러 핸들러 구현
  - [ ] 9.1 ErrorHandler 클래스 구현
    - 에러 처리 및 로깅
    - 재시도 가능 여부 판단
    - 사용자 친화적 메시지 생성
    - _Requirements: 2.4, 3.4, 6.4_

- [ ] 9.2 에러 카테고리별 처리
  - 파일 시스템 에러
  - 네트워크 에러
  - 검증 에러
  - _Requirements: 2.4, 3.4_

- [x] 10. 메인 워크플로우 통합




  - [x] 10.1 main.py 작성


    - CLI 초기화
    - 설정 로드
    - 워크플로우 실행
    - _Requirements: 1.1, 7.1_

- [x] 10.2 전체 워크플로우 연결


  - 파일 선택 → ZIP 생성 → 업로드 파이프라인
  - _Requirements: 1.1, 2.1, 3.1_

- [ ]* 10.3 통합 테스트 작성
  - 전체 워크플로우 end-to-end 테스트
  - 샘플 모드 전체 실행 테스트
  - 에러 시나리오 테스트

- [ ] 11. Checkpoint - 모든 테스트 통과 확인
  - 모든 테스트가 통과하는지 확인하고, 문제가 있으면 사용자에게 질문합니다.

- [ ] 12. 문서화
  - [ ] 12.1 README.md 작성
    - 설치 방법
    - 사용 방법
    - 설정 가이드
    - _Requirements: 7.1, 7.2_

- [ ] 12.2 코드 주석 추가
  - 각 클래스 및 메서드에 docstring 추가
  - 복잡한 로직에 인라인 주석 추가
