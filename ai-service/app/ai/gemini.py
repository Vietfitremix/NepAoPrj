"""Client Gemini: gọi model trả JSON theo schema, có timeout và báo lỗi thống nhất để rơi về fallback."""
import asyncio
import json
import time


class AIError(Exception):
    """Mọi lỗi khi gọi Gemini (chưa có key, timeout, 429, JSON hỏng...). Service bắt lỗi này để dùng fallback."""


class GeminiClient:
    def __init__(self, settings):
        self.settings = settings
        self._client = None

    @property
    def model(self) -> str:
        return self.settings.gemini_model

    def _get_client(self):
        if self._client is None:
            from google import genai          # import trễ: service vẫn chạy khi chưa cài google-genai
            self._client = genai.Client(api_key=self.settings.gemini_api_key)
        return self._client

    async def call_json(self, system: str, contents: str, schema: dict, temperature: float) -> tuple[dict, int]:
        """Trả về (dữ liệu JSON, thời gian ms). Ném AIError khi không dùng được Gemini."""
        s = self.settings
        if s.ai_force_fallback:
            raise AIError("FORCED_FALLBACK")
        if not s.gemini_api_key:
            raise AIError("NO_API_KEY")

        from google.genai import types
        cfg = dict(system_instruction=system, response_mime_type="application/json",
                   response_schema=schema, temperature=temperature,
                   # không dùng tự gọi hàm (function calling): tắt để SDK không in cảnh báo mỗi lần gọi
                   automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
        if s.ai_thinking_budget is not None:
            cfg["thinking_config"] = types.ThinkingConfig(thinking_budget=s.ai_thinking_budget)

        start = time.perf_counter()
        try:
            resp = await asyncio.wait_for(       # hủy hẳn request khi quá hạn
                self._get_client().aio.models.generate_content(
                    model=s.gemini_model, contents=contents, config=types.GenerateContentConfig(**cfg)),
                timeout=s.ai_timeout_s,
            )
        except asyncio.TimeoutError as e:
            raise AIError("TIMEOUT") from e
        except Exception as e:                   # 429, 503, lỗi mạng, key sai...
            raise AIError(f"{type(e).__name__}: {e}") from e
        ms = int((time.perf_counter() - start) * 1000)
        try:
            return json.loads(resp.text or ""), ms
        except (json.JSONDecodeError, TypeError) as e:
            raise AIError("BAD_JSON") from e
