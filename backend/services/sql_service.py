from pathlib import Path

from db import get_connection


SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def _split_sql_script(script_text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []

    for line in script_text.splitlines():
        if line.strip() == "/":
            statement = "\n".join(current).strip()
            if statement:
                blocks.append(statement)
            current = []
            continue
        current.append(line)

    trailing = "\n".join(current).strip()
    if trailing:
        blocks.append(trailing)

    return [stmt for stmt in blocks if stmt and not stmt.startswith("--")]


def execute_sql_file(file_name: str, auto_commit: bool = True) -> bool:
    file_path = SQL_DIR / file_name
    if not file_path.exists():
        return False

    script_text = file_path.read_text(encoding="utf-8")
    statements = _split_sql_script(script_text)

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                for statement in statements:
                    cursor.execute(statement)
            if auto_commit:
                conn.commit()
        return True
    except Exception:
        return False
