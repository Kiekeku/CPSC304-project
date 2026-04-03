import os
from contextlib import contextmanager
from pathlib import Path

import oracledb
from dotenv import load_dotenv

BACKEND_ENV_FILE = Path(__file__).resolve().parent / ".env"
ROOT_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(ROOT_ENV_FILE)
load_dotenv(BACKEND_ENV_FILE, override=True)

_POOL = None


def get_db_config() -> dict:
    pool_min = int(os.getenv("ORACLE_POOL_MIN", "1"))
    pool_max = int(os.getenv("ORACLE_POOL_MAX", "1"))
    pool_increment = int(os.getenv("ORACLE_POOL_INCREMENT", "1"))
    return {
        "user": os.getenv("ORACLE_USER"),
        "password": os.getenv("ORACLE_PASS"),
        "dsn": f"{os.getenv('ORACLE_HOST')}:{os.getenv('ORACLE_PORT')}/{os.getenv('ORACLE_DBNAME')}",
        "min": pool_min,
        "max": pool_max,
        "increment": pool_increment,
        "timeout": 60,
    }


def init_pool() -> None:
    global _POOL
    if _POOL is None:
        _POOL = oracledb.create_pool(**get_db_config())


def close_pool() -> None:
    global _POOL
    if _POOL is not None:
        _POOL.close(force=True)
        _POOL = None


@contextmanager
def get_connection():
    if _POOL is None:
        raise RuntimeError("Database pool has not been initialized")

    conn = _POOL.acquire()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        _POOL.release(conn)


def delete_predicted_gesture(connection, def_id):
    cursor = connection.cursor()
    query = "DELETE FROM Predicted_Gesture_Handmark2 WHERE def_id = :input_def_id"
    bind_vars = {"input_def_id": def_id}
    cursor.execute(query, bind_vars)
    connection.commit()
    return f"Deleted {cursor.rowcount} row(s)."


def view_user_attributes(connection, user_id, selected_columns):
    """
    selected_columns example: ["name", "email"]
    """
    if not selected_columns:
        return "No columns selected."

    ALLOWED_COLS = {"user_id", "name", "email", "created_at"} 
    safe_columns = []
    
    for col in selected_columns:
        clean_col = str(col).lower()
        if clean_col in ALLOWED_COLS:
            safe_columns.append(clean_col)
        else:
            raise ValueError(f"Security Alert: Invalid column requested -> {col}")

    cursor = connection.cursor()
    columns_string = ", ".join(safe_columns)
    
    query = f"SELECT {columns_string} FROM Calibrated_User WHERE user_id = :input_user_id"
    bind_vars = {"input_user_id": user_id}
    
    cursor.execute(query, bind_vars)
    return cursor.fetchall()


def get_highly_active_users(connection, min_recordings):
    cursor = connection.cursor()
    query = """
        SELECT user_id, COUNT(recording_id) AS total_recordings
        FROM Created_Documented_Recording
        GROUP BY user_id
        HAVING COUNT(recording_id) > :input_min_recordings
    """
    bind_vars = {"input_min_recordings": min_recordings}
    cursor.execute(query, bind_vars)
    return cursor.fetchall()