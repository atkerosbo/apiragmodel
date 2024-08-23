from langchain_openai import ChatOpenAI
from langchain.schema import BaseOutputParser
from langchain.prompts.chat import ChatPromptTemplate
from semantic_search import semantic_search, SearchQuery
from fastapi import Depends, APIRouter, HTTPException
from tokens import verify_key, verify_token
from schemas import UserQuery, SearchQuery
from sqlalchemy.orm import Session
from database import get_db
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

class AnswerOutputParser(BaseOutputParser):
    def parse(self, text: str) -> str:
        return text.strip().split("answer = ")[-1]

MODEL = os.getenv("MODEL")
KEY = os.getenv("OPEN_AI_KEY")
ORG = os.getenv("ORG")
PROJECT = os.getenv("PROJECT")
os.environ["OPENAI_API_KEY"] = os.getenv("OPEN_AI_KEY")

instructions_summarization = """You are an AI assistant that helps summarize and answer questions based on provided context. You will be given a user query and relevant context retrieved from a knowledge base. Your task is to provide a concise and informative answer to the query using the given context. If the context doesn't contain enough information to answer the query, say so. Always base your answer on the provided context. Output the answer in the following format: answer = <answer here>"""

chat_model = ChatOpenAI(model=MODEL, temperature=0.7, openai_api_key=KEY)

human_template = "Query: {query}\n\nContext: {context}\n\nPlease provide a concise answer to the query based on the given context."

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", instructions_summarization),
    ("human", human_template)
])

def generate_answer(query: str, context: str):
    messages = chat_prompt.format_messages(query=query, context=context)
    result = chat_model.invoke(messages)
    parsed = AnswerOutputParser().parse(result.content)
    return parsed

@router.post("/ragchat", dependencies=[Depends(verify_token), Depends(verify_key)], status_code=200)
async def rag_chat(user_query: UserQuery, db: Session = Depends(get_db)):
    try:
        # Perform semantic search
        search_query = SearchQuery(query=user_query.query, top_k=3)  
        semantic_results = semantic_search(search_query, db=db)
        
        context = " ".join([result["text"] for result in semantic_results])
        
        answer = generate_answer(user_query.query, context)
        
        return {"answer": answer, "sources": semantic_results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")