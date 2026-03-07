import os
from contextlib import contextmanager
from pathlib import Path

import oracledb
from dotenv import load_dotenv

BACKEND_ENV_FILE = Path(__file__).resolve().parent / ".env"
ROOT_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

# Load root .env first, then allow backend/.env to override when present.
load_dotenv(ROOT_ENV_FILE)
load_dotenv(BACKEND_ENV_FILE, override=True)

_POOL = None


def get_db_config() -> dict:
    return {
        "user": os.getenv("ORACLE_USER"),
        "password": os.getenv("ORACLE_PASS"),
        "dsn": f"{os.getenv('ORACLE_HOST')}:{os.getenv('ORACLE_PORT')}/{os.getenv('ORACLE_DBNAME')}",
        "min": 1,
        "max": 3,
        "increment": 1,
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
    finally:
        _POOL.release(conn)
