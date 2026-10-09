# Bộ asset trang phục riêng, bốn hướng

Đầu ra sử dụng: `viet-fit-separate-items-4-views.zip` hoặc thư mục `kit/`.

Bộ này có 19 món cho nhân vật nam và nữ, tổng cộng 76 PNG RGBA nền trong suốt, kích thước 1024 × 1536. Mỗi món có `front.png`, `left.png`, `right.png`, `back.png`. Áo, quần và giày là các lớp riêng; mỗi lớp không chứa toàn bộ nhân vật hay các món khác. Các phần áo tứ thân (áo ngoài, áo trong, thắt lưng) nằm trong cùng một món áo.

Trong kit, đường dẫn là `{male|female}/{outfits|pants|shoes}/{id}/{view}.png`. `manifest.json` liệt kê toàn bộ món và các hướng. `body/` chứa nhân vật gốc từng hướng; `hands/` chứa bàn tay tiền cảnh ở các góc nghiêng và sau. `preview-male.png`, `preview-female.png` là ảnh kiểm tra mặc thử, không dùng thay cho lớp trang phục riêng.

Vị trí của các ảnh đã được căn theo nhân vật gốc. Khi kết hợp, vẽ trên cùng canvas 1024 × 1536 tại (0, 0), không tự căn giữa theo vùng có màu. Studio vẽ thân người, tà sau (góc nghiêng), giày, quần, áo/tà trước và bàn tay. Xem `frontend/src/utils/sourceDirectionRenderer.ts` để dùng đúng phần che khuất tà áo. Giữ nguyên các ID áo/quần/giày đã chọn khi đổi góc; chỉ đổi ảnh `view` của mỗi món. Mỗi item có bốn góc đã render sẵn; đây là bộ sprite 2D bốn hướng, không phải mesh xoay 3D liên tục.

Nguồn hình ảnh là bộ nhân vật và quần áo photorealistic hiện có trong `frontend/public/figure/{male|female}-layers/`. Dùng skill imagegen và công cụ built-in image_gen để tạo góc trái, phải, sau của từng món từ ảnh cơ thể đúng hướng và ảnh món gốc. Góc trước được xuất riêng từ phép fit của ảnh nguồn đã có. Không thay nhân vật bằng mẫu hoạt hình.

`male/`, `female/` bên ngoài kit lưu 57 ảnh tạo ban đầu; file JSON cạnh mỗi PNG lưu prompt đầy đủ, ảnh tham chiếu và đường dẫn ảnh được tạo. `alignment.json` lưu phép căn ảnh vào cơ thể. Các PNG cuối Studio dùng nằm trong `frontend/public/figure/{male|female}-layers/views/*-source.png`. Công cụ tái xuất: `tools/align_source_layers.mjs` và `tools/export_front_source_layers.mjs`; cần Node và dependency `@napi-rs/canvas` của `.tools/asset-qa`.

Kiểm tra: 13 bài kiểm thử frontend đạt, gồm mọi tổ hợp chọn/bỏ áo, quần, giày qua bốn hướng, giữ nguyên selection, và kiểm tra đủ 76 PNG RGBA đúng kích thước. Đã render và kiểm tra ảnh mặc thử cả hai nhân vật. Build frontend đạt. Phiên làm việc không có trình duyệt được kết nối, nên chưa kiểm tra thao tác trực tiếp trên trình duyệt.
