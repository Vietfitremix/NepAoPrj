-- Keep the imported PostgreSQL migration unchanged while running local H2 tests.
CREATE DOMAIN IF NOT EXISTS TIMESTAMPTZ AS TIMESTAMP WITH TIME ZONE;
