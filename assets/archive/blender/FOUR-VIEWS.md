# Nhân vật nền — 4 hướng

Studio 3D có nút Trước, Phải, Sau, Trái, xoay từng 90° và vuốt ngang.
Bàn phím: đặt tiêu điểm trên nhóm nút, dùng mũi tên trái/phải.
Mỗi giới tính có bốn PNG riêng; các ảnh cạnh và sau được tạo bằng imagegen
tích hợp, giữ trang phục nền xám và chân trần. Prompt: four-view-prompts.json.

Asset trước: male-layers/base-barefoot.png và female-layers/base.png.
Asset ba hướng bổ sung: frontend/public/figure/{male,female}-layers/views/base-{left,right,back}.png.
character-view-layout.json giữ chiều cao và đường chân ổn định khi đổi ảnh.
PNG nguồn: RGBA 1024 × 1536. Hướng trái/phải nghĩa là nhân vật nhìn sang
trái/phải màn hình. Đây là bốn góc ảnh, không phải mô hình xoay 360° liên tục.

Chế độ 4 hướng hiện xem nhân vật nền. Trang phục rời được phối ở góc trước.
Các lựa chọn áo/quần/giày được giữ trong chế độ xoay; bấm “Xem bộ đồ đã chọn”
để trở lại bản phối trước đó. Nút tải xuất đúng góc đang hiển thị.

Kiểm tra: tám ảnh đủ kích thước, nền trong suốt, đầu/chân thống nhất;
xoay trọn vòng hai chiều, lưu góc nhìn, asset tồn tại, test và build frontend.
