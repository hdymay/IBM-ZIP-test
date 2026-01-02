"""
Git Manager 단위 테스트
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.git_manager import GitManager, GitResult


class TestGitManager(unittest.TestCase):
    """GitManager 클래스 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # GitPython Repo를 mock
        with patch('src.core.git_manager.Repo'):
            self.git_manager = GitManager()
    
    @patch('src.core.git_manager.Repo')
    def test_check_status_with_changes(self, mock_repo_class):
        """변경사항이 있을 때 상태 확인 테스트"""
        # Mock 설정
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        # 변경된 파일 mock
        mock_diff_item = MagicMock()
        mock_diff_item.a_path = "file1.py"
        mock_repo.index.diff.return_value = [mock_diff_item]
        mock_repo.untracked_files = ["file2.py"]
        
        git_manager = GitManager()
        
        # 실행
        result = git_manager.check_status()
        
        # 검증
        self.assertTrue(result.success)
        self.assertEqual(result.message, "변경된 파일이 있습니다")
        self.assertIn("file1.py", result.output)
        self.assertIn("file2.py", result.output)
    
    @patch('src.core.git_manager.Repo')
    def test_check_status_no_changes(self, mock_repo_class):
        """변경사항이 없을 때 상태 확인 테스트"""
        # Mock 설정
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        # 변경사항 없음
        mock_repo.index.diff.return_value = []
        mock_repo.untracked_files = []
        
        git_manager = GitManager()
        
        # 실행
        result = git_manager.check_status()
        
        # 검증
        self.assertTrue(result.success)
        self.assertEqual(result.message, "변경된 파일이 없습니다")
        self.assertEqual(result.output, "")
    
    @patch('src.core.git_manager.Repo')
    def test_add_all_success(self, mock_repo_class):
        """파일 스테이징 성공 테스트"""
        # Mock 설정
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        git_manager = GitManager()
        
        # 실행
        result = git_manager.add_all()
        
        # 검증
        self.assertTrue(result.success)
        self.assertEqual(result.message, "모든 파일이 스테이징되었습니다")
        mock_repo.git.add.assert_called_once_with('.')
    
    @patch('src.core.git_manager.Repo')
    def test_commit_success(self, mock_repo_class):
        """커밋 성공 테스트"""
        # Mock 설정
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        mock_commit = MagicMock()
        mock_commit.hexsha = "abc1234567890"
        mock_repo.index.commit.return_value = mock_commit
        
        git_manager = GitManager()
        
        # 실행
        result = git_manager.commit("Test commit")
        
        # 검증
        self.assertTrue(result.success)
        self.assertIn("Test commit", result.message)
        mock_repo.index.commit.assert_called_once_with("Test commit")
    
    def test_commit_empty_message(self):
        """빈 커밋 메시지 테스트"""
        # 실행
        result = self.git_manager.commit("")
        
        # 검증
        self.assertFalse(result.success)
        self.assertEqual(result.message, "커밋 메시지가 필요합니다")
    
    @patch('src.core.git_manager.Repo')
    def test_commit_nothing_to_commit(self, mock_repo_class):
        """커밋할 내용이 없을 때 테스트"""
        # Mock 설정
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        from git import GitCommandError
        mock_repo.index.commit.side_effect = GitCommandError("commit", "nothing to commit")
        
        git_manager = GitManager()
        
        # 실행
        result = git_manager.commit("Test commit")
        
        # 검증
        self.assertTrue(result.success)
        self.assertEqual(result.message, "커밋할 변경사항이 없습니다")
    
    @patch('src.core.git_manager.Repo')
    def test_pull_success(self, mock_repo_class):
        """Pull 성공 테스트"""
        # Mock 설정
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        mock_remote = MagicMock()
        mock_repo.remote.return_value = mock_remote
        
        mock_pull_info = MagicMock()
        # HEAD_UPTODATE가 아닌 경우를 시뮬레이션
        # flags & HEAD_UPTODATE가 False가 되도록 설정
        mock_pull_info.flags = 4  # 임의의 다른 플래그
        mock_pull_info.HEAD_UPTODATE = 128  # 일반적인 HEAD_UPTODATE 값
        mock_remote.pull.return_value = [mock_pull_info]
        
        git_manager = GitManager()
        
        # 실행
        result = git_manager.pull()
        
        # 검증
        self.assertTrue(result.success)
        self.assertIn("변경사항을 가져왔습니다", result.message)
        mock_remote.pull.assert_called_once_with("main")
    
    @patch('src.core.git_manager.Repo')
    def test_pull_already_up_to_date(self, mock_repo_class):
        """이미 최신 상태일 때 Pull 테스트"""
        # Mock 설정
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        mock_remote = MagicMock()
        mock_repo.remote.return_value = mock_remote
        
        mock_pull_info = MagicMock()
        mock_pull_info.flags = mock_pull_info.HEAD_UPTODATE
        mock_remote.pull.return_value = [mock_pull_info]
        
        git_manager = GitManager()
        
        # 실행
        result = git_manager.pull()
        
        # 검증
        self.assertTrue(result.success)
        self.assertEqual(result.message, "이미 최신 상태입니다")
    
    @patch('src.core.git_manager.Repo')
    def test_push_success(self, mock_repo_class):
        """Push 성공 테스트"""
        # Mock 설정
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        mock_remote = MagicMock()
        mock_repo.remote.return_value = mock_remote
        
        mock_push_info = MagicMock()
        mock_remote.push.return_value = [mock_push_info]
        
        git_manager = GitManager()
        
        # 실행
        result = git_manager.push()
        
        # 검증
        self.assertTrue(result.success)
        self.assertIn("푸시 완료", result.message)
        mock_remote.push.assert_called_once_with("main")
    
    @patch('src.core.git_manager.Repo')
    def test_push_failure(self, mock_repo_class):
        """Push 실패 테스트"""
        # Mock 설정
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        mock_remote = MagicMock()
        mock_repo.remote.return_value = mock_remote
        
        from git import GitCommandError
        mock_remote.push.side_effect = GitCommandError("push", "error: failed to push some refs")
        
        git_manager = GitManager()
        
        # 실행
        result = git_manager.push()
        
        # 검증
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Push 실패")
        self.assertIn("failed to push", result.error)
    
    @patch.object(GitManager, 'push')
    @patch.object(GitManager, 'commit')
    @patch.object(GitManager, 'add_all')
    @patch.object(GitManager, 'check_status')
    def test_auto_commit_and_push_success(self, mock_status, mock_add, mock_commit, mock_push):
        """자동 커밋 및 푸시 성공 테스트"""
        # Mock 설정
        mock_status.return_value = GitResult(
            success=True,
            message="변경된 파일이 있습니다",
            output=" M file.py\n"
        )
        mock_add.return_value = GitResult(success=True, message="스테이징 완료")
        mock_commit.return_value = GitResult(success=True, message="커밋 완료")
        mock_push.return_value = GitResult(success=True, message="푸시 완료")
        
        # 실행
        result = self.git_manager.auto_commit_and_push("Test commit")
        
        # 검증
        self.assertTrue(result.success)
        mock_status.assert_called_once()
        mock_add.assert_called_once()
        mock_commit.assert_called_once()
        mock_push.assert_called_once()
    
    @patch.object(GitManager, 'check_status')
    def test_auto_commit_and_push_no_changes(self, mock_status):
        """변경사항이 없을 때 자동 커밋 및 푸시 테스트"""
        # Mock 설정
        mock_status.return_value = GitResult(
            success=True,
            message="변경된 파일이 없습니다",
            output=""
        )
        
        # 실행
        result = self.git_manager.auto_commit_and_push("Test commit")
        
        # 검증
        self.assertTrue(result.success)
        self.assertIn("변경사항이 없어", result.message)
        mock_status.assert_called_once()
    
    @patch('src.core.git_manager.Repo')
    def test_command_timeout(self, mock_repo_class):
        """명령어 타임아웃 테스트 (GitPython은 타임아웃 처리가 다름)"""
        # Mock 설정
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        # GitPython에서는 일반 Exception으로 처리
        mock_repo.index.diff.side_effect = Exception("Operation timed out")
        
        git_manager = GitManager()
        
        # 실행
        result = git_manager.check_status()
        
        # 검증
        self.assertFalse(result.success)
        self.assertIn("Operation timed out", result.error)


if __name__ == '__main__':
    unittest.main()
