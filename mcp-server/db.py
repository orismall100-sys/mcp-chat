import csv
import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "people.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "../data/people-list-export.csv")


def get_db_connection() -> sqlite3.Connection:
    """Read-only connection to the SQLite database."""
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)


def _ingest(cursor: sqlite3.Cursor) -> None:
    """Clear and re-populate the people table from the CSV."""
    cursor.execute("DELETE FROM people")
    with open(CSV_PATH, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            cursor.execute("""
                INSERT INTO people (
                    full_name, work_status, start_date, job, work_email,
                    team, reports_to, office, salary_amount, salary_currency,
                    salary_type, tenure, country, city, first_name, last_name,
                    date_of_birth, gender, contract_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["Full Name"],
                row["Work Status"],
                row["Start Date"],
                row["Job"],
                row["Work Email"],
                row["Team"],
                row["Reports To"],
                row["Office"],
                float(row["Salary Amount"]) if row["Salary Amount"] else None,
                row["Salary Currency"],
                row["Salary Type"],
                row["Tenure"],
                row["Country"],
                row["City"],
                row["First Name"],
                row["Last Name"],
                row["Date of Birth"],
                row["Gender"],
                row["Contract Type"],
            ))
    logger.info(f"DB ingested from {CSV_PATH}")


def init_db() -> None:
    """Create the table and ingest the CSV if it's newer than the existing DB."""
    db_exists = os.path.exists(DB_PATH)
    csv_newer = not db_exists or os.path.getmtime(CSV_PATH) > os.path.getmtime(DB_PATH)

    # Writable connection — get_db_connection() is read-only and used only by tools
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            work_status TEXT,
            start_date TEXT,
            job TEXT,
            work_email TEXT,
            team TEXT,
            reports_to TEXT,
            office TEXT,
            salary_amount REAL,
            salary_currency TEXT,
            salary_type TEXT,
            tenure TEXT,
            country TEXT,
            city TEXT,
            first_name TEXT,
            last_name TEXT,
            date_of_birth TEXT,
            gender TEXT,
            contract_type TEXT
        )
    """)

    if csv_newer:
        _ingest(cursor)
    else:
        logger.info("DB is up to date, skipping ingestion")

    connection.commit()
    connection.close()
