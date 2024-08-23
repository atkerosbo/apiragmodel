from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import Data
from database import get_db
import numpy as np

def save_to_database(pages_data_with_embeddings: list, db: Session):
    try:
        for page in pages_data_with_embeddings:
            # Convert embedding to bytes if it's not already
            if isinstance(page['embedding'], list):
                embedding_bytes = np.array(page['embedding'], dtype=np.float32).tobytes()
            else:
                embedding_bytes = page['embedding']

            new_data = Data(
                page_number=page['page_number'],
                page_char_count=page['page_char_count'],
                page_word_count=page['page_word_count'],
                page_sentence_count=page['page_sentence_count'],
                page_token_count=page['page_token_count'],
                text=page['text'],
                embedding=embedding_bytes
            )
            db.add(new_data)
        
        db.commit()
        print("All data added successfully")
        return {"message": "All data saved successfully"}
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while saving data: {str(e)}")


