from fastapi import APIRouter
from pydantic import BaseModel
from app.service.search import search_knowledge, build_context_from_hits
from app.service.llm import generate_llm_answer



router = APIRouter()

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str


@router.post("/chat", response_model=Answer)
async def send_answer(
    payload: Question
) -> Answer:
    
    normalized_question = payload.question
    
    if not normalized_question.strip():
        return Answer(answer="Извините, но Вы отправили пустой запрос")
    
    normalized_question = " ".join(normalized_question.split())

    results = search_knowledge(normalized_question)

    if results == []:
        return Answer(answer="Извините, но ничего не найдено. Перенаправляю на специалиста")
    
    # used_chunks тут нужны просто для логов, по факту я могу их убрать, если мы их не будем делать
    # это обозначает то, что мы использовали для генерации контекста
    context_text, used_chunks = build_context_from_hits(

        hits = results,
        max_context_chars = 2500,
        max_chunks = 3

    )

    if not context_text:
        return Answer(answer=results[0]["answer"])
    
    llm_answer = generate_llm_answer(normalized_question, context_text)

    if not llm_answer:
        return Answer(answer=results[0]["answer"])
    
    return Answer(answer=llm_answer)

