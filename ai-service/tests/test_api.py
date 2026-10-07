"""Gọi thật các endpoint qua TestClient, ở chế độ không có Gemini (nhánh dự phòng)."""

STATE = {"garment": "ao_ngu_than", "gender": "nu", "occasion": "ky_yeu", "style": "pastel",
         "colors": {"main": "hong_dao", "bottom": "trang_nga"}, "accessories": ["sneaker"]}


def test_health(client):
    r = client.get("/ai/health").json()
    assert r["ok"] and r["catalogSource"] == "json" and r["gemini"] == "forced_fallback"


def test_stylist_returns_three_outfits_with_comments(client):
    r = client.post("/ai/stylist", json={"text": "lớp mình chụp kỷ yếu, muốn nhẹ nhàng, thích đi sneaker"}).json()
    assert r["kind"] == "outfits" and r["source"] == "fallback"
    assert len(r["outfits"]) == 3
    for o in r["outfits"]:
        assert o["title"] and o["comment"] and o["tip"]
        assert 0 <= o["color"]["score"] <= 100


def test_stylist_asks_when_occasion_unknown(client):
    r = client.post("/ai/stylist", json={"text": "muốn mặc gì đó cho đẹp"}).json()
    assert r["kind"] == "clarify" and len(r["options"]) >= 3


def test_stylist_override_occasion(client):
    r = client.post("/ai/stylist", json={"text": "muốn mặc gì đó cho đẹp", "override": {"occasion": "tet"}}).json()
    assert r["kind"] == "outfits" and all(o["state"]["occasion"] == "tet" for o in r["outfits"])


def test_evaluate(client):
    r = client.post("/ai/evaluate", json={"state": STATE}).json()
    assert any(e["id"] == "R07" and e["level"] == "consider" for e in r["evaluations"])


def test_evaluate_rejects_unknown_codes(client):
    bad = {**STATE, "accessories": ["kiem_si"]}
    r = client.post("/ai/evaluate", json={"state": bad})
    assert r.status_code == 422 and r.json()["code"] == "INVALID_OUTFIT"


def test_explain_and_review(client):
    e = client.post("/ai/explain", json={"state": STATE}).json()
    assert e["comment"] and e["source"] == "fallback"
    rv = client.post("/ai/review", json={"state": STATE, "userRequest": "kỷ yếu"}).json()
    assert rv["current"]["comment"] and isinstance(rv["alternatives"], list)
    for a in rv["alternatives"]:
        assert a["changes"] and a["comment"]


def test_admin_requires_token(client):
    assert client.post("/ai/admin/reload-catalog").status_code == 401
    ok = client.post("/ai/admin/reload-catalog", headers={"X-Admin-Token": "dev-admin-token"}).json()
    assert ok["ok"] and ok["counts"]["rules"] >= 4
