# VIỆT FIT Backend

Triển khai từ [VIET_FIT_BACKEND.md](VIET_FIT_BACKEND.md):
Java 21, Spring Boot 3, Gradle Groovy DSL, PostgreSQL, Flyway, Spring Data JPA,
Bean Validation và Lombok. Có đủ các API outfit, knowledge, weather, recommendation,
remix, cultural-score và save/read look. [Contract và ví dụ request](docs/API.md).

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
