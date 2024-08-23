from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from database import engine
import models
import text_summerizer, suggest_price, semantic_search, chat_complete, price_with_assistent, pdf_handler, rag_query_endpoint


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

models.Base.metadata.create_all(engine)


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(text_summerizer.router)
app.include_router(chat_complete.router)
app.include_router(suggest_price.router)
app.include_router(price_with_assistent.router)
app.include_router(pdf_handler.router)
app.include_router(semantic_search.router)
app.include_router(rag_query_endpoint.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}








