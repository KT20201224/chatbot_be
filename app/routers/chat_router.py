# app/routers/chat_router.py
from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import chat_service
from app.repositories.session_repository import session_repo

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """채팅 메시지 처리"""
    try:
        # 세션 조회 또는 생성
        session_id = chat_service.get_or_create_session(request.session_id)
        
        # 채팅 처리
        ai_response = chat_service.chat(session_id, request.message)
        
        # 메시지 개수
        message_count = chat_service.get_message_count(session_id)
        
        return ChatResponse(
            session_id=session_id,
            response=ai_response,
            message_count=message_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """세션 조회"""
    messages = session_repo.get_session(session_id)
    if not messages:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
    
    return {
        "session_id": session_id,
        "messages": messages,
        "message_count": len(messages) - 1
    }

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """세션 삭제"""
    success = session_repo.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
    return {"message": "세션이 삭제되었습니다"}

@router.get("/sessions")
async def list_sessions():
    """모든 세션 목록"""
    session_ids = session_repo.get_all_session_ids()
    return {
        "total_sessions": len(session_ids),
        "session_ids": session_ids
    }