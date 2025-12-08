from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import sys
import os

# 모듈로 실행될 때를 가정한 상대 임포트
try:
    from .main import run_mentor
except ImportError:
    # 스크립트로 직접 실행 시 (경로 문제로 main.py 내부의 상대 임포트가 실패할 수 있음)
    # 이 경우 사용자가 'python -m backend.server'로 실행하도록 가이드는 것이 좋습니다.
    try:
        from main import run_mentor
    except ImportError:
        # 경로가 완전히 꼬인 경우
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from main import run_mentor

app = FastAPI(title="Mentor Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, Any]] = []
    interests: Optional[str] = None
    mode: str = "react"

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Call the existing run_mentor function
        # Note: run_mentor might be synchronous or asynchronous. 
        # Based on main.py, it seems synchronous (graph.invoke).
        # FastAPI handles synchronous route handlers by running them in a thread pool.
        
        response_content = run_mentor(
            question=request.message,
            interests=request.interests,
            mode=request.mode,
            chat_history=request.history
        )
        
        # run_mentor returns a string or a dict (if state). 
        # The main.py logic says it returns `last_message.content` string usually.
        
        if isinstance(response_content, dict):
             # Handle case where it returns state (e.g. awaiting input)
             # For now, let's just convert it to string or extract something
             return ChatResponse(response=str(response_content))
        
        return ChatResponse(response=str(response_content))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
