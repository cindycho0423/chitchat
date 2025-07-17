from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    chat_id: str
    timestamp: datetime

class ChatListResponse(BaseModel):
    chat_id: str
    created_at: datetime
    last_message: Optional[str]
    message_count: int

class WebSocketMessage(BaseModel):
    type: str  # "user_message", "ai_start", "ai_chunk", "ai_complete", "error"
    message: Optional[str] = None
    chunk: Optional[str] = None
    timestamp: str