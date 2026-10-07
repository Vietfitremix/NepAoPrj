"""Endpoint quản trị (cần header X-Admin-Token): nạp lại catalog, xem thống kê lượt gọi AI."""
from fastapi import APIRouter, Depends

from app.api.deps import get_service, require_admin
from app.services.stylist import StylistService

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.post("/reload-catalog", summary="Nạp lại catalog (Spring Boot gọi sau khi seed dữ liệu)")
async def reload_catalog(svc: StylistService = Depends(get_service)):
    cat = await svc.catalogs.reload()
    return {"ok": True, "version": cat.version, "counts": cat.counts()}


@router.get("/stats", summary="Thống kê lượt gọi Gemini trong phiên chạy hiện tại")
async def stats(svc: StylistService = Depends(get_service)):
    return await svc.log.stats()
