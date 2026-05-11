from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None


root = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(root / "frontend"))

class Prompt(BaseModel):
    message : str

@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"name": "World"})

@app.post("/chat")
async def chat(prompt: Prompt):
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not configured. Set the GROQ_API_KEY environment variable.",
        )

    response = client.chat.completions.create(
        messages=[
            # Set an optional system message. This sets the behavior of the
            # assistant and can be used to provide specific instructions for
            # how it should behave throughout the conversation.
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            # Set a user message for the assistant to respond to.
            {
                "role": "user",
                "content": prompt.message,
            }
        ],

        # The language model which will generate the completion.
        model="llama-3.3-70b-versatile"
    )
    return {
        "reply": response.choices[0].message.content
    }
