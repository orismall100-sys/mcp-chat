import sqlite3
from db import get_db_connection


def convert_rows_to_dicts(cursor: sqlite3.Cursor) -> list[dict]:
    column_names = [col[0] for col in cursor.description]
    return [dict(zip(column_names, raw_row)) for raw_row in cursor.fetchall()]


def search_people(filters: dict) -> list[dict]:
    """
    Search people by any combination of fields.
    filters keys: full_name, job, team, office, country, city, gender, contract_type, work_status
    Values are matched with LIKE (case-insensitive, partial match).
    """
    allowed_filter_fields = {
        "full_name", "job", "team", "office", "country",
        "city", "gender", "contract_type", "work_status", "reports_to"
    }
    where_conditions = []
    query_params = []

    for key, value in filters.items():
        if key in allowed_filter_fields and value:
            where_conditions.append(f"{key} LIKE ?")
            query_params.append(f"%{value}%")

    sql_query = "SELECT * FROM people"
    if where_conditions:
        sql_query += " WHERE " + " AND ".join(where_conditions)

    connection = get_db_connection()
    cursor = connection.execute(sql_query, query_params)
    rows = convert_rows_to_dicts(cursor)
    connection.close()
    return rows


def get_person(name: str) -> dict | None:
    """Get a single person's full record by name (partial match)."""
    connection = get_db_connection()
    cursor = connection.execute("SELECT * FROM people WHERE full_name LIKE ?", (f"%{name}%",))
    rows = convert_rows_to_dicts(cursor)
    connection.close()
    return rows[0] if rows else None


def get_statistics(group_by: str, metric: str) -> list[dict]:
    """
    Get aggregate statistics.
    group_by: any text column (city, team, country, gender, office, job, contract_type)
    metric: "count" | "avg_salary"
    """
    allowed_group_by_fields = {"city", "team", "country", "gender", "office", "job", "contract_type", "work_status"}
    if group_by not in allowed_group_by_fields:
        return [{"error": f"Invalid group_by field: {group_by}"}]

    if metric == "count":
        sql_query = f"SELECT {group_by}, COUNT(*) as count FROM people GROUP BY {group_by} ORDER BY count DESC"
    elif metric == "avg_salary":
        sql_query = f"SELECT {group_by}, ROUND(AVG(salary_amount), 2) as avg_salary FROM people GROUP BY {group_by} ORDER BY avg_salary DESC"
    else:
        return [{"error": f"Invalid metric: {metric}. Use 'count' or 'avg_salary'"}]

    connection = get_db_connection()
    cursor = connection.execute(sql_query)
    rows = convert_rows_to_dicts(cursor)
    connection.close()
    return rows


def list_field_values(field: str) -> list[str]:
    """Get all distinct values for a given field."""
    allowed_fields = {
        "team", "office", "country", "city", "gender",
        "contract_type", "work_status", "job", "salary_currency"
    }
    if field not in allowed_fields:
        return [f"Invalid field: {field}"]

    connection = get_db_connection()
    cursor = connection.execute(f"SELECT DISTINCT {field} FROM people ORDER BY {field}")
    rows = [row[0] for row in cursor.fetchall() if row[0]]
    connection.close()
    return rows
