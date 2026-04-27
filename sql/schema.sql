-- SF Bay Area house prices (Vercel Postgres)
-- Run this against Vercel Postgres before seeding.

CREATE TABLE IF NOT EXISTS listings (
  id BIGSERIAL PRIMARY KEY,
  address TEXT,
  city TEXT,
  state TEXT,
  zip INTEGER,
  price INTEGER,
  beds INTEGER,
  baths NUMERIC,
  home_size NUMERIC,
  lot_size NUMERIC,
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  sf_time INTEGER,
  pa_time INTEGER,
  school_score NUMERIC,
  commute_time INTEGER
);

CREATE INDEX IF NOT EXISTS idx_listings_city ON listings (city);
CREATE INDEX IF NOT EXISTS idx_listings_zip ON listings (zip);
CREATE INDEX IF NOT EXISTS idx_listings_price ON listings (price);
CREATE INDEX IF NOT EXISTS idx_listings_home_size ON listings (home_size);

