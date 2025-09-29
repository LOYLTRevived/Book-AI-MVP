#embed.py

"""
Documentation:

Dependencies:
Requires os, sqlite3, argparse, qdrant_client (with models), sentence_transformers, and dotenv.

Key Functionality
    1. Data Source Shift (load_claims_for_embedding)
    New Source: The script loads data directly from the knowledge.db SQLite file.
    Data Retrieved: It queries the claims table to fetch the claim_id, claim_text, line_id, and source_ref for all existing claims.

    2. Vectorization and Upload (create_embeddings_and_upload_claims)
    Model Consistency: Uses the same standard embedding model, 'all-MiniLM-L6-v2'.
    Vectorization Content: It encodes the claim_text (the asserted fact) into a vector.
    Qdrant Collection: The claims are uploaded to the default collection named "knowledge_base" (the primary fact store).
    Point Structuring: Each point uploaded to Qdrant is highly structured and critical for retrieval:
    Point ID: Set directly to the claim_id from the SQLite database. This provides a direct link back to the source fact in the relational database.
    Payload: Contains all the claim metadata (claim_id, claim_text, line_id, source_ref). This ensures the search results can be easily filtered and cited by helper.py.

    3. Execution (main)
    The script automatically calls load_claims_for_embedding to fetch all claims.
    It then calls create_embeddings_and_upload_claims to vectorize and upload all claims, effectively rebuilding the vector store for facts.
"""

import os
import sqlite3
import argparse
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

def load_claims_for_embedding(db_path="knowledge.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT claim_id, claim_text, line_id, source_ref FROM claims")
    claims = [{"claim_id": row[0], "claim_text": row[1], "line_id": row[2], "source_ref": row[3]} for row in c.fetchall()]
    conn.close()
    return claims

def create_embeddings_and_upload_claims(claims, collection_name="knowledge_base"):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=models.Distance.COSINE)
    )
    vectors = model.encode([claim["claim_text"]for claim in claims], show_progress_bar=True).tolist()
    points = [
        models.PointStruct(
            id=int(claim["claim_id"]),
            vector=vectors[i],
            payload={
                "claim_id": int(claim["claim_id"]),
                "claim_text": claim["claim_text"],
                "line_id": claim["line_id"],
                "source_ref": claim["source_ref"]
            }
        )
        for i, claim in enumerate(claims)
    ]
    client.upsert(collection_name=collection_name, wait=True, points=points)
    print(f"Uploaded {len(claims)} claims to Qdrant.")

def main ():
    """
    Main function to create embeddings for claims and upload to Qdrant.
    """
    claims = load_claims_for_embedding("knowledge.db")
    if claims:
        create_embeddings_and_upload_claims(claims)
    else:
        print("No claims found in the database.")

if __name__ == "__main__":
    main()