# Bộ quần / váy riêng, bốn hướng

Đầu ra: `viet-fit-bottoms-4-views.zip` hoặc `kit/`.

- Nam: quần dài xanh navy, quần đùi kaki be, quần lửng xanh olive, quần ống bó đen, quần ống rộng xám than.
- Nữ: váy ngắn xanh navy, váy dài xếp ly trắng ngà, quần ngắn denim xanh, quần dài đen.

Tổng cộng **9 món / 36 PNG RGBA trong suốt**, mỗi món có `front.png`, `left.png`, `right.png`, `back.png`, kích thước 1024 × 1536. `male/{id}/` và `female/{id}/` chứa các món riêng. Các PNG trang phục không chứa nhân vật, áo hay giày. Hai ảnh `preview-*.png` chỉ để xem mặc thử.

Mỗi ảnh đã căn theo cơ thể nhân vật gốc và giữ nguyên tọa độ trên canvas. Vẽ ảnh tại (0,0) trên canvas 1024 × 1536; không tự căn giữa theo phần có màu. Khi đổi hướng, giữ nguyên ID món đã chọn và lấy PNG cùng ID của hướng mới. Đây là sprite 2D bốn hướng, không phải mesh xoay 3D liên tục.

Kit có `characters/{male|female}/base/`, `prepared-base/` và `hands/`. Khi không chọn quần/váy, dùng `base`. Khi chọn quần/váy, dùng `prepared-base`, vẽ giày nếu có, vẽ món quần/váy, rồi lớp áo nếu có và `hands` đúng hướng. Prepared base xử lý phần vải xám của quần nền, giúp quần bó và váy có dáng riêng. Lớp tay tiền cảnh giúp bàn tay nằm trước quần/váy. Ghép cùng áo dài trong dự án theo quy tắc tà trước/tà sau của `frontend/src/utils/sourceDirectionRenderer.ts`.

Các món đã được thêm vào tủ đồ của Studio; nữ có mục “Quần / Váy”. Áo, quần/váy và giày vẫn chọn độc lập; đổi góc không đặt lại lựa chọn. Trong frontend, ảnh được dùng ở `public/figure/{male|female}-layers/views/*-source.png`. Ảnh thumbnail nằm riêng và không dùng để render nhân vật.

Nguồn: ảnh cơ thể photorealistic gốc của dự án. Dùng skill imagegen, công cụ **built-in image_gen** để tạo mẫu trước và các góc trái/phải/sau theo mẫu trước, giữ màu vải, kiểu túi và đường may. `prompts.json` trong kit lưu toàn bộ 36 prompt cuối cùng và ảnh tham chiếu; các JSON cạnh PNG nguồn bên ngoài kit cũng lưu thông tin này. Ảnh có hậu tố `-discarded` là bản loại, không có trong kit.

`items.json` lưu thiết kế và chiều dài mỗi món; `alignment.json` lưu phép căn ảnh cuối. Tái xuất từ PNG nguồn bằng `node tools/prepare_bottom_assets.mjs --register`; cần `@napi-rs/canvas` trong `.tools/asset-qa`. Đóng gói bằng `node --experimental-strip-types tools/package_bottom_assets.mjs`.

Đã render và kiểm tra mặc thử tất cả 36 góc trên cơ thể gốc, chạy kiểm thử frontend cho chọn/bỏ món, lưu lựa chọn và xoay bốn hướng, và build frontend. Phiên làm việc chưa kiểm tra thao tác trực tiếp trong trình duyệt.
