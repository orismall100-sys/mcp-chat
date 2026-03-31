import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from db import init_db
import tools

load_dotenv()

init_db()

mcp = FastMCP(
    "people-server",
    host=os.getenv("MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("MCP_PORT", 3001)),
)


@mcp.tool()
def search_people(filters: dict) -> list[dict]:
    """
    Search people by any combination of fields.
    Available filter keys: full_name, job, team, office, country, city, gender, contract_type, work_status, reports_to.
    Values use partial, case-insensitive matching.
    Example: {"city": "London", "team": "Bread"}
    """
    return tools.search_people(filters)


@mcp.tool()
def get_person(name: str) -> dict | None:
    """
    Get the full record of a single person by name (partial match).
    Example: "Alaric"
    """
    return tools.get_person(name)


@mcp.tool()
def get_statistics(group_by: str, metric: str) -> list[dict]:
    """
    Get aggregate statistics grouped by a field.
    group_by options: city, team, country, gender, office, job, contract_type, work_status
    metric options: "count" | "avg_salary"
    Example: group_by="city", metric="count" → how many people per city
    """
    return tools.get_statistics(group_by, metric)


@mcp.tool()
def list_field_values(field: str) -> list[str]:
    """
    List all distinct values for a given field.
    Available fields: team, office, country, city, gender, contract_type, work_status, job, salary_currency
    Example: field="team" → ["Bread", "Barista", "Marketing", ...]
    """
    return tools.list_field_values(field)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
