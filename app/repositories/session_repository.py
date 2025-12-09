# app/repositories/session_repository.py
from typing import Dict, List, Optional
import uuid

class SessionRepository:
    def __init__(self):
        self.sessions: Dict[str, List[Dict]] = {}
    
    def create_session(self, system_prompt: str) -> str:
        """새 세션 생성"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = [
            {"role": "system", "content": system_prompt}
        ]
        return session_id
    
    def get_session(self, session_id: str) -> Optional[List[Dict]]:
        """세션 조회"""
        return self.sessions.get(session_id)
    
    def session_exists(self, session_id: str) -> bool:
        """세션 존재 여부"""
        return session_id in self.sessions
    
    def add_message(self, session_id: str, role: str, content: str):
        """메시지 추가"""
        if session_id in self.sessions:
            self.sessions[session_id].append({
                "role": role,
                "content": content
            })
    
    def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_all_session_ids(self) -> List[str]:
        """모든 세션 ID 조회"""
        return list(self.sessions.keys())
    
    def trim_messages(self, session_id: str, max_count: int = 21):
        """오래된 메시지 제거 (시스템 프롬프트는 유지)"""
        if session_id in self.sessions:
            messages = self.sessions[session_id]
            if len(messages) > max_count:
                self.sessions[session_id] = [messages[0]] + messages[-20:]

# 싱글톤 인스턴스
session_repo = SessionRepository()