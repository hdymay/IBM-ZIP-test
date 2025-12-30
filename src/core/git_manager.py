"""
Git 저장소 관리 모듈

자동으로 Git push/pull을 수행하는 기능을 제공합니다.
"""

import subprocess
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class GitResult:
    """Git 작업 결과"""
    success: bool
    message: str
    output: str = ""
    error: str = ""


class GitManager:
    """Git 저장소 자동 관리 클래스
    
    커밋, 푸시, 풀 등의 Git 작업을 자동화합니다.
    """
    
    def __init__(self, repo_path: str = "."):
        """
        Args:
            repo_path: Git 저장소 경로 (기본값: 현재 디렉토리)
        """
        self.repo_path = Path(repo_path).resolve()
        
    def _run_command(self, command: list) -> Tuple[bool, str, str]:
        """Git 명령어 실행
        
        Args:
            command: 실행할 명령어 리스트
            
        Returns:
            (성공 여부, 표준 출력, 표준 에러)
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "명령어 실행 시간 초과 (30초)"
        except Exception as e:
            return False, "", str(e)
    
    def check_status(self) -> GitResult:
        """Git 상태 확인
        
        Returns:
            GitResult: 상태 확인 결과
        """
        success, output, error = self._run_command(["git", "status", "--porcelain"])
        
        if not success:
            return GitResult(
                success=False,
                message="Git 상태 확인 실패",
                error=error
            )
        
        if output.strip():
            return GitResult(
                success=True,
                message="변경된 파일이 있습니다",
                output=output
            )
        else:
            return GitResult(
                success=True,
                message="변경된 파일이 없습니다",
                output=""
            )
    
    def add_all(self) -> GitResult:
        """모든 변경사항을 스테이징
        
        Returns:
            GitResult: 스테이징 결과
        """
        success, output, error = self._run_command(["git", "add", "."])
        
        if success:
            return GitResult(
                success=True,
                message="모든 파일이 스테이징되었습니다",
                output=output
            )
        else:
            return GitResult(
                success=False,
                message="파일 스테이징 실패",
                error=error
            )
    
    def commit(self, message: str) -> GitResult:
        """변경사항 커밋
        
        Args:
            message: 커밋 메시지
            
        Returns:
            GitResult: 커밋 결과
        """
        if not message:
            return GitResult(
                success=False,
                message="커밋 메시지가 필요합니다",
                error="Empty commit message"
            )
        
        success, output, error = self._run_command(["git", "commit", "-m", message])
        
        if success:
            return GitResult(
                success=True,
                message=f"커밋 완료: {message}",
                output=output
            )
        elif "nothing to commit" in output or "nothing to commit" in error:
            return GitResult(
                success=True,
                message="커밋할 변경사항이 없습니다",
                output=output
            )
        else:
            return GitResult(
                success=False,
                message="커밋 실패",
                error=error
            )
    
    def pull(self, remote: str = "origin", branch: str = "main") -> GitResult:
        """원격 저장소에서 변경사항 가져오기
        
        Args:
            remote: 원격 저장소 이름 (기본값: origin)
            branch: 브랜치 이름 (기본값: main)
            
        Returns:
            GitResult: Pull 결과
        """
        success, output, error = self._run_command(["git", "pull", remote, branch])
        
        if success:
            if "Already up to date" in output:
                return GitResult(
                    success=True,
                    message="이미 최신 상태입니다",
                    output=output
                )
            else:
                return GitResult(
                    success=True,
                    message=f"{remote}/{branch}에서 변경사항을 가져왔습니다",
                    output=output
                )
        else:
            return GitResult(
                success=False,
                message="Pull 실패",
                error=error
            )
    
    def push(self, remote: str = "origin", branch: str = "main") -> GitResult:
        """원격 저장소로 변경사항 푸시
        
        Args:
            remote: 원격 저장소 이름 (기본값: origin)
            branch: 브랜치 이름 (기본값: main)
            
        Returns:
            GitResult: Push 결과
        """
        success, output, error = self._run_command(["git", "push", remote, branch])
        
        if success:
            return GitResult(
                success=True,
                message=f"{remote}/{branch}로 푸시 완료",
                output=output
            )
        else:
            return GitResult(
                success=False,
                message="Push 실패",
                error=error
            )
    
    def auto_commit_and_push(
        self,
        commit_message: str,
        remote: str = "origin",
        branch: str = "main"
    ) -> GitResult:
        """자동으로 커밋하고 푸시
        
        변경사항 확인 → 스테이징 → 커밋 → 푸시를 자동으로 수행합니다.
        
        Args:
            commit_message: 커밋 메시지
            remote: 원격 저장소 이름
            branch: 브랜치 이름
            
        Returns:
            GitResult: 전체 작업 결과
        """
        # 1. 상태 확인
        status = self.check_status()
        if not status.success:
            return status
        
        if not status.output:
            return GitResult(
                success=True,
                message="변경사항이 없어 푸시할 내용이 없습니다",
                output=""
            )
        
        # 2. 스테이징
        add_result = self.add_all()
        if not add_result.success:
            return add_result
        
        # 3. 커밋
        commit_result = self.commit(commit_message)
        if not commit_result.success:
            return commit_result
        
        # 4. 푸시
        push_result = self.push(remote, branch)
        
        return push_result
    
    def auto_pull_and_merge(
        self,
        remote: str = "origin",
        branch: str = "main"
    ) -> GitResult:
        """자동으로 풀하고 병합
        
        원격 저장소의 변경사항을 가져와 현재 브랜치와 병합합니다.
        
        Args:
            remote: 원격 저장소 이름
            branch: 브랜치 이름
            
        Returns:
            GitResult: Pull 결과
        """
        return self.pull(remote, branch)
