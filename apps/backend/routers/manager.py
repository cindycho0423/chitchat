from fastapi import WebSocket
from typing import Dict
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, chat_id: str):
        """웹소켓 연결"""
        await websocket.accept()
        self.active_connections[chat_id] = websocket
        print(f"WebSocket connected: {chat_id}")
    
    def disconnect(self, chat_id: str):
        """웹소켓 연결 해제"""
        if chat_id in self.active_connections:
            del self.active_connections[chat_id]
            print(f"WebSocket disconnected: {chat_id}")
    
    async def send_message(self, chat_id: str, message: dict):
        """메시지 전송"""
        if chat_id in self.active_connections:
            try:
                await self.active_connections[chat_id].send_text(json.dumps(message))
            except Exception as e:
                print(f"Error sending message to {chat_id}: {e}")
                self.disconnect(chat_id)
    
    async def broadcast(self, message: dict):
        """모든 연결에 브로드캐스트"""
        for chat_id in list(self.active_connections.keys()):
            await self.send_message(chat_id, message)
    
    def get_active_connections(self):
        """활성 연결 수 반환"""
        return len(self.active_connections)

# 전역 매니저 인스턴스
manager = ConnectionManager()