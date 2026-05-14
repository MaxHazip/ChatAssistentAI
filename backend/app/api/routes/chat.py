from fastapi import APIRouter
from pydantic import BaseModel
from app.service.search import search_knowledge, build_context_from_hits
from app.service.llm import generate_llm_answer

from app.service.logger import save_log


router = APIRouter()

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str
    status: str

def calculate_status(score):

    if score > 0.85:
        return "answer"

    elif score > 0.5 and score< 0.77:
        return "clarification"

    else:
        return "human"

@router.post("/chat", response_model=Answer)
async def send_answer(payload: Question) -> Answer:
    normalized_question = payload.question.strip()
    
    normalized_question = payload.question
    
    if not normalized_question.strip():
        return Answer(answer="Извините, но Вы отправили пустой запрос", status="answer")
    
    normalized_question = " ".join(normalized_question.split())

    if not normalized_question:
        return Answer(
            answer="Извините, но Вы отправили пустой запрос",
            status="ready"
        )

    normalized_question = " ".join(normalized_question.split())
    results = search_knowledge(normalized_question)

    if results == []:

        return Answer(answer="Извините, но ничего не найдено. Перенаправляю на специалиста", status="human")
    
    # used_chunks тут нужны просто для логов, по факту я могу их убрать, если мы их не будем делать
    # это обозначает то, что мы использовали для генерации контекста

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

    score = results[0]["score"]

    status = calculate_status(score)

    if status == "clarification":
        ...

    save_log({

        "query": payload.question,
        "matched_question": results[0]["question"],
        "score": round(float(score), 3),
        "status": status,
        "category": results[0]["metadata"]["category"]

    })

    if not context_text:
        return Answer(answer=results[0]["answer"], status=status)
    
    llm_answer = generate_llm_answer(normalized_question, context_text)

    if not llm_answer:
        return Answer(answer=results[0]["answer"], status=status)
    
    return Answer(answer=llm_answer, status=status)