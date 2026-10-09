# VIỆT FIT Backend

Triển khai từ [VIET_FIT_BACKEND.md](VIET_FIT_BACKEND.md):
Java 21, Spring Boot 3, Gradle Groovy DSL, PostgreSQL, Flyway, Spring Data JPA,
Bean Validation và Lombok. Có đủ các API outfit, knowledge, weather, recommendation,
remix, cultural-score và save/read look. [Contract và ví dụ request](docs/API.md).

## Phần ghép từ NepAoPrj

- `GET/POST /ai/**` chuyển tiếp các API catalog, quiz, stylist, evaluate, review,
  recommendations và remix tới AI service qua `AI_SERVICE_URL`. Các route admin/dev
  không mở qua proxy này.
- `POST /api/shared-looks` nhận một object có `state` và trả `{ "id": "UUID" }`.
  `GET /api/shared-looks/{id}` trả lại JSON đã lưu, gồm bối cảnh, thẻ điểm và lời stylist.
  Payload giới hạn 64 KiB UTF-8; migration `V6__shared_looks.sql` tạo bảng JSONB riêng.
  API `/api/looks` hiện có tiếp tục dùng định dạng lựa chọn của frontend PROMPTxPTIT.
- Đặt `WEB_ROOT` tới bản build `frontend/dist` để Spring phục vụ React và các route SPA.
  Ví dụ từ `backend`: `$env:WEB_ROOT = (Resolve-Path ../frontend/dist).Path` trước khi
  chạy `./gradlew.bat bootRun`. API và asset không tồn tại vẫn trả 404.

Code vẫn nằm trong `src/main/java`, migration trong `src/main/resources/db/migration`;
AI và dữ liệu của nó nằm ở `../ai-service`, không có backend/AI service lồng nhau.

## Chạy bằng Docker

Cần Docker Compose, mạng để tải image/dependency và khóa OpenWeather/Gemini.

```powershell
Copy-Item .env.example .env
# Điền DATABASE_PASSWORD, WEATHER_API_KEY, GEMINI_API_KEY và GEMINI_MODEL trong .env
docker compose up --build -d
Invoke-RestMethod http://localhost/api/health
Invoke-RestMethod http://localhost/api/outfits
```

Compose tự đọc .env. Chỉ Nginx cổng 80 được public; PostgreSQL, Spring Boot và FastAPI
nằm trong mạng nội bộ. Nginx proxy /api tới backend. Frontend React và chứng chỉ TLS
chưa được cung cấp; thêm frontend vào Nginx và cấu hình HTTPS trước khi triển khai public.
Dữ liệu PostgreSQL nằm trong volume `postgres-data`.

Gemini model bắt buộc cấu hình bằng tên model đang khả dụng trong tài khoản.
[Danh sách model](https://ai.google.dev/gemini-api/docs/models).
Gemini key chỉ truyền cho container AI; không truyền cho Spring Boot/React.

## Chạy JVM trên Windows

Cần JDK 21 và PostgreSQL đang chạy với database viet_fit.
PowerShell phải export biến môi trường; Spring Boot không tự nạp file .env.

```powershell
$env:DATABASE_URL = 'jdbc:postgresql://localhost:5432/viet_fit'
$env:DATABASE_USERNAME = 'viet_fit'
$env:DATABASE_PASSWORD = 'your-password'
$env:WEATHER_API_KEY = 'your-weather-key'
$env:AI_SERVICE_URL = 'http://localhost:8000'
.\gradlew.bat bootRun
```

Trong terminal khác, Python 3.12+:

```powershell
cd ../ai-service
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:BACKEND_COMPAT_ONLY = 'true'
$env:GEMINI_API_KEY = 'your-gemini-key'
$env:GEMINI_MODEL = 'your-available-model'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Nếu thiếu Weather key, chỉ weather/recommendations báo lỗi cấu hình;
catalog, culture, looks vẫn dùng được. AI service bên ngoài có nhánh dự phòng khi thiếu Gemini key; backend vẫn kiểm tra mã và đúng 3 concept.

## Build và kiểm thử

```powershell
.\gradlew.bat test bootJar
```

Linux/macOS: `sh gradlew test bootJar`.
Tests dùng H2 ở PostgreSQL mode, chạy chính migration Flyway và Hibernate validate;
mock provider cho luồng demo và dùng HTTP server cục bộ để kiểm tra client contract,
JSON lỗi, HTTP lỗi, encoding, timeout và việc không làm lộ secret.
JAR: `build/libs/viet-fit-backend-0.1.0.jar`.

Bản này pin Spring Boot 3.3.4 và Gradle 8.9 theo dependency cache có sẵn để kiểm chứng
offline trong môi trường hiện tại. Chưa kiểm chứng nâng cấp lên bản Spring Boot 3
đang được hỗ trợ; cần nâng dependency và kiểm tra lại trước production.
[Thông tin tương thích chính thức](https://docs.spring.io/spring-boot/3.5/system-requirements.html).

## Dữ liệu và giới hạn hiện tại

### Dữ liệu tập trung trong PostgreSQL

Migration `V16__sync_merged_ai_catalog.sql` bổ sung các luật R40–R50 sau merge,
đồng bộ điểm thưởng màu yêu thích và 4 prompt với bản AI hiện tại. Các nguồn và
ghi chú phạm vi kiểm chứng của V11 được giữ nguyên. Sau khi backend chạy migration,
khởi động lại AI nếu dùng `AI_CATALOG_SOURCE=postgres` để nạp luật và prompt mới.
V13/V14 bổ sung màu và quần cho stylist; V15 giữ phạm vi giới tính của tủ đồ.
Không sửa checksum hay xóa lịch sử migration để nhận cập nhật này.

Flyway V7–V11 lưu đủ catalog nam/nữ (86 món), 8 câu hỏi, cấu hình chấm điểm,
checklist, luật AI, thẻ văn hóa và 4 prompt vào các bảng backend. `asset_files`
lưu cả metadata và byte gốc của toàn bộ `frontend/public` và `assets` (1.848 file
ở bộ dữ liệu hiện tại). Import không chỉnh sửa file nguồn và chạy lại không tạo bản trùng.

Từ thư mục gốc, chạy `start-all.ps1`: backend chạy migration, import asset,
rồi AI kết nối cùng PostgreSQL và frontend tải `/api/data/bootstrap`.
`/figure/**` phục vụ byte từ database; `/api/assets/**` dùng đường dẫn tương đối
để lấy cả file nguồn. `/api/data/assets` trả manifest, không trả byte ảnh trong JSON.

```powershell
& ai-service/.venv/Scripts/python.exe -X utf8 backend/import_data.py --assets
& ai-service/.venv/Scripts/python.exe -X utf8 backend/import_data.py --audit
```

Audit chỉ đọc, đếm mọi bảng ngoài schema hệ thống, đối chiếu SHA-256 của byte
trong DB với metadata và file nguồn; báo cáo ở `.tools/database-audit.json`.
Bảng giao dịch như `looks` có thể trống trên database mới, audit sẽ báo đúng
tình trạng đó và không tạo bản phối giả để lấp bảng.

V11 thay các URL 404 hoặc dẫn sai bài bằng 7 nguồn bài viết được kiểm tra ngày
09/10/2026; danh mục ở `/api/data/documents/cultural.sources`. Nội dung giới thiệu
được đối chiếu theo nguồn. URL và nội dung cũ được giữ trong các cột `original_*`
để tra cứu. Nguồn bối cảnh trang phục không xác nhận toàn bộ gợi ý phối đồ:
API warning có `sourceVerified` và `sourceNote` để biểu đạt giới hạn này.

Các ghi chú về seed V1/V2 bên dưới mô tả dữ liệu ban đầu; bộ hiện tại đã được
bổ sung bằng các migration sau. Không sửa checksum của migration đã chạy.

Flyway V1 tạo 11 bảng, ràng buộc khóa ngoại/unique/check và index.
V2 seed 5 trang phục, 7 màu, 5 phong cách, 5 sự kiện và 4 phụ kiện.
Mapping outfit_accessories ban đầu thể hiện khả năng hiển thị kỹ thuật;
compatibility_score để null, không phải đánh giá văn hóa.

Không seed kiến thức, rule văn hóa hoặc URL ảnh chưa có nguồn/tài nguyên thật.
Cultural-score trả INSUFFICIENT_DATA và score null cho tới khi có rule kiểm chứng
cho đủ 5 tiêu chí. Thêm dữ liệu đã được thẩm định bằng migration mới;
không sửa migration đã chạy. Quy ước category/target/rule được CHECK trong DB.
Có thể thêm knowledge và outfit_assets bằng migration khi đã có nguồn/ảnh.

Không có login/admin/feed/3D, đúng ưu tiên MVP. Chưa có API upload ảnh.
Lưu look tính cultural score trong backend; hai điểm style/color chưa có thuật toán
nên để null. Backend kiểm tra mọi mã AI trả về và đúng 3 concept.
Không có retry tự động cho Gemini để tránh lặp chi phí không cần thiết.

[Tài liệu OpenWeather](https://openweathermap.org/api/current),
[Gemini Generate Content và cấu hình JSON](https://ai.google.dev/api/generate-content),
[FastAPI Docker](https://fastapi.tiangolo.com/deployment/docker/).
