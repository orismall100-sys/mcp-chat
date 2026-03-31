import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from db import init_db
import tools

load_dotenv()

init_db()

mcp = FastMCP(
    "people-server",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", 3001)),
)


@mcp.tool()
def search_people(
    full_name: str = None,
    job: str = None,
    team: str = None,
    office: str = None,
    country: str = None,
    city: str = None,
    gender: str = None,
    contract_type: str = None,
    work_status: str = None,
    reports_to: str = None,
) -> list[dict]:
    """
    Search people by any combination of fields. All parameters are optional.
    Values use partial, case-insensitive matching.
    Example: city="London", team="Bread"
    """
    return tools.search_people(
        full_name=full_name, job=job, team=team, office=office,
        country=country, city=city, gender=gender, contract_type=contract_type,
        work_status=work_status, reports_to=reports_to,
    )


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
