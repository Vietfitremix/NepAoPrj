# VIỆT FIT — Frontend

Frontend theo `VIET_FIT_FRONTEND.md`: React, TypeScript, Vite, Tailwind CSS, React Router và Axios. Giao diện tiếng Việt, responsive, tông kem / đỏ trầm / xanh ngọc.

## Chạy dự án

Cần Node.js **22.18 trở lên** và npm.

```sh
npm install
npm run dev
```

Vite chạy tại `http://localhost:5173`. Mặc định `/api` được proxy tới Spring Boot tại `http://localhost:8080`. Nếu backend ở địa chỉ khác, chỉnh `server.proxy` trong `vite.config.ts`, hoặc sao chép `.env.example` thành `.env.local` và đặt `VITE_API_BASE_URL`.

```sh
npm run test
npm run typecheck
npm run build
npm run preview
```

Không đặt Gemini API key hoặc Weather API key trong biến `VITE_*`; các biến này được đưa vào bundle trình duyệt.

## Luồng đã triển khai

- `/`: landing page, hình minh họa SVG tự dựng, hướng dẫn sử dụng.
- `/stylist`: chọn sự kiện, phong cách, màu sắc, thành phố; lấy thời tiết thực tế; gửi prompt và sở thích.
- `/concepts`: hiển thị đúng 3 concept backend trả về; mở dialog kiến thức văn hóa có nguồn tham khảo.
- `/mix/:conceptId`: preview nhiều lớp ảnh, chọn màu/phụ kiện/phong cách/bối cảnh; AI Remix; Cultural Check có debounce 450 ms và hủy request cũ; áp dụng gợi ý có dữ liệu `changes`; tạo look.
- `/look/:lookId`: tải look theo ID, điểm số backend, kiến thức văn hóa, lưu ID trên thiết bị, chia sẻ URL qua Web Share hoặc clipboard, remix lại.

Các lựa chọn được giữ trong `sessionStorage` để tải lại trang không mất bản phối. Lưu look dùng `localStorage` theo thiết bị, chưa có đồng bộ tài khoản vì đặc tả không cung cấp API tài khoản/lưu bộ sưu tập. Link look có thể mở trực tiếp khi backend cung cấp dữ liệu tương ứng. Link Mix Studio cần bản phối trong phiên; nếu thiếu, ứng dụng hướng dẫn tạo concept mới.

Không có recommendation, thời tiết, điểm số hoặc kiến thức lịch sử giả. Thiếu backend sẽ hiển thị lỗi/thử lại; nút tạo concept đợi thời tiết thực tế. Các hình trên landing chỉ minh họa trang phục, không phải gợi ý AI hoặc tư liệu phục dựng.

## Kết nối backend

Xem [API_CONTRACT.md](./API_CONTRACT.md) và [src/types/index.ts](./src/types/index.ts). Đặc tả gốc chưa định nghĩa đầy đủ JSON cho recommendation, outfit assets và look; frontend sử dụng hợp đồng được ghi trong tài liệu này. Nếu backend dùng envelope `{ data: ... }` hoặc tên thuộc tính khác, cần ánh xạ ở `src/services/`.

Các layer ảnh phải có cùng kích thước canvas và điểm neo, nền trong suốt, URL truy cập được từ trình duyệt. Frontend dùng `object-fit: contain` và `zIndex` của asset. Màu được chọn bằng asset tương ứng, không nhuộm ảnh bằng CSS. `styleCode` được gửi cho remix, kiểm tra văn hóa và tạo look; preview chỉ thay đổi theo các asset/màu/phụ kiện backend cung cấp.

## Triển khai hosting

Build tạo thư mục `dist/`. Cấu hình web server trả `index.html` cho route frontend không phải file thật (SPA fallback), và proxy `/api` tới backend. Vite proxy chỉ áp dụng khi phát triển. Khi dùng backend khác origin, cấu hình CORS tại backend. Lưu ý URL ảnh và source văn hóa cần HTTPS khi deploy trên HTTPS.

## Kiểm tra

`npm test` kiểm tra việc áp dụng thay đổi remix/cultural suggestion: giữ nguyên dữ liệu gốc, partial update, loại bỏ trùng lặp và tính idempotent. `npm run build` chạy TypeScript strict trước khi build Vite.

Đã chạy 4 kiểm thử logic remix bằng Node runtime có sẵn: 4/4 pass. Đã parse/transform 27 file TypeScript/TSX (gồm cấu hình Vite), kiểm tra đường dẫn import nội bộ và JSON cấu hình: pass. Đây là kiểm tra cú pháp, không thay thế TypeScript typecheck.

Môi trường triển khai ban đầu không truy cập được npm registry, nên chưa cài dependency, chạy typecheck/build Vite hoặc kiểm tra giao diện trên trình duyệt. Cần chạy `npm install`, `npm run typecheck` và `npm run build` trên máy có Node/npm và mạng. Chưa xác minh tích hợp với Spring Boot thực tế.
