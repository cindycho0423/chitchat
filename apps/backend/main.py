from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import create_tables
from routers import chat, websocket

app = FastAPI(title="Chatbot API with WebSocket")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(websocket.router, tags=["websocket"])

# 앱 시작시 테이블 생성
@app.on_event("startup")
async def startup_event():
    create_tables()

# 기본 라우팅
@app.get("/")
async def root():
    return {"message": "Chatbot API with WebSocket"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}