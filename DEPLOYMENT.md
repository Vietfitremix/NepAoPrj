# Hướng dẫn Triển khai & Quy trình CI/CD (Viet-Fit / Nếp Áo)

Tài liệu này hướng dẫn chi tiết quy trình kiểm thử tự động (CI), đóng gói Docker container, đẩy image lên **GitHub Container Registry (GHCR)** và tự động triển khai (CD) lên máy chủ VPS.

---

## 1. Kiến trúc Triển khai (Production Architecture)

```
                            [Internet / Người dùng]
                                       │
                                       ▼ (Port 80 / 443 HTTPS)
                   ┌───────────────────────────────────────┐
                   │       Nginx Web Server (Frontend)     │
                   │   - Phục vụ React SPA (Vite bundle)   │
                   │   - Nén Gzip & Cache tĩnh             │
                   │   - Reverse proxy /api & /figure      │
                   └───────────────────┬───────────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                │                                             │
                ▼ (Port 8080)                                 ▼ (Port 8000)
    ┌───────────────────────┐                     ┌───────────────────────┐
    │  Spring Boot Backend  │◄───────────────────►│   FastAPI AI Service  │
    │  - Java 21 Temurin    │     HTTP REST       │   - Python 3.12       │
    │  - Flyway Migrations  │                     │   - 80 Luật văn hóa   │
    │  - Quản lý tài nguyên │                     │   - Gemini AI API     │
    └───────────┬───────────┘                     └───────────────────────┘
                │
                ▼ (Port 5432)
    ┌───────────────────────┐
    │  PostgreSQL 16 DB     │
    │  - Lưu trữ dữ liệu    │
    │  - Lưu trữ byte ảnh   │
    └───────────────────────┘
```

---

## 2. Quy trình CI/CD qua GitHub Actions

Hệ thống CI/CD được cấu hình trong thư mục `.github/workflows/`:

### A. CI Pipeline (`.github/workflows/ci.yml`)
Chạy tự động mỗi khi có **Pull Request** hoặc **Push** lên nhánh `main`, `develop`, `thang/**`:
1. **Frontend CI**:
   - Node.js 22 + npm caching.
   - Kiểm tra kiểu dữ liệu tĩnh: `npm run typecheck` (`tsc -b`).
   - Chạy 45 unit tests: `npm test`.
   - Build thử nghiệm production: `npm run build`.
2. **AI Service CI**:
   - Python 3.12 + pip caching.
   - Cài đặt thư viện: `pip install -r requirements.txt`.
   - Chạy toàn bộ 135 unit tests & rule engine: `pytest -q`.
3. **Backend CI**:
   - Java 21 (Eclipse Temurin) + Gradle cache.
   - Kiểm thử đơn vị & tích hợp với cơ sở dữ liệu in-memory H2: `./gradlew test`.
   - Đóng gói file thực thi: `./gradlew bootJar -x test`.
4. **Docker Validation**:
   - Kiểm tra cú pháp và cấu trúc các file `docker-compose.yml` và `docker-compose.prod.yml`.

### B. CD Pipeline (`.github/workflows/deploy.yml`)
Chạy tự động khi code được merge vào `main`, hoặc có thể kích hoạt bằng tay (**workflow_dispatch**) trên giao diện GitHub Actions:
1. **Build & Push Docker Images**:
   - Tự động đóng gói 3 container images:
     - `ghcr.io/dth251/vietfit-frontend`
     - `ghcr.io/dth251/vietfit-backend`
     - `ghcr.io/dth251/vietfit-ai-service`
   - Gắn tag `latest` và mã commit `sha-<hash>`.
   - Lưu cache tầng Docker trên GitHub Actions để các lần build tiếp theo chỉ mất ~1-2 phút.
2. **Deploy lên VPS qua SSH**:
   - Kết nối an toàn đến máy chủ từ xa qua SSH Private Key.
   - Cập nhật file `docker-compose.prod.yml`.
   - Kéo images mới nhất từ GHCR về VPS.
   - Chạy lệnh khởi động mượt mà (`docker compose up -d --remove-orphans`).
   - Dọn dẹp images cũ không sử dụng (`docker image prune -f`).

---

## 3. Cấu hình GitHub Secrets (Cho CD tự động)

Để kích hoạt tính năng tự động deploy lên VPS, vào repository GitHub:
**Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**:

| Tên Secret | Bắt buộc | Mô tả | Ví dụ |
| :--- | :---: | :--- | :--- |
| `SSH_HOST` | Có | Địa chỉ IP hoặc Domain của máy chủ VPS | `103.xxx.xxx.xxx` hoặc `server.yourdomain.com` |
| `SSH_USER` | Có | Tên tài khoản SSH trên máy chủ | `ubuntu` hoặc `root` |
| `SSH_PRIVATE_KEY` | Có | Toàn bộ nội dung file private key SSH (`id_rsa` / `id_ed25519`) | `-----BEGIN OPENSSH PRIVATE KEY----- ...` |
| `SSH_PORT` | Không | Cổng SSH nếu khác cổng mặc định | `22` |
| `DEPLOY_PATH` | Không | Đường dẫn thư mục chạy dự án trên VPS | `/home/ubuntu/vietfit-app` |

> *Lưu ý: Nếu chưa cấu hình SSH Secrets, GitHub Actions vẫn tự động build và lưu trữ Docker Images lên GHCR bình thường, không gây lỗi.*

---

## 4. Hướng dẫn Chuẩn bị Máy chủ VPS (Ubuntu / Debian)

### Bước 1: Cài đặt Docker & Docker Compose trên VPS
Chạy các lệnh sau trên VPS:
```bash
# Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# Cài đặt Docker và Docker Compose Plugin
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Kiểm tra phiên bản
docker --version
docker compose version
```

### Bước 2: Tạo thư mục chạy ứng dụng và cấu hình `.env`
```bash
mkdir -p ~/vietfit-app && cd ~/vietfit-app

# Tạo file .env cho production
nano .env
```
Nội dung file `.env` trên VPS:
```env
DATABASE_USERNAME=viet_fit
DATABASE_PASSWORD=mat_khau_bao_mat_cua_ban_123456
GEMINI_API_KEY=AIzaSy...khoa_gemini_cua_ban
GEMINI_MODEL=gemini-3.5-flash
WEATHER_API_KEY=khoa_openweather_neu_co
CORS_ALLOWED_ORIGINS=http://IP_VPS,https://yourdomain.com
HOST_PORT=80
```

### Bước 3: Tải file triển khai và chạy thử
```bash
# Tải file docker-compose.prod.yml
curl -sSL -o docker-compose.prod.yml https://raw.githubusercontent.com/dth251/AI---ARENA/main/docker-compose.prod.yml

# Khởi động dịch vụ
docker compose -f docker-compose.prod.yml up -d
```

---

## 5. Triển khai Cục bộ (Local Docker Deployment)

Nếu bạn muốn chạy thử toàn bộ hệ thống bằng Docker ngay trên máy cá nhân:

### Trên Windows (PowerShell):
```powershell
.\scripts\deploy.ps1
```

### Trên Linux / macOS:
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

Hoặc dùng lệnh Docker Compose trực tiếp:
```bash
docker compose up -d --build
```

Mở trình duyệt truy cập:
- **Giao diện Web (Frontend):** <http://localhost>
- **Backend Health Check:** <http://localhost:8080/api/health>
- **AI Service Health Check:** <http://localhost:8000/ai/health>

---

## 6. Cấu hình Tên miền & HTTPS (SSL Miễn phí)

Để sử dụng domain riêng với SSL (HTTPS), cách đơn giản và an toàn nhất:

### Cách 1: Sử dụng Cloudflare Proxy (Khuyên dùng)
1. Trỏ DNS Domain (A record) về IP VPS của bạn qua Cloudflare.
2. Bật đám mây màu cam (Proxied).
3. Trong mục **SSL/TLS** trên Cloudflare, chọn chế độ **Flexible** hoặc **Full**.

### Cách 2: Sử dụng Certbot Nginx trên máy chủ
Nếu cài đặt Nginx trực tiếp trên máy chủ làm Reverse Proxy bên ngoài:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 7. Giám sát & Quản trị Vận hành

- **Xem nhật ký hoạt động (Logs):**
  ```bash
  docker compose -f docker-compose.prod.yml logs -f
  # Xem riêng một dịch vụ:
  docker compose -f docker-compose.prod.yml logs -f backend
  ```
- **Khởi động lại dịch vụ:**
  ```bash
  docker compose -f docker-compose.prod.yml restart
  ```
- **Dừng dịch vụ:**
  ```bash
  docker compose -f docker-compose.prod.yml down
  ```
- **Rollback về phiên bản trước:**
  Nếu bản deploy mới gặp vấn đề, bạn có thể quay lại image trước bằng cách đổi tag image trong `.env`:
  ```bash
  BACKEND_IMAGE=ghcr.io/dth251/vietfit-backend:sha-<commit_cu>
  docker compose -f docker-compose.prod.yml up -d
  ```
