"""Điều phối pipeline AI theo workflow:

① quiz()        : câu hỏi bối cảnh cho giao diện
② stylist()     : câu trả lời quiz (+/- câu gõ) -> bối cảnh -> ứng viên hợp lệ -> Gemini chọn 3 bộ
③ evaluate()    : chấm luật + màu theo bối cảnh mỗi lần đổi đồ trong studio (không gọi Gemini)
④ review()      : nút "Hỏi stylist" -> nhận xét bộ đang mặc theo bối cảnh + 2 phương án nâng cấp + kết luận
   explain_one(): lời nhận xét cho 1 bộ (dùng riêng khi cần)
"""
import hashlib
import json

from app.ai import AIError, GeminiClient, explain, select_outfits, understand
from app.catalog import CatalogStore
from app.engine import candidate_outfits, count_levels, score_outfit, suggest_alternatives, validate_outfit
from app.models import (
    ClarifyResponse, EvaluateResponse, ExplainResponse, Intent, OutfitsResponse, OutfitState, Override,
    QuizAnswer, ReviewAlternative, ReviewResponse, StylistOutfit,
)
from app.storage.cache import MemoryCache, cache_key

from .context import build_context, build_quiz


class _DisabledGemini(GeminiClient):
    """Dùng khi IP vượt giới hạn: mọi lần gọi đều rơi về dự phòng."""

    async def call_json(self, *a, **kw):
        raise AIError("RATE_LIMITED")


def _ctx_for(state: OutfitState, ctx: Intent | None) -> Intent:
    """Bối cảnh dùng để chấm: lấy từ quiz nếu có, luôn đồng bộ dịp/phong cách với bộ đồ đang mặc."""
    base = ctx.model_copy() if ctx else Intent()
    base.occasion, base.style = state.occasion, state.style
    if state.gender in ("nu", "nam"):
        base.gender = state.gender
    return base


def verdict_of(evals) -> tuple[str, str]:
    lv = count_levels(evals)
    n = lv["risk"] + lv["consider"]
    if n == 0:
        return "hop", "Hợp bối cảnh"
    return "nen_chinh", f"Nên chỉnh {n} điểm" if n > 1 else "Nên chỉnh 1 điểm"


class StylistService:
    def __init__(self, settings, catalogs: CatalogStore, gemini: GeminiClient, cache, call_log, limiter):
        self.settings = settings
        self.catalogs = catalogs
        self.gemini = gemini
        self.cache = cache
        self.review_cache = MemoryCache(ttl_s=3600, max_items=300)    # bộ đồ + bối cảnh không đổi -> không gọi lại
        self.log = call_log
        self.limiter = limiter
        self._disabled = _DisabledGemini(settings)

    @property
    def catalog(self):
        return self.catalogs.get()

    def _gemini_for(self, ip: str | None) -> GeminiClient:
        if ip and not self.limiter.allow(ip):
            return self._disabled
        return self.gemini

    def _build(self, outfit_id: str, state: OutfitState, ctx: Intent | None = None) -> StylistOutfit:
        _, evals, color = score_outfit(state, self.catalog, ctx)
        return StylistOutfit(outfitId=outfit_id, state=state, evaluations=evals, color=color)

    # ------------------------------------------------------------------ /ai/quiz
    def quiz(self):
        return build_quiz(self.catalog)

    # ------------------------------------------------------------------ /ai/stylist
    async def stylist(self, text: str | None, answers: list[QuizAnswer], override: Override | None,
                      ip: str | None = None):
        ov = override.model_dump(exclude_none=True) if override else {}
        key = cache_key((text or "") + json.dumps([a.model_dump() for a in answers], ensure_ascii=False,
                                                  sort_keys=True), ov)
        cached = await self.cache.get(key)
        if cached:
            return {**cached, "source": "cache"}

        gemini = self._gemini_for(ip)
        cat = self.catalog
        intent, src_understand = await build_context(answers, text, cat, gemini, self.log)
        intent = intent.model_copy(update=ov)
        if ov.get("occasion"):
            intent.needsClarification = None

        if not intent.occasion:
            clar = intent.needsClarification
            return ClarifyResponse(question=clar.question, options=clar.options, intent=intent,
                                   source=src_understand or "fallback").model_dump()

        candidates = [self._build(f"c{i + 1}", s, intent) for i, s in enumerate(candidate_outfits(intent, cat))]
        outfits, src_select = await select_outfits(candidates, intent, cat, gemini, user_request=text, log=self.log)
        source = "gemini" if "gemini" in (src_understand, src_select) else "fallback"
        resp = OutfitsResponse(intent=intent, outfits=outfits, source=source).model_dump()
        if source == "gemini":                        # chỉ cache kết quả có AI, để lần sau thử lại Gemini
            await self.cache.set(key, text or "", resp, source)
        return resp

    # ------------------------------------------------------------------ /ai/evaluate
    def evaluate(self, state: OutfitState, ctx: Intent | None = None) -> EvaluateResponse:
        validate_outfit(state, self.catalog)
        _, evals, color = score_outfit(state, self.catalog, _ctx_for(state, ctx))
        return EvaluateResponse(evaluations=evals, color=color)

    # ------------------------------------------------------------------ /ai/explain
    async def explain_one(self, state: OutfitState, ctx: Intent | None, user_request: str | None,
                          ip: str | None = None):
        validate_outfit(state, self.catalog)
        c = _ctx_for(state, ctx)
        o = self._build("o1", state, c)
        source = await explain([o], self.catalog, self._gemini_for(ip), user_request=user_request,
                               log=self.log, ctx=c)
        return ExplainResponse(title=o.title, comment=o.comment, tip=o.tip,
                               evaluations=o.evaluations, color=o.color, source=source)

    # ------------------------------------------------------------------ /ai/review (nút "Hỏi stylist")
    async def review(self, state: OutfitState, ctx: Intent | None, user_request: str | None,
                     ip: str | None = None):
        validate_outfit(state, self.catalog)
        c = _ctx_for(state, ctx)
        key = hashlib.sha1((state.model_dump_json() + c.model_dump_json() + (user_request or "")).encode()).hexdigest()
        hit = await self.review_cache.get(key)
        if hit:
            return {**hit, "source": "cache"}

        cat = self.catalog
        current = self._build("current", state, c)
        alts: list[ReviewAlternative] = []
        for i, (alt_state, changes) in enumerate(suggest_alternatives(state, cat, c)):
            base = self._build(f"alt{i + 1}", alt_state, c)
            alts.append(ReviewAlternative(**base.model_dump(), changes=changes))
        changes = {a.outfitId: a.changes for a in alts}
        source = await explain([current, *alts], cat, self._gemini_for(ip), user_request=user_request,
                               prompt="review", changes=changes, log=self.log, ctx=c)
        verdict, verdict_text = verdict_of(current.evaluations)
        resp = ReviewResponse(verdict=verdict, verdictText=verdict_text, current=current,
                              alternatives=alts, source=source).model_dump()
        if source == "gemini":
            await self.review_cache.set(key, "", resp, source)
        return resp

    # ------------------------------------------------------------------ dev
    async def understand_only(self, text: str) -> tuple[Intent, str]:
        return await understand(text, self.catalog, self.gemini, self.log)
