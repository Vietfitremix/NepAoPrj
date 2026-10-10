# Hợp đồng API frontend

Base URL mặc định: `/api`. Response JSON trực tiếp, không bọc `data`. Lỗi HTTP khác 2xx được frontend hiển thị với nút thử lại khi phù hợp. Tên mã cần được thống nhất với backend.

## Weather

`GET /weather?city=Hanoi`

```json
{ "city": "Hanoi", "temperature": 30, "condition": "RAIN", "humidity": 82 }
```

Thành phố có sẵn: `Hanoi`, `Ho Chi Minh City`, `Da Nang`, `Hue`. Điều kiện có bản dịch: `RAIN`, `SUNNY`, `CLEAR`, `CLOUDY`, `SNOW`.

## Recommendations

`POST /recommendations`

```json
{
  "prompt": "Mình thích màu đỏ trầm, trẻ trung",
  "eventCode": "TET",
  "styleCode": "GEN_Z",
  "city": "Hanoi",
  "context": { "setting": "ngoai_troi", "preferredColors": ["DARK_RED"] }
}
```

Event: `TET | FESTIVAL | GRADUATION | PHOTOSHOOT`. Style ở form: `GEN_Z | MINIMAL | ELEGANT | TRADITIONAL`. Màu ở form: `RED | WHITE | BLUE | ANY`.

API trả `analysis` và `concepts` (**đúng 3 phần tử**). `analysis` có `event`, `weather` hiện tại từ backend,
`styles`, `understanding`, `character`, `context`, `source`. Frontend dùng nguyên `analysis.understanding`
để hiển thị “AI hiểu bạn đang tìm”, và giữ event/phong cách/người mặc đã phân tích khi vào Mix Studio.
Prompt chỉ gồm câu người dùng nhập và câu trả lời quiz thật; không thêm Tết/Gen Z/nữ mặc định.
Lựa chọn quiz đã bấm được gửi trong `context` và ưu tiên hơn suy luận từ câu tự do.

Sau khi ánh xạ ở frontend, recommendation có `id`, `understanding`, bối cảnh đã phân tích và `concepts`. Mỗi concept:

```json
{
  "id": "concept-1",
  "name": "Modern Tết",
  "outfitCode": "AO_DAI",
  "outfitName": "Áo dài",
  "imageUrl": "/assets/concept-1.webp",
  "colorCode": "DARK_RED",
  "colorName": "Đỏ trầm",
  "styleCode": "GEN_Z",
  "styleName": "Gen Z",
  "matchScore": 94,
  "reason": "Lý do do backend cung cấp",
  "accessoryCodes": []
}
```

Các giá trị trên là ví dụ hợp đồng, không được dùng làm recommendation trong ứng dụng.

## Outfits / assets

`GET /outfits` trả `Outfit[]`; `GET /outfits/{code}` trả một `Outfit`:

```json
{
  "code": "AO_DAI",
  "name": "Áo dài",
  "baseAvatarUrl": "/assets/avatar.png",
  "assets": [{ "id": "red-layer", "url": "/assets/ao-dai-red.png", "colorCode": "DARK_RED", "zIndex": 10 }],
  "colors": [{ "code": "DARK_RED", "label": "Đỏ trầm", "hex": "#923930" }],
  "styles": [{ "code": "GEN_Z", "label": "Gen Z" }],
  "accessories": [{ "code": "FAN", "label": "Quạt", "assetUrl": "/assets/fan.png", "zIndex": 20 }],
  "otherLayers": [{ "id": "shoes", "url": "/assets/shoes.png", "zIndex": 30 }]
}
```

`otherLayers` là tùy chọn. Asset không có `colorCode` là layer mặc định. Layer base có z-index 0. Outfit, phụ kiện và các layer khác dùng mặc định lần lượt 10, 20, 30. Mọi ảnh dùng chung canvas/điểm neo; thứ tự được backend quy định.

## Cultural knowledge

`GET /outfits/{code}/cultural-knowledge`

```json
{
  "name": "Áo dài",
  "origin": "Nội dung đã được kiểm chứng từ backend",
  "meaning": "Nội dung đã được kiểm chứng từ backend",
  "characteristics": "Nội dung đã được kiểm chứng từ backend",
  "sources": [{ "title": "Tên tài liệu nguồn", "url": "https://example.org/source" }]
}
```

Frontend chỉ render văn bản; không render HTML từ backend. `sources` tùy chọn, chỉ mở liên kết HTTP/HTTPS.

## Cấu hình bản phối chung

`MixConfig` được dùng làm body cho cultural-score và tạo look:

```json
{
  "conceptId": "concept-1",
  "outfitCode": "AO_DAI",
  "colorCode": "DARK_RED",
  "styleCode": "GEN_Z",
  "eventCode": "TET",
  "accessoryCodes": ["FAN"]
}
```

## Remix

`POST /remix`: body gồm toàn bộ trường `MixConfig` và `prompt`.

```json
{
  "changes": { "colorCode": "DARK_RED", "styleCode": "GEN_Z", "removeAccessories": ["NON_LA"], "addAccessories": ["MINIMAL_BAG"] },
  "explanation": "Giải thích thay đổi từ backend"
}
```

Mọi trường trong `changes` là tùy chọn. Mã được trả về phải có trong catalog outfit. Backend chịu trách nhiệm sinh bản phối hợp lệ.

## Cultural score

`POST /cultural-score`: body `MixConfig`.

```json
{
  "score": 72,
  "level": "WARNING",
  "warnings": [{
    "severity": "MEDIUM",
    "category": "ACCESSORY",
    "message": "Giải thích từ backend",
    "suggestion": "Gợi ý chỉnh sửa từ backend",
    "changes": { "removeAccessories": ["NON_LA"] }
  }]
}
```

`changes` trên warning là phần mở rộng tùy chọn để hiện nút “Áp dụng gợi ý”; thiếu trường này vẫn hiển thị gợi ý văn bản. `score` trong khoảng 0–100, `warnings` luôn là mảng. Frontend không tính điểm hoặc xác định cultural rule.

## Looks

`POST /looks`: body `MixConfig`. `GET /looks/{id}`: lấy lại look. Cả hai trả cùng kiểu:

```json
{
  "id": "look-1",
  "name": "Modern Tết",
  "imageUrl": "/assets/final-look-1.webp",
  "outfitCode": "AO_DAI",
  "outfitName": "Áo dài",
  "styleName": "Gen Z",
  "eventName": "Tết",
  "matchScore": 94,
  "culturalScore": 87,
  "colorHarmony": 91,
  "config": { "conceptId": "concept-1", "outfitCode": "AO_DAI", "colorCode": "DARK_RED", "styleCode": "GEN_Z", "eventCode": "TET", "accessoryCodes": [] }
}
```

`culturalKnowledge` tùy chọn cùng kiểu response cultural-knowledge; thiếu trường này frontend gọi endpoint riêng. Backend tạo/persist look và ảnh cuối cùng. Lưu yêu thích hiện là localStorage, chia sẻ dùng URL `/look/{id}`.
