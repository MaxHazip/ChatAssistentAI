from sentence_transformers import SentenceTransformer

modelAI = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str):
    return modelAI.encode(text).tolist()