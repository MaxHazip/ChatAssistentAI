from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

router = APIRouter()

# --- 1. Инициализация клиента ---
# Хост "qdrant" — это ИМЯ СЕРВИСА в docker-compose.
# Docker сам связывает контейнеры внутри одной сети по именам сервисов.
client = QdrantClient(host="qdrant", port=6333)

# --- 2. Константы и вспомогательная функция ---
COLLECTION_NAME = "my_texts"
VECTOR_SIZE = 384   # размерность для модели "all-MiniLM-L6-v2", которую использует fastembed

def ensure_collection_exists():
    """Создаём коллекцию, если её ещё нет."""
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
    if not exists:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=qdrant_models.VectorParams(
                size=VECTOR_SIZE,
                distance=qdrant_models.Distance.COSINE
            )
        )

# Вызовем при старте приложения (можно через lifespan, но для примера – сразу)
ensure_collection_exists()

# --- 3. Модели запросов и ответов Pydantic ---
class AddTextRequest(BaseModel):
    text: str
    metadata: dict = {}

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

# --- 4. Эндпоинты ---
@router.post("/add_text")
async def add_text(req: AddTextRequest):
    """Превращаем текст в вектор и сохраняем в Qdrant."""
    # Для генерации вектора используем fastembed
    from fastembed import TextEmbedding
    embedding_model = TextEmbedding()
    embeddings = list(embedding_model.embed([req.text]))
    vector = embeddings[0].tolist()

    # Upsert (вставить или обновить) точку в коллекцию
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            qdrant_models.PointStruct(
                id=None,  # Qdrant сам назначит UUID v4
                vector=vector,
                payload={
                    "text": req.text,
                    **req.metadata
                }
            )
        ]
    )
    return {"status": "ok"}

@router.post("/search")
async def search(req: SearchRequest):
    """Ищем похожие тексты по запросу."""
    from fastembed import TextEmbedding
    embedding_model = TextEmbedding()
    embeddings = list(embedding_model.embed([req.query]))
    query_vector = embeddings[0].tolist()

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=req.top_k
    )
    # Превращаем результаты в удобный формат
    return [
        {
            "id": hit.id,
            "score": hit.score,
            "payload": hit.payload
        }
        for hit in results
    ]