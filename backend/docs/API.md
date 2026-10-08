# API VIỆT FIT

Base URL: `http://localhost/api` với Docker; `http://localhost:8080/api` khi chạy JVM.

| Method | Path | Chức năng |
|---|---|---|
| GET | /health | Kiểm tra backend và kết nối DB |
| GET | /outfits | Danh sách 5 trang phục |
| GET | /outfits/{code} | Chi tiết, màu, assets và phụ kiện được hỗ trợ |
| GET | /outfits/{code}/cultural-knowledge | Kiến thức kèm nguồn |
| GET | /reference-data | Danh mục cho frontend |
| GET | /weather?city=Hanoi | city, temperature (°C), condition, humidity (%) |
| POST | /recommendations | 3 concept đã kiểm tra mã |
| POST | /remix | Đề xuất thay đổi look đã kiểm tra |
| POST | /cultural-score | Điểm, breakdown, cảnh báo và nguồn |
| POST | /looks | Lưu look, HTTP 201 + Location |
| GET | /looks/{id} | Đọc look đã lưu |

## Gợi ý

```json
{
  "prompt": "Tôi đi lễ hội ở Hà Nội, muốn phong cách Gen Z",
  "city": "Hanoi",
  "eventCode": "FESTIVAL",
  "styleCode": "GEN_Z"
}
```

Response: `analysis` chứa event từ request, weather do backend lấy và styles từ concept;
`concepts` có đúng 3 phần tử, mỗi phần tử gồm
`conceptName, outfitCode, colorCode, styleCode, accessories, matchScore, reason`.
Backend không dùng weather do AI tự trả về.

## Lựa chọn look / chấm điểm văn hóa

```json
{
  "outfitCode": "AO_DAI",
  "colorCode": "RED",
  "styleCode": "GEN_Z",
  "eventCode": "FESTIVAL",
  "accessories": ["NON_LA"]
}
```

Mọi mã đều phải tồn tại. Phụ kiện phải thuộc danh sách hỗ trợ của trang phục và không trùng lặp.
Danh mục màu hiện áp dụng chung cho 5 trang phục; assets ảnh được cấp riêng khi có tài nguyên.
Không có asset ảnh thì API trả `assets: []`; frontend không nên dựng URL ảnh giả.

Công thức: mỗi tiêu chí khởi đầu 100, cộng tất cả `score_modifier` của rule khớp,
sau đó giới hạn 0–100. Điểm tổng là tổng có trọng số, làm tròn:
structure 30%, garmentCharacteristics 25%, accessories 20%, context 15%, modernRemix 10%.
Rule khớp theo outfit/color/style/event hoặc phụ kiện hiện có; mỗi rule tính một lần.

Chỉ tính điểm tổng khi outfit có rule được kiểm chứng cho cả 5 tiêu chí.
Nếu thiếu, response trả `score: null, level: "INSUFFICIENT_DATA"`, danh sách
`missingCategories` và breakdown có `null` ở tiêu chí thiếu. Cảnh báo của rule đã có vẫn hiển thị.
Đây là mở rộng contract để biểu đạt dữ liệu chưa đủ; không tự gán 100 điểm khi DB chưa có rule.

Level: `WELL_PRESERVED` (90–100), `SUITABLE` (75–89), `WARNING` (60–74), `HIGH_RISK` (0–59).
Cảnh báo có severity, category, message, suggestion, sourceName, sourceUrl.
Trọng số và thuật toán này là định hướng MVP; cần kiểm chứng trước khi coi là đánh giá chính thức.

## Remix

```json
{
  "currentLook": {
    "outfitCode": "AO_DAI",
    "colorCode": "RED",
    "styleCode": "GEN_Z",
    "eventCode": "FESTIVAL",
    "accessories": ["NON_LA"]
  },
  "prompt": "Cho outfit trẻ hơn nhưng vẫn giữ màu đỏ."
}
```

Response:

```json
{
  "changes": {
    "colorCode": "DARK_RED",
    "styleCode": "GEN_Z",
    "removeAccessories": ["NON_LA"],
    "addAccessories": ["MINIMAL_BAG"]
  },
  "explanation": "..."
}
```

`colorCode/styleCode` có thể thiếu hoặc null, nghĩa là giữ nguyên.
Danh sách thêm/xóa luôn bắt buộc. Không xóa phụ kiện chưa chọn, thêm phụ kiện đã chọn,
hay đồng thời thêm và xóa cùng mã. Backend kiểm tra look sau khi áp dụng thay đổi.
Frontend áp dụng changes rồi gọi lại cultural-score; remix không tự lưu.

## Lưu look

Body giống lựa chọn look, thêm tùy chọn `originalPrompt` và `previewImageUrl` (HTTP/HTTPS).
Backend tính `culturalScore`, không nhận điểm do frontend gửi.
`styleMatchScore/colorHarmonyScore` đang null vì đặc tả chưa định nghĩa thuật toán tính/lưu tin cậy.
Nếu chưa đủ rule, look vẫn lưu được với `culturalScore: null`.
GET trả điểm tại thời điểm lưu; POST cultural-score đánh giá lại theo rule hiện tại.

Ảnh preview do frontend dựng từ layer 2D và cung cấp URL đã lưu; backend này lưu URL,
chưa có API upload, render ảnh hoặc tạo ảnh bằng Gemini.

## Lỗi

```json
{
  "code": "INVALID_SELECTION",
  "message": "Mã màu không được hỗ trợ.",
  "fields": {},
  "timestamp": "2026-10-08T00:00:00Z"
}
```

400: JSON/validation/lựa chọn sai. 404: không tìm thấy.
502: AI/weather lỗi, timeout hoặc dữ liệu AI không hợp lệ.
503: chưa cấu hình Weather API key.
Không trả provider body, API key hoặc stack trace xuống frontend.
JSON có trường ngoài contract bị từ chối.

Weather condition: CLEAR, CLOUDS, RAIN, SNOW, FOG, THUNDERSTORM, OTHER.
Timeout kết nối 5s, weather 10s, AI 45s.
