"""
C to Java 변환 파이프라인 - 메인 진입점

watsonx.ai TP에서 실행되는 메인 스크립트입니다.
모든 파이프라인 단계를 순차적으로 실행합니다.
"""

import sys
from datetime import datetime

# 각 단계 모듈 import
import ingest
import parse
import extract
import transform
import generate
import validate
import report


def run_pipeline():
    """전체 파이프라인 실행"""
    print("=" * 60)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] C to Java 변환 파이프라인 시작")
    print("=" * 60)
    
    steps = [
        ("1. 데이터 수집", ingest.main),
        ("2. 파싱", parse.main),
        ("3. 추출", extract.main),
        ("4. 변환", transform.main),
        ("5. 생성", generate.main),
        ("6. 검증", validate.main),
        ("7. 보고서", report.main),
    ]
    
    results = []
    
    for step_name, step_func in steps:
        print(f"\n{'=' * 40}")
        print(f"[단계] {step_name}")
        print("=" * 40)
        
        try:
            result = step_func()
            results.append((step_name, "성공", result))
            print(f"✓ {step_name} 완료")
        except Exception as e:
            results.append((step_name, "실패", str(e)))
            print(f"✗ {step_name} 실패: {e}")
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("파이프라인 실행 결과 요약")
    print("=" * 60)
    
    success_count = sum(1 for _, status, _ in results if status == "성공")
    total_count = len(results)
    
    for step_name, status, _ in results:
        icon = "✓" if status == "성공" else "✗"
        print(f"  {icon} {step_name}: {status}")
    
    print(f"\n총 {total_count}개 단계 중 {success_count}개 성공")
    print("=" * 60)
    
    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    sys.exit(run_pipeline())
