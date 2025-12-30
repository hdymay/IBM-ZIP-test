"""
GitHub 업로더 모듈

이 모듈은 ZIP 파일을 GitHub 저장소에 업로드하는 기능을 제공합니다.
Requirements: GitHub API를 통한 파일 업로드
"""

import base64
import requests
import time
from typing import Optional, Callable
from pathlib import Path

from src.models.data_models import Configuration, UploadResult


class GitHubUploader:
    """GitHub 저장소 업로드 클래스
    
    ZIP 파일을 GitHub 저장소에 업로드하고, 재시도 메커니즘과
    진행 상황 추적 기능을 제공합니다.
    """
    
    def __init__(self, repo_url: str, github_token: Optional[str] = None):
        """GitHubUploader 초기화
        
        Args:
            repo_url: GitHub 저장소 URL (예: https://github.com/user/repo.git)
            github_token: GitHub Personal Access Token (선택적)
        """
        # .git 확장자 제거 (올바른 방법)
        self.repo_url = repo_url
        if self.repo_url.endswith('.git'):
            self.repo_url = self.repo_url[:-4]
        
        self.github_token = github_token
        self._upload_progress = 0.0
        
        # URL에서 owner와 repo 추출
        parts = self.repo_url.replace('https://github.com/', '').split('/')
        if len(parts) >= 2:
            self.owner = parts[0]
            self.repo = parts[1]
        else:
            raise ValueError(f"잘못된 GitHub URL 형식: {repo_url}")
    
    def upload_file(
        self, 
        file_path: str,
        target_path: Optional[str] = None,
        commit_message: Optional[str] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> UploadResult:
        """GitHub 저장소에 파일 업로드
        
        Args:
            file_path: 업로드할 파일 경로
            target_path: GitHub 저장소 내 대상 경로 (None이면 파일명 사용)
            commit_message: 커밋 메시지 (None이면 자동 생성)
            progress_callback: 진행 상황 콜백 함수 (선택적)
        
        Returns:
            UploadResult: 업로드 결과 정보
        """
        # GitHub 토큰 확인
        if not self.github_token:
            return UploadResult(
                asset_id='',
                asset_url='',
                upload_time=0.0,
                file_size=0,
                success=False,
                error_message=(
                    "GitHub 토큰이 설정되지 않았습니다. "
                    "https://github.com/settings/tokens 에서 토큰을 생성하고 "
                    "GITHUB_TOKEN 환경 변수에 설정하세요. (repo 권한 필요)"
                )
            )
        
        # 파일 존재 확인
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return UploadResult(
                asset_id='',
                asset_url='',
                upload_time=0.0,
                file_size=0,
                success=False,
                error_message=f"파일을 찾을 수 없습니다: {file_path}"
            )
        
        file_size = file_path_obj.stat().st_size
        start_time = time.time()
        
        # 대상 경로 설정
        if target_path is None:
            target_path = file_path_obj.name
        
        # 커밋 메시지 설정
        if commit_message is None:
            commit_message = f"Upload {file_path_obj.name}"
        
        try:
            # 1. 파일 내용을 base64로 인코딩
            if progress_callback:
                progress_callback(0.1)
            
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            content_base64 = base64.b64encode(file_content).decode('utf-8')
            
            if progress_callback:
                progress_callback(0.3)
            
            # 2. GitHub API 헤더 설정
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'C-to-Java-Pipeline'
            }
            
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'
            
            # 3. 기존 파일 확인 (SHA 값 필요)
            get_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{target_path}"
            
            if progress_callback:
                progress_callback(0.5)
            
            get_response = requests.get(get_url, headers=headers)
            
            # 4. 파일 업로드/업데이트 요청 데이터
            data = {
                'message': commit_message,
                'content': content_base64
            }
            
            # 기존 파일이 있으면 SHA 추가
            if get_response.status_code == 200:
                existing_file = get_response.json()
                data['sha'] = existing_file['sha']
                print(f"   기존 파일 업데이트: {target_path}")
            else:
                print(f"   새 파일 생성: {target_path}")
            
            if progress_callback:
                progress_callback(0.7)
            
            # 5. 파일 업로드
            put_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{target_path}"
            
            put_response = requests.put(put_url, headers=headers, json=data)
            
            if progress_callback:
                progress_callback(1.0)
            
            upload_time = time.time() - start_time
            
            if put_response.status_code in (200, 201):
                response_data = put_response.json()
                
                # GitHub 파일 URL 생성
                file_url = f"https://github.com/{self.owner}/{self.repo}/blob/main/{target_path}"
                raw_url = f"https://github.com/{self.owner}/{self.repo}/raw/main/{target_path}"
                
                return UploadResult(
                    asset_id=response_data.get('content', {}).get('sha', ''),
                    asset_url=file_url,
                    upload_time=upload_time,
                    file_size=file_size,
                    success=True,
                    error_message=f"Raw URL: {raw_url}"  # Raw URL을 error_message에 저장
                )
            else:
                error_msg = f"GitHub API 오류: HTTP {put_response.status_code}"
                try:
                    error_detail = put_response.json()
                    if 'message' in error_detail:
                        error_msg += f" - {error_detail['message']}"
                except:
                    error_msg += f" - {put_response.text}"
                
                return UploadResult(
                    asset_id='',
                    asset_url='',
                    upload_time=upload_time,
                    file_size=file_size,
                    success=False,
                    error_message=error_msg
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
        """
        return self._upload_progress
    
    def retry_upload(
        self, 
        file_path: str,
        target_path: Optional[str] = None,
        commit_message: Optional[str] = None,
        max_retries: int = 3,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> UploadResult:
        """재시도 로직 포함 업로드
        
        Args:
            file_path: 업로드할 파일 경로
            target_path: GitHub 저장소 내 대상 경로
            commit_message: 커밋 메시지
            max_retries: 최대 재시도 횟수
            progress_callback: 진행 상황 콜백 함수
        
        Returns:
            UploadResult: 업로드 결과 정보
        """
        last_result = None
        
        for attempt in range(max_retries + 1):
            try:
                result = self.upload_file(
                    file_path, 
                    target_path, 
                    commit_message, 
                    progress_callback
                )
                
                if result.success:
                    return result
                
                last_result = result
                
                # 마지막 시도가 아니면 재시도
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # 지수 백오프
                    print(f"   재시도 대기 중... ({wait_time}초)")
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