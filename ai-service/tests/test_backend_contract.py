"""Integration contract tests use only Spring reference data, not data/*.json."""
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


@pytest.fixture
def backend_client(monkeypatch):
    monkeypatch.setenv("BACKEND_COMPAT_ONLY", "true")
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        yield client
    get_settings.cache_clear()


@pytest.fixture
def payload():
    acc = {"code": "NON_LA", "name": "Nón lá", "type": "HEADWEAR"}
    return {"prompt": "Màu đỏ", "city": "Hanoi", "eventCode": "TET", "styleCode": "GEN_Z",
            "weather": {"temperature": 30, "condition": "CLEAR", "humidity": 80, "city": "Hanoi"},
            "culturalContext": {}, "referenceData": {
                "outfits": [{"outfit": {"code": code, "name": code}, "accessories": [acc]}
                            for code in ("AO_DAI", "AO_NGU_THAN", "NHAT_BINH")],
                "colors": [{"code": "RED", "name": "Đỏ", "hexCode": "#D32F2F"},
                           {"code": "WHITE", "name": "Trắng", "hexCode": "#FFFFFF"}],
                "styles": [{"code": "GEN_Z", "name": "Gen Z"}],
                "events": [{"code": "TET", "name": "Tết"}], "accessories": [acc]}}


def test_recommendations_use_backend_codes_without_native_data(backend_client, payload):
    response = backend_client.post("/ai/recommendations", json=payload)
    assert response.status_code == 200, response.text
    concepts = response.json()["concepts"]
    assert len(concepts) == 3
    assert len({c["outfitCode"] for c in concepts}) == 3
    assert all(c["colorCode"] == "RED" and c["styleCode"] == "GEN_Z" for c in concepts)
    assert all(0 <= c["matchScore"] <= 100 and c["reason"] for c in concepts)


def test_remix_applies_explicit_accessory_removal(backend_client, payload):
    payload["prompt"] = "Bỏ nón lá, đổi màu trắng"
    payload["currentLook"] = {"outfitCode": "AO_DAI", "colorCode": "RED", "styleCode": "GEN_Z",
                              "eventCode": "TET", "accessories": ["NON_LA"]}
    response = backend_client.post("/ai/remix", json=payload)
    assert response.status_code == 200, response.text
    changes = response.json()["changes"]
    assert changes["removeAccessories"] == ["NON_LA"]
    assert changes["colorCode"] == "WHITE"
    assert changes["addAccessories"] == []


def test_invalid_selection_rejected(backend_client, payload):
    payload["currentLook"] = {"outfitCode": "UNKNOWN", "colorCode": "RED", "styleCode": "GEN_Z",
                              "eventCode": "TET", "accessories": []}
    assert backend_client.post("/ai/remix", json=payload).status_code == 422


def test_request_catalogs_are_isolated(backend_client, payload):
    assert backend_client.post("/ai/recommendations", json=payload).status_code == 200
    payload["referenceData"]["styles"] = [{"code": "MINIMAL", "name": "Tối giản"}]
    assert backend_client.post("/ai/recommendations", json=payload).status_code == 422


def test_native_routes_report_missing_catalog(backend_client):
    assert backend_client.get("/ai/health").json()["catalogSource"] == "backend-request"
    assert backend_client.post("/ai/stylist", json={"text": "Tết"}).status_code == 503


def test_gemini_schema_has_no_unsupported_keys():
    from app.api.routers.backend import RemixOutput, gemini_schema
    text = str(gemini_schema(RemixOutput))
    assert "additionalProperties" not in text and "$ref" not in text and "$defs" not in text
