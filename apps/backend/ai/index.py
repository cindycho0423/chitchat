import openai
from typing import List, AsyncGenerator
from config.index import settings

class AIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )
        self.model = settings.MODEL_NAME
    
    async def generate_response(self, message: str, history: List) -> str:
        """일반 응답 생성"""
        messages = self._prepare_messages(message, history)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    async def generate_stream_response(self, message: str, history: List) -> AsyncGenerator[str, None]:
        """스트리밍 응답 생성"""
        messages = self._prepare_messages(message, history)
        
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def _prepare_messages(self, message: str, history: List) -> List[dict]:
        """메시지 준비"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        
        # 히스토리 추가 (최근 10개만)
        for msg in history[-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # 현재 메시지
        messages.append({
            "role": "user",
            "content": message
        })
        
        return messages