import fitz
from tqdm.auto import tqdm
import re
from sentence_transformers import SentenceTransformer
import numpy as np
from fastapi import Depends, APIRouter, UploadFile, File, HTTPException
from tokens import verify_key, verify_token
import os
import shutil
from embeding_to_database import save_to_database
from sqlalchemy.orm import Session
from database import get_db
from dotenv import load_dotenv

load_dotenv()
E_MODELS = os.getenv("E_MODELS")

UPLOAD_DIR = "uploads"
router = APIRouter()

embedding_model = SentenceTransformer(model_name_or_path="all-mpnet-base-v2", device="cpu")

class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pages_data = []

    def text_formatter(self, text: str) -> str:
        return text.replace("\n", " ").strip()

    def open_and_read_pdf(self):
        try:
            with fitz.open(self.pdf_path) as doc:
                for page_number, page in enumerate(doc):
                    text = page.get_text()
                    text = self.text_formatter(text)
                    page_data = {
                        "page_number": page_number,
                        "page_char_count": len(text),
                        "page_word_count": len(text.split()),
                        "page_sentence_count": len(text.split('. ')),
                        "page_token_count": len(text) // 4,
                        "text": text
                    }
                    self.pages_data.append(page_data)
        except Exception as e:
            raise ValueError(f"Error reading PDF: {str(e)}")

class EmbeddingAdder:
    def __init__(self, embedding_model: SentenceTransformer):
        self.embedding_model = embedding_model

    def add_embeddings(self, pages_data: list) -> list:
        sentences = [page["text"] for page in pages_data]
        embeddings = self.embedding_model.encode(sentences)

        for page, embedding in zip(pages_data, embeddings):
            page["embedding"] = embedding.tolist()
        
        return pages_data

def main_pdf_embeding(file_path):
    pdf_processor = PDFProcessor(file_path)
    pdf_processor.open_and_read_pdf()
    pages_data = pdf_processor.pages_data
    embedding_adder = EmbeddingAdder(embedding_model)
    return embedding_adder.add_embeddings(pages_data)

@router.post("/upload-pdf/", dependencies=[Depends(verify_token), Depends(verify_key)], status_code=200)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while saving the file: {str(e)}")
    
    try:
        data = main_pdf_embeding(file_path)
        save_to_database(data,db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with decoding and embedding: {str(e)}")

    return {"filename": file.filename, "message": "PDF uploaded, processed, and saved successfully"}