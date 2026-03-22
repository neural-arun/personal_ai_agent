from pydantic import BaseModel
from typing import List, Dict, Optional


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"


class ChatResponse(BaseModel):
    response: str