fu# VIỆT FIT -- Backend Specification

## 1. Công nghệ

-   Java 21
-   Gradle với Groovy DSL (`build.gradle`, `settings.gradle`)
-   Spring Boot 3
-   Spring Web
-   Spring Data JPA
-   Hibernate
-   PostgreSQL
-   Lombok
-   Bean Validation
-   WebClient / HTTP Client

Spring Boot là gateway trung tâm giữa React, PostgreSQL, AI
Service/Gemini và Weather API.

------------------------------------------------------------------------

## 2. Kiến trúc

``` text
React Frontend
      │
      ▼
Spring Boot Backend
      │
      ├──────────► PostgreSQL
      │
      ├──────────► Weather API
      │
      └──────────► AI FastAPI
                       │
                       ▼
                     Gemini
```

Frontend không gọi trực tiếp Gemini hoặc Weather API có secret.

------------------------------------------------------------------------

## 3. Trách nhiệm Backend

Backend chịu trách nhiệm:

-   Cung cấp dữ liệu outfit/reference data
-   Validate outfit/color/style/accessory/event code
-   Gọi Weather API
-   Gọi AI Service
-   Validate JSON Gemini trả về
-   Cung cấp Cultural Knowledge
-   Tính Cultural Compatibility Score
-   Sinh Cultural Warning
-   Lưu Final Look
-   Cung cấp API cho frontend
-   Giữ API keys/secrets an toàn

Gemini không được dùng làm nguồn quyết định Cultural Score.

------------------------------------------------------------------------

## 4. Cấu trúc thư mục

``` text
backend/
├── src/main/java/com/vietphuc/remix/
│   ├── controller/
│   │   ├── OutfitController.java
│   │   ├── RecommendationController.java
│   │   ├── CulturalScoreController.java
│   │   ├── AiController.java
│   │   ├── WeatherController.java
│   │   └── LookController.java
│   │
│   ├── service/
│   │   ├── OutfitService.java
│   │   ├── RecommendationService.java
│   │   ├── CulturalScoreService.java
│   │   ├── AiService.java
│   │   ├── WeatherService.java
│   │   └── LookService.java
│   │
│   ├── repository/
│   │
│   ├── entity/
│   │
│   ├── dto/
│   │   ├── request/
│   │   └── response/
│   │
│   ├── client/
│   │   ├── AiClient.java
│   │   └── WeatherClient.java
│   │
│   ├── mapper/
│   ├── exception/
│   ├── config/
│   ├── enums/
│   └── VietPhucRemixApplication.java
│
├── src/main/resources/
│   └── application.properties
├── build.gradle
├── settings.gradle
├── gradlew
├── gradlew.bat
├── gradle/wrapper/
└── .env
```

------------------------------------------------------------------------

## 5. Database

Core database gồm 11 bảng:

1.  `outfits`
2.  `colors`
3.  `outfit_assets`
4.  `accessories`
5.  `outfit_accessories`
6.  `styles`
7.  `events`
8.  `cultural_rules`
9.  `cultural_knowledge`
10. `looks`
11. `look_accessories`

Weather không cần lưu thành bảng cho MVP.

------------------------------------------------------------------------

## 6. outfits

``` text
outfits
-------------------------
id                  PK
code                UNIQUE NOT NULL
name                NOT NULL
description
origin
cultural_meaning
thumbnail_url
created_at
updated_at
```

Seed 5 outfit:

``` text
AO_DAI
AO_TU_THAN
AO_NGU_THAN
NHAT_BINH
AO_BA_BA
```

------------------------------------------------------------------------

## 7. colors

``` text
colors
-------------------------
id                  PK
code                UNIQUE
name
hex_code
```

Ví dụ:

``` text
RED
DARK_RED
WHITE
BLUE
YELLOW
BLACK
CREAM
```

------------------------------------------------------------------------

## 8. outfit_assets

``` text
outfit_assets
-------------------------
id                  PK
outfit_id           FK → outfits.id
color_id            FK → colors.id
asset_type
variant_code
image_url
layer_order
```

Dùng để map outfit/color sang layer ảnh 2D.

------------------------------------------------------------------------

## 9. accessories

``` text
accessories
-------------------------
id                  PK
code                UNIQUE
name
type
description
image_url
layer_order
```

Ví dụ:

``` text
NON_LA
FAN
MINIMAL_BAG
WHITE_SNEAKERS
```

------------------------------------------------------------------------

## 10. outfit_accessories

Quan hệ N:M giữa outfit và accessory.

``` text
outfit_accessories
-------------------------
outfit_id           PK, FK → outfits.id
accessory_id        PK, FK → accessories.id
compatibility_score
```

Cho biết accessory nào được hệ thống hỗ trợ/cho phép hiển thị với từng
outfit.

------------------------------------------------------------------------

## 11. styles

``` text
styles
-------------------------
id                  PK
code                UNIQUE
name
description
```

Seed:

``` text
TRADITIONAL
GEN_Z
MINIMAL
ELEGANT
VINTAGE
```

------------------------------------------------------------------------

## 12. events

``` text
events
-------------------------
id                  PK
code                UNIQUE
name
description
```

Seed:

``` text
TET
FESTIVAL
GRADUATION
PHOTOSHOOT
CULTURAL_EVENT
```

------------------------------------------------------------------------

## 13. cultural_rules

Dùng cho Cultural Check và Cultural Compatibility Score.

``` text
cultural_rules
-------------------------
id                  PK
outfit_id           FK → outfits.id
category
target_type
target_code
rule_type
score_modifier
severity
message
suggestion
source_name
source_url
created_at
```

`severity`:

``` text
LOW
MEDIUM
HIGH
```

`rule_type`:

``` text
RECOMMENDED
CAUTION
INCOMPATIBLE
```

Rule thực tế phải được kiểm chứng văn hóa trước khi seed.

------------------------------------------------------------------------

## 14. cultural_knowledge

Lưu kiến thức văn hóa đã kiểm chứng.

``` text
cultural_knowledge
-------------------------
id                  PK
outfit_id           FK → outfits.id
category
title
content
source_name
source_url
created_at
```

Category gợi ý:

``` text
HISTORY
STRUCTURE
MEANING
USAGE
STYLING
```

Dùng cho:

-   `ⓘ Tìm hiểu`
-   `Bạn đang mặc gì?`
-   Grounding cho Gemini khi cần giải thích

------------------------------------------------------------------------

## 15. looks

Lưu Final Look.

``` text
looks
-------------------------
id                  PK
outfit_id           FK → outfits.id
color_id            FK → colors.id
style_id            FK → styles.id
event_id            FK → events.id
original_prompt
style_match_score
cultural_score
color_harmony_score
preview_image_url
created_at
updated_at
```

------------------------------------------------------------------------

## 16. look_accessories

Quan hệ N:M giữa Look và Accessory.

``` text
look_accessories
-------------------------
look_id             PK, FK → looks.id
accessory_id        PK, FK → accessories.id
```

------------------------------------------------------------------------

## 17. Quan hệ database

``` text
                         OUTFITS
                            │
          ┌─────────────────┼────────────────┐
          ▼                 ▼                ▼
   OUTFIT_ASSETS    CULTURAL_RULES   CULTURAL_KNOWLEDGE
          │
          ▼
        COLORS

OUTFITS
   │
   ▼
OUTFIT_ACCESSORIES
   │
   ▼
ACCESSORIES

                     LOOKS
            ┌──────────┼───────────┐
            ▼          ▼           ▼
          COLORS     STYLES      EVENTS
            │
OUTFITS ────┤
            ▼
    LOOK_ACCESSORIES
            │
            ▼
       ACCESSORIES
```

------------------------------------------------------------------------

## 18. API chính

### Outfit

``` http
GET /api/outfits
GET /api/outfits/{code}
```

### Cultural Knowledge

``` http
GET /api/outfits/{code}/cultural-knowledge
```

### Weather

``` http
GET /api/weather?city=Hanoi
```

### AI Recommendation

``` http
POST /api/recommendations
```

### AI Remix

``` http
POST /api/remix
```

### Cultural Check

``` http
POST /api/cultural-score
```

### Look

``` http
POST /api/looks
GET /api/looks/{id}
```

------------------------------------------------------------------------

## 19. Weather Flow

``` text
React
 ↓
GET /api/weather?city=Hanoi
 ↓
WeatherController
 ↓
WeatherService
 ↓
WeatherClient
 ↓
Weather API
 ↓
temperature / condition / humidity
 ↓
Spring Boot
 ↓
React
```

Backend chỉ trả các field cần thiết:

``` json
{
  "city": "Hanoi",
  "temperature": 30.5,
  "condition": "RAIN",
  "humidity": 82
}
```

API key đặt ở backend environment, không gửi xuống React.

------------------------------------------------------------------------

## 20. Recommendation Flow

Frontend gửi:

``` json
{
  "prompt": "Mình muốn đi lễ hội, thích phong cách trẻ trung.",
  "city": "Hanoi",
  "eventCode": "FESTIVAL",
  "styleCode": "GEN_Z"
}
```

Backend xử lý:

``` text
RecommendationController
          ↓
RecommendationService
          │
          ├── WeatherService
          │       ↓
          │   Weather API
          │
          ├── OutfitRepository / reference data
          │
          ├── Cultural Knowledge nếu cần
          │
          └── AiClient
                  ↓
              AI FastAPI
                  ↓
                Gemini
```

Gemini nhận:

-   Prompt
-   Event
-   Current Weather
-   5 supported outfits
-   Allowed colors
-   Allowed styles
-   Allowed accessories
-   Cultural context cần thiết

Gemini trả đúng 3 concept.

Response ví dụ:

``` json
{
  "analysis": {
    "event": "FESTIVAL",
    "weather": {
      "condition": "HOT",
      "temperature": 31
    },
    "styles": ["GEN_Z"]
  },
  "concepts": [
    {
      "conceptName": "Modern Festival",
      "outfitCode": "AO_DAI",
      "colorCode": "DARK_RED",
      "styleCode": "GEN_Z",
      "accessories": ["MINIMAL_BAG"],
      "matchScore": 92,
      "reason": "Concept được lựa chọn dựa trên bối cảnh lễ hội, thời tiết và phong cách người dùng."
    }
  ]
}
```

Backend phải validate mọi code Gemini trả về trước khi trả cho frontend.

------------------------------------------------------------------------

## 21. AI Remix Flow

Frontend gửi outfit hiện tại và prompt remix:

``` text
"Cho outfit trẻ hơn nhưng vẫn giữ màu đỏ."
```

Backend gọi AI Service/Gemini.

Response chuẩn:

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

Backend validate `colorCode`, `styleCode` và accessory codes.

------------------------------------------------------------------------

## 22. Cultural Check Flow

``` text
Current Look
    ↓
CulturalScoreController
    ↓
CulturalScoreService
    ↓
cultural_rules
    ↓
Rule Evaluation
    ↓
Score + Warnings
```

Request có thể chứa:

``` json
{
  "outfitCode": "AO_DAI",
  "colorCode": "RED",
  "styleCode": "GEN_Z",
  "eventCode": "TET",
  "accessories": ["MINIMAL_BAG"]
}
```

Response:

``` json
{
  "score": 87,
  "level": "SUITABLE",
  "breakdown": {
    "structure": 95,
    "garmentCharacteristics": 90,
    "accessories": 78,
    "context": 90,
    "modernRemix": 82
  },
  "warnings": []
}
```

Nếu có vấn đề:

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

------------------------------------------------------------------------

## 23. Cultural Score

Công thức định hướng:

``` text
Structure/Form                 30%
Garment Characteristics       25%
Accessories                    20%
Context                        15%
Modern Remix                   10%
```

Mức hiển thị:

``` text
90–100   🟢 Bảo tồn tốt
75–89    🔵 Phù hợp
60–74    🟡 Cần cân nhắc
0–59     🔴 Có nguy cơ sai lệch
```

Đây là `Cultural Compatibility Score`, không phải phán quyết tuyệt đối
về đúng/sai văn hóa.

Trọng số và rule phải được kiểm chứng trước khi coi là dữ liệu chính
thức.

------------------------------------------------------------------------

## 24. Gemini làm gì?

Gemini được phép:

-   Hiểu prompt
-   Phân tích nhu cầu
-   Kết hợp weather + event + preference
-   Sinh 3 concept
-   Giải thích lý do recommendation
-   Hiểu prompt Remix
-   Đề xuất thay đổi outfit

Gemini không được:

-   Tự tạo loại outfit ngoài 5 loại hỗ trợ
-   Trả code không tồn tại
-   Tự bịa lịch sử/văn hóa
-   Tự tính Cultural Score
-   Tự quyết tuyệt đối đúng/sai văn hóa

------------------------------------------------------------------------

## 25. Spring Boot làm gì?

Spring Boot chịu trách nhiệm:

-   Reference data
-   Database access
-   Validate AI output
-   Weather API gateway
-   AI Service gateway
-   Cultural Knowledge
-   Cultural Rules
-   Cultural Score
-   Cultural Warning
-   Save Look
-   Error handling
-   API contract
-   Secrets

------------------------------------------------------------------------

## 26. Security / Configuration

Secrets chỉ nằm ở backend/AI service:

``` text
DATABASE_URL
DATABASE_USERNAME
DATABASE_PASSWORD
WEATHER_API_KEY
AI_SERVICE_URL
```

Gemini key nằm trong AI service, không nằm ở React.

Production:

``` text
Internet
   ↓
Nginx :80/:443
   ├── React
   └── /api → Spring Boot :8080
                     │
                     ├── PostgreSQL :5432
                     ├── AI Service :8000
                     └── Weather API
```

Chỉ port 80/443 public.

------------------------------------------------------------------------

## 27. Thứ tự triển khai Backend

### Ngày 1

-   Khởi tạo Spring Boot
-   PostgreSQL
-   11 entities
-   Repositories
-   Seed 5 outfits/reference data
-   Outfit API
-   Cultural Knowledge API
-   Weather API integration

### Ngày 2

-   Recommendation API
-   `AiClient`
-   Gemini/FastAPI integration
-   CulturalScoreService
-   Cultural Warning
-   Remix API

### Ngày 3

-   Look API
-   Validate AI responses
-   Global exception handling
-   End-to-end integration
-   Deployment
-   Test demo flow

------------------------------------------------------------------------

## 28. Demo flow mục tiêu

``` text
"Tôi đi lễ hội ở Hà Nội, muốn phong cách Gen Z"
        ↓
Backend lấy thời tiết thật
        ↓
Gemini tạo 3 concept
        ↓
User đọc nguồn gốc / ý nghĩa
        ↓
Chọn concept
        ↓
Mix / AI Remix
        ↓
Cultural Check
        ↓
Score + Warning + Suggestion
        ↓
Generate Final Look
        ↓
Save / Share
```

Đây là luồng cần ưu tiên chạy ổn trước khi thêm login, admin, social
feed, 3D hoặc các tính năng phụ.
