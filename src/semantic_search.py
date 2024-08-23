from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Data
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from schemas import SearchQuery
import os
from dotenv import load_dotenv




router = APIRouter()

model = SentenceTransformer("all-mpnet-base-v2")

def build_faiss_index(db: Session):
    results = db.query(Data.id, Data.embedding).all()
    
    if not results:
        raise HTTPException(status_code=404, detail="No embeddings found in the database")

    ids, embeddings = zip(*results)
    embeddings_array = np.array([np.frombuffer(e, dtype=np.float32) for e in embeddings])

    print(f"Shape of embeddings array: {embeddings_array.shape}")
    print(f"Sample embedding shape: {embeddings_array[0].shape}")
    
    dimension = embeddings_array.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)

    return index, ids

@router.post("/semantic-search/")
def semantic_search(search_query: SearchQuery, top_k: int = 1, db: Session = Depends(get_db)):
    query = search_query.query
    top_k = search_query.top_k
    index, ids = build_faiss_index(db)

    query_vector = model.encode([query])[0]
    # print(f"Query vector shape: {query_vector.shape}")

    query_vector = query_vector.reshape(1, -1)
    # print(f"Reshaped query vector shape: {query_vector.shape}")

    # print(f"FAISS index dimension: {index.d}")

    if query_vector.shape[1] != index.d:
        raise HTTPException(status_code=500, detail=f"Dimension mismatch: Query vector has {query_vector.shape[1]} dimensions, but index expects {index.d}")

    # Perform the search
    distances, indices = index.search(query_vector.astype(np.float32), top_k)

    if query_vector.shape[1] != index.d:
        raise HTTPException(status_code=500, detail=f"Dimension mismatch: Query vector has {query_vector.shape[1]} dimensions, but index expects {index.d}")


    # Retrieve the corresponding database entries
    result_ids = [ids[i] for i in indices[0]]
    results = db.query(Data).filter(Data.id.in_(result_ids)).all()

    # Sort the results to match the order returned by FAISS
    sorted_results = sorted(results, key=lambda x: result_ids.index(x.id))

    # Format the results
    formatted_results = [
        {
            "id": result.id,
            "text": result.text,
            "page_number": result.page_number,
            "page_char_count": result.page_char_count,
            "page_word_count": result.page_word_count,
            "page_sentence_count": result.page_sentence_count,
            "page_token_count": result.page_token_count,
            "similarity_score": 1 - distances[0][i]  # Convert distance to similarity
        }
        for i, result in enumerate(sorted_results)
    ]

    return formatted_results



