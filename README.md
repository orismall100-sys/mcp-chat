# MCP Chat — Crumb & Culture Data Assistant

## Overview

A natural language chat interface for querying employee data, built as a home assignment.

The system consists of three services:

| Service | Description |
|---------|-------------|
| **MCP Server** | Ingests a CSV of people records into SQLite and exposes query tools via the MCP protocol over streamable HTTP |
| **Chat Backend** | Receives user messages, connects to the MCP server as a client, and runs an agentic loop with Gemini to answer questions using the available tools |
| **Chat Frontend** | React web app — a clean chat interface for natural language queries |

---

## Architecture

```
Browser
  └── Chat Frontend
        └── Chat Backend
              └── MCP Server
                    └── SQLite (people.db)
```

The chat backend acts as an MCP client — on each user message it connects to the MCP server, retrieves the available tools, and runs an agentic loop where Gemini calls tools iteratively until it has a final answer.

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- A [Google AI Studio](https://aistudio.google.com/) API key (Gemini)

### Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd mcp-chat
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Open `.env` in any text editor and fill in your `GEMINI_API_KEY`. Note: `.env` is a hidden file — use `ls -la` to verify it was created.

3. Make sure Docker Desktop is running, then build and run:
   ```bash
   docker compose up --build -d
   ```

4. Open [http://localhost](http://localhost) in your browser.

---

## Project Structure

```
mcp-chat/
├── data/
│   └── people-list-export.csv     # Source data
├── docker-compose.yml             # Orchestration
├── .env                           # Environment variables (not committed)
├── .env.example                   # Template — copy to .env and fill in values
├── mcp-server/
│   ├── main.py                    # Tool registration (FastMCP)
│   ├── tools.py                   # Tool implementations
│   ├── db.py                      # CSV ingestion + SQLite connection
│   ├── Dockerfile
│   └── requirements.txt
├── chat-backend/
│   ├── main.py                    # FastAPI app + CORS
│   ├── chat.py                    # Agentic loop + MCP client
│   ├── schemas.py                 # Request/response models
│   ├── Dockerfile
│   └── requirements.txt
└── chat-frontend/
    ├── src/
    │   ├── App.jsx                # Chat UI
    │   ├── App.css                # Styles
    │   ├── api.js                 # HTTP client
    │   └── main.jsx               # Entry point
    ├── Dockerfile
    └── package.json
```

---

## Author
Ori Small
