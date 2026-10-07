"""Giữ catalog đang dùng và cho phép nạp lại khi Spring Boot cập nhật dữ liệu."""
from .catalog import Catalog
from .sources import load_from_json, load_from_postgres


class CatalogStore:
    def __init__(self, settings, pool=None):
        self._settings = settings
        self._pool = pool
        self._catalog: Catalog | None = None

    async def reload(self) -> Catalog:
        if self._pool is not None:
            self._catalog = await load_from_postgres(self._pool, self._settings.data_dir)
        else:
            self._catalog = load_from_json(self._settings.data_dir)
        return self._catalog

    def get(self) -> Catalog:
        if self._catalog is None:
            raise RuntimeError("Catalog chưa được nạp")
        return self._catalog


__all__ = ["Catalog", "CatalogStore", "load_from_json", "load_from_postgres"]
