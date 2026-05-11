from fastapi import APIRouter
from app.models import ChatRequest, ChatResponse
from app.service.chat_service import chat_service

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Принимает вопрос пользователя в теле запроса и возвращает
    структурированный ответ: answer, clarification или human.
    """
    result = await chat_service.process_question(request.question)
    return ChatResponse(**result)