import openai
import re
from dotenv import load_dotenv
import os

from fastapi import Depends, APIRouter
from tokens import verify_key, verify_token
from schemas import UserQuery

router = APIRouter()


load_dotenv()

MODEL = "gpt-4o"
KEY = os.getenv("OPEN_AI_KEY")
ORG = os.getenv("ORG")
PROJECT = os.getenv("PROJECT")
THREAD_ID = os.getenv("THREAD_ID")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
 
client = openai.OpenAI(api_key=KEY, organization=ORG, project=PROJECT)


def get_value(answer):
    value = answer
    return value


def create_thread(query,assistant_id ):
    thread = client.beta.threads.create(
        
        messages=[
            {"role": "user", "content": query}
        ]
        
    )
    thread_id = thread.id
    thread_message = client.beta.threads.messages.create(thread_id,role="user",content=query,)
    
    stream = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id,
    stream=True
    )
    for event in stream:
        i = 1

    thread_messages = client.beta.threads.messages.list(thread_id)
        
    return  thread_messages


    
router.get("/getpriceassistant", dependencies=[Depends(verify_token), Depends(verify_key)], status_code=200)
def suggest_price_with_assistant(query):
    assistant_id = ASSISTANT_ID
    print("Assistant accessed.")
    response = create_thread(query, assistant_id)
    answer = get_value(response)

    parsed = answer
    
    return parsed   




@router.post("/getpriceassistant", dependencies=[Depends(verify_token), Depends(verify_key)], status_code=200)
async def get_price_assistant(querry:UserQuery):
    answer = suggest_price_with_assistant(querry)
    return {"AI answer": answer }
