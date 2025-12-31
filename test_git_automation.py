"""
Git 자동화 기능 테스트 스크립트

실제로 Git push/pull이 자동으로 동작하는지 테스트합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.git_manager import GitManager


def print_result(title: str, result):
    """결과를 보기 좋게 출력"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print(f"성공 여부: {'✓ 성공' if result.success else '✗ 실패'}")
    print(f"메시지: {result.message}")
    if result.output:
        print(f"\n출력:\n{result.output}")
    if result.error:
        print(f"\n에러:\n{result.error}")


def test_git_status():
    """Git 상태 확인 테스트"""
    print("\n" + "=" * 60)
    print("Git 자동화 기능 테스트")
    print("=" * 60)
    
    git = GitManager()
    
    # 1. 상태 확인
    print("\n[1] Git 상태 확인 중...")
    status = git.check_status()
    print_result("Git 상태", status)
    
    return git, status


def test_auto_commit_push(git: GitManager):
    """자동 커밋 및 푸시 테스트"""
    print("\n\n" + "=" * 60)
    print("자동 커밋 및 푸시 테스트")
    print("=" * 60)
    
    # 테스트 파일 생성
    test_file = Path("test_auto_git.txt")
    test_file.write_text("Git 자동화 테스트 파일\n")
    print(f"\n테스트 파일 생성: {test_file}")
    
    # 자동 커밋 및 푸시
    print("\n[2] 자동 커밋 및 푸시 실행 중...")
    result = git.auto_commit_and_push(
        commit_message="Test: Git 자동화 기능 테스트",
        remote="origin",
        branch="main"
    )
    print_result("자동 커밋 및 푸시", result)
    
    return result


def test_auto_pull(git: GitManager):
    """자동 풀 테스트"""
    print("\n\n" + "=" * 60)
    print("자동 풀 테스트")
    print("=" * 60)
    
    print("\n[3] 원격 저장소에서 변경사항 가져오기...")
    result = git.auto_pull_and_merge(
        remote="origin",
        branch="main"
    )
    print_result("자동 풀", result)
    
    return result


def interactive_test():
    """대화형 테스트"""
    print("\n" + "=" * 60)
    print("Git 자동화 대화형 테스트")
    print("=" * 60)
    
    git = GitManager()
    
    while True:
        print("\n\n옵션을 선택하세요:")
        print("  1. Git 상태 확인")
        print("  2. 자동 커밋 및 푸시")
        print("  3. 자동 풀 (원격 변경사항 가져오기)")
        print("  4. 전체 테스트 실행")
        print("  5. 종료")
        
        choice = input("\n선택 (1-5): ").strip()
        
        if choice == "1":
            status = git.check_status()
            print_result("Git 상태", status)
            
        elif choice == "2":
            commit_msg = input("\n커밋 메시지를 입력하세요: ").strip()
            if not commit_msg:
                commit_msg = "Auto commit: 자동 커밋 테스트"
            
            result = git.auto_commit_and_push(commit_msg)
            print_result("자동 커밋 및 푸시", result)
            
        elif choice == "3":
            result = git.auto_pull_and_merge()
            print_result("자동 풀", result)
            
        elif choice == "4":
            # 전체 테스트
            git_obj, status = test_git_status()
            
            if status.output:  # 변경사항이 있으면
                test_auto_commit_push(git_obj)
            else:
                print("\n변경사항이 없어 커밋/푸시를 건너뜁니다.")
            
            test_auto_pull(git_obj)
            
        elif choice == "5":
            print("\n테스트를 종료합니다.")
            break
            
        else:
            print("\n잘못된 선택입니다. 다시 시도하세요.")


def main():
    """메인 함수"""
    print("\n" + "=" * 60)
    print("Git 자동화 기능 테스트 시작")
    print("=" * 60)
    print("\n이 스크립트는 다음을 테스트합니다:")
    print("  - Git 상태 확인")
    print("  - 자동 커밋 및 푸시")
    print("  - 자동 풀 (원격 변경사항 가져오기)")
    
    print("\n\n테스트 모드를 선택하세요:")
    print("  1. 자동 테스트 (테스트 파일 생성 후 자동 실행)")
    print("  2. 대화형 테스트 (직접 선택)")
    
    mode = input("\n선택 (1-2): ").strip()
    
    if mode == "1":
        # 자동 테스트
        git, status = test_git_status()
        
        # 테스트 파일이 없으면 생성
        if not status.output or "test_auto_git.txt" not in status.output:
            test_auto_commit_push(git)
        else:
            print("\n이미 변경사항이 있습니다. 커밋/푸시를 진행합니다...")
            result = git.auto_commit_and_push("Test: 기존 변경사항 커밋")
            print_result("자동 커밋 및 푸시", result)
        
        test_auto_pull(git)
        
    elif mode == "2":
        # 대화형 테스트
        interactive_test()
        
    else:
        print("\n잘못된 선택입니다.")
        return
    
    print("\n\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n\n예상치 못한 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
