import sqlite3
from db import get_connection


def dict_rows(cursor: sqlite3.Cursor) -> list[dict]:
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def search_people(filters: dict) -> list[dict]:
    """
    Search people by any combination of fields.
    filters keys: full_name, job, team, office, country, city, gender, contract_type, work_status
    Values are matched with LIKE (case-insensitive, partial match).
    """
    allowed = {
        "full_name", "job", "team", "office", "country",
        "city", "gender", "contract_type", "work_status", "reports_to"
    }
    conditions = []
    params = []

    for key, value in filters.items():
        if key in allowed and value:
            conditions.append(f"{key} LIKE ?")
            params.append(f"%{value}%")

    query = "SELECT * FROM people"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    con = get_connection()
    cur = con.execute(query, params)
    results = dict_rows(cur)
    con.close()
    return results


def get_person(name: str) -> dict | None:
    """Get a single person's full record by name (partial match)."""
    con = get_connection()
    cur = con.execute("SELECT * FROM people WHERE full_name LIKE ?", (f"%{name}%",))
    results = dict_rows(cur)
    con.close()
    return results[0] if results else None


def get_statistics(group_by: str, metric: str) -> list[dict]:
    """
    Get aggregate statistics.
    group_by: any text column (city, team, country, gender, office, job, contract_type)
    metric: "count" | "avg_salary"
    """
    allowed_group = {"city", "team", "country", "gender", "office", "job", "contract_type", "work_status"}
    if group_by not in allowed_group:
        return [{"error": f"Invalid group_by field: {group_by}"}]

    if metric == "count":
        query = f"SELECT {group_by}, COUNT(*) as count FROM people GROUP BY {group_by} ORDER BY count DESC"
    elif metric == "avg_salary":
        query = f"SELECT {group_by}, ROUND(AVG(salary_amount), 2) as avg_salary FROM people GROUP BY {group_by} ORDER BY avg_salary DESC"
    else:
        return [{"error": f"Invalid metric: {metric}. Use 'count' or 'avg_salary'"}]

    con = get_connection()
    cur = con.execute(query)
    results = dict_rows(cur)
    con.close()
    return results


def list_field_values(field: str) -> list[str]:
    """Get all distinct values for a given field."""
    allowed = {
        "team", "office", "country", "city", "gender",
        "contract_type", "work_status", "job", "salary_currency"
    }
    if field not in allowed:
        return [f"Invalid field: {field}"]

    con = get_connection()
    cur = con.execute(f"SELECT DISTINCT {field} FROM people ORDER BY {field}")
    results = [row[0] for row in cur.fetchall() if row[0]]
    con.close()
    return results
