"""Pool kết nối PostgreSQL (chỉ tạo khi có DATABASE_URL). User ai_user: SELECT schema catalog, ghi schema ai."""


async def create_pool(database_url: str):
    from psycopg_pool import AsyncConnectionPool   # import trễ: chạy local không cần cài psycopg

    pool = AsyncConnectionPool(database_url, min_size=1, max_size=5, open=False,
                               kwargs={"autocommit": True})
    await pool.open(wait=True, timeout=10)
    return pool
