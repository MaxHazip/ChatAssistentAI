from app.core.qdrant_db import model, client

COLLECTION_NAME = "knowledge_base"

def search_knowledge(user_question: str, top_k: int = 3, min_score: float = 0.6):
    """
    Возвращает список словарей с ключами: score, answer, question, status, confidence, metadata.
    Если подходящих не найдено — пустой список.
    """
    vector = model.encode(user_question).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=top_k,
        with_payload=True,
        score_threshold=min_score
    )

    points = results.points

    if not points:
        []

    return [
        {
            "score": hit.score,
            "answer": hit.payload["answer"],
            "question": hit.payload["question"],
            "status": hit.payload["status"],
            "confidence": hit.payload.get("confidence"),
            "metadata": hit.payload
        }
        for hit in points
    ]