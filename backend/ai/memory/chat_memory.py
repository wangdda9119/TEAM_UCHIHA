# backend/ai/memory/chat_memory.py

from langchain_core.messages import BaseMessage

class ChatMemoryStore:
    """
    세션 단위 지속 메모리 저장소
    """
    def __init__(self):
        self.sessions = {}  # {session_id: List[BaseMessage]}

    def get(self, session_id: str):
        return self.sessions.get(session_id, [])

    def add(self, session_id: str, message: BaseMessage):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(message)

    def clear(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]


chat_memory = ChatMemoryStore()
