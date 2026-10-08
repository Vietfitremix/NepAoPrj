"""Điểm vào của service AI Nếp Áo.

Chạy local:  uvicorn app.main:app --reload --port 8000
Tài liệu API: http://localhost:8000/ai/docs   ·   Giao diện thử: http://localhost:8000/ai/playground
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.ai import GeminiClient
from app.api.routers import admin, backend, catalog, dev, stylist
from app.catalog import Catalog, CatalogStore
from app.core.config import get_settings
from app.engine import InvalidOutfit
from app.services.stylist import StylistService
from app.storage.cache import MemoryCache, PostgresCache, load_demo_cache
from app.storage.call_log import MemoryCallLog, PostgresCallLog
from app.storage.rate_limit import RateLimiter

WEB_DIR = Path(__file__).parent / "web"


@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    pool = None
    if s.use_postgres and not s.backend_compat_only:
        from app.storage.db import create_pool
        pool = await create_pool(s.database_url)

    catalogs = CatalogStore(s, pool)
    if s.backend_compat_only:
        catalogs._catalog = Catalog({}, {}, {}, {}, {}, [], {}, version="backend-request")
    else:
        await catalogs.reload()
    pinned = load_demo_cache(s.data_dir)
    cache = PostgresCache(pool, s.cache_ttl_s, pinned) if pool else MemoryCache(s.cache_ttl_s, pinned)
    call_log = PostgresCallLog(pool) if pool else MemoryCallLog()

    app.state.service = StylistService(s, catalogs, GeminiClient(s), cache, call_log,
                                       RateLimiter(s.rate_limit_per_min))
    yield
    if pool:
        await pool.close()


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(title="Nếp Áo – AI service", version="0.1.0", lifespan=lifespan,
                  docs_url="/ai/docs", openapi_url="/ai/openapi.json", redoc_url=None)
    app.add_middleware(CORSMiddleware, allow_origins=s.cors_origins, allow_methods=["*"], allow_headers=["*"])

    @app.exception_handler(InvalidOutfit)
    async def invalid_outfit(_: Request, exc: InvalidOutfit):
        return JSONResponse(status_code=422, content={"code": "INVALID_OUTFIT", "message": str(exc)})

    app.include_router(backend.router, prefix="/ai")
    for r in (catalog.router, stylist.router, admin.router):
        app.include_router(r, prefix="/ai")

    if s.backend_compat_only:
        @app.middleware("http")
        async def integration_mode(request: Request, call_next):
            if request.url.path in ("/ai/quiz", "/ai/stylist", "/ai/evaluate", "/ai/review", "/ai/explain") or request.url.path.startswith(("/ai/admin/", "/ai/dev/")):
                return JSONResponse(status_code=503, content={"detail": "Native catalog unavailable in BACKEND_COMPAT_ONLY mode; use /ai/recommendations and /ai/remix via Spring."})
            return await call_next(request)

    if s.enable_dev_routes:
        app.include_router(dev.router, prefix="/ai")
        if s.figure_dir.exists():
            app.mount("/ai/figure", StaticFiles(directory=s.figure_dir), name="figure")

        @app.get("/ai/playground", include_in_schema=False)
        def playground():
            return FileResponse(WEB_DIR / "playground.html")

    return app


app = create_app()
