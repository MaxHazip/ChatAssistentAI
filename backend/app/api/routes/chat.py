from fastapi import APIRouter
from pydantic import BaseModel
from app.service.search import search_knowledge, build_context_from_hits
from app.service.llm import generate_llm_answer
from typing import Optional, Literal

router = APIRouter()

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str
    status: Literal["thinking", "clarifying", "human", "ready"]
    confidence: Optional[float] = None

@router.post("/chat", response_model=Answer)
async def send_answer(payload: Question) -> Answer:
    normalized_question = payload.question.strip()
    
    if not normalized_question:
        return Answer(
            answer="Извините, но Вы отправили пустой запрос",
            status="ready"
        )

    normalized_question = " ".join(normalized_question.split())
    results = search_knowledge(normalized_question)

    if not results:
        return Answer(
            answer="Извините, но ничего не найдено. Перенаправляю на специалиста",
            status="human"
        )

    context_text, used_chunks = build_context_from_hits(
        hits=results,
        max_context_chars=2500,
        max_chunks=3
    )

    if not context_text:
        first_result = results[0]
        return Answer(
            answer=first_result["answer"],
            status="ready",
            confidence=first_result.get("score", 0.0)
        )

    llm_answer = generate_llm_answer(normalized_question, context_text)
    
    if not llm_answer:
        first_result = results[0]
        return Answer(
            answer=first_result["answer"],
            status="ready",
            confidence=first_result.get("score", 0.0)
        )

    status = "thinking"
    if "уточн" in llm_answer.lower() or "вопрос" in llm_answer.lower():
        status = "clarifying"
    elif any(r.get("status") == "human" for r in results):
        status = "human"
    
    return Answer(
        answer=llm_answer,
        status=status,
        confidence=results[0].get("score", 0.0) if results else None
    )