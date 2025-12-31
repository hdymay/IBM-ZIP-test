"""
watsonx.ai 연결 테스트 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.config_manager import ConfigManager

def test_connection():
    """watsonx.ai 연결 테스트"""
    
    print("=" * 60)
    print("watsonx.ai 연결 테스트")
    print("=" * 60)
    
    try:
        # 설정 로드
        print("1. 설정 로드 중...")
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        print(f"   ✓ API 키: {config.watsonx_api_key[:10]}...")
        print(f"   ✓ 엔드포인트: {config.watsonx_endpoint}")
        print(f"   ✓ 프로젝트 ID: {config.watsonx_project_id}")
        
        # 설정 검증
        print("\n2. 설정 검증 중...")
        config_manager.validate_config(config)
        print("   ✓ 설정 검증 완료")
        
        # 연결 테스트
        print("\n3. watsonx.ai 연결 테스트 중...")
        success, error_message = config_manager.test_connection(config)
        
        if success:
            print("   ✅ 연결 성공!")
            print("\n모든 설정이 올바릅니다. 파이프라인을 실행할 수 있습니다.")
        else:
            print(f"   ❌ 연결 실패: {error_message}")
            print("\n해결 방법:")
            
            if "404" in str(error_message):
                print("   - 프로젝트 ID가 존재하지 않습니다")
                print("   - https://dataplatform.cloud.ibm.com/projects 에서 프로젝트 확인")
            elif "401" in str(error_message):
                print("   - API 키가 유효하지 않습니다")
                print("   - https://cloud.ibm.com/iam/apikeys 에서 API 키 확인")
            elif "timeout" in str(error_message).lower():
                print("   - 네트워크 연결 또는 엔드포인트 확인")
                print("   - 리전별 엔드포인트가 올바른지 확인")
        
        return success
        
    except FileNotFoundError:
        print("❌ .env 파일이 없거나 환경 변수가 설정되지 않았습니다.")
        print("\n.env 파일을 생성하고 다음 값들을 설정하세요:")
        print("   WATSONX_API_KEY=your_api_key")
        print("   WATSONX_ENDPOINT=https://us-south.ml.cloud.ibm.com")
        print("   WATSONX_PROJECT_ID=your_project_id")
        return False
        
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_connection()
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 설정 완료! 이제 'python main.py'를 실행하세요.")
    else:
        print("⚠️ 설정을 수정한 후 다시 테스트하세요.")
        print("   python test_connection.py")