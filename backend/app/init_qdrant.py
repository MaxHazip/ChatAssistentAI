import json
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.core.qdrant_db import client
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "knowledge_base"
VECTOR_SIZE = 384  # для модели all-MiniLM-L6-v2

def init_qdrant():


    # Пересоздаём коллекцию (осторожно: удалит старые данные)
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE,
            distance=models.Distance.COSINE
        ),
    )
    print(f"Коллекция {COLLECTION_NAME} создана.")

    # Загружаем модель
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Путь к JSON-файлу внутри контейнера
    data_path = Path(__file__).resolve().parent.parent / "data" / "faq_data.json"
    # или можно явно: "/app/data/faq_data.json"
    with open(data_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    points = []
    for rec in records:
        # Векторизуем только текст вопроса
        vector = model.encode(rec["question"]).tolist()

        payload = {
            "id": rec["id"],
            "user": rec["user"],
            "last_question": rec["last_question"],
            "question": rec["question"],
            "answer": rec["answer"],
            "additional_questions": rec["additional_questions"]
        }

        points.append(models.PointStruct(
            id=rec["id"],
            vector=vector,
            payload=payload
        ))

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Загружено {len(points)} записей.")

if __name__ == "__main__":
    init_qdrant()