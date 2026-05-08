from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from app.core.config import settings   # если захотите брать хост из настроек

# Если в Settings добавите QDRANT_HOST и QDRANT_PORT, используйте их,
# пока можно захардкодить, но лучше вынести в .env
QDRANT_HOST = "qdrant"   # имя сервиса в docker-compose
QDRANT_PORT = 6333
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
model = SentenceTransformer(EMBEDDING_MODEL_NAME)
