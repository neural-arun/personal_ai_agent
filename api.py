from fastapi import APIRouter
from models.schemas import ChatRequest, ChatResponse
from services.me_agent import Me
from services.tools import push

router = APIRouter()

# create agent once
me_agent = Me()

# store sessions in memory
SESSIONS = {}

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    is_new = request.session_id not in SESSIONS
    if is_new:
        SESSIONS[request.session_id] = []
        push(f"<b>🆕 New Chat Started:</b> <code>{request.session_id[-6:]}</code>")
        
    response = me_agent.chat(
        message=request.message,
        history=SESSIONS[request.session_id]
    )

    # Forward the real-time chat log to Telegram
    push(f"<b>💬 Chat Log [{request.session_id[-6:]}]</b>\n<b>User:</b> {request.message}\n<b>AI:</b> {response}")

    return {"response": response}