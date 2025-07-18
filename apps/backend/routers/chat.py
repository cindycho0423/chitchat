from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, cast
from datetime import datetime
import uuid

from db.database import get_db, Chat, Message
from ai.index import AIService
from schema.chat import ChatRequest, ChatResponse, ChatListResponse

router = APIRouter()
ai_service = AIService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """REST API 채팅"""
    chat_id = request.chat_id or str(uuid.uuid4())
    
    # 채팅 생성 또는 가져오기
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        chat = Chat(id=chat_id, created_at=datetime.utcnow())
        db.add(chat)
        db.commit()
    
    # 히스토리 가져오기
    history = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()
    
    # AI 응답 생성
    try:
        response_chunks = []
        async for chunk in ai_service.generate_stream_response(
            user_message=request.message,
            history=history
        ):
            response_chunks.append(chunk)
        
        ai_response = "".join(response_chunks).strip()
        
        # 메시지 저장
        user_msg = Message(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            role="user",
            content=request.message,
            created_at=datetime.utcnow()
        )
        ai_msg = Message(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            role="assistant",
            content=ai_response,
            created_at=datetime.utcnow()
        )
        
        db.add_all([user_msg, ai_msg])
        db.commit()
        
        return ChatResponse(
            message=ai_response,
            chat_id=chat_id,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chats", response_model=List[ChatListResponse])
async def get_chats(db: Session = Depends(get_db)):
    """채팅 목록 조회"""
    chats = db.query(Chat).order_by(Chat.created_at.desc()).all()
    
    result = []
    for chat in chats:
        last_message = db.query(Message).filter(Message.chat_id == chat.id).order_by(Message.created_at.desc()).first()
        result.append(ChatListResponse(
            chat_id=cast(str, chat.id),
            created_at=cast(datetime, chat.created_at),
            last_message=cast(str, last_message.content) if last_message else None,
            message_count=db.query(Message).filter(Message.chat_id == chat.id).count()
        ))
    
    return result

@router.get("/chat/{chat_id}")
async def get_chat_history(chat_id: str, db: Session = Depends(get_db)):
    """채팅 히스토리 조회"""
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()
    
    if not messages:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    return {
        "chat_id": chat_id,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at
            }
            for msg in messages
        ]
    }

@router.delete("/chat/{chat_id}")
async def delete_chat(chat_id: str, db: Session = Depends(get_db)):
    """채팅 삭제"""
    # 메시지 먼저 삭제
    db.query(Message).filter(Message.chat_id == chat_id).delete()
    # 채팅 삭제
    db.query(Chat).filter(Chat.id == chat_id).delete()
    db.commit()
    
    return {"message": "Chat deleted"}