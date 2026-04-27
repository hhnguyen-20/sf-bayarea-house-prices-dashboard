import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import psycopg
from psycopg.rows import dict_row


def _sanitize_postgres_url(url: str) -> str:
    # Supabase pooler URLs sometimes include `supa=...` which psycopg rejects.
    try:
        parts = urlsplit(url)
        q = [(k, v) for (k, v) in parse_qsl(parts.query, keep_blank_values=True) if k.lower() != "supa"]
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q), parts.fragment))
    except Exception:
        return url


def _postgres_url() -> str:
    """
    Connection string precedence:
    - Supabase (commonly set by integrations / users)
      - SUPABASE_DB_URL
      - SUPABASE_DATABASE_URL
    - Vercel Postgres
      - POSTGRES_URL
      - POSTGRES_URL_NON_POOLING (recommended for scripts / long ops)
    - Generic
      - DATABASE_URL
    """
    return (
        os.environ.get("SUPABASE_DB_URL")
        or os.environ.get("SUPABASE_DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_URL_NON_POOLING")
        or os.environ.get("DATABASE_URL")
        or ""
    )


def get_connection():
    url = _sanitize_postgres_url(_postgres_url())
    if not url:
        raise RuntimeError(
            "Missing Postgres connection string. Set SUPABASE_DB_URL (Supabase), "
            "POSTGRES_URL (Vercel Postgres), or DATABASE_URL."
        )
    sslmode = os.environ.get("PGSSLMODE") or os.environ.get("POSTGRES_SSLMODE")
    if not sslmode:
        # Supabase + hosted Postgres requires SSL; local Postgres often doesn't.
        sslmode = "disable" if ("localhost" in url or "127.0.0.1" in url) else "require"
    return psycopg.connect(url, row_factory=dict_row, sslmode=sslmode)


def query(sql: str, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()