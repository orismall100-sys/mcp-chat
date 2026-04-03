import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv
from schemas import ChatRequest, ChatResponse
from chat import run_chat

logging.basicConfig(level=logging.INFO)
load_dotenv(find_dotenv())

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ["CORS_ORIGIN"]],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Receive a user message and return the assistant's response."""
    try:
        response = await run_chat(request.message, request.history)
        return ChatResponse(response=response)
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")
