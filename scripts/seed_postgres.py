import csv
import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import psycopg


def _sanitize_postgres_url(url: str) -> str:
    """
    Some Supabase pooler URLs include extra query params like `supa=...` which
    psycopg doesn't accept. Strip unknown params while keeping important ones
    (e.g. sslmode).
    """
    try:
        parts = urlsplit(url)
        q = [(k, v) for (k, v) in parse_qsl(parts.query, keep_blank_values=True) if k.lower() != "supa"]
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q), parts.fragment))
    except Exception:
        return url


def postgres_url() -> str:
    return (
        os.environ.get("SUPABASE_DB_URL")
        or os.environ.get("SUPABASE_DATABASE_URL")
        or os.environ.get("POSTGRES_URL_NON_POOLING")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("DATABASE_URL")
        or ""
    )


def main():
    url = _sanitize_postgres_url(postgres_url())
    if not url:
        raise SystemExit(
            "Missing database connection string. Set SUPABASE_DB_URL (recommended) "
            "or DATABASE_URL."
        )

    csv_path = os.environ.get("CSV_PATH", "").strip()
    candidates = [
        csv_path if csv_path else None,
        "data/cleaned_sf_bayarea_house_prices.csv",
        "data/sf_bayarea_house_prices.csv",
        "sf_bayarea_house_prices.csv",
    ]
    csv_path = next((p for p in candidates if p and os.path.exists(p)), None)
    if not csv_path:
        raise SystemExit(
            "CSV not found. Set CSV_PATH or place the dataset at one of:\n"
            "- data/cleaned_sf_bayarea_house_prices.csv\n"
            "- data/sf_bayarea_house_prices.csv\n"
            "- sf_bayarea_house_prices.csv"
        )

    sslmode = os.environ.get("PGSSLMODE") or ("disable" if ("localhost" in url or "127.0.0.1" in url) else "require")
    with psycopg.connect(url, sslmode=sslmode) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE listings;")

            with open(csv_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = []
                for r in reader:
                    rows.append(
                        (
                            r.get("Address") or None,
                            r.get("City") or None,
                            r.get("State") or None,
                            int(r["Zip"]) if r.get("Zip") else None,
                            int(float(r["Price"])) if r.get("Price") else None,
                            int(float(r["Beds"])) if r.get("Beds") else None,
                            float(r["Baths"]) if r.get("Baths") else None,
                            float(r["Home size"]) if r.get("Home size") else None,
                            float(r["Lot size"]) if r.get("Lot size") else None,
                            float(r["Latitude"]) if r.get("Latitude") else None,
                            float(r["Longitude"]) if r.get("Longitude") else None,
                            int(float(r["SF time"])) if r.get("SF time") else None,
                            int(float(r["PA time"])) if r.get("PA time") else None,
                            float(r["School score"]) if r.get("School score") else None,
                            int(float(r["Commute time"])) if r.get("Commute time") else None,
                        )
                    )

                cur.executemany(
                    """
                    INSERT INTO listings (
                      address, city, state, zip, price, beds, baths, home_size, lot_size,
                      latitude, longitude, sf_time, pa_time, school_score, commute_time
                    )
                    VALUES (
                      %s, %s, %s, %s, %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, %s
                    );
                    """,
                    rows,
                )

        conn.commit()

    print(f"Seeded {len(rows)} rows into listings.")


if __name__ == "__main__":
    main()

