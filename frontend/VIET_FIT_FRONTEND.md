# VIỆT FIT -- Frontend Specification

## 1. Công nghệ

-   React
-   Vite
-   TypeScript
-   Tailwind CSS
-   React Router
-   Axios

Frontend chịu trách nhiệm về trải nghiệm người dùng, hiển thị dữ liệu,
2D Mix Studio và giao tiếp với Spring Boot API. Frontend không chứa
Gemini API key, Weather API key hoặc logic tính Cultural Score.

------------------------------------------------------------------------

## 2. Luồng người dùng

``` text
HOME
 ↓
✨ AI VIỆT STYLIST
 ↓
[Gợi ý nhanh] / [Viết mong muốn]
 ↓
LẤY THỜI TIẾT THỰC TẾ
 ↓
AI HIỂU NHU CẦU
 ├── Sự kiện
 ├── Thời tiết
 ├── Màu sắc
 └── Phong cách
 ↓
AI TẠO 3 CONCEPT OUTFIT
 ↓
📖 Đọc nguồn gốc / ý nghĩa trang phục
 ↓
NGƯỜI DÙNG CHỌN CONCEPT
 ↓
MIX / REMIX
 ↓
🛡 CULTURAL CHECK
 ├── Cultural Score
 ├── Cảnh báo kết hợp có nguy cơ sai lệch
 └── Gợi ý chỉnh sửa
 ↓
GENERATE LOOK
 ↓
📖 BẠN ĐANG MẶC GÌ?
 ↓
LƯU / CHIA SẺ
```

------------------------------------------------------------------------

## 3. Các trang chính

Frontend MVP gồm 5 page.

  ----------------------------------------------------------------------------
  Route                   Page                    Chức năng
  ----------------------- ----------------------- ----------------------------
  `/`                     `HomePage.tsx`          Landing page, giới thiệu sản
                                                  phẩm

  `/stylist`              `StylistPage.tsx`       Nhập prompt, chọn
                                                  event/style/color/location

  `/concepts`             `ConceptPage.tsx`       Hiển thị AI hiểu nhu cầu và
                                                  3 concept

  `/mix/:conceptId`       `MixStudioPage.tsx`     Mix/Remix 2D và Cultural
                                                  Check

  `/look/:lookId`         `FinalLookPage.tsx`     Final Look, kiến thức văn
                                                  hóa, lưu/chia sẻ
  ----------------------------------------------------------------------------

------------------------------------------------------------------------

## 4. Home Page

### Mục tiêu

Giới thiệu sản phẩm và dẫn người dùng vào AI Việt Stylist.

### Nội dung chính

``` text
VIỆT FIT

VIỆT PHỤC REMIX

Mặc chất riêng – Giữ hồn Việt.

AI giúp bạn khám phá và remix
Việt phục theo phong cách riêng.

[✨ BẮT ĐẦU VỚI AI]

Áo dài • Áo tứ thân • Áo ngũ thân
Nhật Bình • Áo bà ba
```

Nút `BẮT ĐẦU VỚI AI` điều hướng tới `/stylist`.

------------------------------------------------------------------------

## 5. AI Việt Stylist

### Route

`/stylist`

### Gợi ý nhanh

``` text
SỰ KIỆN
[Tết] [Lễ hội] [Kỷ yếu] [Chụp ảnh]

PHONG CÁCH
[Gen Z] [Minimal] [Thanh lịch] [Truyền thống]

MÀU SẮC
[Đỏ] [Trắng] [Xanh] [Không quan trọng]

ĐỊA ĐIỂM
[Hà Nội ▼]

🌦 30°C • Có mưa
Độ ẩm: 82%
```

### Prompt tự do

``` text
Mình muốn mặc Việt phục đi chơi Tết,
thích màu đỏ nhưng không quá nổi,
phong cách trẻ trung...

[✨ TẠO OUTFIT]
```

### API sử dụng

``` http
GET /api/weather?city=Hanoi
POST /api/recommendations
```

------------------------------------------------------------------------

## 6. Weather UI

Frontend lấy thời tiết thông qua Spring Boot, không gọi trực tiếp
Weather API có secret.

Response mẫu:

``` json
{
  "city": "Hanoi",
  "temperature": 30,
  "condition": "RAIN",
  "humidity": 82
}
```

Thông tin thời tiết được hiển thị cho người dùng và gửi cùng yêu cầu
recommendation.

------------------------------------------------------------------------

## 7. Concept Page

### Route

`/concepts`

### AI hiểu nhu cầu

``` text
✨ AI HIỂU BẠN ĐANG TÌM

🎎 Tết
📍 Hà Nội
🌧 30°C
🎨 Đỏ trầm
✨ Gen Z
```

### Ba concept

Mỗi `ConceptCard` hiển thị:

-   Ảnh
-   Tên concept
-   Loại Việt phục
-   Màu đề xuất
-   Style
-   Match Score
-   Lý do AI đề xuất
-   `ⓘ Tìm hiểu`
-   `Chọn Concept`

Ví dụ:

``` text
MODERN TẾT

Áo dài
Đỏ trầm
Gen Z

Match 94%

[ⓘ Tìm hiểu]
[Chọn Concept]
```

Gemini sinh 3 concept. Frontend không hard-code recommendation.

------------------------------------------------------------------------

## 8. Cultural Information Modal

Khi người dùng chọn `ⓘ Tìm hiểu`, mở modal/drawer:

``` text
ÁO DÀI

📖 Nguồn gốc
...

🌸 Ý nghĩa văn hóa
...

👘 Đặc trưng
...

[Chọn trang phục này]
```

Dữ liệu lấy từ backend:

``` http
GET /api/outfits/{code}/cultural-knowledge
```

Thông tin văn hóa được lưu và kiểm chứng ở backend/database; không để
Gemini tự tạo fact lịch sử không có nguồn.

------------------------------------------------------------------------

## 9. Mix / Remix Studio

### Route

`/mix/:conceptId`

Đây là màn hình quan trọng nhất.

### Layout desktop

``` text
┌───────────────────────────────────────────────────────────┐
│                      MIX / REMIX                          │
├───────────────┬───────────────────────┬───────────────────┤
│ TÙY CHỈNH     │                       │ CULTURAL CHECK    │
│               │                       │                   │
│ Màu           │                       │       87%         │
│ ● ● ● ●      │      2D MODEL         │                   │
│               │                       │ ✓ Cấu trúc        │
│ Phụ kiện      │          👤           │ ⚠ Phụ kiện       │
│ □ Nón         │                       │ ✓ Bối cảnh        │
│ □ Túi         │                       │                   │
│ □ Quạt        │                       │ 💡 Gợi ý          │
│               │                       │                   │
│ Style         │                       │ [Áp dụng]         │
│ [Gen Z]       │                       │                   │
│ [Minimal]     │                       │                   │
├───────────────┴───────────────────────┴───────────────────┤
│ ✨ "Cho outfit trẻ hơn nhưng vẫn giữ màu đỏ..." [Remix] │
└───────────────────────────────────────────────────────────┘

                     [ GENERATE LOOK ]
```

------------------------------------------------------------------------

## 10. 2D Outfit Engine

Render bằng layer:

``` text
Base Avatar
    +
Outfit Layer
    +
Accessory Layer
    +
Shoes/Other Layer
    =
Final Preview
```

Assets được backend/database định nghĩa qua `outfit_assets` và
`accessories`.

Các component chính:

-   `Avatar2D.tsx`
-   `ColorSelector.tsx`
-   `AccessorySelector.tsx`
-   `StyleSelector.tsx`

------------------------------------------------------------------------

## 11. AI Remix

Người dùng có thể nhập:

> Cho outfit trẻ hơn nhưng vẫn giữ màu đỏ.

Frontend gọi:

``` http
POST /api/remix
```

Response mẫu:

``` json
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

Frontend đọc `changes` và cập nhật Mix Studio.

------------------------------------------------------------------------

## 12. Cultural Check

Cultural Check nằm ngay trong Mix Studio, không cần page riêng.

Khi người dùng thay đổi màu, phụ kiện, style hoặc event:

``` http
POST /api/cultural-score
```

Response mẫu:

``` json
{
  "score": 72,
  "level": "WARNING",
  "warnings": [
    {
      "severity": "MEDIUM",
      "category": "ACCESSORY",
      "message": "Cách kết hợp này có thể làm giảm một số đặc trưng nhận diện của trang phục.",
      "suggestion": "Ưu tiên phụ kiện không che các chi tiết cấu trúc đặc trưng."
    }
  ]
}
```

Frontend hiển thị:

-   Cultural Score
-   Mức độ
-   Cảnh báo
-   Nguyên nhân
-   Gợi ý chỉnh sửa
-   Nút áp dụng gợi ý nếu có

Không tính Cultural Score tại frontend.

------------------------------------------------------------------------

## 13. Final Look Page

### Route

`/look/:lookId`

### Nội dung

``` text
YOUR VIỆT LOOK

MODERN TẾT

[FINAL LOOK IMAGE]

ÁO DÀI • GEN Z • TẾT

✨ Style Match             94%
🛡 Cultural Score          87%
🎨 Color Harmony           91%

────────────────────────────

📖 BẠN ĐANG MẶC GÌ?

ÁO DÀI

Nguồn gốc
...

Ý nghĩa văn hóa
...

Đặc trưng
...

────────────────────────────

[♡ LƯU LOOK]
[↗ CHIA SẺ]
[← REMIX LẠI]
```

------------------------------------------------------------------------

## 14. Cấu trúc thư mục Frontend

``` text
frontend/
├── src/
│   ├── assets/
│   │   ├── avatars/
│   │   ├── outfits/
│   │   └── accessories/
│   │
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Loading.tsx
│   │   ├── ai/
│   │   │   ├── PromptBox.tsx
│   │   │   └── AiSuggestion.tsx
│   │   ├── concept/
│   │   │   ├── ConceptCard.tsx
│   │   │   └── CulturalInfoModal.tsx
│   │   ├── mix/
│   │   │   ├── Avatar2D.tsx
│   │   │   ├── ColorSelector.tsx
│   │   │   ├── AccessorySelector.tsx
│   │   │   └── StyleSelector.tsx
│   │   └── cultural/
│   │       ├── CulturalScore.tsx
│   │       └── CulturalWarning.tsx
│   │
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── StylistPage.tsx
│   │   ├── ConceptPage.tsx
│   │   ├── MixStudioPage.tsx
│   │   └── FinalLookPage.tsx
│   │
│   ├── services/
│   │   ├── api.ts
│   │   ├── outfitApi.ts
│   │   ├── recommendationApi.ts
│   │   ├── weatherApi.ts
│   │   ├── culturalApi.ts
│   │   ├── remixApi.ts
│   │   └── lookApi.ts
│   │
│   ├── types/
│   ├── App.tsx
│   └── main.tsx
├── .env
├── package.json
└── vite.config.ts
```

------------------------------------------------------------------------

## 15. API Frontend cần sử dụng

``` text
GET  /api/outfits
GET  /api/outfits/{code}
GET  /api/outfits/{code}/cultural-knowledge

GET  /api/weather?city=Hanoi

POST /api/recommendations
POST /api/remix
POST /api/cultural-score

POST /api/looks
GET  /api/looks/{id}
```

------------------------------------------------------------------------

## 16. Trách nhiệm Frontend

Frontend chịu trách nhiệm:

-   Nhập nhu cầu người dùng
-   Chọn event/style/color/location
-   Hiển thị thời tiết
-   Hiển thị 3 AI concepts
-   Hiển thị thông tin nguồn gốc/ý nghĩa Việt phục
-   2D Mix Studio
-   Manual Mix
-   AI Remix
-   Hiển thị Cultural Score realtime
-   Hiển thị Cultural Warning
-   Generate/hiển thị Final Look
-   Save/Share

Frontend không chịu trách nhiệm:

-   Tính Cultural Score
-   Quyết định cultural rule
-   Gọi trực tiếp Gemini bằng secret key
-   Gọi trực tiếp Weather API bằng secret key
-   Tạo dữ liệu lịch sử/văn hóa không có nguồn

------------------------------------------------------------------------

## 17. Ưu tiên triển khai

1.  Router + 5 pages
2.  Stylist form
3.  Concept cards
4.  Mix Studio layout
5.  2D layering
6.  Cultural Check UI
7.  Final Look
8.  Kết nối API thật
9.  Loading/error/fallback
10. Responsive và polish UI
