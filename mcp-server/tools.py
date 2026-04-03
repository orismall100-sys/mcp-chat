import sqlite3
from db import get_db_connection


def convert_rows_to_dicts(cursor: sqlite3.Cursor) -> list[dict]:
    column_names = [col[0] for col in cursor.description]
    return [dict(zip(column_names, raw_row)) for raw_row in cursor.fetchall()]


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
    Search people by any combination of fields.
    All parameters are optional and use partial, case-insensitive matching.
    """
    provided_filters = {
        "full_name": full_name,
        "job": job,
        "team": team,
        "office": office,
        "country": country,
        "city": city,
        "gender": gender,
        "contract_type": contract_type,
        "work_status": work_status,
        "reports_to": reports_to,
    }

    where_conditions = []
    query_params = []

    for key, value in provided_filters.items():
        if value:
            where_conditions.append(f"{key} LIKE ?")
            query_params.append(f"%{value}%")

    sql_query = "SELECT full_name, job, team, city, country, work_status, contract_type FROM people"
    if where_conditions:
        sql_query += " WHERE " + " AND ".join(where_conditions)

    try:
        connection = get_db_connection()
        cursor = connection.execute(sql_query, query_params)
        rows = convert_rows_to_dicts(cursor)
        connection.close()
        return rows
    except Exception as e:
        return [{"error": str(e)}]


def get_person(person_name: str) -> dict | None:
    """Get a single person's full record by name (partial match)."""
    try:
        connection = get_db_connection()
        cursor = connection.execute("SELECT * FROM people WHERE full_name LIKE ?", (f"%{person_name}%",))
        rows = convert_rows_to_dicts(cursor)
        connection.close()
        return rows[0] if rows else None
    except Exception as e:
        return {"error": str(e)}


def get_statistics(group_by: str, metric: str) -> list[dict]:
    """
    Get aggregate statistics grouped by a field.
    group_by options: city, team, country, gender, office, job, contract_type, work_status
    metric options: count | avg_salary | max_salary | min_salary | total_salary
    Example: group_by="team", metric="avg_salary" → average salary per team
    """
    allowed_group_by_fields = {"city", "team", "country", "gender", "office", "job", "contract_type", "work_status"}
    if group_by not in allowed_group_by_fields:
        return [{"error": f"Invalid group_by field: {group_by}. Choose from: {', '.join(sorted(allowed_group_by_fields))}"}]

    metric_expressions = {
        "count":        ("COUNT(*)",                          "count"),
        "avg_salary":   ("ROUND(AVG(salary_amount), 2)",      "avg_salary"),
        "max_salary":   ("ROUND(MAX(salary_amount), 2)",      "max_salary"),
        "min_salary":   ("ROUND(MIN(salary_amount), 2)",      "min_salary"),
        "total_salary": ("ROUND(SUM(salary_amount), 2)",      "total_salary"),
    }

    if metric not in metric_expressions:
        return [{"error": f"Invalid metric: {metric}. Choose from: {', '.join(metric_expressions.keys())}"}]

    expr, alias = metric_expressions[metric]
    sql_query = f"SELECT {group_by}, {expr} as {alias} FROM people GROUP BY {group_by} ORDER BY {alias} DESC"

    try:
        connection = get_db_connection()
        cursor = connection.execute(sql_query)
        rows = convert_rows_to_dicts(cursor)
        connection.close()
        return rows
    except Exception as e:
        return [{"error": str(e)}]


def list_field_values(field_name: str) -> list[str]:
    """Get all distinct values for a given field."""
    allowed_fields = {
        "team", "office", "country", "city", "gender",
        "contract_type", "work_status", "job", "salary_currency"
    }
    if field_name not in allowed_fields:
        return [f"Invalid field: {field_name}"]

    try:
        connection = get_db_connection()
        cursor = connection.execute(f"SELECT DISTINCT {field_name} FROM people ORDER BY {field_name}")
        rows = [row[0] for row in cursor.fetchall() if row[0]]
        connection.close()
        return rows
    except Exception as e:
        return [str(e)]


def run_query(sql_query: str) -> list[dict] | dict:
    """
    Execute a read-only SQL SELECT query against the people table.
    Use this for any question the other tools cannot answer.
    The table is called 'people' and has these columns:
    id, full_name, first_name, last_name, work_status, start_date, job,
    work_email, team, reports_to, office, salary_amount, salary_currency,
    salary_type, tenure, country, city, date_of_birth, gender, contract_type
    """
    if not sql_query.strip().upper().startswith("SELECT"):
        return {"error": "Only SELECT queries are allowed."}

    try:
        connection = get_db_connection()
        cursor = connection.execute(sql_query, [])
        rows = convert_rows_to_dicts(cursor)
        connection.close()
        return rows
    except Exception as e:
        return {"error": str(e)}
