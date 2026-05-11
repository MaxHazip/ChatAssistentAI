from typing import List
from app.core.config import settings
from app.utils.search import search_knowledge


class ChatService:
    """
    Сервис обработки входящих вопросов с маршрутизацией на основе score из Qdrant.
    Пороги берутся из настроек (settings):
      - score > ANSWER_THRESHOLD        → answer
      - CLARIFICATION_THRESHOLD <= score <= ANSWER_THRESHOLD → clarification
      - score < CLARIFICATION_THRESHOLD → human
    """

    async def process_question(self, question: str) -> dict:
        """
        Принимает текст вопроса, ищет в Qdrant и возвращает словарь
        с полями для ChatResponse.
        """
       
        search_results = search_knowledge(question, top_k=1, min_score=0.0)

        if not search_results:
       
            return {
                "status": "human",
                "answer_text": None,
                "clarification_questions": None,
                "original_question": question,
                "confidence": 0.0,
                "human_notification": (
                    "К сожалению, я не нашёл подходящего ответа. "
                    "Ваш запрос передан оператору."
                ),
            }

        best = search_results[0]
        score = best.get("score", 0.0)
        answer = best.get("answer", "")
        additional_questions = best.get("additional_questions", [])

        if score > settings.ANSWER_THRESHOLD:
            return {
                "status": "answer",
                "answer_text": answer,
                "clarification_questions": None,
                "original_question": question,
                "confidence": score,
                "human_notification": None,
            }

        elif score >= settings.CLARIFICATION_THRESHOLD:
            clarification_list = self._build_clarification_list(answer, additional_questions)
            return {
                "status": "clarification",
                "answer_text": None,
                "clarification_questions": clarification_list,
                "original_question": question,
                "confidence": score,
                "human_notification": None,
            }

        else:  
            return {
                "status": "human",
                "answer_text": None,
                "clarification_questions": None,
                "original_question": question,
                "confidence": score,
                "human_notification": (
                    "Ваш запрос требует уточнения и передан оператору. "
                    "Пожалуйста, ожидайте ответа."
                ),
            }

    def _build_clarification_list(
        self, base_answer: str, additional_questions: List[str]
    ) -> List[str]:
        """Собирает список уточняющих вопросов."""
        questions = []
        if base_answer:
            questions.append(
                f"Нашлась похожая информация: «{base_answer}». Уточните, это ваша ситуация?"
            )
        if additional_questions:
            questions.extend(additional_questions)
        if not questions:
            questions = [
                "Уточните, пожалуйста, что именно не работает?",
                "На какой странице возникла проблема?",
                "Когда вы это заметили?",
            ]
        return questions



chat_service = ChatService()