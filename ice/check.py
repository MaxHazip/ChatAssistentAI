from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)
modelAI = SentenceTransformer('all-MiniLM-L6-v2')

def search(query: str):
    query_vector = modelAI.encode(query).tolist()
    results = client.query_points(
        collection_name="kb",
        query=query_vector,
        limit=3
    )
    return results.points

print("=== SEMANTIC SEARCH TEST ===\n")

queries = {
    "форма не работает": "Должен найти про форму",
    "отчет по рекламе": "Должен найти про отчет", 
    "сменить телефон": "Должен найти про телефон",
    "не заходит в админку": "Должен найти про админку"
}

for query, expected in queries.items():
    print(f"Q: {query}")
    try:
        results = search(query)
        print(f"Expected: {expected}")
        print("Results:")
        for r in results:
            print(f"  {r.score:.3f} - {r.payload['text']}")
    except Exception as e:
        print(f"Error: {e}")
    print()

print("\n=== MANUAL TEST ===")
while True:
    q = input("\nYour question (или Enter для выхода): ")
    if not q:
        break
    try:
        results = search(q)
        for r in results:
            print(f"  {r.payload['text']} (score: {r.score:.3f})")
    except Exception as e:
        print(f"Error: {e}")