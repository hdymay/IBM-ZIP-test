"""
watsonx.ai 업로더 모듈

이 모듈은 ZIP 파일을 watsonx.ai asset에 업로드하는 기능을 제공합니다.
Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

import time
import requests
from typing import Optional, Callable
from pathlib import Path

from src.models.data_models import Configuration, UploadResult


class WatsonxUploader:
    """watsonx.ai asset 업로드 클래스
    
    ZIP 파일을 watsonx.ai asset에 업로드하고, 재시도 메커니즘과
    진행 상황 추적 기능을 제공합니다.
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
    """
    
    # IBM Cloud IAM 토큰 엔드포인트
    IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
    
    def __init__(self, config: Configuration):
        """WatsonxUploader 초기화
        
        Args:
            config: watsonx.ai 연결 설정
        """
        self.config = config
        self._upload_progress = 0.0
        self._is_authenticated = False
        self._session = requests.Session()
        self._access_token = None
    
    def _get_iam_token(self) -> str:
        """IBM Cloud IAM 토큰 획득
        
        API 키를 사용하여 IAM 액세스 토큰을 획득합니다.
        
        Returns:
            str: IAM 액세스 토큰
            
        Raises:
            ValueError: 토큰 획득 실패 시
        """
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
            'apikey': self.config.watsonx_api_key
        }
        
        try:
            response = requests.post(
                self.IAM_TOKEN_URL,
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get('access_token')
            else:
                raise ValueError(f"IAM 토큰 획득 실패: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise ValueError(f"IAM 토큰 요청 중 오류: {str(e)}") from e
    
    def authenticate(self) -> bool:
        """watsonx.ai API 인증
        
        API 키를 사용하여 IAM 토큰을 획득하고 인증합니다.
        
        Returns:
            bool: 인증 성공 여부
            
        Raises:
            ValueError: 설정이 유효하지 않은 경우
            
        Requirements: 3.1, 3.2
        """
        if not self.config.watsonx_api_key:
            raise ValueError("API 키가 설정되지 않았습니다")
        
        if not self.config.watsonx_endpoint:
            raise ValueError("엔드포인트가 설정되지 않았습니다")
        
        try:
            # IAM 토큰 획득
            self._access_token = self._get_iam_token()
            
            if not self._access_token:
                raise ValueError("IAM 토큰을 획득할 수 없습니다")
            
            # 세션 헤더 설정
            self._session.headers.update({
                'Authorization': f'Bearer {self._access_token}',
                'Content-Type': 'application/json'
            })
            
            self._is_authenticated = True
            return True
                
        except Exception as e:
            raise ValueError(f"인증 중 오류 발생: {str(e)}") from e
    
    def upload_asset(
        self, 
        file_path: str,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> UploadResult:
        """asset 업로드
        
        ZIP 파일을 watsonx.ai asset으로 업로드합니다.
        
        Args:
            file_path: 업로드할 ZIP 파일 경로
            progress_callback: 진행 상황 콜백 함수 (선택적)
        
        Returns:
            UploadResult: 업로드 결과 정보
            
        Raises:
            FileNotFoundError: 파일을 찾을 수 없는 경우
            ValueError: 인증되지 않은 경우
            IOError: 업로드 실패 시
            
        Requirements: 3.1, 3.2, 3.3, 3.5
        """
        # 인증 확인
        if not self._is_authenticated:
            raise ValueError("인증이 필요합니다. authenticate()를 먼저 호출하세요")
        
        # 파일 존재 확인
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
        
        file_size = file_path_obj.stat().st_size
        start_time = time.time()
        
        try:
            # Watson Data API를 사용한 자산 업로드
            # 참고: https://cloud.ibm.com/apidocs/watson-data-api
            base_url = self.config.watsonx_endpoint.rstrip('/')
            
            # 1단계: 자산 메타데이터 생성
            asset_metadata = {
                "metadata": {
                    "name": file_path_obj.name,
                    "description": "C to Java Pipeline ZIP Archive",
                    "asset_type": "data_asset",
                    "origin_country": "us",
                    "asset_category": "USER"
                },
                "entity": {
                    "data_asset": {
                        "mime_type": "application/zip"
                    }
                }
            }
            
            # 자산 생성 URL (Watson Data API)
            create_url = f"{base_url}/v2/assets?project_id={self.config.watsonx_project_id}"
            
            # Content-Type을 JSON으로 설정
            headers = {
                'Authorization': f'Bearer {self._access_token}',
                'Content-Type': 'application/json'
            }
            
            # 자산 메타데이터 생성 요청
            create_response = requests.post(
                create_url,
                headers=headers,
                json=asset_metadata,
                timeout=30
            )
            
            if create_response.status_code not in (200, 201):
                return UploadResult(
                    asset_id='',
                    asset_url='',
                    upload_time=time.time() - start_time,
                    file_size=file_size,
                    success=False,
                    error_message=f"자산 생성 실패: HTTP {create_response.status_code} - {create_response.text}"
                )
            
            asset_data = create_response.json()
            asset_id = asset_data.get('metadata', {}).get('asset_id', '')
            
            # 2단계: 파일 첨부 URL 획득
            attachment_url = f"{base_url}/v2/assets/{asset_id}/attachments?project_id={self.config.watsonx_project_id}"
            
            attachment_metadata = {
                "asset_type": "data_asset",
                "name": file_path_obj.name,
                "mime": "application/zip"
            }
            
            attach_response = requests.post(
                attachment_url,
                headers=headers,
                json=attachment_metadata,
                timeout=30
            )
            
            if attach_response.status_code not in (200, 201):
                return UploadResult(
                    asset_id=asset_id,
                    asset_url='',
                    upload_time=time.time() - start_time,
                    file_size=file_size,
                    success=False,
                    error_message=f"첨부 생성 실패: HTTP {attach_response.status_code}"
                )
            
            attach_data = attach_response.json()
            upload_url = attach_data.get('url', '')
            attachment_id = attach_data.get('attachment_id', '')
            
            # 3단계: 실제 파일 업로드
            if upload_url:
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    
                    if progress_callback:
                        progress_callback(0.5)  # 50% 진행
                    
                    upload_headers = {
                        'Content-Type': 'application/zip'
                    }
                    
                    upload_response = requests.put(
                        upload_url,
                        headers=upload_headers,
                        data=file_content,
                        timeout=self.config.timeout
                    )
                    
                    if progress_callback:
                        progress_callback(1.0)  # 100% 완료
                    
                    if upload_response.status_code not in (200, 201):
                        return UploadResult(
                            asset_id=asset_id,
                            asset_url='',
                            upload_time=time.time() - start_time,
                            file_size=file_size,
                            success=False,
                            error_message=f"파일 업로드 실패: HTTP {upload_response.status_code}"
                        )
            
            # 4단계: 첨부 완료 표시
            complete_url = f"{base_url}/v2/assets/{asset_id}/attachments/{attachment_id}/complete?project_id={self.config.watsonx_project_id}"
            
            complete_response = requests.post(
                complete_url,
                headers=headers,
                timeout=30
            )
            
            upload_time = time.time() - start_time
            asset_url = f"{base_url}/projects/{self.config.watsonx_project_id}/assets/{asset_id}"
            
            return UploadResult(
                asset_id=asset_id,
                asset_url=asset_url,
                upload_time=upload_time,
                file_size=file_size,
                success=True
            )
                
        except requests.exceptions.Timeout:
            return UploadResult(
                asset_id='',
                asset_url='',
                upload_time=time.time() - start_time,
                file_size=file_size,
                success=False,
                error_message="업로드 시간 초과"
            )
        except Exception as e:
            return UploadResult(
                asset_id='',
                asset_url='',
                upload_time=time.time() - start_time,
                file_size=file_size,
                success=False,
                error_message=f"업로드 중 오류 발생: {str(e)}"
            )
    
    def get_upload_progress(self) -> float:
        """업로드 진행률 반환
        
        Returns:
            float: 진행률 (0.0 ~ 1.0)
            
        Requirements: 3.3
        """
        return self._upload_progress
    
    def retry_upload(
        self, 
        file_path: str,
        max_retries: Optional[int] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> UploadResult:
        """재시도 로직 포함 업로드
        
        업로드 실패 시 지수 백오프를 적용하여 재시도합니다.
        
        Args:
            file_path: 업로드할 ZIP 파일 경로
            max_retries: 최대 재시도 횟수 (None이면 config 값 사용)
            progress_callback: 진행 상황 콜백 함수 (선택적)
        
        Returns:
            UploadResult: 업로드 결과 정보
            
        Requirements: 3.4
        """
        if max_retries is None:
            max_retries = self.config.max_retries
        
        last_result = None
        
        for attempt in range(max_retries + 1):
            try:
                # 업로드 시도
                result = self.upload_asset(file_path, progress_callback)
                
                if result.success:
                    return result
                
                last_result = result
                
                # 마지막 시도가 아니면 재시도
                if attempt < max_retries:
                    # 지수 백오프 (1초, 2초, 4초)
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    
            except Exception as e:
                last_result = UploadResult(
                    asset_id='',
                    asset_url='',
                    upload_time=0.0,
                    file_size=0,
                    success=False,
                    error_message=f"업로드 중 예외 발생: {str(e)}"
                )
                
                # 마지막 시도가 아니면 재시도
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
        
        # 모든 재시도 실패
        if last_result:
            last_result.error_message = f"최대 재시도 횟수({max_retries})를 초과했습니다. " + (last_result.error_message or "")
        
        return last_result or UploadResult(
            asset_id='',
            asset_url='',
            upload_time=0.0,
            file_size=0,
            success=False,
            error_message=f"최대 재시도 횟수({max_retries})를 초과했습니다"
        )
    
    def _create_progress_wrapper(
        self, 
        file_obj, 
        total_size: int,
        callback: Callable[[float], None]
    ):
        """진행 상황 추적을 위한 파일 객체 래퍼
        
        Args:
            file_obj: 원본 파일 객체
            total_size: 전체 파일 크기
            callback: 진행 상황 콜백 함수
            
        Returns:
            래핑된 파일 객체
            
        Requirements: 3.3
        """
        class ProgressWrapper:
            def __init__(self, f, size, cb):
                self.file = f
                self.total_size = size
                self.callback = cb
                self.bytes_read = 0
            
            def read(self, size=-1):
                data = self.file.read(size)
                self.bytes_read += len(data)
                
                # 진행률 계산 및 콜백 호출
                progress = min(self.bytes_read / self.total_size, 1.0)
                self.callback(progress)
                
                return data
            
            def __getattr__(self, attr):
                return getattr(self.file, attr)
        
        return ProgressWrapper(file_obj, total_size, callback)
    
    def close(self):
        """세션 종료
        
        리소스를 정리하고 세션을 종료합니다.
        """
        if self._session:
            self._session.close()
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()
