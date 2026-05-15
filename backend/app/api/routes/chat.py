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

    if score > 0.7:
        return "answer"

    elif 0.40 <= score < 0.7:
        return "clarification"

    else:
        return "human"

@router.post("/chat", response_model=Answer)
async def send_answer(payload: Question) -> Answer:
    user_query = payload.question.strip()
    
    # проверка на пустоту
    if not user_query:
        return Answer(answer="Вы отправили пустой запрос", status="answer")

    # Поиск в базе 
    results = search_knowledge(user_query)

    #  Если ничего не найдено  статус human
    if not results:
        return Answer(
            answer="Я не нашел точного ответа в своей базе. Переключаю вас на специалиста, он скоро ответит.",
            status="human"
        )

    score = results[0]["score"]
    status = calculate_status(score)

    #  Если статус human по скору 
    if status == "human":
        return Answer(
            answer="Моих знаний недостаточно для точного ответа. Передаю диалог оператору.",
            status="human"
        )

    
    if status == "clarification":
            # Собираем уникальные вопросы из топ-результатов 
            # Исключаем дубликаты, если они вдруг есть
            options = []
            for res in results:
                q_text = res["question"]
                if q_text not in options:
                    options.append(q_text)
            
            # Формируем текст ответа
            options_text = "\n".join([f"• {opt}" for opt in options])
            
            return Answer(
                answer=(
                    f"Я не совсем уверен, что правильно вас понял.\n"
                    f"Возможно, вас интересует один из этих вопросов:\n\n"
                    f"{options_text}\n\n"
                    f"Если нет, напишите в чат вызовите оператора."
                ),
                status="clarification"
            )

    #  status == "answer" — работаем с LLM или базой
    context_text, used_chunks = build_context_from_hits(hits=results)
    
    # Логируем успех
    save_log({
        "query": user_query,
        "matched_question": results[0]["question"],
        "score": round(float(score), 3),
        "status": status,
        "category": results[0]["metadata"].get("category", "general")
    })

    if not context_text:
        return Answer(answer=results[0]["answer"], status=status)
    
    # Вызов LLM (пока ваша старая функция)
    llm_answer = generate_llm_answer(user_query, context_text)
    
    final_text = llm_answer if llm_answer else results[0]["answer"]
    return Answer(answer=final_text, status=status)