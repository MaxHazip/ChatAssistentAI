from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

QDRANT_HOST = "qdrant"
QDRANT_PORT = 6333
COLLECTION_NAME = "knowledge_base"

# Загружаем модель один раз при старте приложения
model = SentenceTransformer('all-MiniLM-L6-v2')

def search_knowledge(user_question: str, top_k: int = 3, min_score: float = 0.6):
    """
    Возвращает список словарей с ключами: score, answer, question, status, confidence, metadata.
    Если подходящих не найдено — пустой список.
    """
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    vector = model.encode(user_question).tolist()

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=top_k,
        with_payload=True,
        score_threshold=min_score
    )

    return [
        {
            "score": hit.score,
            "answer": hit.payload["answer"],
            "question": hit.payload["question"],
            "status": hit.payload["status"],
            "confidence": hit.payload.get("confidence"),
            "metadata": hit.payload
        }
        for hit in results
    ]