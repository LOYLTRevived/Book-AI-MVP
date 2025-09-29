# embed_chunks.py

import os
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import json
import dotenv
import argparse

dotenv.load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

def load_chunks(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def embed_chunks(chunks, collection_name="chunks_collection"):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=models.Distance.COSINE)
    )
    vectors = model.encode([chunk for chunk in chunks], show_progress_bar=True).tolist()
    points = [
        models.PointStruct(
            id=i,
            vector=vectors[i],
            payload={
                "chunk_text": chunks[i],
                "source_ref": "your_source_file.json"
            }
        )
        for i in range(len(chunks))
    ]

    client.upsert(collection_name=collection_name, wait=True, points=points)
    print(f"Uploaded {len(chunks)} chunks to Qdrant")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embed chunks from a JSON file into Qdrant.")
    parser.add_argument("file_path", help="Path to the chunk JSON file.")
    args = parser.parse_args()

    chunks = load_chunks(args.file_path)
    embed_chunks(chunks)
