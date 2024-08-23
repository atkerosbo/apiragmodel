from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Data
import numpy as np
import faiss

#router = APIRouter()

def build_faiss_index(db: Session):
    # Retrieve all embeddings from the database
    results = db.query(Data.id, Data.embedding).all()
    
    if not results:
        raise HTTPException(status_code=404, detail="No embeddings found in the database")

    ids = []
    embeddings = []
    for id, embedding_bytes in results:
        ids.append(id)
        embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
        embeddings.append(embedding)

    embeddings_array = np.array(embeddings, dtype=np.float32)
    
    # Create and populate the FAISS index
    dimension = embeddings_array.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)

    return index, ids

#@router.post("/semantic-search/")
def semantic_search(query: str, top_k: int = 5, db: Session = Depends(get_db)):
    # Build the FAISS index
    index, ids = build_faiss_index(db)

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-mpnet-base-v2')  
    query_vector = model.encode([query])[0]

    distances, indices = index.search(np.array([query_vector], dtype=np.float32), top_k)

    result_ids = [ids[i] for i in indices[0]]
    results = db.query(Data).filter(Data.id.in_(result_ids)).all()

    sorted_results = sorted(results, key=lambda x: result_ids.index(x.id))

    formatted_results = [
        {
            "id": result.id,
            "text": result.text,
            "page_number": result.page_number,
            "similarity_score": 1 - distances[0][i]  
        }
        for i, result in enumerate(sorted_results)
    ]

    return formatted_results