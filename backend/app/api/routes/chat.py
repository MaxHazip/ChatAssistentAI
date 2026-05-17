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

def calculate_status(score: float) -> str:
   
    if score >= 0.75:
        return "answer"
    elif 0.55 <= score < 0.75:
        return "clarification"
    else:
        return "human"

@router.post("/chat", response_model=Answer)
async def send_answer(payload: Question) -> Answer:
    user_query = payload.question.strip()
    
    if not user_query:
        return Answer(answer="Запрос не может быть пустым.", status="answer")

    
    results = search_knowledge(user_query)
    
    # Если в базе вообще пусто или поиск ничего не вернул
    if not results:
        return Answer(
            answer="Я не нашел точного ответа в своей базе. Переключаю вас на специалиста, он скоро ответит.",
            status="human"
        )

    score = results[0]["score"]
    status = calculate_status(score)

    if status == "human":
        return Answer(
            answer="Я не нашел точного ответа в своей базе. Переключаю вас на специалиста, он скоро ответит.",
            status="human"
        )

    if status == "clarification":
        options = [res["question"] for res in results[:2]]
        options_fmt = "\n — ".join(options)
        return Answer(
            answer=f"Возможно, вы имели в виду:\n — {options_fmt}?",
            status="clarification"
        )

   
    context_text, _ = build_context_from_hits(hits=results)
    llm_final_answer = generate_llm_answer(user_query, context_text)

    # модерации LLM
    if "[NONSENSE]" in llm_final_answer or "[NOT_FOUND]" in llm_final_answer:
        return Answer(
            answer="Я не нашел точного ответа в своей базе. Переключаю вас на специалиста, он скоро ответит.",
            status="human"
        )

    # случай сетевой ошибки 
    if "[ERROR]" in llm_final_answer:
        return Answer(answer=results[0]["answer"], status="answer")

    # Успешный ответ
    save_log({
        "query": user_query,
        "matched_question": results[0]["question"],
        "score": round(float(score), 3),
        "status": status,
        "category": results[0].get("metadata", {}).get("category", "general")
    })

    return Answer(answer=llm_final_answer, status="answer")