"""
네트워크 접근 테스트 DAG

회사 Airflow 환경에서 외부 네트워크 접근 가능 여부를 테스트합니다.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import socket


def test_dns():
    """DNS 해석 테스트"""
    print("=" * 50)
    print("DNS 해석 테스트")
    print("=" * 50)
    
    test_domains = [
        'google.com',
        'github.com',
        'iam.cloud.ibm.com',
        'api.dataplatform.cloud.ibm.com'
    ]
    
    results = []
    for domain in test_domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"✓ {domain} -> {ip}")
            results.append((domain, ip, True))
        except Exception as e:
            print(f"✗ {domain} -> 실패: {e}")
            results.append((domain, str(e), False))
    
    success_count = sum(1 for _, _, success in results if success)
    print(f"\n결과: {success_count}/{len(test_domains)} 성공")
    
    return results


def test_http():
    """HTTP 접근 테스트"""
    print("=" * 50)
    print("HTTP 접근 테스트")
    print("=" * 50)
    
    try:
        import urllib.request
        response = urllib.request.urlopen('http://www.google.com', timeout=5)
        print(f"✓ HTTP 접근 가능: {response.status}")
        return True
    except Exception as e:
        print(f"✗ HTTP 접근 불가: {e}")
        return False


def test_https():
    """HTTPS 접근 테스트"""
    print("=" * 50)
    print("HTTPS 접근 테스트")
    print("=" * 50)
    
    try:
        import urllib.request
        response = urllib.request.urlopen('https://www.google.com', timeout=5)
        print(f"✓ HTTPS 접근 가능: {response.status}")
        return True
    except Exception as e:
        print(f"✗ HTTPS 접근 불가: {e}")
        return False


def test_watsonx():
    """watsonx.ai 접근 테스트"""
    print("=" * 50)
    print("watsonx.ai 접근 테스트")
    print("=" * 50)
    
    endpoints = [
        'https://iam.cloud.ibm.com',
        'https://api.dataplatform.cloud.ibm.com'
    ]
    
    results = []
    for endpoint in endpoints:
        try:
            import urllib.request
            response = urllib.request.urlopen(endpoint, timeout=5)
            print(f"✓ {endpoint} 접근 가능: {response.status}")
            results.append((endpoint, True))
        except Exception as e:
            print(f"✗ {endpoint} 접근 불가: {e}")
            results.append((endpoint, False))
    
    success_count = sum(1 for _, success in results if success)
    print(f"\n결과: {success_count}/{len(endpoints)} 성공")
    
    return results


def test_github():
    """GitHub 접근 테스트"""
    print("=" * 50)
    print("GitHub 접근 테스트")
    print("=" * 50)
    
    try:
        import urllib.request
        response = urllib.request.urlopen('https://api.github.com', timeout=5)
        print(f"✓ GitHub 접근 가능: {response.status}")
        return True
    except Exception as e:
        print(f"✗ GitHub 접근 불가: {e}")
        return False


def test_proxy():
    """프록시 설정 확인"""
    print("=" * 50)
    print("프록시 설정 확인")
    print("=" * 50)
    
    import os
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY', 'no_proxy']
    
    found_proxy = False
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"✓ {var} = {value}")
            found_proxy = True
        else:
            print(f"  {var} = (설정 안 됨)")
    
    if not found_proxy:
        print("\n프록시 설정이 없습니다.")
    
    return found_proxy


with DAG(
    'test_network_access',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['test', 'network', 'company'],
    description='회사 Airflow 환경 네트워크 접근 테스트'
) as dag:
    
    test_dns_task = PythonOperator(
        task_id='test_dns',
        python_callable=test_dns
    )
    
    test_http_task = PythonOperator(
        task_id='test_http',
        python_callable=test_http
    )
    
    test_https_task = PythonOperator(
        task_id='test_https',
        python_callable=test_https
    )
    
    test_watsonx_task = PythonOperator(
        task_id='test_watsonx',
        python_callable=test_watsonx
    )
    
    test_github_task = PythonOperator(
        task_id='test_github',
        python_callable=test_github
    )
    
    test_proxy_task = PythonOperator(
        task_id='test_proxy',
        python_callable=test_proxy
    )
    
    # 순차 실행
    test_proxy_task >> test_dns_task >> [test_http_task, test_https_task, test_watsonx_task, test_github_task]
