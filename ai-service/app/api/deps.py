"""Dependency dùng chung cho router: lấy service, IP người dùng, kiểm tra token admin."""
from fastapi import Header, HTTPException, Request

from app.core.config import get_settings
from app.services.stylist import StylistService


def get_service(request: Request) -> StylistService:
    return request.app.state.service


def client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")          # Caddy gắn header này khi đứng trước service
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def require_admin(x_admin_token: str = Header(default="")) -> None:
    if x_admin_token != get_settings().admin_token:
        raise HTTPException(status_code=401, detail="Sai X-Admin-Token")
