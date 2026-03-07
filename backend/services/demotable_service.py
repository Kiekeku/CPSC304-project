from db import get_connection
from services.sql_service import execute_sql_file


def test_oracle_connection() -> bool:
    try:
        with get_connection():
            return True
    except Exception:
        return False


def fetch_demotable() -> list[list]:
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM DEMOTABLE")
                rows = cursor.fetchall()
                return [[*row] for row in rows]
    except Exception:
        return []


def initiate_demotable() -> bool:
    schema_ok = execute_sql_file("demotable_schema.sql", auto_commit=True)
    if not schema_ok:
        return False

    execute_sql_file("demotable_seed.sql", auto_commit=True)
    return True


def insert_demotable(row_id: int, name: str) -> bool:
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO DEMOTABLE (id, name) VALUES (:id, :name)",
                    {"id": row_id, "name": name},
                )
                rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected > 0
    except Exception:
        return False


def update_name_demotable(old_name: str, new_name: str) -> bool:
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE DEMOTABLE SET name = :newName WHERE name = :oldName",
                    {"newName": new_name, "oldName": old_name},
                )
                rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected > 0
    except Exception:
        return False


def count_demotable() -> int:
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM DEMOTABLE")
                row = cursor.fetchone()
                return int(row[0]) if row else -1
    except Exception:
        return -1
