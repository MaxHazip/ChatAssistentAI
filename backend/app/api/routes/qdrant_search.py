from fastapi import APIRouter
from qdrant_client import QdrantClient

router = APIRouter()

client = QdrantClient(host="qdrant", port=6333)