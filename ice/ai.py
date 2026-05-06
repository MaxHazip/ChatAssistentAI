from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.models import PointStruct



knowledge = [
    "не работает форма обратной связи",
    "не могу войти в админку",
    "где посмотреть отчет по рекламе",
    "поменяйте телефон на сайте"
]

client = QdrantClient("localhost", port=6333)

client.recreate_collection(  # when end work(recreate_collection swith create_collection)
    collection_name="kb",#knowladge base
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE
    )
)


modelAI = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str):
    return modelAI.encode(text).tolist()

points = []

for i, text in enumerate(knowledge):
    vector = get_embedding(text)

    points.append(
        PointStruct(
            id=i,
            vector=vector,
            payload={"text": text}
        )
    )  


client.upsert(
    collection_name="kb",
    points=points
)

def search(query: str):
    query_vector = get_embedding(query)

    results = client.search(
        collection_name="kb",
        query_vector=query_vector,
        limit=3
    )
    return results



print(get_embedding("не работает форма")[:5]) #test
print("Points inserted:", len(points))