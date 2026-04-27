import os

import psycopg
from psycopg.rows import dict_row


def _postgres_url() -> str:
    """
    Vercel Postgres provides one of these at runtime:
    - POSTGRES_URL
    - POSTGRES_URL_NON_POOLING (recommended for scripts / long ops)
    - DATABASE_URL
    """
    return (
        os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_URL_NON_POOLING")
        or os.environ.get("DATABASE_URL")
        or ""
    )


def get_connection():
    url = _postgres_url()
    if not url:
        raise RuntimeError(
            "Missing Postgres connection string. Set POSTGRES_URL (Vercel Postgres) "
            "or DATABASE_URL."
        )
    sslmode = os.environ.get("PGSSLMODE") or os.environ.get("POSTGRES_SSLMODE")
    if not sslmode:
        # Vercel Postgres requires SSL in production; local Postgres often doesn't.
        sslmode = "disable" if ("localhost" in url or "127.0.0.1" in url) else "require"
    return psycopg.connect(url, row_factory=dict_row, sslmode=sslmode)


def query(sql: str, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()