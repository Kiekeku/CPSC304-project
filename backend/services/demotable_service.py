import logging
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from db import (
    delete_predicted_gesture,
    get_connection,
    get_highly_active_users,
    get_transcript_counts_per_user,
    get_translated_words_for_transcript,
    get_user_with_highest_avg_fps,
    get_users_with_all_languages,
    insert_calibrated_definition,
    search_recordings,
    update_user_profile,
    view_user_attributes,
)
from services.sql_service import SQL_DIR, _normalize_statement, _split_sql_script, execute_sql_file

logger = logging.getLogger(__name__)
IDENTIFIER_RE = re.compile(r"^[A-Z][A-Z0-9_$#]*$")
DEFAULT_QUERY_BINDS = {
    "transcript_id": 1,
    "input_def_id": 99999,
    "input_user_id": 1,
    "input_gesture": "preview_gesture",
    "input_def_name": "Preview Definition",
    "input_description": "Docs preview row",
}

DOCS_QUERY_DEFINITIONS: list[dict[str, Any]] = [
    {
        "id": "delete_predicted_gesture",
        "title": "Delete Predicted Gesture",
        "description": "Deletes rows from Predicted_Gesture_Handmark2 by definition id.",
        "inputs": [
            {"name": "def_id", "label": "Definition ID", "type": "number", "required": True, "placeholder": "101"},
        ],
    },
    {
        "id": "view_user_attributes",
        "title": "View User Attributes",
        "description": "Returns selected columns for a single Calibrated_User row.",
        "inputs": [
            {"name": "user_id", "label": "User ID", "type": "number", "required": True, "placeholder": "1"},
            {
                "name": "selected_columns",
                "label": "Columns",
                "type": "csv",
                "required": True,
                "placeholder": "name, email",
                "helpText": "Allowed values: user_id, name, email, created_at",
            },
        ],
        "resultColumns": ["selected columns"],
    },
    {
        "id": "get_highly_active_users",
        "title": "Get Highly Active Users",
        "description": "Lists users with more than the supplied number of recordings.",
        "inputs": [
            {"name": "min_recordings", "label": "Minimum Recordings", "type": "number", "required": True, "placeholder": "3"},
        ],
        "resultColumns": ["USER_ID", "TOTAL_RECORDINGS"],
    },
    {
        "id": "update_user_profile",
        "title": "Update User Profile",
        "description": "Updates a user name, email, or both.",
        "inputs": [
            {"name": "user_id", "label": "User ID", "type": "number", "required": True, "placeholder": "1"},
            {"name": "new_name", "label": "New Name", "type": "text", "required": False, "placeholder": "Ada Lovelace"},
            {"name": "new_email", "label": "New Email", "type": "text", "required": False, "placeholder": "ada@example.com"},
        ],
    },
    {
        "id": "get_translated_words_for_transcript",
        "title": "Get Translated Words For Transcript",
        "description": "Returns translated words and confidence for one transcript.",
        "inputs": [
            {"name": "transcript_id", "label": "Transcript ID", "type": "number", "required": True, "placeholder": "1"},
        ],
        "resultColumns": ["INSTANCE_ID", "TRANSLATION", "TRANSLATION_CONFIDENCE", "TRANSCRIPT_ID"],
    },
    {
        "id": "get_transcript_counts_per_user",
        "title": "Get Transcript Counts Per User",
        "description": "Counts transcripts grouped by user.",
        "inputs": [],
        "resultColumns": ["USER_ID", "TRANSCRIPT_COUNT"],
    },
    {
        "id": "insert_calibrated_definition",
        "title": "Insert Calibrated Definition",
        "description": "Inserts a new Calibrated_Definition row.",
        "inputs": [
            {"name": "def_id", "label": "Definition ID", "type": "number", "required": True, "placeholder": "999"},
            {"name": "user_id", "label": "User ID", "type": "number", "required": True, "placeholder": "1"},
            {"name": "gesture", "label": "Gesture", "type": "text", "required": True, "placeholder": "hello"},
            {"name": "def_name", "label": "Definition Name", "type": "text", "required": True, "placeholder": "Greeting"},
            {"name": "description", "label": "Description", "type": "text", "required": True, "placeholder": "Example definition"},
        ],
    },
    {
        "id": "get_user_with_highest_avg_fps",
        "title": "Get User With Highest Avg FPS",
        "description": "Returns the user whose recordings have the highest average FPS.",
        "inputs": [],
        "resultColumns": ["USER_ID", "AVG_FPS"],
    },
    {
        "id": "get_users_with_all_languages",
        "title": "Get Users With All Languages",
        "description": "Finds users who have transcripts in every language present in the dataset.",
        "inputs": [],
        "resultColumns": ["USER_ID", "NAME"],
    },
    {
        "id": "search_recordings",
        "title": "Search Recordings",
        "description": "Runs a filtered recording search using the validated dynamic query builder.",
        "inputs": [
            {
                "name": "filters",
                "label": "Filters JSON",
                "type": "json",
                "required": True,
                "placeholder": '[{"logic":"AND","col":"fps","op":">","val":30}]',
                "helpText": "Provide a JSON array. Allowed cols: recording_id, recording_name, fps, recording_date, user_id",
            },
        ],
        "resultColumns": ["RECORDING_ID", "RECORDING_NAME", "FPS", "RECORDING_DATE"],
    },
]


def test_oracle_connection() -> bool:
    try:
        with get_connection():
            return True
    except Exception:
        logger.exception("Oracle connection test failed")
        return False


def list_docs_queries() -> list[dict[str, Any]]:
    return DOCS_QUERY_DEFINITIONS


def _serialize_scalar(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _serialize_rows(rows: Any) -> list[list[Any]]:
    serialized_rows: list[list[Any]] = []
    for row in rows or []:
        if isinstance(row, (list, tuple)):
            serialized_rows.append([_serialize_scalar(cell) for cell in row])
        else:
            serialized_rows.append([_serialize_scalar(row)])
    return serialized_rows


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_required_text(params: dict[str, Any], name: str) -> str:
    value = _normalize_text(params.get(name))
    if value is None:
        raise ValueError(f"Missing required input: {name}")
    return value


def _parse_number_param(params: dict[str, Any], name: str) -> int:
    raw_value = params.get(name)
    if raw_value is None or str(raw_value).strip() == "":
        raise ValueError(f"Missing required input: {name}")
    try:
        return int(str(raw_value).strip())
    except ValueError as exc:
        raise ValueError(f"Input '{name}' must be an integer.") from exc


def _parse_csv_param(params: dict[str, Any], name: str) -> list[str]:
    raw_value = params.get(name)
    if raw_value is None:
        raise ValueError(f"Missing required input: {name}")
    values = [part.strip() for part in str(raw_value).split(",") if part.strip()]
    if not values:
        raise ValueError(f"Input '{name}' must include at least one value.")
    return values


def _parse_json_param(params: dict[str, Any], name: str) -> Any:
    raw_value = params.get(name)
    if raw_value is None:
        raise ValueError(f"Missing required input: {name}")
    if isinstance(raw_value, (list, dict)):
        return raw_value
    try:
        return json.loads(str(raw_value))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Input '{name}' must be valid JSON.") from exc


def _format_query_result(query_id: str, result: Any, params: dict[str, Any]) -> dict[str, Any]:
    definition = next((item for item in DOCS_QUERY_DEFINITIONS if item["id"] == query_id), None)
    if isinstance(result, str):
        return {"queryId": query_id, "type": "message", "message": result}

    if isinstance(result, list):
        columns = (definition or {}).get("resultColumns") or []
        if query_id == "view_user_attributes":
            columns = [column.upper() for column in _parse_csv_param(params, "selected_columns")]
        return {
            "queryId": query_id,
            "type": "table",
            "columns": columns,
            "rows": _serialize_rows(result),
            "rowCount": len(result),
        }

    return {"queryId": query_id, "type": "message", "message": str(_serialize_scalar(result))}


def run_docs_query(query_id: str, params: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as conn:
        if query_id == "delete_predicted_gesture":
            result = delete_predicted_gesture(conn, _parse_number_param(params, "def_id"))
        elif query_id == "view_user_attributes":
            result = view_user_attributes(
                conn,
                _parse_number_param(params, "user_id"),
                _parse_csv_param(params, "selected_columns"),
            )
        elif query_id == "get_highly_active_users":
            result = get_highly_active_users(conn, _parse_number_param(params, "min_recordings"))
        elif query_id == "update_user_profile":
            result = update_user_profile(
                conn,
                _parse_number_param(params, "user_id"),
                new_name=_normalize_text(params.get("new_name")),
                new_email=_normalize_text(params.get("new_email")),
            )
        elif query_id == "get_translated_words_for_transcript":
            result = get_translated_words_for_transcript(conn, _parse_number_param(params, "transcript_id"))
        elif query_id == "get_transcript_counts_per_user":
            result = get_transcript_counts_per_user(conn)
        elif query_id == "insert_calibrated_definition":
            result = insert_calibrated_definition(
                conn,
                _parse_number_param(params, "def_id"),
                _parse_number_param(params, "user_id"),
                _parse_required_text(params, "gesture"),
                _parse_required_text(params, "def_name"),
                _parse_required_text(params, "description"),
            )
        elif query_id == "get_user_with_highest_avg_fps":
            result = get_user_with_highest_avg_fps(conn)
        elif query_id == "get_users_with_all_languages":
            result = get_users_with_all_languages(conn)
        elif query_id == "search_recordings":
            filters = _parse_json_param(params, "filters")
            if not isinstance(filters, list):
                raise ValueError("Input 'filters' must be a JSON array.")
            result = search_recordings(conn, filters)
        else:
            raise ValueError(f"Unknown query id: {query_id}")

    return _format_query_result(query_id, result, params)


def _normalize_identifier(identifier: str) -> str:
    normalized = identifier.strip().upper()
    if not IDENTIFIER_RE.fullmatch(normalized): 
        # only valid oracle identifier characters are allowed through
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


def run_demotable_queries_preview() -> list[dict[str, Any]]:
    file_path = Path(SQL_DIR) / "demotable_queries.sql"
    script_text = file_path.read_text(encoding="utf-8")
    statements = _split_sql_script(script_text)
    results: list[dict[str, Any]] = []

    with get_connection() as conn:
        with conn.cursor() as cursor:
            for index, statement in enumerate(statements, start=1):
                normalized = _normalize_statement(statement)
                upper = normalized.lstrip().upper()

                if not normalized:
                    continue

                if upper == "COMMIT" or upper == "ROLLBACK":
                    results.append(
                        {
                            "index": index,
                            "statement": normalized,
                            "type": upper,
                            "status": "skipped",
                            "message": f"{upper} skipped for preview mode.",
                        }
                    )
                    continue

                executable = normalized.replace("&attributes", "user_id, email, name")
                bind_names = {name.lower() for name in re.findall(r":([A-Za-z_][A-Za-z0-9_]*)", executable)}
                bind_values = {
                    bind_name: value
                    for bind_name, value in DEFAULT_QUERY_BINDS.items()
                    if bind_name.lower() in bind_names
                }

                try:
                    cursor.execute(executable, bind_values)
                    if cursor.description:
                        columns = [column[0] for column in cursor.description]
                        rows = cursor.fetchall()
                        results.append(
                            {
                                "index": index,
                                "statement": normalized,
                                "type": "SELECT",
                                "status": "success",
                                "columns": columns,
                                "rows": [[*row] for row in rows],
                                "rowCount": len(rows),
                                "binds": bind_values,
                            }
                        )
                    else:
                        statement_type = upper.split(None, 1)[0]
                        results.append(
                            {
                                "index": index,
                                "statement": normalized,
                                "type": statement_type,
                                "status": "success",
                                "rowCount": cursor.rowcount,
                                "binds": bind_values,
                            }
                        )
                except Exception as exc:
                    logger.exception("Failed to preview demotable query %s", index)
                    results.append(
                        {
                            "index": index,
                            "statement": normalized,
                            "type": upper.split(None, 1)[0],
                            "status": "error",
                            "message": str(exc),
                            "binds": bind_values,
                        }
                    )
        conn.rollback()

    return results


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
                    bind_data, # all values are bound separately via :v0, :v1, :v2 etc.
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
