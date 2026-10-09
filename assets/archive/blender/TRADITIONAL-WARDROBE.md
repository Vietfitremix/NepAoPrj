# VIỆT FIT — Bộ trang phục

Mở Studio 3D tại /male-studio hoặc /female-studio.

- Mỗi nhân vật có đủ: áo dài, áo tứ thân, áo ngũ thân, Nhật Bình, áo bà ba.
- Nam: 7 mẫu áo; nữ: 6 mẫu áo, gồm các màu áo dài bổ sung.
- Quần và giày chọn riêng. Nền nam/nữ đi chân trần.
- Nhân vật nữ có dáng nhỏ nhắn; trang phục và lựa chọn được lưu riêng theo nhân vật.
- Nút tải ảnh xuất bản phối thành PNG trong suốt.

## Tệp

- Asset nam: frontend/public/figure/male-layers/
- Asset nữ: frontend/public/figure/female-layers/
- catalog.json: danh sách asset, căn chỉnh thân áo và vị trí cắt từng giày.
- Mã ghép: frontend/src/utils/renderMaleCharacter.ts
- Prompt: traditional-wardrobe-prompts.json
- Ảnh kiểm tra: male-traditional-preview.png, female-traditional-preview.png
- Gói tải: viet-fit-traditional-wardrobe.zip
- Gói ghép trực tiếp đã căn: viet-fit-fitted-layers.zip

## Bản căn theo cơ thể

Mỗi áo được căn theo đường viền vai, khuỷu tay, cổ tay và eo của từng nhân vật.
Áo bà ba có độ dốc vai và vị trí cổ riêng. Tay rộng của Nhật Bình giữ độ rộng
nhưng tâm tay áo đi theo cánh tay. Quần và giày vẫn chọn độc lập.

Trong fitted-layers/male và fitted-layers/female, các PNG đã được xuất qua
renderer: giữ canvas 1024 × 1536 và ghép tại (0, 0), không cần nắn lại.
Thứ tự: nền → giày → quần → áo. Không cắt sát mép của các PNG này.

Ảnh được tạo bằng công cụ imagegen tích hợp, PNG RGBA 1024 × 1536, phong cách 3D.
Đây là asset ảnh góc nhìn thẳng dùng để ghép lớp; không phải mesh 3D có rig.
Các thiết kế là mẫu cách điệu cho ứng dụng, gồm bản phối nam của Nhật Bình và áo tứ thân.
Ảnh gốc được giữ nguyên; ứng dụng căn chỉnh khi render.

## Kiểm tra

Kiểm tra từng mẫu ghép bằng cùng renderer dùng trong ứng dụng, kiểm tra mesh không lật,
asset đầy đủ, lựa chọn độc lập, khôi phục lựa chọn cũ; chạy test và build frontend.
