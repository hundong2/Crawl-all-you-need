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
        return [
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-4o",
            "gpt-4o-mini"
        ]


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
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]


class GoogleProvider(LLMProvider):
    """Google/Gemini 제공자"""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
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
        return [
            "gemini-pro",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]


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
