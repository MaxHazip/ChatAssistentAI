# backend/app/api/routes/knowledge.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime, timezone

from app.core.qdrant_db import client, model
from app.init_qdrant import COLLECTION_NAME
from qdrant_client.models import Distance, VectorParams

router = APIRouter()

# VECTOR_SIZE = 384 

# def ensure_collection_exists():
#     """Создаёт коллекцию в Qdrant, если её ещё нет"""
#     if not client.collection_exists(COLLECTION_NAME):
#         client.create_collection(
#             collection_name=COLLECTION_NAME,
#             vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
#         )

class KnowledgeItemCreate(BaseModel):
    question: str = Field(..., min_length=1, description="Вопрос пользователя")
    answer: str = Field(..., min_length=1, description="Ответ на вопрос")
    metadata: Optional[dict] = Field(default_factory=dict, description="Дополнительные метаданные")

class KnowledgeItemResponse(BaseModel):
    id: str
    status: str
    message: str

@router.post("/", response_model=KnowledgeItemResponse, tags=["knowledge"])
async def add_knowledge_item(item: KnowledgeItemCreate):
    """
    Добавить новый вопрос-ответ в базу знаний Qdrant
    """
    try:
        # 1. Гарантируем, что коллекция существует
        # ensure_collection_exists()
        
        # 2. Генерируем вектор для вопроса
        vector = model.encode(item.question).tolist()
        
        # 3. Формируем payload
        payload = {
            "question": item.question,
            "answer": item.answer,
            "status": "ready",
            "confidence": 1.0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **item.metadata
        }
        
        point_id = str(uuid.uuid4())
        
        # 4. Сохраняем в Qdrant
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[{
                "id": point_id,
                "vector": vector,
                "payload": payload
            }]
        )
        
        return KnowledgeItemResponse(
            id=point_id,
            status="success",
            message="Запись успешно добавлена в базу знаний"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении: {str(e)}")