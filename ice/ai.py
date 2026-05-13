import json
from qdrant_client.models import VectorParams, Distance, PointStruct
from db import client
from search_engine import get_embedding
from logger import save_log

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
                    "category": item["category"],
                    "additional_questions": item["additional_questions"]
                }
            )
        )

    client.upsert(
        collection_name=collection_name,
        points=points
    )

    print("Inserted:", len(points))


def calculate_status(score):

    if score > 0.85:
        return "answer"

    elif score > 0.5 and score< 0.77:
        return "clarification"

    else:
        return "human"

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

    if not results:
        return {
            "status": "human",
            "answer": "Ничего не найдено"
        }

    best_result = results[0]

    score = best_result.score

    status = calculate_status(score)

    response = {
        "status": status,
        "answer": best_result.payload["answer"],
        "score": round(float(score), 3),
        "category": best_result.payload["category"]
    }

    if status == "clarification":
        response["questions"] = best_result.payload["additional_questions"]

    save_log({
        "query": query,
        "matched_question": best_result.payload["question"],
        "score": round(float(score), 3),
        "status": status,
        "category": best_result.payload["category"]
    })

    return response
