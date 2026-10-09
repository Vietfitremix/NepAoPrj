# Cấu trúc asset VIỆT FIT

Asset được chia theo nhân vật, danh mục và từng món. `shirts` là áo, `pants` là quần, `skirts` là váy, `shoes` là giày; `body` là cơ thể nhân vật.

```text
assets/
  wardrobe/
    male/
      body/
      shirts/{id}/source/
      pants/{id}/source/
      shoes/{id}/source/
    female/
      body/
      shirts/{id}/source/
      pants/{id}/source/
      skirts/{id}/source/
      shoes/{id}/source/
  metadata/                 Thiết kế, phép căn ảnh, bảng chuyển đường dẫn
  patterns/{id}/source/     Ảnh họa tiết nền trong suốt và prompt
  previews/                 Ảnh mặc thử nam/nữ
  exports/                  Bộ PNG và ZIP để tải về
  archive/                  Bộ cũ, Blender, bản loại và tài liệu lịch sử
```

Mỗi thư mục `source` giữ ảnh tạo ban đầu và prompt cạnh ảnh: `front.png` nếu có, `left.png`, `right.png`, `back.png`, các JSON tương ứng, cùng `reference.png` là ảnh tham chiếu trước. Các món áo/quần/giày cũ dùng ảnh tham chiếu để xuất góc trước; ba góc còn lại có PNG nguồn riêng. Áo dài navy nam có thêm `validation/` lưu các ảnh mặc thử nguồn.

Ảnh frontend dùng được tổ chức cùng danh mục:

```text
frontend/public/figure/{male|female}-layers/
  catalog.json
  body/{front,left,right,back}.png
  shirts/{id}/{front,left,right,back,thumbnail}.png
  pants/{id}/{front,left,right,back,thumbnail}.png
  skirts/{id}/{front,left,right,back,thumbnail}.png
  shoes/{id}/{front,left,right,back,thumbnail}.png
  headwear/{id}/{front,left,right,back,thumbnail}.png
  hair-accessories/{id}/...
  headphones/{id}/...
  eyewear/{id}/...
  jewelry/{necklaces|earrings|bracelets}/{id}/...
  gloves/{id}/...
  waist-accessories/{id}/...
  backpacks/{id}/...
  bags/{id}/...
  bag-charms/{id}/...
  handheld/{id}/...
frontend/public/figure/patterns/{id}/{tile,thumbnail}.png
```

Danh mục váy hiện có ở nhân vật nữ. Ví dụ: `female-layers/skirts/skirt-short-navy/left.png`, `male-layers/pants/slim-black/back.png`. `catalog.json` giữ ID, tên món, đường dẫn góc trước, thumbnail và ảnh nguồn; không đổi ID khi đổi hướng. Váy và quần dùng chung lựa chọn phần dưới trong Studio, nhưng có thư mục riêng.

Có **86 món theo nhân vật / 344 ảnh PNG RGBA 1024 × 1536**, gồm 28 món trang phục ban đầu và 29 kiểu phụ kiện/giày mới được căn riêng cho nam và nữ. Có thêm **18 họa tiết nền trong suốt**. Mỗi PNG góc nhìn là một món riêng, không chứa toàn bộ nhân vật. Không tự căn giữa theo vùng có màu. `thumbnail.png` chỉ dùng trong tủ đồ. Đổi hướng giữ nguyên ID món, màu và họa tiết. Đây là sprite bốn hướng, không phải mesh 3D xoay liên tục.

Canvas phối đồ và ảnh tải xuống là **1024 × 1736**, có thêm 200 px phía trên cho nón rộng/cao. Toàn bộ cơ thể, trang phục và phụ kiện được vẽ tại y = 200; riêng món có `offsetY: -200` được vẽ thêm dịch chuyển đó để nón không bị cắt. `rearViews` trong catalog/manifest chỉ các hướng món nằm phía sau cơ thể; ba lô góc nghiêng có quai tiền cảnh riêng qua clip của renderer. Các ảnh nguồn gốc không bị sửa khi thêm khoảng trống này.

Các phụ kiện có 13 nhóm chọn độc lập: đồ đội đầu, tai nghe, kính, hoa cài tóc, kiềng, bông tai, vòng tay, găng tay, dây xích hông, ba lô, túi, móc khóa bông, quạt. Cùng một nhóm chọn một món hoặc bỏ món; các nhóm khác vẫn giữ lựa chọn. Túi tote, túi đeo chéo và túi xách thời trang là các món riêng. Giày, dép và guốc dùng lựa chọn giày hiện có. Phụ kiện phía xa được cơ thể che đúng hướng; túi/quạt ở dưới lớp bàn tay để giữ điểm cầm. Găng tay được căn và mask theo vùng da bàn tay từng nhân vật; các ngón hở giữ ảnh cơ thể gốc. Móc khóa bông tự chuyển điểm treo theo túi hoặc ba lô đang chọn, mặc định ở bên hông. Renderer dùng bóng tiếp xúc nhẹ cho phụ kiện.

`assets/wardrobe/shared/{category}/{id}/source/turnaround.png` giữ sheet bốn hướng do built-in `image_gen` tạo. `assets/wardrobe/{gender}/{category}/{id}/source/` giữ từng ô nguồn và JSON prompt. `metadata/accessory-alignment.json` lưu phép căn từng món vào cơ thể. Họa tiết ở `assets/patterns/{id}/source/`, prompt ở cạnh ảnh và `metadata/pattern-sources/`. Tên “Của nó” trong yêu cầu đang chờ xác định, chưa tự thay bằng một họa tiết khác.

Studio có màu gốc, 9 màu có sẵn và ô chọn màu bất kỳ cho áo, quần/váy, giày. `frontend/src/utils/wardrobeStyles.ts` giữ độ sáng/nếp vải và alpha khi đổi màu, rồi áp họa tiết lặp chỉ trong vùng có trang phục; ảnh cơ thể, phụ kiện và PNG nguồn giữ nguyên. Chọn “Giữ họa tiết gốc” bỏ phần họa tiết thêm. Màu/họa tiết lưu riêng theo nhóm áo, quần/váy, giày trong lựa chọn của mỗi nhân vật.

`exports/wardrobe/kit` chứa toàn bộ các món và họa tiết theo cùng danh mục; `exports/bottoms/kit` chứa 9 món quần/váy mới. Trong kit đầy đủ, `characters/{gender}` có `base`, `prepared-base`, `shoe-base`, `prepared-shoe-base` và `hands`. Chọn prepared base khi có quần/váy; món giày có `coversFeet` dùng shoe base để không lộ bàn chân nền dưới đế. Dép có `footbedClipY` chỉ vẽ cơ thể đến tọa độ y đó, giữ phần chân phía trên và bỏ vùng da nền thừa dưới đế dép. Vẽ phụ kiện hậu cảnh, cơ thể, giày, quần/váy, áo, túi/quạt, tay rồi phụ kiện tiền cảnh. Áo dài góc nghiêng dùng phần tà trước/tà sau theo `frontend/src/utils/sourceDirectionRenderer.ts`.

Ảnh được tạo bằng công cụ built-in image_gen từ các tham chiếu cơ thể/trang phục gốc. Prompt của từng góc nằm cạnh PNG nguồn và trong `prompts.json` của kit. Bộ cũ trong `archive/packages` và các ZIP lịch sử được giữ nguyên; các đường dẫn cũ trong tài liệu lịch sử mô tả cấu trúc tại thời điểm xuất bộ đó.

Công cụ:

- `tools/align_source_layers.mjs`: căn ba góc của 19 món ban đầu.
- `tools/export_front_source_layers.mjs`: xuất góc trước của 19 món ban đầu từ `reference.png`.
- `tools/prepare_bottom_assets.mjs --register`: căn và đăng ký 9 món quần/váy mới.
- `tools/prepare_accessory_assets.mjs --register`: tách sheet, căn và đăng ký phụ kiện cho cả hai nhân vật.
- `tools/prepare_pattern_assets.mjs`: chuẩn bị tile/thumbnail họa tiết.
- `tools/preview_accessory_assets.mjs`, `tools/preview_styled_outfits.mjs`: kiểm tra mặc thử ở bốn hướng.
- `tools/package_bottom_assets.mjs`: xuất bộ quần/váy mới theo danh mục.
- `tools/package_wardrobe_assets.mjs`: xuất toàn bộ tủ đồ theo danh mục.
- `tools/verify_asset_layout.mjs`: kiểm tra đường dẫn, PNG và hash sau sắp xếp.

Dùng Node 22.18+; các công cụ canvas cần `@napi-rs/canvas` trong `.tools/asset-qa`. Các công cụ nhập TypeScript chạy với `--experimental-strip-types`. `metadata/path-migration.json` ghi lại đường dẫn cũ/mới và hash 112 sprite; việc sắp xếp không thay đổi nội dung các ảnh.
