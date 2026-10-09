# Asset trang phục nam và nữ

Mở /male-studio hoặc /female-studio; chọn Nam/Nữ, sau đó chọn áo, quần và giày riêng.
Mỗi nhân vật có áo dài, áo tứ thân, áo ngũ thân, Nhật Bình, áo bà ba.
Lựa chọn được lưu riêng theo nhân vật. Bấm “Đi chân trần” để tháo giày.

Asset đang dùng được khai báo trong catalog.json của từng thư mục:
- male-layers: base-barefoot.png, 7 áo, quần trắng ngà, loafer và sneaker.
- female-layers: base.png, 6 áo, quần trắng ngà, giày búp bê và sneaker.
- Các base.png và female-base.png cũ trong male-layers chỉ là bản lưu trước đây.

PNG RGBA 1024 × 1536, được tạo bằng imagegen tích hợp.
Đây là ảnh phong cách 3D góc nhìn thẳng, chưa phải mesh hoặc rig Blender.
Các thiết kế là mẫu cách điệu, gồm phiên bản phối nam của áo tứ thân và Nhật Bình.

Thứ tự ghép: nền → giày → quần → áo.
Renderer dùng catalog và mesh để căn vai, thân, cổ tay; cùng một renderer được dùng
cho màn hình và ảnh PNG tải xuống. Các asset gốc được giữ nguyên.
mapY ánh xạ các mốc dọc; sleeveX/sleeveDx căn tay áo; crops cắt từng chiếc giày.
fitRows căn đường viền theo vai, khuỷu tay, cổ tay và eo của nhân vật.
Các PNG ghép trực tiếp đã căn tại assets/blender/fitted-layers dùng chung canvas
1024 × 1536 tại (0, 0), không áp dụng lại những phép nắn trong catalog nguồn.

Tài liệu, prompt và ảnh kiểm tra: assets/blender/TRADITIONAL-WARDROBE.md.
