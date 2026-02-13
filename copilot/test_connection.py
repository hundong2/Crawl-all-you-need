"""
API 연결 상태 테스트 스크립트
"""
import os
from dotenv import load_dotenv
from ai_web_crawler.models.llm_providers import get_llm_provider

# 환경 변수 로드
load_dotenv()

def test_provider_connection(provider_name, env_var):
    """제공자 연결 테스트"""
    print(f"\n{'='*50}")
    print(f"테스트: {provider_name}")
    print(f"{'='*50}")
    
    api_key = os.getenv(env_var)
    
    if not api_key or api_key.startswith("your_"):
        print(f"⚪ API 키 없음 ({env_var})")
        return False
    
    try:
        # 제공자 초기화
        provider = get_llm_provider(provider_name, api_key, "")
        
        # 연결 확인
        is_connected, message = provider.check_connection()
        print(f"연결 상태: {message}")
        
        if is_connected:
            # 사용 가능한 모델 가져오기
            models = provider.get_available_models()
            print(f"사용 가능한 모델: {len(models)}개")
            print(f"모델 목록:")
            for i, model in enumerate(models[:5], 1):
                print(f"  {i}. {model}")
            if len(models) > 5:
                print(f"  ... 외 {len(models) - 5}개")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🔌 AI Web Crawler - API 연결 상태 테스트")
    print("="*50)
    
    providers = {
        "OpenAI (ChatGPT)": "OPENAI_API_KEY",
        "Anthropic (Claude)": "ANTHROPIC_API_KEY",
        "Google (Gemini)": "GOOGLE_API_KEY"
    }
    
    results = {}
    for provider_name, env_var in providers.items():
        results[provider_name] = test_provider_connection(provider_name, env_var)
    
    # 요약
    print(f"\n{'='*50}")
    print("📊 연결 상태 요약")
    print(f"{'='*50}")
    for provider_name, success in results.items():
        status = "✅ 연결됨" if success else "❌ 연결 안됨"
        print(f"{provider_name.split(' ')[0]:15s}: {status}")
    
    connected_count = sum(results.values())
    print(f"\n총 {connected_count}/{len(results)}개 제공자 연결됨")

if __name__ == "__main__":
    main()
