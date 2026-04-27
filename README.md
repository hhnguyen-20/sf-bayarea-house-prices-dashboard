# SF Bay Area House Prices Dashboard (Vercel + Postgres)

Flask dashboard built on the SF Bay Area house prices dataset:

- Dataset: `data/sf_bayarea_house_prices.csv` (source: `https://raw.githubusercontent.com/csbfx/cs133/main/sf_bayarea_house_prices.csv`)
- Database: **Vercel Postgres** (no MySQL)
- Visualizations: **5+** charts (city medians, price distribution, scatter plots, bedroom pricing, ZIP-level map)

## Local setup

### 1) Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Set `POSTGRES_URL_NON_POOLING`

This app reads one of:

- `POSTGRES_URL_NON_POOLING` (preferred)
- `POSTGRES_URL`
- `DATABASE_URL`

### 3) Create schema + seed data

Run the schema in `sql/schema.sql` against your Postgres database (Vercel Postgres or local).

Then seed:

```bash
python3 scripts/seed_postgres.py
```

### 4) Run the app

```bash
python3 app.py
```

Open `http://localhost:5001`.

## Deploy to Vercel (with Vercel Postgres)

1. Create a Vercel project from this repo.
2. In Vercel, add **Storage → Postgres** (Vercel Postgres).
3. Ensure env vars are present (Vercel sets them automatically for Postgres).
4. Run `sql/schema.sql` on the Vercel Postgres database.
5. Seed the database using the Vercel-provided connection string (set `POSTGRES_URL_NON_POOLING` locally and run `python3 scripts/seed_postgres.py`).

The serverless entrypoint is `api/index.py` and routing is configured in `vercel.json`.