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
    if score >= 0.70:
        return "answer"
    elif 0.40 <= score < 0.70:
        return "clarification"
    else:
        return "human"

@router.post("/chat", response_model=Answer)
async def send_answer(payload: Question):
    user_query = payload.question.strip()
    
    # 1. Поиск в Qdrant
    results = search_knowledge(user_query)
    if not results:
        return Answer(answer="Я не нашел информации. Переключаю на оператора.", status="human")

    score = results[0]["score"]
    status = calculate_status(score)

    # 2. Обработка низкого скора
    if status == "human":
        return Answer(answer="Затрудняюсь ответить. Позову человека.", status="human")

    # 3. Формирование контекста
    context_text, _ = build_context_from_hits(hits=results)

    # 4. Если статус "уточнение" — сразу предлагаем варианты, не тратя токены
    if status == "clarification":
        options = [res["question"] for res in results[:2]]
        options_fmt = "\n — ".join(options)
        return Answer(
            answer=f"Возможно, вы имели в виду:\n — {options_fmt}?",
            status="clarification"
        )

    # 5. Вызов LLM (Baidu CoBuddy)
    llm_final_answer = generate_llm_answer(user_query, context_text)

    # Логика обработки ответов LLM
    if "[NONSENSE]" in llm_final_answer:
        return Answer(answer="Я не понимаю это сообщение. Зову человека.", status="human")
    
    if "[NOT_FOUND]" in llm_final_answer:
        return Answer(answer="В базе нет точного ответа. Передаю вопрос менеджеру.", status="human")

    # Если нейронка выдала ошибку (например, 429), отдаем лучший ответ из базы напрямую
    if "[ERROR]" in llm_final_answer:
        return Answer(answer=results[0]["answer"], status="answer")

    # Сохраняем успешный лог
    save_log({
        "query": user_query,
        "matched_question": results[0]["question"],
        "score": round(float(score), 3),
        "status": status,
        "category": results[0].get("metadata", {}).get("category", "general")
    })

    return Answer(answer=llm_final_answer, status="answer")
