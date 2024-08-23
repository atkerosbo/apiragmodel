from langchain_openai import ChatOpenAI
from langchain.schema import BaseOutputParser
from langchain.prompts.chat import ChatPromptTemplate

from fastapi import Depends, APIRouter
from tokens import verify_key, verify_token
from schemas import UserQuery

from dotenv import load_dotenv
import os

router = APIRouter()
load_dotenv()

class AnswerOutputParser(BaseOutputParser):
    def parse(self, text: str) -> str:
       return text.strip().split("answer = ")

OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
ORG = os.getenv("ORG")
PROJECT = os.getenv("PROJECT")

#MODEL = "gpt-4o"
MODEL = "gpt-3.5-turbo"


chat_model = ChatOpenAI(model = MODEL, temperature=0.9, openai_api_key=OPEN_AI_KEY)


template = """ You are a helpfull assistant on the website agrimar.rs. YOUR JOB is to find same product on other webpages, competitor websites. Make sure that the URL that you suggest is correct. Output each found product that you find with a product name, price and a link to the product, and return the answer in the following format: answer = <answer here>
Make sure that you find at least 3 alternative prices. 
Make sure to output the answer in all lowercases and to have exactly one space and one equal sign following it"""

human_template =  "{problem}"

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", template),
    ("human", human_template)
])

def suggest_product(problem):
    messages = chat_prompt.format_messages(problem = problem)
    result = chat_model.invoke(messages)
    parsed = AnswerOutputParser().parse(result.content)
    answer = parsed
    return answer



@router.post("/suggestprice", dependencies=[Depends(verify_token), Depends(verify_key)], status_code=200)
async def suggest_price(query:UserQuery):
    
    answer = suggest_product(query)
    return {"AI answer": answer }