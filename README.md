# SF Bay Area House Prices Dashboard (Vercel + Supabase)

Flask dashboard built on the SF Bay Area house prices dataset:

- Dataset: `data/sf_bayarea_house_prices.csv` (source: `https://raw.githubusercontent.com/csbfx/cs133/main/sf_bayarea_house_prices.csv`)
- Database: **Supabase Postgres** (via Vercel + Supabase integration)
- Visualizations: **5+** charts (city medians, price distribution, scatter plots, bedroom pricing, ZIP-level map)

## Local setup

### 1) Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Set a database connection string

This app reads one of:

- `SUPABASE_DB_URL` (recommended)
- `SUPABASE_DATABASE_URL`
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

## Deploy to Vercel (with Supabase)

1. Create a Vercel project from this repo.
2. Connect the project to Supabase (Vercel integration or by setting env vars).
3. Ensure your connection string is present as `SUPABASE_DB_URL` (or `DATABASE_URL`).
4. Run `sql/schema.sql` on the Supabase database.
5. Seed using that same connection string and run `python3 scripts/seed_postgres.py`.

The serverless entrypoint is `api/index.py` and routing is configured in `vercel.json`.