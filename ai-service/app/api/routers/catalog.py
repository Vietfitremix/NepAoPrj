"""Catalog cho giao diện thử và trạng thái service. (Bản chính thức cho frontend là GET /api/catalog của Spring Boot.)"""
from fastapi import APIRouter, Depends

from app.api.deps import get_service
from app.services.stylist import StylistService

router = APIRouter(tags=["catalog"])


@router.get("/health", summary="Trạng thái service")
def health(svc: StylistService = Depends(get_service)):
    s = svc.settings
    return {
        "ok": True,
        "catalogVersion": svc.catalog.version,
        "catalogSource": "postgres" if s.use_postgres else "json",
        "model": s.gemini_model,
        "gemini": "enabled" if s.gemini_enabled else ("forced_fallback" if s.ai_force_fallback else "no_api_key"),
    }


@router.get("/catalog", summary="Dữ liệu catalog (tên, màu, trang phục, phụ kiện, thẻ văn hóa)")
def catalog(svc: StylistService = Depends(get_service)):
    return svc.catalog.public_view()
