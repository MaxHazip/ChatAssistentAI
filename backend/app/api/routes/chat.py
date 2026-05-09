from fastapi import APIRouter
from app.models import ChatResponse
from app.service.chat_service import chat_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(question: str):
    return chat_service.process_question(question)