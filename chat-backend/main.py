import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from schemas import ChatRequest, ChatResponse
from chat import run_chat

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ["CORS_ORIGIN"]],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response = await run_chat(request.message, request.history)
    except Exception:
        response = "Something went wrong. Please try again."
    return ChatResponse(response=response)
