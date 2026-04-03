# MCP Chat — Crumb & Culture Data Assistant

## Overview

A natural language chat interface for querying employee data, built as a home assignment.

The system consists of three services:

| Service | Description |
|---------|-------------|
| **MCP Server** | Ingests a CSV of people records into SQLite and exposes query tools via the MCP protocol over streamable HTTP |
| **Chat Backend** | Receives user messages, connects to the MCP server as a client, and runs an agentic loop with Gemini to answer questions using the available tools |
| **Chat Frontend** | React web app served via nginx — a clean chat interface for natural language queries |

---

## Architecture

```
Browser
  └── Chat Frontend (nginx :80)
        └── Chat Backend (FastAPI :8000)
              └── MCP Server (FastMCP :3001)
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

2. Configure the chat backend environment:
   ```bash
   cp chat-backend/.env.example chat-backend/.env
   ```
   Fill in your `GEMINI_API_KEY` in `chat-backend/.env`.

3. Build and run:
   ```bash
   docker compose up --build -d
   ```

4. Open [http://localhost](http://localhost) in your browser.

### Environment Variables

**`chat-backend/.env`**
```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=models/gemini-2.5-flash
MCP_SERVER_URL=http://mcp-server:3001/mcp
CORS_ORIGIN=http://localhost
```

> `MCP_SERVER_URL` and `CORS_ORIGIN` are overridden by `docker-compose.yml` at runtime — no need to change them.

---

## Project Structure

```
mcp-chat/
├── data/
│   └── people-list-export.csv     # Source data
├── docker-compose.yml             # Orchestration
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
