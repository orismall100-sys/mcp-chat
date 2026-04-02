import os
import json
from groq import AsyncGroq
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:3001/mcp")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))


def _clean_schema_for_groq(schema: dict) -> dict:
    """Recursively remove JSON Schema fields that Groq does not support."""
    unsupported_fields = {"additionalProperties", "$schema", "$defs", "definitions", "default", "title"}
    cleaned = {k: v for k, v in schema.items() if k not in unsupported_fields}
    if "properties" in cleaned:
        cleaned["properties"] = {
            key: _clean_schema_for_groq(value)
            for key, value in cleaned["properties"].items()
        }
    return cleaned


def _mcp_tool_to_groq_format(mcp_tool) -> dict:
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description or "",
            "parameters": _clean_schema_for_groq(mcp_tool.inputSchema),
        },
    }


async def run_chat(user_message: str, conversation_history: list) -> str:
    async with streamablehttp_client(MCP_SERVER_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as mcp_session:
            await mcp_session.initialize()

            mcp_tools = await mcp_session.list_tools()
            groq_tools = [_mcp_tool_to_groq_format(t) for t in mcp_tools.tools]

            system_prompt = (
                "You are an HR data assistant for Crumb and Culture, a bakery company. "
                "You have access to a SQLite database with an employees table called 'people'. "
                "Always use tools to answer — never guess or make up data. "
                "Tool usage rules:\n"
                "- For looking up a specific person: use get_person\n"
                "- For searching/filtering employees (e.g. by city, team, gender): use search_people\n"
                "- For ANY analytical question (averages, counts, max, min, rankings, breakdowns, age calculations, salary analysis, org chart): use run_query with a SQL SELECT statement\n"
                "The 'people' table columns: id, full_name, first_name, last_name, work_status, start_date, "
                "job, work_email, team, reports_to, office, salary_amount, salary_currency, salary_type, "
                "tenure, country, city, date_of_birth, gender, contract_type. "
                "date_of_birth and start_date are stored as text in YYYY-MM-DD format. "
                "Use strftime('%Y','now') for current year calculations."
            )
            messages = (
                [{"role": "system", "content": system_prompt}]
                + conversation_history
                + [{"role": "user", "content": user_message}]
            )

            # Agentic loop: Groq may call tools multiple times before giving a final answer
            while True:
                try:
                    response = await groq_client.chat.completions.create(
                        model=GROQ_MODEL,
                        messages=messages,
                        tools=groq_tools,
                        tool_choice="auto",
                    )
                except Exception as e:
                    return f"Error contacting the AI model: {e}"

                assistant_message = response.choices[0].message

                if not assistant_message.tool_calls:
                    return assistant_message.content or ""

                # Add assistant's response (with tool calls) to message history
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                        for tool_call in assistant_message.tool_calls
                    ],
                })

                # Execute each tool call against the MCP server and feed results back
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
