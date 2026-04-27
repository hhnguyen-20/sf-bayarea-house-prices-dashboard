from flask import Flask, render_template, request

from db import query


def _filters_from_request(req):
    city = (req.args.get("city") or "").strip()
    min_price = req.args.get("min_price") or ""
    max_price = req.args.get("max_price") or ""
    beds = req.args.get("beds") or ""

    def _to_int(v):
        try:
            return int(v)
        except Exception:
            return None

    return {
        "city": city or None,
        "min_price": _to_int(min_price),
        "max_price": _to_int(max_price),
        "beds": _to_int(beds),
    }


def _where_clause(filters):
    where = ["1=1"]
    params = []

    if filters["city"]:
        where.append("city = %s")
        params.append(filters["city"])
    if filters["min_price"] is not None:
        where.append("price >= %s")
        params.append(filters["min_price"])
    if filters["max_price"] is not None:
        where.append("price <= %s")
        params.append(filters["max_price"])
    if filters["beds"] is not None:
        where.append("beds = %s")
        params.append(filters["beds"])

    return " AND ".join(where), params


def create_app():
    app = Flask(__name__)

    @app.get("/health")
    def health():
        try:
            n = query("SELECT COUNT(*)::int AS n FROM listings;")[0]["n"]
            return {"ok": True, "listings": n}
        except Exception as e:
            # Keep response safe (no secrets), but actionable.
            return {"ok": False, "error": str(e)}, 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        # Vercel often shows a generic 500; make it obvious what to fix.
        msg = str(e)
        print("Unhandled exception:", msg)
        return (
            render_template(
                "error.html",
                error=msg,
            ),
            500,
        )

    @app.route("/")
    def index():
        filters = _filters_from_request(request)
        where, params = _where_clause(filters)

        cities = query(
            """
            SELECT city, COUNT(*) AS n
            FROM listings
            WHERE city IS NOT NULL
            GROUP BY city
            ORDER BY n DESC, city ASC;
            """
        )

        summary = query(
            f"""
            SELECT
              COUNT(*)::int AS n_listings,
              percentile_cont(0.5) WITHIN GROUP (ORDER BY price) AS median_price,
              percentile_cont(0.5) WITHIN GROUP (ORDER BY home_size) AS median_home_size
            FROM listings
            WHERE {where};
            """,
            params,
        )[0]

        median_by_city = query(
            f"""
            SELECT
              city,
              COUNT(*)::int AS n,
              percentile_cont(0.5) WITHIN GROUP (ORDER BY price) AS median_price
            FROM listings
            WHERE {where} AND city IS NOT NULL AND price IS NOT NULL
            GROUP BY city
            ORDER BY median_price DESC
            LIMIT 15;
            """,
            params,
        )

        price_histogram = query(
            f"""
            WITH Buckets AS (
              SELECT
                CASE
                  WHEN price < 750000 THEN '< $750k'
                  WHEN price < 1000000 THEN '$750k–$1.0M'
                  WHEN price < 1500000 THEN '$1.0M–$1.5M'
                  WHEN price < 2000000 THEN '$1.5M–$2.0M'
                  WHEN price < 3000000 THEN '$2.0M–$3.0M'
                  ELSE '$3.0M+'
                END AS bucket,
                COUNT(*)::int AS n
              FROM listings
              WHERE {where} AND price IS NOT NULL
              GROUP BY 1
            ),
            Total AS (
              SELECT SUM(n)::numeric AS total FROM Buckets
            )
            SELECT bucket, n, ROUND(((n::numeric / NULLIF(t.total, 0)) * 100), 2) AS pct
            FROM Buckets b CROSS JOIN Total t
            ORDER BY
              CASE bucket
                WHEN '< $750k' THEN 1
                WHEN '$750k–$1.0M' THEN 2
                WHEN '$1.0M–$1.5M' THEN 3
                WHEN '$1.5M–$2.0M' THEN 4
                WHEN '$2.0M–$3.0M' THEN 5
                ELSE 6
              END;
            """,
            params,
        )

        scatter_price_vs_size = query(
            f"""
            SELECT
              price,
              home_size,
              beds,
              baths,
              city
            FROM listings
            WHERE {where}
              AND price IS NOT NULL
              AND home_size IS NOT NULL
            ORDER BY random()
            LIMIT 600;
            """,
            params,
        )

        avg_price_by_beds = query(
            f"""
            SELECT
              beds,
              COUNT(*)::int AS n,
              ROUND(AVG(price))::int AS avg_price,
              percentile_cont(0.5) WITHIN GROUP (ORDER BY price) AS median_price
            FROM listings
            WHERE {where} AND beds IS NOT NULL AND price IS NOT NULL
            GROUP BY beds
            HAVING beds BETWEEN 0 AND 10
            ORDER BY beds ASC;
            """,
            params,
        )

        zip_map = query(
            f"""
            SELECT
              zip,
              COUNT(*)::int AS n,
              ROUND(AVG(price))::int AS avg_price,
              AVG(latitude) AS lat,
              AVG(longitude) AS lng
            FROM listings
            WHERE {where}
              AND zip IS NOT NULL
              AND price IS NOT NULL
              AND latitude IS NOT NULL
              AND longitude IS NOT NULL
            GROUP BY zip
            HAVING COUNT(*) >= 10
            ORDER BY n DESC
            LIMIT 250;
            """,
            params,
        )

        return render_template(
            "dashboard.html",
            cities=cities,
            filters=filters,
            summary=summary,
            median_by_city=median_by_city,
            price_histogram=price_histogram,
            scatter_price_vs_size=scatter_price_vs_size,
            avg_price_by_beds=avg_price_by_beds,
            zip_map=zip_map,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5001)