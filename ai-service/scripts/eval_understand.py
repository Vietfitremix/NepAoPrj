"""Đo độ chính xác của bước Hiểu ý trên tests/understand_cases.json: Gemini và bắt từ khóa.

Chạy:  python -m scripts.eval_understand            (gọi Gemini nếu có GEMINI_API_KEY)
       python -m scripts.eval_understand --fallback (chỉ đo bắt từ khóa, không tốn lượt gọi)
"""
import asyncio
import json
import sys
import time

from app.ai import parse_by_keywords
from app.core.config import SERVICE_DIR


def check(intent, expect: dict) -> dict[str, bool]:
    out = {}
    for k, v in expect.items():
        if k == "needsClarification":
            out[k] = (intent.needsClarification is not None) == v
        elif isinstance(v, list):
            got = getattr(intent, k)
            out[k] = set(v) <= set(got) if v else not got
        else:
            out[k] = getattr(intent, k) == v
    return out


def summarize(rows: list[dict], key: str) -> dict:
    fields: dict[str, list[bool]] = {}
    for r in rows:
        for f, ok in r[key].items():
            fields.setdefault(f, []).append(ok)
    return {f: f"{sum(v)}/{len(v)}" for f, v in fields.items()} | {
        "allFieldsCorrect": f"{sum(all(r[key].values()) for r in rows)}/{len(rows)}"}


async def evaluate_cases(cases: list[dict], svc, use_gemini: bool = True) -> dict:
    rows, latencies = [], []
    for c in cases:
        kw = parse_by_keywords(c["text"], svc.catalog)
        row = {"text": c["text"], "keywords": check(kw, c["expect"])}
        if use_gemini:
            t = time.perf_counter()
            intent, source = await svc.understand_only(c["text"])
            latencies.append(time.perf_counter() - t)
            row["gemini"], row["source"] = check(intent, c["expect"]), source
        rows.append(row)
    result = {"keywords": summarize(rows, "keywords")}
    if use_gemini:
        result["gemini"] = summarize(rows, "gemini")
        result["avgSeconds"] = round(sum(latencies) / len(latencies), 2)
        result["usedFallback"] = sum(r["source"] == "fallback" for r in rows)
    result["failed"] = [{"text": r["text"], **{k: [f for f, ok in r[k].items() if not ok]
                                               for k in ("keywords", "gemini") if k in r}}
                        for r in rows if not all(r["keywords"].values()) or not all(r.get("gemini", {}).values())]
    return result


async def _main():
    from app.ai import GeminiClient
    from app.catalog import CatalogStore
    from app.core.config import get_settings
    from app.services.stylist import StylistService
    from app.storage.cache import MemoryCache
    from app.storage.call_log import MemoryCallLog
    from app.storage.rate_limit import RateLimiter

    s = get_settings()
    catalogs = CatalogStore(s)
    await catalogs.reload()
    svc = StylistService(s, catalogs, GeminiClient(s), MemoryCache(0), MemoryCallLog(), RateLimiter(10_000))
    cases = json.loads((SERVICE_DIR / "tests" / "understand_cases.json").read_text(encoding="utf-8"))
    use_gemini = "--fallback" not in sys.argv and s.gemini_enabled
    print(json.dumps(await evaluate_cases(cases, svc, use_gemini), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(_main())
