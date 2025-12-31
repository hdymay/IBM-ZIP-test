"""Unit tests for SampleExecutor class."""

import pytest
import tempfile
import os
from pathlib import Path
from src.core.sample_executor import SampleExecutor
from src.models.data_models import SampleExecutionResult, SampleExecutionSummary


class TestSampleExecutor:
    """SampleExecutor 클래스 테스트"""
    
    def test_execute_sample_success(self):
        """성공적인 샘플 실행 테스트"""
        executor = SampleExecutor()
        
        # 임시 성공 샘플 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import sys\nprint("Success")\nsys.exit(0)\n')
            temp_file = f.name
        
        try:
            result = executor.execute_sample(temp_file)
            
            assert result.success is True
            assert result.error_message is None
            assert result.execution_time > 0
            assert result.sample_name is not None
            assert result.timestamp is not None
        finally:
            os.unlink(temp_file)
    
    def test_execute_sample_failure(self):
        """실패하는 샘플 실행 테스트"""
        executor = SampleExecutor()
        
        # 임시 실패 샘플 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import sys\nprint("Failure")\nsys.exit(1)\n')
            temp_file = f.name
        
        try:
            result = executor.execute_sample(temp_file)
            
            assert result.success is False
            assert result.error_message is not None
            assert "반환 코드" in result.error_message
        finally:
            os.unlink(temp_file)
    
    def test_execute_sample_file_not_found(self):
        """존재하지 않는 파일 실행 테스트"""
        executor = SampleExecutor()
        
        result = executor.execute_sample("nonexistent_file.py")
        
        assert result.success is False
        assert result.error_message is not None
        # 파일이 없을 때는 반환 코드 2가 나올 수 있음
        assert ("찾을 수 없음" in result.error_message or "반환 코드" in result.error_message)
    
    def test_execute_samples_multiple(self):
        """여러 샘플 파일 실행 테스트"""
        executor = SampleExecutor()
        
        # 임시 샘플 파일들 생성
        temp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(f'import sys\nprint("Sample {i}")\nsys.exit(0)\n')
                temp_files.append(f.name)
        
        try:
            results = executor.execute_samples(temp_files)
            
            assert len(results) == 3
            assert all(r.success for r in results)
        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)
    
    def test_get_execution_summary_all_success(self):
        """모든 샘플 성공 시 요약 테스트"""
        executor = SampleExecutor()
        
        # 임시 성공 샘플 파일들 생성
        temp_files = []
        for i in range(5):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(f'import sys\nprint("Sample {i}")\nsys.exit(0)\n')
                temp_files.append(f.name)
        
        try:
            executor.execute_samples(temp_files)
            summary = executor.get_execution_summary()
            
            assert summary.total_samples == 5
            assert summary.successful_samples == 5
            assert summary.failed_samples == 0
            assert summary.success_rate == 100.0
            assert len(summary.failed_sample_names) == 0
            assert summary.total_execution_time > 0
        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)
    
    def test_get_execution_summary_mixed_results(self):
        """성공/실패 혼합 시 요약 테스트"""
        executor = SampleExecutor()
        
        # 성공 샘플 2개
        success_files = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(f'import sys\nprint("Success {i}")\nsys.exit(0)\n')
                success_files.append(f.name)
        
        # 실패 샘플 3개
        failure_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(f'import sys\nprint("Failure {i}")\nsys.exit(1)\n')
                failure_files.append(f.name)
        
        all_files = success_files + failure_files
        
        try:
            executor.execute_samples(all_files)
            summary = executor.get_execution_summary()
            
            assert summary.total_samples == 5
            assert summary.successful_samples == 2
            assert summary.failed_samples == 3
            assert summary.success_rate == 40.0
            assert len(summary.failed_sample_names) == 3
        finally:
            for temp_file in all_files:
                os.unlink(temp_file)
    
    def test_get_execution_summary_empty(self):
        """실행 결과가 없을 때 요약 테스트"""
        executor = SampleExecutor()
        summary = executor.get_execution_summary()
        
        assert summary.total_samples == 0
        assert summary.successful_samples == 0
        assert summary.failed_samples == 0
        assert summary.success_rate == 0.0
        assert len(summary.failed_sample_names) == 0
        assert summary.total_execution_time == 0.0
    
    def test_clear_results(self):
        """결과 초기화 테스트"""
        executor = SampleExecutor()
        
        # 임시 샘플 파일 생성 및 실행
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import sys\nprint("Test")\nsys.exit(0)\n')
            temp_file = f.name
        
        try:
            executor.execute_sample(temp_file)
            assert len(executor.get_results()) == 1
            
            executor.clear_results()
            assert len(executor.get_results()) == 0
        finally:
            os.unlink(temp_file)
    
    def test_get_results(self):
        """결과 조회 테스트"""
        executor = SampleExecutor()
        
        # 임시 샘플 파일들 생성
        temp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(f'import sys\nprint("Sample {i}")\nsys.exit(0)\n')
                temp_files.append(f.name)
        
        try:
            executor.execute_samples(temp_files)
            results = executor.get_results()
            
            assert len(results) == 3
            assert all(isinstance(r, SampleExecutionResult) for r in results)
        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)
    
    def test_execute_actual_samples(self):
        """실제 샘플 파일들 실행 테스트"""
        executor = SampleExecutor()
        
        # samples 디렉토리의 실제 샘플 파일들
        samples_dir = Path("samples")
        if not samples_dir.exists():
            pytest.skip("samples 디렉토리가 존재하지 않습니다")
        
        sample_files = [
            "samples/ingest.py",
            "samples/parse.py",
            "samples/extract.py",
            "samples/transform.py",
            "samples/generate.py",
            "samples/validate.py",
            "samples/report.py"
        ]
        
        # 존재하는 파일만 필터링
        existing_files = [f for f in sample_files if Path(f).exists()]
        
        if not existing_files:
            pytest.skip("샘플 파일이 존재하지 않습니다")
        
        results = executor.execute_samples(existing_files)
        summary = executor.get_execution_summary()
        
        # 모든 샘플이 성공해야 함
        assert summary.success_rate == 100.0
        assert summary.failed_samples == 0
        assert len(results) == len(existing_files)
