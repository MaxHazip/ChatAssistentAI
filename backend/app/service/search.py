from app.core.qdrant_db import model, client
from typing import List, Dict, Tuple
import re

COLLECTION_NAME = "knowledge_base"

def is_nonsense(text: str) -> bool:
    """Проверяет, является ли текст набором случайных букв."""
    # Если в тексте нет ни одной гласной (для кириллицы и латиницы) 
    # или слишком мало пробелов при большой длине
    if not re.search(r'[аеёиоуыэюяaeiouy]', text.lower()):
        return True
    return False

def search_knowledge(user_question: str, top_k: int = 3, min_score: float = 0.45):
    """
    Возвращает список подходящих ответов. 
    Порог min_score подняли, чтобы совсем мусор не проходил.
    """
    if is_nonsense(user_question):
        return []

    vector = model.encode(user_question).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=top_k,
        with_payload=True,
        score_threshold=min_score  # Qdrant сам отсечет 
    )

    points = results.points
    if not points:
        return []

    return [
        {
            "score": hit.score,
            "answer": hit.payload["answer"],
            "question": hit.payload["question"],
            "metadata": hit.payload
        }
        for hit in points
    ]

def build_context_from_hits(
        
    hits: List[Dict],
    max_context_chars: int = 2500,
    max_chunks: int = 3

) -> Tuple[str, List[Dict]]:
    

    used_chunks = []
    blocks = []
    current_size = 0

    for i, hit in enumerate(hits[:max_chunks]):
        
        text = (hit.get("answer") or "").strip()

        if not text:
            continue

        source_question = (hit.get("question") or "").strip()

        score = hit.get("score", 0.0)

        block = (
            f"[Chunk {i} | score={score:.3f}]\n"
            f"Q: {source_question}\n"
            f"A: {text}\n"
        )

        if current_size + len(block) > max_context_chars:
            break

        blocks.append(block)
        used_chunks.append(hit)
        current_size += len(block)

    context_text = "\n---\n".join(blocks).strip()
    return context_text, used_chunks