from fastapi import APIRouter
from pydantic import BaseModel
from app.service.search import search_knowledge, build_context_from_hits



router = APIRouter()

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str

def generate_llm_answer(user_question: str, context: str) -> str:

    instructions = (
        "Ты помощник. Отвечай только на основе контекста. "
        "Если контекста недостаточно, честно скажи об этом."
    )

    prompt = (

        f"Контекст:\n{context}\n\n"
        f"Вопрос пользователя:\n{user_question}\n\n"
        f"Дай понятный ответ на русском языке."

    )

    # Здесь уже скормите этот промпт и инструкции модели, чтобы она уже сконструировала готовый ответ.
    # Я просто понял так, что нужно именно подключить еще одну модель чтобы она из трех вариантов ответа сделала один корректный,
    # если нет, то можно обойтись без этой функции и просто возвращать Answer(answer=results[0]["answer"])

    return None


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

