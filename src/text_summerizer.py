from langchain_openai import ChatOpenAI
from langchain.schema import BaseOutputParser
from langchain.prompts.chat import ChatPromptTemplate

from langchain.agents.openai_assistant import OpenAIAssistantRunnable
import openai

from fastapi import Depends, APIRouter
from tokens import verify_key, verify_token
from schemas import UserQuery

from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

class AnswerOutputParser(BaseOutputParser):
    def parse(self, text: str) -> str:
       return text.strip().split("answer = ")

MODEL = os.getenv("MODEL")
KEY = os.getenv("OPEN_AI_KEY")
ORG = os.getenv("ORG")
PROJECT = os.getenv("PROJECT")
os.environ["OPENAI_API_KEY"] = os.getenv("OPEN_AI_KEY")

instructions_summerization = """You are an assistant that help summerize text, Output the answer in the following format: answer = <answer here>
Make sure to output the answer in all lowercases and to have exactly one space and one equal sign following it"""



#client = openai.OpenAI(api_key=KEY, organization=ORG, project=PROJECT)



chat_model = ChatOpenAI(model = MODEL, temperature=0.9, openai_api_key=KEY)

human_template =  "{problem}"

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", instructions_summerization),
    ("human", human_template)
    
])

def summerize_text(text:str):
    messages = chat_prompt.format_messages(problem = text)
    result = chat_model.invoke(messages)
    parsed = AnswerOutputParser().parse(result.content)
    # steps, answer = parsed
    # print(steps, answer)
    return parsed

def summerize(query:str):
    # input_file = "data/pdf-500KB.pdf"
    
    # # Extract text from PDF
    # extracted_text = extract_text_from_pdf(input_file)
    
    # # Summarize the extracted text
    summarized_text = summerize_text(query)
    
    return(summarized_text)



@router.post("/summerize", dependencies=[Depends(verify_token), Depends(verify_key)], status_code=200)
async def summerzie_text(query:UserQuery):
    #print(query)
    summerized_text = summerize(query)
         
    
    return {"Your summerized text": summerized_text}