"""Sample executor module for running and tracking sample file executions."""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.models.data_models import SampleExecutionResult, SampleExecutionSummary


class SampleExecutor:
    """
    샘플 파일 실행 및 결과 추적 클래스.
    
    샘플 Python 파일들을 실행하고 성공/실패를 추적합니다.
    Requirements: 5.4, 5.5
    """
    
    def __init__(self):
        """SampleExecutor 초기화."""
        self._execution_results: List[SampleExecutionResult] = []
    
    def execute_sample(self, file_path: str) -> SampleExecutionResult:
        """
        단일 샘플 파일을 실행하고 결과를 기록합니다.
        
        Requirements: 5.4
        
        Args:
            file_path: 실행할 샘플 파일 경로
            
        Returns:
            SampleExecutionResult: 실행 결과
        """
        path = Path(file_path)
        sample_name = path.stem
        
        start_time = time.time()
        success = False
        error_message = None
        
        try:
            # Python 인터프리터로 샘플 파일 실행
            result = subprocess.run(
                [sys.executable, str(path)],
                capture_output=True,
                text=True,
                timeout=30,  # 30초 타임아웃
                check=True
            )
            
            # 반환 코드가 0이면 성공
            success = (result.returncode == 0)
            
        except subprocess.TimeoutExpired:
            error_message = "실행 시간 초과 (30초)"
        except subprocess.CalledProcessError as e:
            error_message = f"실행 실패: 반환 코드 {e.returncode}"
        except FileNotFoundError:
            error_message = f"파일을 찾을 수 없음: {file_path}"
        except Exception as e:
            error_message = f"예상치 못한 오류: {str(e)}"
        
        execution_time = time.time() - start_time
        
        result = SampleExecutionResult(
            sample_name=sample_name,
            file_path=str(path.absolute()),
            success=success,
            execution_time=execution_time,
            error_message=error_message,
            timestamp=datetime.now()
        )
        
        self._execution_results.append(result)
        return result
    
    def execute_samples(self, file_paths: List[str]) -> List[SampleExecutionResult]:
        """
        여러 샘플 파일을 순차적으로 실행합니다.
        
        Requirements: 5.4
        
        Args:
            file_paths: 실행할 샘플 파일 경로 목록
            
        Returns:
            실행 결과 목록
        """
        results = []
        
        for file_path in file_paths:
            result = self.execute_sample(file_path)
            results.append(result)
        
        return results
    
    def get_execution_summary(self) -> SampleExecutionSummary:
        """
        실행 결과 요약을 생성합니다.
        
        Requirements: 5.5
        
        Returns:
            SampleExecutionSummary: 실행 요약
        """
        total_samples = len(self._execution_results)
        successful_samples = sum(1 for r in self._execution_results if r.success)
        failed_samples = total_samples - successful_samples
        
        # 성공률 계산 (0으로 나누기 방지)
        success_rate = (successful_samples / total_samples * 100) if total_samples > 0 else 0.0
        
        # 실패한 샘플 이름 목록
        failed_sample_names = [r.sample_name for r in self._execution_results if not r.success]
        
        # 총 실행 시간
        total_execution_time = sum(r.execution_time for r in self._execution_results)
        
        return SampleExecutionSummary(
            total_samples=total_samples,
            successful_samples=successful_samples,
            failed_samples=failed_samples,
            success_rate=success_rate,
            failed_sample_names=failed_sample_names,
            execution_results=self._execution_results.copy(),
            total_execution_time=total_execution_time
        )
    
    def clear_results(self) -> None:
        """실행 결과를 초기화합니다."""
        self._execution_results.clear()
    
    def get_results(self) -> List[SampleExecutionResult]:
        """
        현재까지의 실행 결과를 반환합니다.
        
        Returns:
            실행 결과 목록
        """
        return self._execution_results.copy()
    
    def print_summary(self) -> None:
        """
        실행 요약을 콘솔에 출력합니다.
        
        Requirements: 5.5
        """
        summary = self.get_execution_summary()
        
        print("\n" + "=" * 60)
        print("샘플 실행 요약")
        print("=" * 60)
        print(f"총 샘플 수: {summary.total_samples}")
        print(f"성공: {summary.successful_samples}")
        print(f"실패: {summary.failed_samples}")
        print(f"성공률: {summary.success_rate:.2f}%")
        print(f"총 실행 시간: {summary.total_execution_time:.2f}초")
        
        if summary.failed_sample_names:
            print("\n실패한 샘플:")
            for name in summary.failed_sample_names:
                # 해당 샘플의 에러 메시지 찾기
                result = next((r for r in summary.execution_results if r.sample_name == name), None)
                if result and result.error_message:
                    print(f"  - {name}: {result.error_message}")
                else:
                    print(f"  - {name}")
        else:
            print("\n모든 샘플이 성공적으로 실행되었습니다!")
        
        print("=" * 60 + "\n")
