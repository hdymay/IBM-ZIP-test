"""
URL 파싱 디버깅 스크립트
"""

import os
from dotenv import load_dotenv

load_dotenv()

github_repo_url = os.getenv('GITHUB_REPO_URL')
print(f"원본 URL: '{github_repo_url}'")
print(f"URL 길이: {len(github_repo_url)}")
print(f"URL 바이트: {github_repo_url.encode()}")

# 단계별 파싱
repo_url = github_repo_url
if repo_url.endswith('.git'):
    repo_url = repo_url[:-4]
print(f"1. .git 제거 후: '{repo_url}'")

without_github = repo_url.replace('https://github.com/', '')
print(f"2. github.com 제거 후: '{without_github}'")

parts = without_github.split('/')
print(f"3. '/' 분리 후: {parts}")
print(f"   parts 개수: {len(parts)}")

if len(parts) >= 2:
    owner = parts[0]
    repo = parts[1]
    print(f"4. Owner: '{owner}' (길이: {len(owner)})")
    print(f"   Repo: '{repo}' (길이: {len(repo)})")
    print(f"   Repo 바이트: {repo.encode()}")