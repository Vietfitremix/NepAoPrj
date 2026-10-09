# Nếp Áo – AI service (Python + FastAPI + Gemini)

Service gợi ý và chấm Việt phục. Thiết kế chi tiết: PLAN-AI, PLAN-DEV (tài liệu nội bộ, không đưa lên git).

**Luật quyết định, AI diễn giải:** bộ luật trong catalog chấm 3 mức (Phù hợp / Nên cân nhắc / Dễ gây sai lệch), Gemini chỉ hiểu câu người dùng và viết lời nhận xét. Mỗi lần gọi Gemini đều có timeout và nhánh dự phòng.

## Chạy local (không cần Postgres, không cần API key)

Mặc định AI đọc catalog, quiz, thang điểm, checklist, luật, thẻ văn hóa và prompt từ
`ai-service/data/*.json` và `ai-service/prompts/` (có lịch sử git, thay đổi đi qua Pull Request).
`GET /ai/health` trả `catalogSource: json`. Tuỳ chọn: đặt `AI_CATALOG_SOURCE=postgres` khi chạy
`start-all.ps1` (hoặc đặt URI PostgreSQL vào `CATALOG_DATABASE_URL` trong `.env`, không dùng URL `jdbc:`)
để AI đọc cùng dữ liệu từ database của backend; khi đó phải giữ JSON và SQL đồng bộ.
Sau merge, chạy backend để Flyway áp dụng V16 rồi khởi động lại AI: V16 bổ sung
R40–R50, điểm thưởng màu yêu thích và 4 prompt mới, giữ nguồn tham khảo từ V11.
Cache và nhật ký runtime dùng bộ nhớ.

Windows với psycopg async cần SelectorEventLoop:

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --loop app.core.event_loop:selector_loop_factory --host 127.0.0.1 --port 8000
```

Các hướng dẫn JSON bên dưới dành cho chế độ chạy riêng khi cả hai biến
`CATALOG_DATABASE_URL` và `DATABASE_URL` đều trống. Thay đổi dữ liệu tập trung
bằng migration mới trong backend; không sửa migration đã áp dụng.
Trong phản hồi đánh giá, `sources` là URL thực; `sourceVerified` và `sourceNote`
phân biệt nguồn về trang phục với nhận định phối đồ chưa được kiểm chứng.

```bash
cd ai-service
python -m venv .venv
.venv\Scripts\activate              # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env              # điền GEMINI_API_KEY nếu có
uvicorn app.main:app --reload --port 8000
```

- Tài liệu API: http://localhost:8000/ai/docs
- Chưa có `GEMINI_API_KEY`: mọi bước tự chạy nhánh dự phòng (bắt từ khóa + câu viết sẵn).
- Chưa có `DATABASE_URL`: catalog đọc từ `data/*.json` bên trong ai-service, cache và log lưu trong bộ nhớ.

Ảnh/layer hiện có ở `../frontend/public/figure`, gồm bộ PNG nam/nữ bốn góc và họa tiết.
Công cụ tạo/kiểm tra hình nằm ở `../frontend/tools`. `DATA_DIR` mặc định là `ai-service/data`;
`FIGURE_DIR` mặc định là `frontend/public/figure`. Đặt `BACKEND_COMPAT_ONLY=false` để dùng
các endpoint native với catalog JSON này. Luồng Spring dùng `/ai/recommendations` và `/ai/remix`
với catalog do backend gửi trong request, không cần chia sẻ schema PostgreSQL.

## Phần ghép từ NepAoPrj

`engine/scoring.py` chấm 5 tiêu chí và trả `scoreCard` trong các phản hồi native
stylist/evaluate/review/explain. Trọng số, bảng xếp loại và trần điểm đọc từ
`data/scoring.json`; mỗi luật trong `data/rules.json` có trường `criterion`.
`GET /ai/catalog` cũng trả cấu hình scoring và checklist từ `data/checklist.json`.
Prompt trong `prompts/` dùng thẻ điểm đã chấm để diễn giải; schema Gemini cho remix
được chuyển đổi để loại bỏ các khóa không hỗ trợ.

Giữ nguyên hai chế độ: `BACKEND_COMPAT_ONLY=true` dùng catalog Spring gửi trong request
(vẫn cần `data/scoring.json`); `BACKEND_COMPAT_ONLY=false` bật cả API native và API
tích hợp. Với native local, để `DATABASE_URL` của AI trống để đọc JSON, không dùng URL
JDBC/database của Spring. Không cần chuyển thư mục `data` ra ngoài `ai-service`.

Giao diện website dùng frontend React hiện có. Bản merge này không khôi phục playground
HTML cũ hoặc bổ sung/sửa bộ asset.

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

## Chấm điểm phối đồ trong tủ đồ (quy định chung)

Bộ luật (`data/rules.json`, tổng 80 luật) xét **từng món** của tủ đồ, không chỉ áo và màu:
- **Quần/váy** (`bottom`): áo truyền thống (áo dài, ngũ thân, tứ thân, nhật bình, bà ba) đi với quần đùi/quần ngắn hoặc váy ngắn là
  luật nặng (trần điểm 35); chưa phối quần/váy là luật nặng (trần 40); quần ống bó hoặc quần lửng với áo dài bị trừ nhẹ.
  Quần suông/rộng/dài có luật cộng điểm theo loại áo; váy dài được xét riêng cho tứ thân, Nhật Bình và biến thể cách tân áo dài/ngũ thân.
- **Giày dép** (`shoes`): dép lê / dép Crocs với áo truyền thống ở dịp trang trọng (Tết, kỷ yếu, cưới hỏi, lễ chùa) là luật nặng
  (trần 45), ở dịp dạo phố chỉ bị trừ; giày thể thao hoặc đi chân trần ở cưới hỏi, đi chùa bị trừ.
- **Phụ kiện đường phố** (mũ lưỡi trai / cao bồi, tai nghe, ba lô, găng tay, dây xích) ở dịp trang trọng bị trừ; yếu tố hiện đại
  được tính tới 4 món trong tiêu chí "Cách tân".
- Bộ nào có luật nặng thì tổng điểm bị chặn ở mức thấp (dưới 60, xếp loại "Cần chỉnh") và nhận xét của stylist nói thẳng là chưa phù hợp.
- Luật về loại quần/váy và giày chỉ áp dụng khi biết hai trường này. Các luật màu, phụ kiện và ngữ cảnh vẫn dùng cho bộ gợi ý gốc của AI.

`context` nhận `weather`, `setting`, `timeOfDay`, `role` từ quiz, dùng chung cho chấm nhanh, nhận xét,
Remix và điểm khi lưu look. Không có câu trả lời thì luật phụ thuộc thông tin đó chưa áp dụng,
kể cả trong điều kiện phủ định. Màu dùng `colorHex` thực tế thay vì chỉ lấy màu gần nhất trong catalog.

Kết quả `/wardrobe-score` bổ sung `checks` (luật khớp, tiêu chí, điểm cơ bản, lý do, gợi ý, nguồn) và
`assessment` (tổng luật, số luật khớp, bối cảnh đã dùng/còn thiếu, chỉ số màu). Luật cùng `group` chỉ
đóng góp một lần. Các nguồn lịch sử không xác nhận ngưỡng điểm thẩm mỹ của ứng dụng.
Tra toàn bộ điều kiện, điểm và giới hạn tại [LUAT-DANH-GIA.md](../LUAT-DANH-GIA.md).

Endpoint cho tủ đồ: `POST /ai/wardrobe-score` (Cultural Check), `POST /ai/wardrobe-review` (stylist nhận xét + Recommend),
`POST /ai/wardrobe-remix` (phân tích bối cảnh, không làm theo nguyên văn yêu cầu không hợp, đưa các lựa chọn phù hợp hơn đã chấm lại bằng luật).

