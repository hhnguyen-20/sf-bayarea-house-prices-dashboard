import csv
import os

import psycopg


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
    url = postgres_url()
    if not url:
        raise SystemExit(
            "Missing POSTGRES_URL(_NON_POOLING) / DATABASE_URL. "
            "If you're using Vercel Postgres, set POSTGRES_URL_NON_POOLING."
        )

    csv_path = os.environ.get("CSV_PATH", "data/sf_bayarea_house_prices.csv")
    if not os.path.exists(csv_path):
        raise SystemExit(f"CSV not found: {csv_path}")

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

