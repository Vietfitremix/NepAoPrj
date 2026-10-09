# Kết nối frontend, backend và AI service

Luồng dữ liệu: React (`frontend`, cổng 5173) → Spring Boot (`backend`, cổng 8080)
→ FastAPI (`ai-service`, cổng 8000) → Spring kiểm tra kết quả → React.
Spring quản lý PostgreSQL, danh mục, thời tiết, cultural-score và lưu look.
FastAPI nhận `referenceData` và `culturalContext` từ Spring theo từng request,
dùng pipeline chọn outfit/Gemini và nhánh dự phòng có sẵn.
Khóa Gemini chỉ ở AI service; khóa OpenWeather chỉ ở backend.

## Trạng thái bản vá

Các thay đổi AI service đã được ghi. Môi trường hiện từ chối ghi/xóa những file
có sẵn trong backend và frontend. `integration.patch` chứa toàn bộ thay đổi còn
lại, gồm xóa ba file trong `backend/ai-service`, sửa Docker, client Spring và
chuyển đổi contract của frontend. `integration-preview/` chứa file sau sửa để xem.

Chạy từ `C:/PROMPTxPTIT` trong terminal có quyền ghi để áp dụng bản vá và xóa
NepAoPrj/AI service cũ sau khi kiểm tra SHA-256 các bản sao:

```powershell
powershell -ExecutionPolicy Bypass -File .\ai-service\integration\finish-integration.ps1
```

Script xác minh lại 169 tệp nguồn bằng SHA-256, áp dụng bản vá, kiểm tra nội dung đã ghi,
build frontend và chạy kiểm thử remix trước khi xóa thư mục nguồn. Script dừng nếu
bất kỳ bước nào thất bại. Có thể chạy lại nếu bản vá đã áp dụng đầy đủ.

Trong phiên hoàn tất hiện tại, bản vá vẫn chưa được áp dụng vì quyền ghi các tệp
backend/frontend bị từ chối. `NepAoPrj` và `backend/ai-service` vẫn còn nguyên.
Bản xem trước đã qua kiểm tra TypeScript/ánh xạ API và 4 kiểm thử remix đã đạt.
Kiểm thử backend chưa chạy được do quyền ghi cache Gradle; Python và Docker
chưa có trong PATH của phiên này. Chạy script trên terminal có quyền ghi dự án
để hoàn tất, rồi dùng hướng dẫn bên dưới để khởi động và kiểm tra các service.
File bản vá và bản xem trước nằm ở `ai-service/integration/integration.patch` và `ai-service/integration/preview/`.

## Docker backend + AI, frontend chạy Vite

```powershell
cd backend
Copy-Item .env.example .env
# Điền DATABASE_PASSWORD và WEATHER_API_KEY; GEMINI_API_KEY tùy chọn.
docker compose up --build -d
cd ../frontend
npm install
npm run dev
```

Mở http://localhost:5173. Vite proxy `/api` đến `localhost:8080`.
Docker build AI từ `../ai-service`, bật `BACKEND_COMPAT_ONLY=true`.
AI không dùng DATABASE_URL của Spring: schema native `catalog/ai` của AI khác
schema hiện có của backend. Danh mục luôn lấy trực tiếp từ request Spring.

## Chạy riêng ba service

Terminal AI (Python 3.12+, từ thư mục gốc):

```powershell
cd ai-service
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# .env đặt BACKEND_COMPAT_ONLY=true; điền GEMINI_API_KEY nếu muốn dùng Gemini.
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

Terminal backend (JDK 21 và PostgreSQL có database `viet_fit`):

```powershell
cd backend
$env:DATABASE_URL='jdbc:postgresql://localhost:5432/viet_fit'
$env:DATABASE_USERNAME='viet_fit'
$env:DATABASE_PASSWORD='your-password'
$env:WEATHER_API_KEY='your-weather-key'
$env:AI_SERVICE_URL='http://localhost:8000'
./gradlew.bat bootRun
```

Terminal frontend: `cd frontend`, `npm install`, `npm run dev`.

## Contract và kiểm tra

- Gợi ý: frontend chỉ gửi prompt/city/eventCode/styleCode. Backend lấy weather,
  gửi catalog đến `POST /ai/recommendations`, kiểm tra đúng 3 concept và mã hợp lệ.
- Remix: frontend gửi `{currentLook, prompt}`; backend gọi `POST /ai/remix`,
  kiểm tra các phụ kiện được thêm/xóa rồi frontend áp dụng và chấm lại.
- Lưu/chấm: frontend đổi `accessoryCodes` thành `accessories`, không gửi `conceptId`.
  Look trả ID số được đổi thành chuỗi; tên lấy từ `/api/reference-data`.
- Khi thiếu rule văn hóa, UI hiển thị chưa đủ dữ liệu, không biến `null` thành 0%.
- `frontend/public/figure` giữ 144 file gốc từ NepAoPrj, gồm 141 SVG và tài liệu/preview.
  `rendered/` thêm 35 layer màu, 35 ảnh ghép và 4 phụ kiện. V3 trong bản vá đăng ký
  70 layer backend, thumbnail và URL phụ kiện; Flyway tự chạy khi khởi động backend.
  Concept hiển thị đúng màu; look đã lưu dựng lại từ layer và phụ kiện.
- `ai-service/data` giữ 10 file JSON; `frontend/tools` giữ 14 công cụ nguồn và
  manifest 169 file để kiểm tra bản sao. Script Python đã chỉnh đường dẫn mới.
  `node frontend/tools/import-figure.cjs` tái tạo SVG màu và migration để xem.
- Các culture-card/rule nhập từ nguồn giữ nguyên trạng thái kiểm chứng; migration
  không biến dữ liệu chưa kiểm chứng thành nguồn hay điểm văn hóa chính thức.
- Native `/ai/stylist`, `/ai/review`… dùng catalog riêng; muốn dùng phải tắt
  `BACKEND_COMPAT_ONLY`. Catalog JSON đã có ở `ai-service/data`.

```powershell
cd ai-service
python -m pytest tests/test_backend_contract.py -q
cd ../frontend
npm run build
npm test
cd ../backend
./gradlew.bat test
```
