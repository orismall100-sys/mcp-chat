import os
import json
from openai import AsyncOpenAI
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:3001/mcp")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")

gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=60.0,
)


def _clean_schema(schema: dict) -> dict:
    """Recursively remove JSON Schema fields unsupported by the Gemini OpenAI-compat endpoint."""
    unsupported_fields = {"additionalProperties", "$schema", "$defs", "definitions", "default", "title"}
    cleaned = {k: v for k, v in schema.items() if k not in unsupported_fields}
    if "properties" in cleaned:
        cleaned["properties"] = {
            key: _clean_schema(value)
            for key, value in cleaned["properties"].items()
        }
    return cleaned


def _mcp_tool_to_openai_format(mcp_tool) -> dict:
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description or "",
            "parameters": _clean_schema(mcp_tool.inputSchema),
        },
    }


async def run_chat(user_message: str, conversation_history: list) -> str:
    async with streamablehttp_client(MCP_SERVER_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as mcp_session:
            await mcp_session.initialize()

            mcp_tools = await mcp_session.list_tools()
            tools = [_mcp_tool_to_openai_format(t) for t in mcp_tools.tools]

            system_prompt = """You are a data assistant for Crumb & Culture, a bakery company.

TOOLS:
- get_person: look up a specific individual by name
- search_people: filter employees by field (city, team, gender, etc.)
- get_statistics: aggregations grouped by field (count, avg/max/min/total salary)
- list_field_values: discover what values exist for a field (e.g. all team names)
- run_query: write SQL for anything else — age calculations, rankings, multi-condition analysis

RULES:
- Always use a tool. Never guess or invent data.
- Prefer specialized tools for simple lookups; use run_query for complex analysis.
- If a specialized tool fails or doesn't cover the question, fall back to run_query.
- Dates are stored as DD/MM/YYYY text. To sort dates correctly use ORDER BY substr(col,7,4), substr(col,4,2), substr(col,1,2). Always filter out NULL or empty date values.
- The tenure column contains text like "2 years 8 months" or "1 year". When calculating average tenure, convert it to a decimal by extracting both years and months.
- Keep answers concise and factual.
- Never expose internal database column names in responses. Use natural language instead (e.g. "job title" not "job", "start date" not "start_date", "salary" not "salary_amount")."""

            messages = (
                [{"role": "system", "content": system_prompt}]
                + conversation_history
                + [{"role": "user", "content": user_message}]
            )

            # Agentic loop: model may call tools multiple times before giving a final answer
            while True:
                try:
                    response = await gemini_client.chat.completions.create(
                        model=GEMINI_MODEL,
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                    )
                except Exception as e:
                    return f"Error contacting the AI model: {e}"

                assistant_message = response.choices[0].message

                if not assistant_message.tool_calls:
                    return assistant_message.content or ""

                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in assistant_message.tool_calls
                    ],
                })

                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    tool_result = await mcp_session.call_tool(tool_name, tool_args)
                    serialized_result = [
                        item.text if hasattr(item, "text") else str(item)
                        for item in tool_result.content
                    ]
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(serialized_result),
                    })
