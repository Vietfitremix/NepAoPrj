import asyncio
from app.ai.gemini import GeminiClient
from app.core.config import get_settings

s = get_settings()
print("API Key:", s.gemini_api_key)
print("Model:", s.gemini_model)
client = GeminiClient(s)

async def test():
    try:
        schema = {"type": "OBJECT", "properties": {"status": {"type": "STRING"}}, "required": ["status"]}
        res, ms = await client.call_json("Return JSON", "Hello", schema, 0.2)
        print("Gemini success:", res, ms)
    except Exception as e:
        print("Gemini error:", type(e), e)

asyncio.run(test())
