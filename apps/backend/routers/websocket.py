from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import json
import uuid

from db.database import get_db, Chat, Message
from ai.index import AIService
from routers.manager import manager

router = APIRouter()
ai_service = AIService()

@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str, db: Session = Depends(get_db)):
    """웹소켓 채팅 엔드포인트"""
    await manager.connect(websocket, chat_id)
    
    # 채팅 생성 또는 가져오기
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        chat = Chat(id=chat_id, created_at=datetime.utcnow())
        db.add(chat)
        db.commit()
    
    try:
        while True:
            # 메시지 수신
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message")
            
            if not user_message:
                continue
            
            # 사용자 메시지 저장
            user_msg = Message(
                id=str(uuid.uuid4()),
                chat_id=chat_id,
                role="user",
                content=user_message,
                created_at=datetime.utcnow()
            )
            db.add(user_msg)
            db.commit()
            
            # 사용자 메시지 에코
            await manager.send_message(chat_id, {
                "type": "user_message",
                "message": user_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # 히스토리 가져오기
            history = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()
            
            # AI 응답 생성 (스트리밍)
            ai_response = ""
            await manager.send_message(chat_id, {
                "type": "ai_start",
                "message": "",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            try:
                async for chunk in ai_service.generate_stream_response(user_message, history):
                    ai_response += chunk
                    await manager.send_message(chat_id, {
                        "type": "ai_chunk",
                        "chunk": chunk,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                # AI 응답 저장
                ai_msg = Message(
                    id=str(uuid.uuid4()),
                    chat_id=chat_id,
                    role="assistant",
                    content=ai_response,
                    created_at=datetime.utcnow()
                )
                db.add(ai_msg)
                db.commit()
                
                # 완료 신호
                await manager.send_message(chat_id, {
                    "type": "ai_complete",
                    "message": ai_response,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                await manager.send_message(chat_id, {
                    "type": "error",
                    "message": f"AI 응답 생성 중 오류: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
    except WebSocketDisconnect:
        manager.disconnect(chat_id)
    except Exception as e:
        await manager.send_message(chat_id, {
            "type": "error",
            "message": f"연결 오류: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        })
        manager.disconnect(chat_id)