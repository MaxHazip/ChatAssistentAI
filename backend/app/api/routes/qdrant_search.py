from fastapi import APIRouter, Query
from app.service.search import search_knowledge
from typing import Optional

router = APIRouter()

@router.get("/search")
async def search(
    q: str = Query(..., description="Текст запроса"),
    top_k: Optional[int] = 3,
    min_score: Optional[float] = 0.6
):
    results = search_knowledge(q, top_k=top_k, min_score=min_score)
    return {"results": results}