import os
import logging
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from db import init_db
import tools

logging.basicConfig(level=logging.INFO)
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
    """
    return tools.search_people(
        full_name=full_name, job=job, team=team, office=office,
        country=country, city=city, gender=gender, contract_type=contract_type,
        work_status=work_status, reports_to=reports_to,
    )


@mcp.tool()
def get_person(person_name: str) -> dict | None:
    """
    Get the full record of a single person by name (partial match).
    """
    return tools.get_person(person_name)


@mcp.tool()
def get_statistics(group_by: str, metric: str) -> list[dict]:
    """
    Get aggregate statistics grouped by a field.
    group_by options: city, team, country, gender, office, job, contract_type, work_status.
    metric options: count | avg_salary | max_salary | min_salary | total_salary.
    """
    return tools.get_statistics(group_by, metric)


@mcp.tool()
def list_field_values(field_name: str) -> list[str]:
    """
    List all distinct values for a given field.
    Available fields: team, office, country, city, gender, contract_type, work_status, job, salary_currency.
    """
    return tools.list_field_values(field_name)


@mcp.tool()
def run_query(sql_query: str) -> list[dict] | dict:
    """
    Execute a read-only SQL SELECT query against the people table.
    Use this for any question the other tools cannot answer.
    """
    return tools.run_query(sql_query)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
