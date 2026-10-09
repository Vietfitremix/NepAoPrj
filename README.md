# VIỆT FIT — Dự án Trải Nghiệm và Remix Việt Phục cùng AI

Hệ thống ứng dụng văn hóa - công nghệ kết hợp **Việt phục truyền thống**, **Công nghệ AI Stylist (Google Gemini + Rule Engine)**, **Backend Spring Boot 3 (Java 21)** và **Frontend React (Vite & Tailwind)**.

---

## 🏛 Kiến trúc tổng thể và Liên kết thư mục

```mermaid
graph TD
    User["👤 Người dùng (Browser)"]
    FE["🎨 Frontend (React + Vite)<br/>Port: 5173"]
    BE["☕ Backend (Spring Boot 3 + Java 21)<br/>Port: 8080"]
    AI["🧠 AI Service (FastAPI + Python 3.12)<br/>Port: 8000"]
    DB[("🐘 PostgreSQL 18<br/>Port: 5432 (viet_fit)")]
    OW["☁️ OpenWeatherMap API<br/>(Thời tiết thực tế)"]
    GM["🤖 Google Gemini API<br/>(Diễn giải ngôn ngữ tự nhiên)"]

    User -->|HTTP / SPA| FE
    FE -->|Vite Proxy /api/* và /figure/*| BE
    BE -->|Flyway / JPA SQL| DB
    BE -->|REST / HTTP 1.1| AI
    BE -->|HTTP GET /weather| OW
    AI -->|Prompt / JSON Schema| GM
    AI -.->|Fallback nội bộ| AI
    AI -->|Catalog, luật, quiz và prompt| DB
```

---

## 📁 Cấu trúc Monorepo

| Thư mục | Ngôn ngữ / Công nghệ | Vai trò trong hệ thống |
| :--- | :--- | :--- |
| **[`frontend/`](./frontend)** | React 19, TypeScript, Vite, Tailwind | Giao diện người dùng: Landing, Stylist Form, Concept Cards, Studio phối đồ 2D canvas nhiều lớp PNG, trang Look detail. |
| **[`backend/`](./backend)** | Java 21, Spring Boot 3, JPA, Flyway | Trung tâm xử lý nghiệp vụ: Quản lý catalog Việt phục, lưu trữ Look, gọi OpenWeather, kết nối AI Service và kiểm tra văn hóa. |
| **[`ai-service/`](./ai-service)** | Python 3.12, FastAPI, Pydantic | Động cơ trí tuệ nhân tạo: Bộ luật phối đồ lịch sử (Rule engine), chấm hài hòa màu sắc OKLCH, tích hợp Google Gemini AI và nhánh dự phòng. |
| **[`frontend/public/figure/`](./frontend/public/figure)** | PNG Layers | Bộ ảnh nam/nữ và phụ kiện 4 góc nhìn; byte gốc được lưu trong bảng `asset_files`, phục vụ qua backend. |
| **[`.vscode/`](./.vscode)** | VS Code Configurations | Cấu hình IDE tích hợp sẵn: Debug Spring Boot + FastAPI (F5), chạy tasks, cấu hình Java LS & Python venv. |

---

## 🚀 Khởi động nhanh (Quick Start)

### Cách 1: Sử dụng PowerShell Script (Khuyến nghị cho Windows)
Chỉ cần chạy lệnh từ thư mục gốc của dự án:
```powershell
.\start-all.ps1
```
Script kiểm tra kết nối của AI, backend và proxy `/api` trước khi báo sẵn sàng.
Log khởi động được lưu trong `.tools/ai.*.log`, `.tools/backend.*.log` và
`.tools/frontend.*.log`. Script import asset sau migration (ảnh người mẫu nằm trong PostgreSQL). AI mặc định đọc luật, 8 câu hỏi,
thang điểm, checklist và prompt từ tệp `ai-service/data/*.json` và `ai-service/prompts/`; muốn AI đọc từ database
thì đặt `AI_CATALOG_SOURCE=postgres` trong `.env`. Chi tiết import/audit: [backend/README.md](backend/README.md).
Sau merge, Flyway V16 đồng bộ luật AI, thang điểm và prompt mới vào PostgreSQL.
Flyway V17 mở rộng lên **80 luật đánh giá chi tiết**; xem [LUAT-DANH-GIA.md](LUAT-DANH-GIA.md)
để tra điều kiện, nhóm chống trùng, tác động điểm, gợi ý và nguồn tham khảo của từng luật.
Khởi động lại backend trước rồi AI để AI nạp dữ liệu mới; không sửa migration đã chạy.
`CORS_ALLOWED_ORIGINS` mặc định cho phép giao diện ở `http://localhost:5173`
và bản preview ở `http://localhost:5176`; nếu dùng URL khác, thêm URL đó vào `.env`.
Để dừng toàn bộ các tiến trình:
```powershell
.\stop-all.ps1
```

### Cách 2: Sử dụng lệnh npm monorepo
```bash
npm run dev:frontend   # Khởi động riêng Frontend
npm run dev:backend    # Khởi động riêng Backend
npm run dev:ai         # Khởi động riêng AI Service
npm test               # Chạy toàn bộ test suites của 3 dịch vụ
npm run build          # Đóng gói build cho cả frontend và backend
```

### Cách 3: Chạy toàn bộ với Docker Compose
```bash
docker compose up --build -d
```

---

## 🔗 Luồng dữ liệu tích hợp (Data Flow)

1. **Khám phá & Chọn bối cảnh (`/stylist`)**:
   - Frontend gửi yêu cầu lấy thời tiết Hà Nội/TP.HCM -> Backend gọi OpenWeatherMap -> Trả về nhiệt độ và điều kiện thời tiết thực tế.
   - Người dùng chọn dịp (Tết, Lễ hội,...), phong cách (Gen Z, Truyền thống,...), màu sắc và nhập mong muốn.
2. **Đề xuất Concept (`/concepts`)**:
   - Frontend gọi `POST /api/recommendations` -> Backend gửi reference data kèm context thời tiết sang AI Service -> AI Service chấm luật và đề xuất đúng 3 concept phù hợp văn hóa -> Trả về kết quả hiển thị.
3. **Phối đồ trong Studio (`/mix/:conceptId`)**:
   - Frontend render nhiều lớp SVG từ thư mục `figure/`.
   - Người dùng thay đổi màu sắc, thêm bớt phụ kiện, gọi **AI Remix** hoặc **Kiểm tra văn hóa** theo thời gian thực.
4. **Lưu trữ & Chia sẻ (`/look/:lookId`)**:
   - Khi hoàn thành, frontend gửi `POST /api/looks` -> Backend lưu vào PostgreSQL và cấp phát ID vĩnh viễn để chia sẻ.

---

## ⚙️ Cấu hình biến môi trường (`.env`)

Tất cả cấu hình tập trung tại file [`.env`](./.env) ở thư mục gốc:
```env
DATABASE_URL=jdbc:postgresql://localhost:5432/viet_fit
DATABASE_USERNAME=viet_fit
DATABASE_PASSWORD=change-me
WEATHER_API_KEY=
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash
AI_SERVICE_URL=http://localhost:8000
```
*(Nếu chưa có `GEMINI_API_KEY`, hệ thống sẽ tự động chuyển sang chạy Rule Engine dự phòng mà không phát sinh lỗi).*

---

## 🚢 Quy trình CI/CD & Triển khai (Deployment)

Dự án đã được tích hợp toàn diện hệ thống **GitHub Actions CI/CD** và **Dockerization**:
- **CI Pipeline (`.github/workflows/ci.yml`)**: Tự động chạy test độc lập cho Frontend (Node 22), Backend (Java 21/Gradle), AI Service (Python 3.12) và kiểm tra Docker Compose khi có PR hoặc push.
- **CD Pipeline (`.github/workflows/deploy.yml`)**: Tự động build và đẩy Docker images lên GitHub Container Registry (GHCR), hỗ trợ triển khai tự động qua SSH lên VPS.
- **Tài liệu hướng dẫn chi tiết:** Xem [DEPLOYMENT.md](DEPLOYMENT.md) để biết cách cấu hình GitHub Secrets, chuẩn bị máy chủ VPS, cài đặt SSL HTTPS và quản trị hệ thống.
