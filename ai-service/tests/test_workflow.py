"""Test luồng: quiz → 3 bộ gợi ý (Gemini chọn) → studio chấm luật theo bối cảnh → nút Hỏi stylist."""
import json

import pytest

STATE = {"garment": "ao_dai", "gender": "nu", "occasion": "le_hoi_chua", "style": "truyen_thong",
         "colors": {"main": "trang_nga", "bottom": "trang_nga"}, "accessories": ["guoc"]}
RAIN = {"occasion": "le_hoi_chua", "weather": "mua", "setting": "ngoai_troi"}
MILD = {"occasion": "le_hoi_chua", "weather": "mat_me", "setting": "ngoai_troi"}


class FakeGemini:
    """Gemini giả: chọn 3 ứng viên đầu tiên khác kiểu áo, viết nhận xét có nhắc mọi luật được đưa vào."""
    model = "fake-gemini"

    def __init__(self):
        self.calls = 0

    async def call_json(self, system, contents, schema, temperature):
        self.calls += 1
        data = json.loads(contents) if contents.startswith("{") else {}

        def item(o):
            return {"outfitId": o["outfitId"], "title": "Bộ thử nghiệm", "comment": "Bộ này hợp bối cảnh của bạn.",
                    "tip": "Giữ nguyên nhé.", "ruleIds": [r["ruleId"] for r in o["rules"]]}
        if "candidates" in data:
            picks, seen = [], set()
            for c in data["candidates"]:
                if c["garment"] not in seen:
                    seen.add(c["garment"]); picks.append({**item(c), "whyChosen": "Hợp thời tiết và dịp."})
            return {"picks": picks[:3]}, 5
        if "outfits" in data:
            return {"outfits": [item(o) for o in data["outfits"]]}, 5
        raise RuntimeError("không dùng cho bước hiểu ý trong test này")


@pytest.fixture
def fake_gemini(client):
    svc = client.app.state.service
    real, fake = svc.gemini, FakeGemini()
    svc.gemini = fake
    yield fake
    svc.gemini = real


def ids(evals):
    return {e["id"] for e in evals}


# ---------------------------------------------------------------- ① quiz
def test_quiz_questions(client):
    qs = client.get("/ai/quiz").json()
    assert [q["id"] for q in qs][:5] == ["occasion", "weather", "setting", "timeOfDay", "role"]
    colors = next(q for q in qs if q["id"] == "colors")
    assert colors["type"] == "multi" and all(o["hex"] for o in colors["options"])
    assert all("placeholder" in q for q in qs)      # mỗi câu đều có ô gõ tự do


# ---------------------------------------------------------------- ② 3 bộ gợi ý
def test_stylist_from_quiz_choices_only(client):
    answers = [{"questionId": "occasion", "value": "tet"}, {"questionId": "weather", "value": "mua"},
               {"questionId": "setting", "value": "ngoai_troi"}, {"questionId": "gender", "value": "nu"}]
    r = client.post("/ai/stylist", json={"answers": answers}).json()
    assert r["kind"] == "outfits"
    assert r["intent"]["weather"] == "mua" and r["intent"]["setting"] == "ngoai_troi"
    assert len(r["outfits"]) == 3 and [o["outfitId"] for o in r["outfits"]] == ["o1", "o2", "o3"]
    assert all(o["whyChosen"] and o["comment"] for o in r["outfits"])
    assert len({o["state"]["garment"] for o in r["outfits"]}) == 3          # 3 kiểu áo khác nhau


def test_stylist_free_text_answer_is_understood(client):
    answers = [{"questionId": "occasion", "text": "đi hội làng cuối tuần, trời mưa phùn"}]
    r = client.post("/ai/stylist", json={"answers": answers}).json()
    assert r["kind"] == "outfits" and r["intent"]["occasion"] == "le_hoi_chua" and r["intent"]["weather"] == "mua"


def test_choice_wins_over_free_text(client):
    answers = [{"questionId": "occasion", "value": "ky_yeu", "text": "đi chùa"}]
    r = client.post("/ai/stylist", json={"answers": answers}).json()
    assert r["intent"]["occasion"] == "ky_yeu"


def test_stylist_asks_when_quiz_has_no_occasion(client):
    r = client.post("/ai/stylist", json={"answers": [{"questionId": "weather", "value": "nang_nong"}]}).json()
    assert r["kind"] == "clarify" and r["intent"]["weather"] == "nang_nong"


def test_stylist_requires_input(client):
    assert client.post("/ai/stylist", json={}).status_code == 422


def test_gemini_selects_three(client, fake_gemini):
    answers = [{"questionId": "occasion", "value": "dao_pho"}, {"questionId": "weather", "value": "nang_nong"}]
    r = client.post("/ai/stylist", json={"answers": answers}).json()
    assert r["source"] == "gemini" and fake_gemini.calls == 1                 # chỉ chọn đáp án -> 1 lượt gọi
    assert all(o["whyChosen"] == "Hợp thời tiết và dịp." for o in r["outfits"])


# ---------------------------------------------------------------- ③ studio: luật theo bối cảnh + hoạ tiết
def test_weather_rules_apply_only_with_context(client):
    with_rain = client.post("/ai/evaluate", json={"state": STATE, "context": RAIN}).json()
    without = client.post("/ai/evaluate", json={"state": STATE}).json()
    assert {"R61", "R24"} <= ids(with_rain["evaluations"])
    assert "R20" not in ids(with_rain["evaluations"])
    assert not ({"R20", "R61", "R24"} & ids(without["evaluations"]))


def test_pattern_validation_and_rule(client):
    bad = client.post("/ai/evaluate", json={"state": {**STATE, "pattern": "ca_ro"}})
    assert bad.status_code == 422
    st = {**STATE, "occasion": "dam_cuoi", "pattern": "cham_bi", "colors": {"main": "hong_dao", "bottom": "trang_nga"}}
    r = client.post("/ai/evaluate", json={"state": st}).json()
    assert "R28" in ids(r["evaluations"])


def test_role_rule(client):
    st = {**STATE, "garment": "nhat_binh", "occasion": "dam_cuoi", "colors": {"main": "vang_hoang", "bottom": "trang_nga"},
          "accessories": []}
    r = client.post("/ai/evaluate", json={"state": st, "context": {"role": "khach"}}).json()
    assert "R25" in ids(r["evaluations"])


# ---------------------------------------------------------------- ④ nút Hỏi stylist
def test_review_verdict_changes_with_context(client):
    rain = client.post("/ai/review", json={"state": STATE, "context": RAIN}).json()
    mild = client.post("/ai/review", json={"state": STATE, "context": MILD}).json()
    assert rain["verdict"] == "nen_chinh"
    rain_issues = [e for e in rain['current']['evaluations'] if e['level'] != 'ok']
    mild_issues = [e for e in mild['current']['evaluations'] if e['level'] != 'ok']
    assert len(rain_issues) > len(mild_issues)
    assert {"R61", "R24"} <= ids(rain['current']['evaluations'])
    assert not {"R61", "R24"} & ids(mild['current']['evaluations'])
    assert rain["current"]["comment"] != mild["current"]["comment"]


def test_review_is_cached_when_nothing_changed(client, fake_gemini):
    body = {"state": STATE, "context": RAIN}
    first = client.post("/ai/review", json=body).json()
    second = client.post("/ai/review", json=body).json()
    assert first["source"] == "gemini" and second["source"] == "cache" and fake_gemini.calls == 1
    changed = client.post("/ai/review", json={**body, "context": MILD}).json()     # đổi bối cảnh -> gọi lại
    assert changed["source"] == "gemini" and fake_gemini.calls == 2
