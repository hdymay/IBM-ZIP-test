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
        self.git_manager = GitManager()
    
    @patch('subprocess.run')
    def test_check_status_with_changes(self, mock_run):
        """변경사항이 있을 때 상태 확인 테스트"""
        # Mock 설정
        mock_run.return_value = Mock(
            returncode=0,
            stdout=" M file1.py\n?? file2.py\n",
            stderr=""
        )
        
        # 실행
        result = self.git_manager.check_status()
        
        # 검증
        self.assertTrue(result.success)
        self.assertEqual(result.message, "변경된 파일이 있습니다")
        self.assertIn("file1.py", result.output)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_check_status_no_changes(self, mock_run):
        """변경사항이 없을 때 상태 확인 테스트"""
        # Mock 설정
        mock_run.return_value = Mock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        # 실행
        result = self.git_manager.check_status()
        
        # 검증
        self.assertTrue(result.success)
        self.assertEqual(result.message, "변경된 파일이 없습니다")
        self.assertEqual(result.output, "")
    
    @patch('subprocess.run')
    def test_add_all_success(self, mock_run):
        """파일 스테이징 성공 테스트"""
        # Mock 설정
        mock_run.return_value = Mock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        # 실행
        result = self.git_manager.add_all()
        
        # 검증
        self.assertTrue(result.success)
        self.assertEqual(result.message, "모든 파일이 스테이징되었습니다")
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_commit_success(self, mock_run):
        """커밋 성공 테스트"""
        # Mock 설정
        mock_run.return_value = Mock(
            returncode=0,
            stdout="[main abc1234] Test commit\n 1 file changed, 1 insertion(+)\n",
            stderr=""
        )
        
        # 실행
        result = self.git_manager.commit("Test commit")
        
        # 검증
        self.assertTrue(result.success)
        self.assertIn("Test commit", result.message)
        mock_run.assert_called_once()
    
    def test_commit_empty_message(self):
        """빈 커밋 메시지 테스트"""
        # 실행
        result = self.git_manager.commit("")
        
        # 검증
        self.assertFalse(result.success)
        self.assertEqual(result.message, "커밋 메시지가 필요합니다")
    
    @patch('subprocess.run')
    def test_commit_nothing_to_commit(self, mock_run):
        """커밋할 내용이 없을 때 테스트"""
        # Mock 설정
        mock_run.return_value = Mock(
            returncode=1,
            stdout="nothing to commit, working tree clean\n",
            stderr=""
        )
        
        # 실행
        result = self.git_manager.commit("Test commit")
        
        # 검증
        self.assertTrue(result.success)
        self.assertEqual(result.message, "커밋할 변경사항이 없습니다")
    
    @patch('subprocess.run')
    def test_pull_success(self, mock_run):
        """Pull 성공 테스트"""
        # Mock 설정
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Updating abc1234..def5678\nFast-forward\n file.py | 2 +-\n",
            stderr=""
        )
        
        # 실행
        result = self.git_manager.pull()
        
        # 검증
        self.assertTrue(result.success)
        self.assertIn("변경사항을 가져왔습니다", result.message)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_pull_already_up_to_date(self, mock_run):
        """이미 최신 상태일 때 Pull 테스트"""
        # Mock 설정
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Already up to date.\n",
            stderr=""
        )
        
        # 실행
        result = self.git_manager.pull()
        
        # 검증
        self.assertTrue(result.success)
        self.assertEqual(result.message, "이미 최신 상태입니다")
    
    @patch('subprocess.run')
    def test_push_success(self, mock_run):
        """Push 성공 테스트"""
        # Mock 설정
        mock_run.return_value = Mock(
            returncode=0,
            stdout="To https://github.com/user/repo.git\n   abc1234..def5678  main -> main\n",
            stderr=""
        )
        
        # 실행
        result = self.git_manager.push()
        
        # 검증
        self.assertTrue(result.success)
        self.assertIn("푸시 완료", result.message)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_push_failure(self, mock_run):
        """Push 실패 테스트"""
        # Mock 설정
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="error: failed to push some refs\n"
        )
        
        # 실행
        result = self.git_manager.push()
        
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
    
    @patch('subprocess.run')
    def test_command_timeout(self, mock_run):
        """명령어 타임아웃 테스트"""
        # Mock 설정
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("git", 30)
        
        # 실행
        result = self.git_manager.check_status()
        
        # 검증
        self.assertFalse(result.success)
        self.assertIn("시간 초과", result.error)


if __name__ == '__main__':
    unittest.main()
