# app/services/chat_service.py
from openai import OpenAI
from app.config import settings
from app.repositories.session_repository import session_repo
from typing import List, Dict

class ChatService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def get_or_create_session(self, session_id: str = None) -> str:
        """세션 조회 또는 생성"""
        if session_id and session_repo.session_exists(session_id):
            return session_id
        return session_repo.create_session(settings.SYSTEM_PROMPT)
    
    def chat(self, session_id: str, user_message: str) -> str:
        """채팅 처리"""
        # 1. 사용자 메시지 저장
        session_repo.add_message(session_id, "user", user_message)
        
        # 2. 전체 메시지 가져오기
        messages = session_repo.get_session(session_id)
        
        # 3. OpenAI API 호출
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )
        
        # 4. AI 응답 추출
        ai_message = response.choices[0].message.content
        
        # 5. AI 응답 저장
        session_repo.add_message(session_id, "assistant", ai_message)
        
        # 6. 오래된 메시지 정리
        session_repo.trim_messages(session_id)
        
        return ai_message
    
    def get_message_count(self, session_id: str) -> int:
        """메시지 개수 조회"""
        messages = session_repo.get_session(session_id)
        return len(messages) - 1 if messages else 0  # 시스템 프롬프트 제외

# 싱글톤 인스턴스
chat_service = ChatService()