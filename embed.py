#embed.py

import os
import json
import argparse
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

def load_chunks_from_json(filepath):
    """
    Loads text chunks from a JSON file.

    Args: 
        filepath (str): The path to the JSON file containing the chunks.

    Returns:
        list: A list of text chunks.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the file {filepath}")
        return None
    except Exception as e:
        print(f"An Error occured while loading the chunks {e}")
        return None
    

def create_embeddings_and_upload(chunks, collection_name="knowledge_base", db_path="knowledge_base_db"):
    """
    Creates embeddings for text chunks and uploads them to a Qdrant collection.

    Args:
        Chunks (list): A list of text chunks.
        collection_name (str): The name of the Qdrant collection to use.
    """
    # Intitialize the sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Intitialize the Qdrant Client
    # For a local instance, you can use 'QdrantClient(":memeroy:")'
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )

    # Create the collection in Qdrant if it doesn't exist
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=models.Distance.COSINE)
    )

    # Generate embeddings and prepare for upload
    vectors = model.encode(chunks, show_progress_bar=True).tolist()
    points = [
        models.PointStruct(
            id=i,
            vector=vectors[i],
            payload={"chunk_text": chunks}
        )
        for i, chunk in enumerate(chunks)
    ]

    # Upload the points to the collection
    operation_info = client.upsert(
        collection_name=collection_name,
        wait=True,
        points=points
    )

    print(f"Successfully uploaded {len(chunks)} points to the '{collection_name}' collection")
    print(f"Operation info: {operation_info}")


def main ():
    """
    Main function to read chunks, create embeddings, and upload to Qdrant.
    """
    parser = argparse.ArgumentParser(description="Create embeddings from text chunks and upload to Qdrant.")
    parser.add_argument("filename", help="The name of the JSON file containing the chunks.")
    args = parser.parse_args()

    input_filepath = os.path.join ("data", args.filename)
    chunks = load_chunks_from_json(input_filepath)
    if chunks:
        create_embeddings_and_upload(chunks)

if __name__ == "__main__":
    main()