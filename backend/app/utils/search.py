import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Настройки подключения к Qdrant через переменные окружения
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "knowledge_base")

# Загружаем модель один раз при старте приложения
model = SentenceTransformer('all-MiniLM-L6-v2')


def search_knowledge(user_question: str, top_k: int = 3, min_score: float = 0.6):
    """
    Ищет релевантные ответы в Qdrant по векторному представлению вопроса.

    Аргументы:
        user_question: текст вопроса пользователя
        top_k: количество возвращаемых результатов
        min_score: минимальный порог схожести (0.0 до 1.0)

    Возвращает:
        Список словарей с ключами:
            - score: float (степень схожести)
            - answer: str (текст ответа)
            - question: str (исходный вопрос из базы знаний)
            - status: str (статус из базы знаний)
            - confidence: float или None
            - metadata: dict (полные метаданные точки)

        Если Qdrant недоступен или ничего не найдено — пустой список.
    """
    try:
        # Подключаемся к Qdrant
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

        # Преобразуем вопрос в вектор (эмбеддинг)
        vector = model.encode(user_question).tolist()

        # Поиск ближайших соседей по косинусному расстоянию
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            limit=top_k,
            with_payload=True,
            score_threshold=min_score
        )

        # Формируем удобный для использования список
        return [
            {
                "score": hit.score,
                "answer": hit.payload.get("answer", ""),
                "question": hit.payload.get("question", ""),
                "status": hit.payload.get("status", "answer"),
                "confidence": hit.payload.get("confidence"),
                "metadata": hit.payload
            }
            for hit in results
        ]

    except Exception as e:
        # Qdrant недоступен — не падаем, возвращаем пустой список
        print(f" Qdrant недоступен: {e}")
        return []


def load_knowledge_base(data: list[dict]) -> bool:
    """
    Загружает данные в коллекцию Qdrant.

    Аргументы:
        data: список словарей с ключами:
            - question: str (текст вопроса)
            - answer: str (текст ответа)
            - status: str (тип: answer, clarification, human)
            - additional_questions: list[str] (опционально)

    Возвращает:
        True если загрузка успешна, иначе False
    """
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

        # Проверяем, существует ли коллекция
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if COLLECTION_NAME not in collection_names:
            # Создаём коллекцию, если её нет
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config={
                    "size": 384,  # размерность эмбеддингов all-MiniLM-L6-v2
                    "distance": "Cosine"
                }
            )
            print(f"Создана коллекция '{COLLECTION_NAME}'")

        # Загружаем точки
        points = []
        for idx, item in enumerate(data):
            question_text = item.get("question", "")
            vector = model.encode(question_text).tolist()

            points.append({
                "id": idx,
                "vector": vector,
                "payload": {
                    "question": question_text,
                    "answer": item.get("answer", ""),
                    "status": item.get("status", "answer"),
                    "additional_questions": item.get("additional_questions", []),
                    "confidence": item.get("confidence"),
                }
            })

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

        print(f"Загружено {len(points)} записей в коллекцию '{COLLECTION_NAME}'")
        return True

    except Exception as e:
        print(f" Ошибка загрузки базы знаний: {e}")
        return False