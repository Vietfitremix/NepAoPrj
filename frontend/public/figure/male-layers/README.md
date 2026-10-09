# Asset Studio nam

`body/` chứa nhân vật gốc bốn hướng. `shirts/`, `pants/`, `shoes/` chia theo ID từng món; mỗi thư mục món có `front.png`, `left.png`, `right.png`, `back.png`, `thumbnail.png`.

Các ảnh góc nhìn là PNG RGBA 1024 × 1536 đã căn vào cơ thể. Canvas phối đồ có chiều cao 1736 và dịch cơ thể/trang phục xuống 200 px; nón có thêm `offsetY: -200` để giữ toàn bộ đỉnh/vành nón. Thumbnail chỉ dùng trong tủ đồ. Đường dẫn và vị trí phụ kiện được khai báo trong `catalog.json`; ảnh nguồn và prompt ở `assets/wardrobe/male/`.

Phụ kiện chia theo `headwear`, `hair-accessories`, `headphones`, `eyewear`, `jewelry`, `gloves`, `waist-accessories`, `backpacks`, `bags`, `bag-charms`, `handheld`. Mỗi món giữ đủ bốn PNG và thumbnail. Họa tiết dùng chung ở `frontend/public/figure/patterns/`.

Mở `/male-studio` để chọn áo, quần, giày và từng nhóm phụ kiện riêng; tùy chọn màu/họa tiết cho áo, quần, giày. Đổi hướng giữ nguyên các món, màu và họa tiết đã chọn. Tài liệu chung: `assets/README.md`.
