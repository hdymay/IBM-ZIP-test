"""
GitHub API 연결 테스트 스크립트

GitHub 토큰과 저장소 접근을 테스트합니다.
"""

import os
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_github_connection():
    """GitHub API 연결 테스트"""
    
    print("=" * 60)
    print("GitHub API 연결 테스트")
    print("=" * 60)
    
    # 환경 변수 확인
    github_token = os.getenv('GITHUB_TOKEN')
    github_repo_url = os.getenv('GITHUB_REPO_URL')
    
    print(f"\n📋 설정 확인:")
    print(f"   GITHUB_TOKEN: {'✓ 설정됨' if github_token else '❌ 없음'}")
    print(f"   GITHUB_REPO_URL: {github_repo_url}")
    
    if not github_token:
        print("\n❌ GitHub 토큰이 설정되지 않았습니다")
        return False
    
    if not github_repo_url:
        print("\n❌ GitHub 저장소 URL이 설정되지 않았습니다")
        return False
    
    # 저장소 URL에서 owner/repo 추출
    repo_url = github_repo_url
    if repo_url.endswith('.git'):
        repo_url = repo_url[:-4]  # .git 제거
    
    parts = repo_url.replace('https://github.com/', '').split('/')
    if len(parts) < 2:
        print(f"\n❌ 잘못된 GitHub URL 형식: {github_repo_url}")
        return False
    
    owner = parts[0]
    repo = parts[1]
    
    print(f"   Owner: {owner}")
    print(f"   Repo: {repo}")
    print(f"   전체 URL: https://github.com/{owner}/{repo}")
    
    # 1. 토큰 유효성 테스트
    print(f"\n🔐 토큰 유효성 테스트...")
    
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'GitHub-Connection-Test'
    }
    
    try:
        # 사용자 정보 확인
        user_response = requests.get('https://api.github.com/user', headers=headers)
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"   ✓ 토큰 유효 (사용자: {user_data.get('login', 'unknown')})")
        elif user_response.status_code == 401:
            print(f"   ❌ 토큰 무효 (401 Unauthorized)")
            print(f"   응답: {user_response.text}")
            return False
        else:
            print(f"   ⚠ 예상치 못한 응답: HTTP {user_response.status_code}")
            print(f"   응답: {user_response.text}")
    
    except Exception as e:
        print(f"   ❌ 토큰 테스트 중 오류: {e}")
        return False
    
    # 2. 저장소 접근 권한 테스트
    print(f"\n📁 저장소 접근 권한 테스트...")
    
    try:
        # 저장소 정보 확인
        repo_url = f'https://api.github.com/repos/{owner}/{repo}'
        repo_response = requests.get(repo_url, headers=headers)
        
        if repo_response.status_code == 200:
            repo_data = repo_response.json()
            print(f"   ✓ 저장소 접근 가능")
            print(f"   저장소: {repo_data.get('full_name')}")
            print(f"   권한: {repo_data.get('permissions', {})}")
        elif repo_response.status_code == 404:
            print(f"   ❌ 저장소를 찾을 수 없음 (404)")
            print(f"   저장소가 존재하는지, 또는 private 저장소에 대한 권한이 있는지 확인하세요")
            return False
        else:
            print(f"   ❌ 저장소 접근 실패: HTTP {repo_response.status_code}")
            print(f"   응답: {repo_response.text}")
            return False
    
    except Exception as e:
        print(f"   ❌ 저장소 테스트 중 오류: {e}")
        return False
    
    # 3. Contents API 권한 테스트
    print(f"\n📝 Contents API 권한 테스트...")
    
    try:
        # 저장소의 README 파일 확인 (읽기 테스트)
        contents_url = f'https://api.github.com/repos/{owner}/{repo}/contents'
        contents_response = requests.get(contents_url, headers=headers)
        
        if contents_response.status_code == 200:
            print(f"   ✓ Contents API 읽기 권한 있음")
            
            # 파일 목록 표시
            contents_data = contents_response.json()
            if isinstance(contents_data, list):
                print(f"   저장소 파일 ({len(contents_data)}개):")
                for item in contents_data[:5]:  # 최대 5개만 표시
                    print(f"     - {item.get('name')} ({item.get('type')})")
                if len(contents_data) > 5:
                    print(f"     ... 외 {len(contents_data) - 5}개")
        else:
            print(f"   ❌ Contents API 접근 실패: HTTP {contents_response.status_code}")
            print(f"   응답: {contents_response.text}")
            return False
    
    except Exception as e:
        print(f"   ❌ Contents API 테스트 중 오류: {e}")
        return False
    
    # 4. 쓰기 권한 테스트 (실제 파일 생성하지 않고 시뮬레이션)
    print(f"\n✏️ 쓰기 권한 확인...")
    
    # 토큰의 스코프 확인
    if user_response.status_code == 200:
        scopes = user_response.headers.get('X-OAuth-Scopes', '')
        print(f"   토큰 스코프: {scopes}")
        
        if 'repo' in scopes or 'public_repo' in scopes:
            print(f"   ✓ 저장소 쓰기 권한 있음")
        else:
            print(f"   ❌ 저장소 쓰기 권한 없음")
            print(f"   토큰 생성 시 'repo' 스코프를 선택했는지 확인하세요")
            return False
    
    print(f"\n✅ 모든 테스트 통과!")
    print(f"GitHub 업로드가 정상적으로 작동해야 합니다.")
    
    return True


def test_rate_limit():
    """GitHub API 속도 제한 확인"""
    
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        return
    
    print(f"\n📊 API 속도 제한 확인...")
    
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get('https://api.github.com/rate_limit', headers=headers)
        
        if response.status_code == 200:
            rate_data = response.json()
            core = rate_data.get('resources', {}).get('core', {})
            
            print(f"   사용량: {core.get('used', 0)}/{core.get('limit', 0)}")
            print(f"   남은 요청: {core.get('remaining', 0)}")
            
            if core.get('remaining', 0) < 10:
                print(f"   ⚠ API 속도 제한에 근접했습니다")
        else:
            print(f"   ❌ 속도 제한 확인 실패: HTTP {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ 속도 제한 확인 중 오류: {e}")


if __name__ == "__main__":
    success = test_github_connection()
    test_rate_limit()
    
    if not success:
        print(f"\n" + "=" * 60)
        print("문제 해결 방법")
        print("=" * 60)
        print(f"\n1. GitHub 토큰 재생성:")
        print(f"   - https://github.com/settings/tokens")
        print(f"   - 'Generate new token (classic)' 선택")
        print(f"   - 'repo' 전체 권한 선택")
        print(f"   - 생성된 토큰을 .env 파일에 설정")
        print(f"\n2. 저장소 확인:")
        print(f"   - 저장소가 존재하는지 확인")
        print(f"   - private 저장소인 경우 접근 권한 확인")
        print(f"\n3. 토큰 만료 확인:")
        print(f"   - GitHub에서 토큰이 만료되지 않았는지 확인")