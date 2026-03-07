import logging
from pathlib import Path

import oracledb

from db import get_connection


SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
logger = logging.getLogger(__name__)


def _split_sql_script(script_text: str) -> list[str]:
    statements: list[str] = []
    buffer: list[str] = []
    in_single_quote = False
    in_plsql_block = False

    def flush_buffer() -> None:
        statement = "".join(buffer).strip()
        buffer.clear()
        if statement and not statement.startswith("--"):
            statements.append(statement)

    for raw_line in script_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not buffer and (not stripped or stripped.startswith("--")):
            continue

        if in_plsql_block and stripped == "/":
            flush_buffer()
            in_plsql_block = False
            continue

        buffer.append(line + "\n")

        if not in_plsql_block and not in_single_quote:
            upper = stripped.upper()
            if upper.startswith("BEGIN") or upper.startswith("DECLARE"):
                in_plsql_block = True
                continue

        found_statement_terminator = False
        i = 0
        while i < len(line):
            if not in_single_quote and i + 1 < len(line) and line[i : i + 2] == "--":
                break
            char = line[i]
            if char == "'":
                if i + 1 < len(line) and line[i + 1] == "'":
                    i += 2
                    continue
                in_single_quote = not in_single_quote
            elif char == ";" and not in_single_quote:
                found_statement_terminator = True
            i += 1

        if in_plsql_block or in_single_quote:
            continue

        if found_statement_terminator:
            flush_buffer()

    if buffer:
        flush_buffer()

    return statements


def _normalize_statement(statement: str) -> str:
    cleaned_lines: list[str] = []
    for raw_line in statement.splitlines():
        line = raw_line
        in_single_quote = False
        i = 0
        while i < len(line):
            if not in_single_quote and i + 1 < len(line) and line[i : i + 2] == "--":
                line = line[:i]
                break
            if line[i] == "'":
                if i + 1 < len(line) and line[i + 1] == "'":
                    i += 2
                    continue
                in_single_quote = not in_single_quote
            i += 1
        cleaned_lines.append(line)

    trimmed = "\n".join(cleaned_lines).strip()
    upper = trimmed.upper()

    if upper.startswith("BEGIN") or upper.startswith("DECLARE"):
        return trimmed

    return trimmed[:-1].rstrip() if trimmed.endswith(";") else trimmed


def _is_ignorable_error(statement: str, exc: Exception) -> bool:
    upper = statement.strip().upper()
    if not upper.startswith("DROP TABLE"):
        return False

    if isinstance(exc, oracledb.DatabaseError) and exc.args:
        error_obj = exc.args[0]
        if getattr(error_obj, "code", None) == 942:
            return True

    return "ORA-00942" in str(exc)


def execute_sql_file(file_name: str, auto_commit: bool = True) -> bool:
    file_path = SQL_DIR / file_name
    if not file_path.exists():
        logger.error("SQL file not found: %s", file_path)
        return False

    script_text = file_path.read_text(encoding="utf-8")
    statements = _split_sql_script(script_text)

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                for statement in statements:
                    normalized = _normalize_statement(statement)
                    try:
                        cursor.execute(normalized)
                    except Exception as exc:
                        if _is_ignorable_error(normalized, exc):
                            logger.info(
                                "Ignoring missing table during drop in '%s': %s",
                                file_name,
                                normalized[:120],
                            )
                            continue
                        logger.error(
                            "Failed SQL statement in '%s' (truncated): %s",
                            file_name,
                            normalized[:300],
                        )
                        raise
            if auto_commit:
                conn.commit()
        return True
    except Exception:
        logger.exception("Failed to execute SQL file '%s'", file_name)
        return False
