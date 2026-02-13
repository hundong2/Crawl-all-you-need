"""LLM 제공자 통합 모듈"""
import os
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """LLM 제공자 추상 베이스 클래스"""
    
    @abstractmethod
    def process_content(self, content: str, prompt: str) -> str:
        """콘텐츠 처리"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> list[str]:
        """사용 가능한 모델 목록"""
        pass
    
    @abstractmethod
    def check_connection(self) -> tuple[bool, str]:
        """
        API 연결 상태 확인
        Returns: (성공 여부, 메시지)
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI/ChatGPT 제공자"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = model
        except Exception as e:
            raise RuntimeError(f"OpenAI 초기화 실패: {e}")
    
    def process_content(self, content: str, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": content}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI 처리 실패: {e}")
    
    def get_available_models(self) -> list[str]:
        """API에서 사용 가능한 모델 목록 가져오기"""
        try:
            models = self.client.models.list()
            # GPT 모델만 필터링
            gpt_models = [
                model.id for model in models.data 
                if 'gpt' in model.id.lower() and not model.id.startswith('ft:')
            ]
            # 최신 모델 우선 정렬
            priority_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
            sorted_models = []
            for pm in priority_models:
                if pm in gpt_models:
                    sorted_models.append(pm)
            for model in gpt_models:
                if model not in sorted_models:
                    sorted_models.append(model)
            return sorted_models if sorted_models else [
                "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"
            ]
        except:
            # API 호출 실패 시 기본 모델 반환
            return [
                "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"
            ]
    
    def check_connection(self) -> tuple[bool, str]:
        """OpenAI API 연결 확인"""
        try:
            models = self.client.models.list()
            return (True, f"✅ 연결됨 ({len(models.data)}개 모델 사용 가능)")
        except Exception as e:
            return (False, f"❌ 연결 실패: {str(e)[:50]}")


class AnthropicProvider(LLMProvider):
    """Anthropic/Claude 제공자"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
            self.model = model
        except Exception as e:
            raise RuntimeError(f"Anthropic 초기화 실패: {e}")
    
    def process_content(self, content: str, prompt: str) -> str:
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": f"{prompt}\n\n{content}"}
                ]
            )
            return message.content[0].text
        except Exception as e:
            raise RuntimeError(f"Anthropic 처리 실패: {e}")
    
    def get_available_models(self) -> list[str]:
        """사용 가능한 Claude 모델 목록"""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    
    def check_connection(self) -> tuple[bool, str]:
        """Anthropic API 연결 확인"""
        try:
            # 간단한 테스트 메시지로 연결 확인
            message = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return (True, "✅ 연결됨")
        except Exception as e:
            return (False, f"❌ 연결 실패: {str(e)[:50]}")


class GoogleProvider(LLMProvider):
    """Google/Gemini 제공자"""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.genai = genai
            self.model = genai.GenerativeModel(model)
            self.model_name = model
        except Exception as e:
            raise RuntimeError(f"Google 초기화 실패: {e}")
    
    def process_content(self, content: str, prompt: str) -> str:
        try:
            full_prompt = f"{prompt}\n\n{content}"
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Google 처리 실패: {e}")
    
    def get_available_models(self) -> list[str]:
        """API에서 사용 가능한 Gemini 모델 목록 가져오기"""
        try:
            models = self.genai.list_models()
            gemini_models = [
                model.name.replace('models/', '') 
                for model in models 
                if 'gemini' in model.name.lower() and model.supported_generation_methods
                and 'generateContent' in model.supported_generation_methods
            ]
            return gemini_models if gemini_models else [
                "gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"
            ]
        except:
            return [
                "gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"
            ]
    
    def check_connection(self) -> tuple[bool, str]:
        """Google Gemini API 연결 확인"""
        try:
            models = list(self.genai.list_models())
            gemini_count = len([m for m in models if 'gemini' in m.name.lower()])
            return (True, f"✅ 연결됨 ({gemini_count}개 모델 사용 가능)")
        except Exception as e:
            return (False, f"❌ 연결 실패: {str(e)[:50]}")


def get_llm_provider(provider_name: str, api_key: str, model: str) -> LLMProvider:
    """LLM 제공자 팩토리 함수"""
    providers = {
        "OpenAI (ChatGPT)": OpenAIProvider,
        "Anthropic (Claude)": AnthropicProvider,
        "Google (Gemini)": GoogleProvider
    }
    
    if provider_name not in providers:
        raise ValueError(f"지원하지 않는 제공자: {provider_name}")
    
    return providers[provider_name](api_key, model)
