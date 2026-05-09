# backend/app/service/chat_service.py
from typing import Optional, Dict, Any, List
from app.utils.search import search_knowledge

class ChatService:
    """
    Сервис для обработки входящих вопросов и маршрутизации
    на основе показателя score из Qdrant.
    """

    async def process_question(self, question: str) -> Dict[str, Any]:
        """
        Обрабатывает вопрос пользователя.
        Возвращает словарь с ключами: status, message, meta.
        """
        # Шаг 1: Ищем лучший результат в Qdrant
        search_results = search_knowledge(question, top_k=1, min_score=0.0)

        if not search_results:
            # Если совсем ничего не найдено, передаем оператору
            return {
                "status": "human",
                "message": "К сожалению, я не нашел подходящего ответа. Ваш запрос передан оператору.",
                "meta": {
                    "source": None,
                    "additional_questions": []
                }
            }

        # Берем первый (лучший) результат
        best_result = search_results[0]
        score = best_result.get("score", 0.0)
        answer = best_result.get("answer", "")
        additional_questions = best_result.get("additional_questions", [])
        source_status = best_result.get("status", "answer")

        # Шаг 2: Применяем пороговую логику к score
        if score > 0.8:
            # Высокий score — сразу даем ответ
            return {
                "status": "answer",
                "message": answer,
                "meta": {
                    "source": "knowledge_base",
                    "score": score,
                    "additional_questions": additional_questions
                }
            }
        elif 0.5 <= score <= 0.8:
            # Средний score — задаем уточняющие вопросы
            clarification_text = self._build_clarification_message(answer, additional_questions)
            return {
                "status": "clarification",
                "message": clarification_text,
                "meta": {
                    "source": "knowledge_base",
                    "score": score,
                    "additional_questions": additional_questions
                }
            }
        else:  # score < 0.5
            # Низкий score — передаем оператору
            return {
                "status": "human",
                "message": "Ваш запрос требует уточнения и передан оператору. Пожалуйста, ожидайте ответа.",
                "meta": {
                    "source": "knowledge_base",
                    "score": score,
                    "additional_questions": additional_questions
                }
            }

    def _build_clarification_message(self, base_answer: str, additional_questions: List[str]) -> str:
        """Формирует сообщение с уточняющими вопросами."""
        msg = base_answer or "Для более точного ответа, пожалуйста, уточните детали."
        if additional_questions:
            questions_formatted = "\n".join([f"- {q}" for q in additional_questions])
            msg += f"\n\nУточняющие вопросы:\n{questions_formatted}"
        return msg

# Экземпляр сервиса для использования в зависимостях
chat_service = ChatService()