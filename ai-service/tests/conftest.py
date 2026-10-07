import os

# Test luôn chạy không cần Gemini và Postgres
os.environ["AI_FORCE_FALLBACK"] = "true"
os.environ["DATABASE_URL"] = ""
os.environ["ENABLE_DEV_ROUTES"] = "true"
os.environ["RATE_LIMIT_PER_MIN"] = "1000"      # test gọi nhiều lần từ cùng một IP

import pytest  # noqa: E402

from app.catalog import load_from_json  # noqa: E402
from app.core.config import get_settings  # noqa: E402


@pytest.fixture(scope="session")
def catalog():
    return load_from_json(get_settings().data_dir)


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient

    from app.main import create_app
    with TestClient(create_app()) as c:
        yield c
