from fastapi import APIRouter
from models.schemas import ChatRequest, ChatResponse
from services.me_agent import Me

router = APIRouter()

# create agent once
me_agent = Me()

# store sessions in memory
SESSIONS = {}

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if request.session_id not in SESSIONS:
        SESSIONS[request.session_id] = []
        
    response = me_agent.chat(
        message=request.message,
        history=SESSIONS[request.session_id]
    )

    return {"response": response}