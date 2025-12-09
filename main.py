from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
from openai import OpenAI
import os

app = FastAPI(title="CI/CD Assistant API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"))

# 인메모리 세션 저장소
sessions: Dict[str, List[Dict]] = {}

# 시스템 프롬프트
SYSTEM_PROMPT = """당신은 사용자와 대화할 수 있는 인간입니다.

주요 역할:
1. 사람들의 감정을 읽고 어떤 감정이였는지 말하면서 위로를 건네주세요.
2. 항상 존댓말로 답변해주세요.
3. 이성적인 판단 보단 감성적으로 보살펴주세요.

항상 명확한 답변을 주세요."""


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    response: str
    message_count: int


@app.get("/")
async def root():
    return {"message": "CI/CD Assistant API is running"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """채팅 메시지 처리"""
    
    # 세션 ID 생성 또는 로드
    session_id = request.session_id or str(uuid.uuid4())
    
    # 새 세션이면 시스템 프롬프트로 초기화
    if session_id not in sessions:
        sessions[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    
    messages = sessions[session_id]
    
    # 사용자 메시지 추가
    messages.append({"role": "user", "content": request.message})
    
    try:
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        # 어시스턴트 응답 추출
        assistant_message = response.choices[0].message.content
        
        # 응답을 히스토리에 추가
        messages.append({"role": "assistant", "content": assistant_message})
        
        # 메시지가 너무 많으면 오래된 것 제거 (시스템 프롬프트는 유지)
        if len(messages) > 21:  # 시스템(1) + 대화(20)
            messages = [messages[0]] + messages[-20:]
        
        # 세션 업데이트
        sessions[session_id] = messages
        
        return ChatResponse(
            session_id=session_id,
            response=assistant_message,
            message_count=len(messages) - 1  # 시스템 프롬프트 제외
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API 호출 실패: {str(e)}"
        )


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """세션 히스토리 조회 (디버깅용)"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
    
    return {
        "session_id": session_id,
        "messages": sessions[session_id],
        "message_count": len(sessions[session_id]) - 1
    }


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """세션 삭제"""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "세션이 삭제되었습니다"}
    raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")


@app.get("/sessions")
async def list_sessions():
    """모든 활성 세션 목록"""
    return {
        "total_sessions": len(sessions),
        "session_ids": list(sessions.keys())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
