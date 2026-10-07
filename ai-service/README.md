# Nếp Áo – AI service (Python + FastAPI + Gemini)

Service gợi ý và chấm Việt phục. Thiết kế chi tiết: PLAN-AI, PLAN-DEV (tài liệu nội bộ, không đưa lên git).

**Luật quyết định, AI diễn giải:** bộ luật trong catalog chấm 3 mức (Phù hợp / Nên cân nhắc / Dễ gây sai lệch), Gemini chỉ hiểu câu người dùng và viết lời nhận xét. Mỗi lần gọi Gemini đều có timeout và nhánh dự phòng.

## Chạy local (không cần Postgres, không cần API key)

```bash
cd ai-service
python -m venv .venv
.venv\Scripts\activate              # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env              # điền GEMINI_API_KEY nếu có
uvicorn app.main:app --reload --port 8000
```

- Giao diện thử, chia 4 trang theo luồng: http://localhost:8000/ai/playground — `#/quiz` (bối cảnh) → `#/goi-y` (3 bộ) → `#/tuy-chinh` (studio) → `#/nhan-xet` (Hỏi stylist). Tiến trình lưu trong phiên, tải lại trang không mất.
- Tài liệu API: http://localhost:8000/ai/docs
- Chưa có `GEMINI_API_KEY`: mọi bước tự chạy nhánh dự phòng (bắt từ khóa + câu viết sẵn).
- Chưa có `DATABASE_URL`: catalog đọc từ `../data/*.json`, cache và log lưu trong bộ nhớ.

## Cấu trúc

```
app/
  main.py            khởi tạo app, nạp catalog, gắn router
  core/              cấu hình (biến môi trường)
  models/            Pydantic: bộ đồ, ý định, request/response
  catalog/           kho tri thức: nạp từ JSON hoặc PostgreSQL
  engine/            code thuần, không gọi AI: luật, chấm màu OKLCH, kiểm tra bộ đồ, ghép đồ
  ai/                Gemini: client, schema, prompt, hiểu ý, diễn giải, dự phòng
  services/          điều phối pipeline (cache → hiểu ý → ghép → chấm → diễn giải)
  storage/           Postgres pool, cache, nhật ký lượt gọi, giới hạn theo IP
  api/routers/       endpoint chia theo chức năng
  web/               trang playground (chỉ bật khi ENABLE_DEV_ROUTES=true)
prompts/             prompt dạng .txt (sửa lời không cần đụng code)
scripts/             đo độ chính xác, tạo cache demo
tests/               pytest + 20 câu test hiểu ý
```

## Endpoint

| Endpoint | Gọi Gemini | Việc |
| --- | --- | --- |
| `GET /ai/quiz` | Không | ① 8 câu hỏi bối cảnh (dịp, thời tiết, nơi, buổi, vai trò, phong cách, giới tính, màu) |
| `POST /ai/stylist` | 1–2 lần | ② Câu trả lời quiz (và/hoặc câu gõ nhanh) → Gemini chọn 3 bộ hợp bối cảnh, hoặc hỏi lại khi thiếu dịp |
| `POST /ai/evaluate` | Không | ③ Chấm luật (kể cả thời tiết, vai trò, hoạ tiết) + điểm màu – studio gọi mỗi lần đổi đồ |
| `POST /ai/review` | 1 lần, có cache | ④ Nút "Hỏi stylist": kết luận hợp bối cảnh / nên chỉnh, nhận xét, 2 phương án nâng cấp |
| `POST /ai/explain` | 1 lần | Lời nhận xét cho 1 bộ |
| `GET /ai/catalog`, `GET /ai/health` | Không | Dữ liệu catalog, trạng thái service |
| `POST /ai/admin/reload-catalog`, `GET /ai/admin/stats` | Không | Cần header `X-Admin-Token` |
| `POST /ai/dev/understand`, `POST /ai/dev/eval` | Có | Chỉ khi `ENABLE_DEV_ROUTES=true` |

## Kiểm thử và đo

```bash
pytest -q                                   # test engine, dự phòng, API (không cần Gemini)
python -m scripts.eval_understand --fallback # độ chính xác bắt từ khóa trên 20 câu
python -m scripts.eval_understand           # so sánh Gemini (cần API key)
python -m scripts.build_demo_cache          # tạo data/demo-cache.json cho 5 câu demo
```

## Trên VPS

Chạy bằng Docker trong `deploy/docker-compose.yml` (PLAN-DEV mục 9). Đặt `DATABASE_URL` trỏ tới Postgres bằng user `ai_user`, `ENABLE_DEV_ROUTES=false`. Bảng do Spring Boot tạo bằng Flyway; service này không tạo bảng.
