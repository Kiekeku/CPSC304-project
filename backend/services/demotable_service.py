import logging
import re
from datetime import date, datetime
from typing import Any

from db import get_connection
from services.sql_service import execute_sql_file

logger = logging.getLogger(__name__)
IDENTIFIER_RE = re.compile(r"^[A-Z][A-Z0-9_$#]*$")


def test_oracle_connection() -> bool:
    try:
        with get_connection():
            return True
    except Exception:
        logger.exception("Oracle connection test failed")
        return False


def _normalize_identifier(identifier: str) -> str:
    normalized = identifier.strip().upper()
    if not IDENTIFIER_RE.fullmatch(normalized):
        raise ValueError(f"Invalid identifier: {identifier}")
    return normalized


def _coerce_input_value(value: Any, data_type: str | None = None) -> Any:
    if isinstance(value, str):
        trimmed = value.strip()
        if not trimmed or trimmed.lower() in {"null", "none"}:
            return None

        normalized_type = (data_type or "").upper()
        if normalized_type in {"NUMBER", "INTEGER", "FLOAT"}:
            try:
                return float(trimmed) if "." in trimmed else int(trimmed)
            except ValueError:
                return trimmed

        if normalized_type == "DATE":
            candidate = trimmed.rstrip("Z").rstrip(".")
            try:
                if "T" in candidate:
                    return datetime.fromisoformat(candidate).date()
                return date.fromisoformat(candidate)
            except ValueError:
                return trimmed

        if normalized_type.startswith("TIMESTAMP"):
            candidate = trimmed.rstrip("Z").rstrip(".")
            try:
                return datetime.fromisoformat(candidate)
            except ValueError:
                return trimmed

        return trimmed
    return value


def _load_columns(cursor, table_name: str) -> list[dict[str, Any]]:
    cursor.execute(
        """
        SELECT column_name, data_type, nullable, column_id
        FROM user_tab_columns
        WHERE table_name = :table_name
        ORDER BY column_id
        """,
        {"table_name": table_name},
    )
    return [
        {
            "name": row[0],
            "dataType": row[1],
            "nullable": row[2] == "Y",
            "position": int(row[3]),
        }
        for row in cursor.fetchall()
    ]


def _load_primary_keys(cursor, table_name: str) -> list[str]:
    cursor.execute(
        """
        SELECT cols.column_name
        FROM user_constraints cons
        JOIN user_cons_columns cols
          ON cons.constraint_name = cols.constraint_name
         AND cons.table_name = cols.table_name
        WHERE cons.table_name = :table_name
          AND cons.constraint_type = 'P'
        ORDER BY cols.position
        """,
        {"table_name": table_name},
    )
    return [row[0] for row in cursor.fetchall()]


def _table_exists(cursor, table_name: str) -> bool:
    cursor.execute(
        "SELECT 1 FROM user_tables WHERE table_name = :table_name",
        {"table_name": table_name},
    )
    return cursor.fetchone() is not None


def list_tables() -> list[str]:
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT table_name FROM user_tables ORDER BY table_name")
                return [row[0] for row in cursor.fetchall()]
    except Exception:
        logger.exception("Failed to list tables")
        return []


def initiate_demotable() -> bool:
    schema_ok = execute_sql_file("demotable_schema.sql", auto_commit=True)
    if not schema_ok:
        return False

    seed_ok = execute_sql_file("demotable_seed.sql", auto_commit=True)
    return seed_ok


def get_table_metadata(table_name: str) -> dict[str, Any] | None:
    try:
        normalized_table = _normalize_identifier(table_name)
    except ValueError:
        return None

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                if not _table_exists(cursor, normalized_table):
                    return None
                columns = _load_columns(cursor, normalized_table)
                primary_key = _load_primary_keys(cursor, normalized_table)
                return {
                    "tableName": normalized_table,
                    "columns": columns,
                    "primaryKey": primary_key,
                }
    except Exception:
        logger.exception("Failed to load metadata for table %s", table_name)
        return None


def fetch_table_rows(table_name: str, limit: int = 200) -> list[list[Any]]:
    try:
        normalized_table = _normalize_identifier(table_name)
    except ValueError:
        return []

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                if not _table_exists(cursor, normalized_table):
                    return []
                cursor.execute(
                    f'SELECT * FROM "{normalized_table}" WHERE ROWNUM <= :limit',
                    {"limit": limit},
                )
                rows = cursor.fetchall()
                return [[*row] for row in rows]
    except Exception:
        logger.exception("Failed to fetch rows from table %s", table_name)
        return []


def insert_table_row(table_name: str, values: dict[str, Any]) -> tuple[bool, str]:
    try:
        normalized_table = _normalize_identifier(table_name)
    except ValueError:
        return False, "Invalid table name."

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                if not _table_exists(cursor, normalized_table):
                    return False, "Table not found."

                columns = _load_columns(cursor, normalized_table)
                column_names = [col["name"] for col in columns]
                column_types = {col["name"]: col["dataType"] for col in columns}

                candidate_columns = [col for col in column_names if col in values]
                if not candidate_columns:
                    return False, "No values were provided."

                bind_data = {}
                placeholders = []
                for idx, column in enumerate(candidate_columns):
                    bind_name = f"v{idx}"
                    bind_data[bind_name] = _coerce_input_value(values[column], column_types.get(column))
                    placeholders.append(f":{bind_name}")

                quoted_columns = ", ".join(f'"{column}"' for column in candidate_columns)
                placeholder_sql = ", ".join(placeholders)

                cursor.execute(
                    f'INSERT INTO "{normalized_table}" ({quoted_columns}) VALUES ({placeholder_sql})',
                    bind_data,
                )
            conn.commit()
            return True, "Row inserted successfully."
    except Exception as exc:
        logger.exception("Failed to insert row into table %s", table_name)
        return False, str(exc)


def update_table_row(
    table_name: str,
    keys: dict[str, Any],
    values: dict[str, Any],
) -> tuple[bool, str]:
    try:
        normalized_table = _normalize_identifier(table_name)
    except ValueError:
        return False, "Invalid table name."

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                if not _table_exists(cursor, normalized_table):
                    return False, "Table not found."

                columns = _load_columns(cursor, normalized_table)
                valid_columns = {col["name"] for col in columns}
                column_types = {col["name"]: col["dataType"] for col in columns}
                primary_keys = _load_primary_keys(cursor, normalized_table)
                if not primary_keys:
                    return False, "Table has no primary key."

                if any(pk not in keys for pk in primary_keys):
                    return False, "Primary key values are required."

                set_columns = [col for col in values if col in valid_columns]
                if not set_columns:
                    return False, "No updatable values were provided."

                set_parts = []
                where_parts = []
                bind_data: dict[str, Any] = {}

                for idx, column in enumerate(set_columns):
                    bind_name = f"s{idx}"
                    set_parts.append(f'"{column}" = :{bind_name}')
                    bind_data[bind_name] = _coerce_input_value(values[column], column_types.get(column))

                for idx, pk_column in enumerate(primary_keys):
                    bind_name = f"k{idx}"
                    where_parts.append(f'"{pk_column}" = :{bind_name}')
                    bind_data[bind_name] = _coerce_input_value(keys[pk_column], column_types.get(pk_column))

                cursor.execute(
                    f'UPDATE "{normalized_table}" '
                    f'SET {", ".join(set_parts)} '
                    f'WHERE {" AND ".join(where_parts)}',
                    bind_data,
                )
                updated = cursor.rowcount
            conn.commit()

            if updated <= 0:
                return False, "No rows matched the selected primary key."
            return True, "Row updated successfully."
    except Exception as exc:
        logger.exception("Failed to update table %s", table_name)
        return False, str(exc)


def delete_table_row(table_name: str, keys: dict[str, Any]) -> tuple[bool, str]:
    try:
        normalized_table = _normalize_identifier(table_name)
    except ValueError:
        return False, "Invalid table name."

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                if not _table_exists(cursor, normalized_table):
                    return False, "Table not found."

                primary_keys = _load_primary_keys(cursor, normalized_table)
                columns = _load_columns(cursor, normalized_table)
                column_types = {col["name"]: col["dataType"] for col in columns}
                if not primary_keys:
                    return False, "Table has no primary key."

                if any(pk not in keys for pk in primary_keys):
                    return False, "Primary key values are required."

                bind_data = {}
                where_parts = []
                for idx, pk_column in enumerate(primary_keys):
                    bind_name = f"k{idx}"
                    where_parts.append(f'"{pk_column}" = :{bind_name}')
                    bind_data[bind_name] = _coerce_input_value(keys[pk_column], column_types.get(pk_column))

                cursor.execute(
                    f'DELETE FROM "{normalized_table}" WHERE {" AND ".join(where_parts)}',
                    bind_data,
                )
                rows_affected = cursor.rowcount
            conn.commit()
            if rows_affected <= 0:
                return False, "No rows matched the selected primary key."
            return True, "Row deleted successfully."
    except Exception as exc:
        logger.exception("Failed to delete row from table %s", table_name)
        return False, str(exc)
