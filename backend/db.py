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
    finally:
        _POOL.release(conn)
