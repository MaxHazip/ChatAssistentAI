import json
from qdrant_client.models import VectorParams, Distance, PointStruct
from db import client
from search_engine import get_embedding


collection_name = "kb"


def create_collection():

    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )

    print("Collection created")




def load_knowledge():

    with open("knowledge_base.json", "r", encoding="utf-8") as f:
        knowledge = json.load(f)

    return knowledge




def upload_data():

    knowledge = load_knowledge()

    points = []

    for item in knowledge:

        vector = get_embedding(item["question"])

        points.append(
            PointStruct(
                id=item["id"],
                vector=vector,

                payload={
                    "question": item["question"],
                    "answer": item["answer"],
                    "status": item["status"],
                    "confidence": item["confidence"],
                    "additional_questions": item["additional_questions"]
                }
            )
        )

    client.upsert(
        collection_name=collection_name,
        points=points
    )

    print("Inserted:", len(points))




def search(query: str):

    query_vector = get_embedding(query)

    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=3
    ).points

    return results




def process_query(query: str):

    results = search(query)

    best_result = results[0]

    if best_result.score > 0.8:

        return {
            "status": "answer",
            "answer": best_result.payload["answer"],
            "score": best_result.score
        }

    elif best_result.score > 0.5:

        return {
            "status": "clarification",
            "answer": best_result.payload["answer"],
            "questions": best_result.payload["additional_questions"],
            "score": best_result.score
        }

    else:

        return {
            "status": "human",
            "answer": "Передаю оператору",
            "score": best_result.score
        }