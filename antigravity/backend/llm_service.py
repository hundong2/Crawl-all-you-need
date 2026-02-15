import os
import google.generativeai as genai
from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
        
        if self.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=self.anthropic_api_key)
        
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)

    async def process_content(self, provider: str, model: str, content: str, instruction: str) -> str:
        if provider == "google":
            return await self._process_gemini(model, content, instruction)
        elif provider == "anthropic":
            return await self._process_claude(model, content, instruction)
        elif provider == "openai":
            return await self._process_openai(model, content, instruction)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _process_gemini(self, model: str, content: str, instruction: str) -> str:
        if not self.google_api_key:
            return "Error: GOOGLE_API_KEY (or GEMINI_API_KEY) not found."
        
        model_instance = genai.GenerativeModel(model)
        prompt = f"{instruction}\n\nExisting Content:\n{content}"
        response = model_instance.generate_content(prompt)
        return response.text

    async def _process_claude(self, model: str, content: str, instruction: str) -> str:
        if not self.anthropic_api_key:
            return "Error: ANTHROPIC_API_KEY not found."
        
        message = self.anthropic_client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[
                {"role": "user", "content": f"{instruction}\n\nExisting Content:\n{content}"}
            ]
        )
        return message.content[0].text

    async def _process_openai(self, model: str, content: str, instruction: str) -> str:
        if not self.openai_api_key:
            return "Error: OPENAI_API_KEY not found."

        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[
                 {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{instruction}\n\nExisting Content:\n{content}"}
            ]
        )
        return response.choices[0].message.content

llm_service = LLMService()
