# Hướng dẫn merge nhánh `vietfit` của Thắng vào `main`

> Gửi: **Thắng (N.D.Thang)** · Người viết: Khai (V.Q.Khai) · Repo: <https://github.com/Vietfitremix/NepAoPrj>
> Đọc hết phần **1–3** trước khi gõ lệnh nào. Phần **4–5** là các bước làm. Phần **6–9** là danh sách thay đổi, cách chạy và cách kiểm tra.

---

## 1. Tóm tắt trong 1 phút

- Nhánh `vietfit` của Thắng (commit **`240f26e`**, 1 commit) tách ra từ `main` ở commit **`bf8e5f4`**.
- Sau đó Khai đã **đưa nội dung của `240f26e` vào `main`** (người mẫu PNG, tủ đồ, giao diện studio, khớp phụ kiện…), rồi sửa tiếp trên `main`.
  Việc này được làm bằng cách **chép nội dung**, không phải `git merge`, nên Git **không biết** `main` đã chứa `240f26e`.
- Vì vậy nếu chạy thẳng `git merge origin/main` trên nhánh `vietfit` sẽ ra **khoảng 38 đường dẫn xung đột**
  (mình đã chạy thử trên một bản sao tạm rồi huỷ merge, repo thật không bị ảnh hưởng: đa số là xung đột do hai bên cùng sửa/thêm một file, không phải mất file).
- **Khuyến nghị: cách A** (mục 4): bắt đầu từ `main` mới nhất, rồi mang *phần việc Thắng làm thêm* sang. Ít xung đột nhất, không phải giải quyết lại những gì đã gộp.
  Cách B (mục 5) là `git merge` trực tiếp, kèm bảng cách xử lý từng xung đột.
- **Thư mục `assets/` rất nặng:** trên `vietfit` có **1151 file, khoảng 587 MB** (ảnh nguồn, turnaround, reference, gói archive…). `main` **cố ý không chứa** chúng, chỉ giữ 13 file `left.png` mà giao diện cần.
  Ứng dụng chạy bằng ảnh trong `frontend/public/figure/` (giống hệt hai nhánh) cộng 13 file đó. **Đừng đưa 587 MB này vào `main`** nếu chưa thống nhất (xem mục 4, bước 2 và mục 9).

### Các mốc commit

| Commit | Tác giả | Nội dung |
| --- | --- | --- |
| `bf8e5f4` | codecodecode | Gốc chung của hai nhánh |
| `240f26e` | Nguyen Duy Thang | Nhánh `vietfit`: wardrobe assets, character accessory fitting |
| `d142b60` | codecodecode | Gộp nội dung `vietfit` (người mẫu/giao diện của Thắng) + lõi AI Nếp Áo |
| `d6392c9` | codecodecode | Chấm điểm chặt hơn, AI Remix biết phân tích, thẻ Lookbook |
| `b19500c` | codecodecode | Logo, in đậm, tủ đồ gọn, nón lá, gợi ý đúng màu/đa dạng (V13, V14) |
| `cd5647e` | codecodecode | "MVP": dải ✳ trang chủ, khung Studio 3D ngang nhau |

> Ngoài ra có một sửa nhỏ **chưa push** lúc viết tài liệu này (màu quần nam khi chấm hài hoà màu, xem mục 6.1). Khai sẽ push trước khi Thắng merge; hãy `git fetch` rồi xem `git log origin/main -3` để chắc đã có.

---

## 2. Vì sao không merge thẳng được (để Thắng hiểu rõ)

`git merge` so ba điểm: gốc chung (`bf8e5f4`), nhánh của Thắng, và `main`. Với một file mà **cả hai phía đều đổi so với gốc**, Git buộc phải hỏi.
Phần lớn file giao diện/AI nằm trong tình huống đó, kể cả khi hai phía đang giống nhau 90%. Có ba kiểu xung đột:

1. **content / add-add**: cả hai cùng sửa/thêm file (ví dụ `MaleStudioPage.tsx`, `accessoryFit.ts`). Cách xử lý chung: **lấy bản `main`** vì nó đã chứa phần của Thắng + sửa thêm.
2. **rename/delete**: `main` chuyển `frontend/src/components/ai/ScoreCardView.tsx` → `components/look/ScoreCard.tsx` (và `ShareDialog`), còn `vietfit` đã xoá thư mục `components/ai/`. Cách xử lý: **giữ bản trong `components/look/`**.
3. **thư mục `tools/`**: `vietfit` chuyển các script về `frontend/tools/`, `main` đã xoá bộ công cụ dựng người mẫu SVG cũ. Cách xử lý: **giữ `frontend/tools/` của Thắng** nếu còn dùng (mục 5).

---

## 3. Chuẩn bị (làm trước khi chạm vào code)

1. **Sao lưu mọi thứ của Thắng**, kể cả thay đổi chưa commit:
   ```bash
   git status                              # xem còn gì chưa commit
   git branch backup/vietfit-truoc-merge   # nhánh sao lưu (từ nhánh hiện tại của Thắng)
   git stash push -u -m "thang-wip"        # chỉ khi còn thay đổi chưa commit; lấy lại bằng: git stash pop
   ```
2. **Lấy bản mới nhất từ GitHub**:
   ```bash
   git fetch origin
   git log origin/main --oneline -6        # phải thấy "MVP" (cd5647e) hoặc commit mới hơn
   ```
3. **Xác định phần việc mới của Thắng** sau `240f26e` (nếu có). Đây là thứ cần giữ bằng mọi giá:
   ```bash
   git diff 240f26e HEAD -- . ':!assets' > ../thang-viec-moi.patch      # các commit đã làm sau 240f26e (bỏ thư mục assets/ quá nặng)
   git diff HEAD -- . ':!assets' >> ../thang-viec-moi.patch              # cả thay đổi chưa commit
   ```
   Nếu nhánh của Thắng không có gì sau `240f26e` thì file patch rỗng, bỏ qua bước "mang việc mới sang".
4. **Công cụ cần có**: Node 22, Java 21, Python 3.11/3.12, PostgreSQL (README ghi 17/18), Git. Chi tiết chạy ở mục 7.

---

## 4. Cách A (khuyến nghị): bắt đầu từ `main`, mang phần của Thắng sang

```bash
# 1. Nhánh làm việc mới, tách từ main
git checkout -b thang/merge-main origin/main

# 2. Khôi phục những thứ nhỏ chỉ có ở nhánh vietfit (KHÔNG lấy cả thư mục assets/ 587 MB)
git checkout origin/vietfit -- frontend/tools    # (tuỳ chọn) script dựng người mẫu cũ, nếu Thắng còn cần
# Ảnh nguồn assets/ vẫn nằm nguyên trên nhánh vietfit và trên máy Thắng, không mất. Xem mục 9 về cách lưu lâu dài.

# 3. Mang phần việc mới của Thắng (nếu có) lên trên main
git apply --3way ../thang-viec-moi.patch         # nếu báo xung đột: sửa tay (xem mục 5.3), rồi git add

# 4. Chạy kiểm tra (mục 8), rồi commit
git add -A
git commit -m "Gộp công việc của Thắng trên nền main mới nhất"

# 5. Đẩy nhánh và mở Pull Request vào main (đừng push thẳng vào main)
git push -u origin thang/merge-main
```

Ghi chú:
- Bước 2 chỉ **thêm** file, không đụng code đang chạy.
- Nếu muốn có đủ ảnh nguồn ngay trên máy để dựng lại người mẫu: giữ nhánh `vietfit` (hoặc thư mục `assets/` đang có trên máy) làm nơi lưu, **không `git add` nó vào nhánh merge**.
- `ai-service/integration/` (các script ghép nối một lần của nhánh `vietfit`) **đã bị bỏ** trên `main` vì đã áp dụng xong. Muốn giữ thì `git checkout origin/vietfit -- ai-service/integration`, nhưng không cần cho việc chạy ứng dụng.
- Nếu `git apply --3way` báo thiếu file gốc, dùng cách thủ công: mở từng file Thắng đã sửa, so với bản trong `main`, chép phần mới sang.

---

## 5. Cách B: merge trực tiếp `main` vào nhánh của Thắng

Dùng khi Thắng muốn giữ nguyên lịch sử commit của mình.

```bash
git checkout vietfit                 # nhánh làm việc của Thắng
git merge origin/main                # sẽ báo ~38 xung đột, đó là bình thường
```

Trong lúc đang merge: **"ours" = nhánh của Thắng, "theirs" = `main`**.

### 5.1. Bảng xử lý từng nhóm xung đột

| Nhóm | File | Cách xử lý | Lý do |
| --- | --- | --- | --- |
| **Cấu hình & README** | `.env.example`, `README.md`, `ai-service/README.md`, `start-all.ps1`, `frontend/vite.config.ts`, `frontend/index.html` | Lấy **`main`** (theirs) | `main` đã bỏ khoá OpenWeather bị lộ, thêm proxy `/ai` ở Vite, AI đọc JSON mặc định, thêm favicon/font |
| **AI service** | `ai-service/app/api/routers/backend.py`, `ai-service/app/api/routers/wardrobe_score.py`, `ai-service/app/main.py`, `ai-service/tests/test_backend_contract.py` | Lấy **`main`** | Đây là phần lõi AI đã nâng cấp (mục 6.1). Nếu Thắng có sửa riêng, ghi lại rồi chép tay vào sau |
| **Giao diện trang** | `frontend/src/pages/ConceptPage.tsx`, `FinalLookPage.tsx`, `MixStudioPage.tsx`, `MaleStudioPage.tsx` | Lấy **`main`** | `main` chứa giao diện của Thắng + Lookbook, Remix, tab tủ đồ. Phần Thắng sửa sau `240f26e` thì chép thêm |
| **Thành phần & tiện ích** | `components/mix/WardrobeFigure.tsx`, `components/common/Header.tsx`, `src/main.tsx`, `src/styles.css`, `utils/accessoryFit.ts`, `utils/outfitPreview.ts`, `utils/stylistQuiz.ts`, `tests/accessoryFit.test.mjs`, `tests/stylistQuiz.test.mjs` | Lấy **`main`** | Có sửa nón lá, màu quần mới, quiz gửi đúng ngữ cảnh. **`accessoryFit.ts` đặc biệt**: xem mục 6.3 nếu Thắng đã sửa file này |
| **Đổi tên / xoá** | `components/ai/ScoreCardView.tsx`, `components/ai/ShareDialog.tsx` | Xoá bản trong `components/ai/`, **giữ** `components/look/ScoreCard.tsx` và `ShareDialog.tsx` | `main` đã chuyển sang thư mục `look/` |
| **`assets/` (587 MB)** | cả thư mục | Không xung đột khi merge `main` vào `vietfit` (thư mục này chỉ có ở `vietfit`). **Nhưng khi mở PR `vietfit` → `main` thì 587 MB sẽ đi vào `main`** | Xem mục 9 trước khi mở PR; nên tạo nhánh sạch từ `main` (cách A) thay vì đẩy nhánh `vietfit` thẳng vào `main` |
| **`tools/`** | `tools/*.py` ↔ `frontend/tools/*.py` | **Giữ `frontend/tools/`** của Thắng, bỏ bản `tools/` gốc | `main` đã xoá bộ SVG cũ |

Lệnh gợi ý (chạy sau `git merge origin/main`):

```bash
# Lấy bản main cho các nhóm "Cấu hình", "AI service", "Giao diện", "Thành phần"
THEIRS=".env.example README.md ai-service/README.md start-all.ps1 \
  frontend/vite.config.ts frontend/index.html \
  ai-service/app/api/routers/backend.py ai-service/app/api/routers/wardrobe_score.py \
  ai-service/app/main.py ai-service/tests/test_backend_contract.py \
  frontend/src/pages/ConceptPage.tsx frontend/src/pages/FinalLookPage.tsx \
  frontend/src/pages/MixStudioPage.tsx frontend/src/pages/MaleStudioPage.tsx \
  frontend/src/components/mix/WardrobeFigure.tsx frontend/src/components/common/Header.tsx \
  frontend/src/main.tsx frontend/src/styles.css frontend/src/utils/accessoryFit.ts \
  frontend/src/utils/outfitPreview.ts frontend/src/utils/stylistQuiz.ts \
  frontend/tests/accessoryFit.test.mjs frontend/tests/stylistQuiz.test.mjs"
git checkout --theirs -- $THEIRS
git add -- $THEIRS                  # chỉ đánh dấu "đã giải quyết" cho đúng các file trên

# Thư mục components/ai: bỏ hẳn, giữ components/look
git rm -f --ignore-unmatch -r frontend/src/components/ai

# tools: giữ frontend/tools của Thắng
git add frontend/tools

git status                      # còn dòng "both modified" nào thì mở file, tìm <<<<<<< rồi xử lý tay
git commit                      # hoàn tất merge
```

Sau khi merge nhớ chạy lại `git status` để chắc **không còn `<<<<<<<`** trong code:

```bash
git grep -n "<<<<<<<\|>>>>>>>" -- ':!*.md'
```

### 5.2. Việc Thắng phải tự kiểm tra sau khi lấy bản `main`

Vì lấy bản `main` cho nhiều file, **mọi chỉnh sửa Thắng làm sau `240f26e` ở các file trong bảng trên sẽ bị ghi đè**. Trước khi chốt, so lại với bản sao lưu:

```bash
git diff backup/vietfit-truoc-merge -- frontend/src ai-service/app | less
```

### 5.3. Cách chép tay một thay đổi của Thắng vào bản `main`

```bash
git show backup/vietfit-truoc-merge:frontend/src/utils/accessoryFit.ts > /tmp/accessoryFit.vietfit.ts
# mở song song với frontend/src/utils/accessoryFit.ts và chép phần Thắng thêm mới sang
```

---

## 6. `main` có gì mới so với `vietfit` (để Thắng biết mình đang nhận gì)

### 6.1. AI service (`ai-service/`)

| Việc | Chi tiết | File chính |
| --- | --- | --- |
| **Chấm điểm chặt hơn, áp dụng chung** | Luật mới **R40–R50**: quần đùi/váy ngắn với áo truyền thống (trần điểm 35), chưa chọn quần/váy (trần 40), dép lê/Crocs ở dịp trang trọng (trần 45), giày thể thao ở cưới/đi chùa, chân trần ở cưới/đi chùa, quần ống bó/lửng, phụ kiện đường phố ở dịp trang trọng. Mỗi luật có thể có `cap` riêng. Khi có lỗi nặng, tổng điểm bị chặn dưới 60, xếp loại "Cần chỉnh". Trạng thái outfit có thêm `bottom` và `shoes` | `data/rules.json`, `data/scoring.json`, `app/engine/{rules,scoring,kinds}.py`, `app/models/outfit.py` |
| **Áp dụng cho cả nam và nữ** | Đã chạy so sánh: quần đùi 35/35, thiếu quần 40/40, Crocs 45/45, chênh lệch còn lại chỉ do màu áo. Có test | `tests/test_backend_contract.py` |
| **Màu quần nam** | 4 quần nam (ống rộng, ống bó, lửng, đùi khaki) trước đây không có màu gốc nên bị coi là "trắng ngà" khi chấm hài hoà màu. Đã thêm màu đo từ ảnh trong tủ đồ | `app/api/routers/wardrobe_score.py` (`ORIGINAL`) |
| **AI Remix biết phản biện** | Endpoint mới `/ai/wardrobe-remix`: phân tích bối cảnh, không làm theo nguyên văn nếu yêu cầu không hợp, trả `analysis`, `scoreBefore/Requested/After`, các lựa chọn phù hợp hơn | `app/api/routers/wardrobe_remix.py` |
| **Nhận xét thẳng thắn** | `/ai/wardrobe-review` trả nhận xét + `Recommend`; kết luận mới `chua_hop` | `wardrobe_score.py`, `app/services/stylist.py`, `prompts/review.txt` |
| **Gợi ý đúng màu** | Sửa lỗi "có thể **bỏ** qua" và "một **bộ** áo dài" bị hiểu là phủ định; hiểu cách gọi màu ("xanh ngọc", "đỏ sẫm", "hồng đào"…); hiểu danh sách sau lời phủ định. Điểm thưởng màu thích tăng 10 → 20 | `app/api/routers/backend.py` (`requested_items`, `COLOR_ALIASES`), `data/scoring.json` |
| **Gợi ý đa dạng** | Mỗi kiểu áo ghép thành 3 bộ khác nhau (quần/váy, giày, nón/khăn, phụ kiện); danh sách ngắn 9 bộ phạt trùng kiểu áo/màu/quần/giày; ép 3 kiểu áo khác nhau khi đủ lựa chọn; bỏ `VAY_XEP_LY` khỏi gợi ý (hình xem trước là váy ngắn) | `app/engine/variety.py` (mới), `app/ai/select.py`, `prompts/select.txt` |
| **Test** | Thêm `test_color_requests.py`, `test_variety.py`, mở rộng `test_backend_contract.py` | `ai-service/tests/` |

AI mặc định đọc luật/quiz/prompt từ `ai-service/data/*.json` và `ai-service/prompts/` (có lịch sử git, duyệt qua Pull Request).
Muốn đọc từ database thì đặt `AI_CATALOG_SOURCE=postgres` trong `.env`.
**Lưu ý:** bản prompt lưu trong DB (migration V10) là bản cũ; nếu bật chế độ postgres, cần cập nhật bản trong DB cho khớp `prompts/*.txt`.

### 6.2. Backend (`backend/`)

| Migration | Nội dung |
| --- | --- |
| **`V13__more_stylist_colors.sql`** | Thêm 4 màu vào danh mục tham chiếu: `GREEN` Xanh lá `#39705B`, `PINK` Hồng `#DE91AA`, `PURPLE` Tím `#765A94`, `BROWN` Nâu `#876044` |
| **`V14__more_bottoms_for_stylist.sql`** | Thêm 3 kiểu quần (loại `BOTTOM`) và liên kết với cả 5 áo: `QUAN_ONG_RONG` (nam), `QUAN_DAI_DEN` (nữ), `QUAN_DAI_XANH` (nam) |

- Cả hai migration viết bằng `INSERT … SELECT … WHERE NOT EXISTS` để chạy được trên PostgreSQL **và** H2 của bộ test. **Không dùng `ON CONFLICT`** (H2 không hiểu).
- `ApiIntegrationTest` đã sửa: 11 màu (`hasSize(11)`), 17 phụ kiện cho áo dài (`hasSize(17)`).
- **Quy ước Flyway:** *không sửa* migration đã chạy trên máy ai đó. Nếu Thắng có migration số **V13 trở lên** của riêng mình, **đổi thành V15, V16…** trước khi merge, để khỏi trùng số.
  (Nhánh `vietfit` hiện dừng ở V12 nên không bị trùng.)

### 6.3. Frontend (`frontend/`)

**File mới:** `src/ai-extra.css`, `src/services/aiApi.ts`, `src/utils/lookbook.ts`, `src/components/look/{ScoreCard,ShareDialog,StylistReview}.tsx`, `src/components/mix/RemixPanel.tsx`, `public/{emblem,logo-nep-ao,favicon-*,apple-touch-icon}.png`, `public/favicon.ico`.

**Giao diện đã đổi**

- **Logo/favicon:** biểu tượng cặp đôi áo dài, nền trong suốt ở đầu/chân trang; favicon nền trắng bo góc.
- **Chữ in đậm:** các tiêu đề `h1–h4` và nhãn quan trọng (xem cuối `ai-extra.css`). Font Playfair Display 700.
- **Slogan** dùng gạch ngang `–` thay vì dấu chấm giữa hai câu.
- **Chân trang:** dòng bản quyền "© 2026 VIỆT FIT · Nếp Áo. Bản quyền thuộc về V.Q.Khai · N.D.Thang · N.N.K.Vy. Bảo lưu mọi quyền."
- **Dải tên áo** ở trang chủ: dấu ✳ nằm giữa hai tên.
- **Trang Việt look:** thẻ Lookbook ở khung trái; Style Match/Color Harmony có số liệu; nhận xét Stylist; dòng **Recommend** in nghiêng; hộp thoại Checklist & Lookbook căn giữa có nút đóng.
- **Studio 3D (`/male-studio`, `/female-studio`):**
  - Tủ đồ chia tab **Áo / Quần / Giày / Phụ kiện**, lưới 3 cột; nhóm phụ kiện là `<details>` gập lại.
  - Khung nhân vật và khung tủ đồ **cùng chiều cao**, tủ đồ cuộn bên trong; cách chân trang 56 px.
  - Nguyên nhân lỗi lệch cũ: `styles.css` có `position:sticky` rồi bị `position:relative` ghi đè nhưng vẫn giữ `top:88px`. Khối CSS sửa nằm **cuối `ai-extra.css`** (file này nạp sau `styles.css` nên thắng về độ ưu tiên).
- **Quiz & gợi ý:** `quizContext()` gửi dạng "Màu ưa thích: Xanh lá, Vàng" thay vì nguyên câu hỏi; `quizPreferences()` ánh xạ đủ 9 màu của tủ đồ; `apiColorHex` thêm 4 màu mới; `outfitPreview.ts` thêm `apiTrousers` cho 3 kiểu quần mới.

**`utils/accessoryFit.ts` (nón lá) — Thắng đọc kỹ nếu có sửa file này**

| Góc nhìn | Thay đổi |
| --- | --- |
| **Trước** | Bỏ mặt trong của nón (ảnh gốc vẽ nhìn từ dưới, mặt trong che đỉnh đầu). Chỉ giữ chóp ngoài: xoá điểm ảnh có `y > 214 + 62·((x−510)/210)² + 3`. Điểm đặt nón `seat = head.y + head.height × 0.43` |
| **Phải / Trái** | Cắt phần lòng nón dưới đường nối hai đầu mép nón; `seat` hệ số **0.34** (cũ 0.30) |
| **Sau** | `seat` hệ số **0.40** (cũ 0.16); quai nón được vẽ ở **lớp phía sau** (`strapBehind`) nên đầu che đoạn vòng qua cằm |
| **Test** | `tests/accessoryFit.test.mjs`: cận trên của mép nón so với đầu nâng từ `0.4` lên `0.5` |

Chạy thử bằng cách mở `/male-studio` → tab **Phụ kiện** → **Nón lá** → xoay đủ 4 góc (cả nam và nữ).

### 6.4. Tài liệu & khác

- `README.md`, `ai-service/README.md`, `.env.example`: khoá OpenWeather đã bị **xoá** (khoá cũ từng lộ trong repo; **Thắng nên huỷ/đổi khoá đó trên OpenWeather**, vì nó vẫn còn trong lịch sử git của `vietfit`).
- Lịch sử `main` sạch: không có commit đồng tác giả bên thứ ba; contributor hiện chỉ có tài khoản của Khai.

---

## 7. Chạy dự án trên máy Thắng sau khi merge

1. **Tạo `.env`** ở thư mục gốc (sao từ `.env.example`, **không commit file này**):
   ```env
   DATABASE_URL=jdbc:postgresql://localhost:5432/viet_fit
   DATABASE_USERNAME=viet_fit
   DATABASE_PASSWORD=<mật khẩu của Thắng>
   WEATHER_API_KEY=<khoá OpenWeather MỚI, hoặc để trống để dùng giả lập>
   GEMINI_API_KEY=<khoá Gemini; để trống thì AI chạy nhánh dự phòng>
   GEMINI_MODEL=gemini-3.5-flash
   AI_SERVICE_URL=http://localhost:8000
   AI_CATALOG_SOURCE=json
   ```
   (Biến Gemini tên là **`GEMINI_API_KEY`**; có thể đặt thêm trong `ai-service/.env`.)
2. **Python**: `cd ai-service && python -m venv .venv && .venv\Scripts\pip install -r requirements.txt`.
3. **Frontend**: `cd frontend && npm install`.
4. **Chạy tất cả**: từ thư mục gốc `.\start-all.ps1` (build backend, **import asset vào PostgreSQL**, chạy AI, chạy Vite). Mở <http://localhost:5173>.
   - Lần đầu sau merge, Flyway tự chạy **V13 và V14**. Nếu DB của Thắng đang ở V12 thì không cần làm gì thêm.
   - Dừng: `.\stop-all.ps1`.
5. **Các cổng**: Frontend 5173 · Backend 8080 · AI 8000 · PostgreSQL 5432.

**Lỗi thường gặp**

| Hiện tượng | Cách xử lý |
| --- | --- |
| `gradlew.bat` báo thiếu `gradle-wrapper.jar` | `.gitignore` đang chặn `*.jar` nên file này không nằm trong repo. Dùng Gradle cài sẵn (`gradle bootRun`), hoặc `gradle wrapper`, hoặc thêm `!backend/gradle/wrapper/gradle-wrapper.jar` vào `.gitignore` rồi commit file đó |
| Backend báo "Migration checksum mismatch" hay "failed migration V13/V14" | DB đã chạy một bản V13/V14 khác. Với DB local: xoá dòng V13/V14 trong bảng `flyway_schema_history` rồi chạy lại (V13/V14 là idempotent, không tạo trùng) |
| AI báo `PoolTimeout` khi khởi động | Biến `DATABASE_URL` kiểu `jdbc:` của Spring bị AI đọc nhầm. Chạy AI bằng `start-all.ps1` (đã xử lý) hoặc bỏ `DATABASE_URL` khỏi môi trường của tiến trình AI |
| Ảnh "Chưa có hình" ở thumbnail góc trái | Chưa import asset: chạy `python backend/import_data.py --assets` (có sẵn trong `start-all.ps1`). Thumbnail góc trái cần 13 file `assets/wardrobe/*/shirts/*/source/left.png` đã có sẵn trên `main`; không cần cả thư mục `assets/` 587 MB |
| Cảnh báo "LF will be replaced by CRLF" | Chỉ là cảnh báo xuống dòng trên Windows; bỏ qua được. Nên thêm `.gitattributes` với `* text=auto` để thống nhất |

---

## 8. Kiểm tra sau khi merge (phải qua hết rồi mới mở Pull Request)

### 8.1. Chạy tự động

| Lệnh | Kết quả mong đợi |
| --- | --- |
| `cd ai-service && .venv\Scripts\python.exe -m pytest -q` | **118 passed** |
| `cd frontend && npm test` | **40 pass, 0 fail** |
| `cd frontend && npx tsc -b` | không có lỗi |
| `cd backend && .\gradlew.bat test` (hoặc `gradle test`) | **BUILD SUCCESSFUL** |

### 8.2. Chạy bằng tay (khoảng 10 phút)

1. **Quiz → gợi ý màu:** `/stylist` → chọn Tết, nữ, màu **Xanh lá + Tím** → "Xem 3 bộ gợi ý". Kỳ vọng: 3 bộ khác kiểu áo, màu là xanh lá/tím (không ra toàn đỏ), phụ kiện và giày khác nhau.
2. **Chấm điểm chặt:** vào Mix studio, đổi quần thành **quần đùi** với áo dài truyền thống. Kỳ vọng điểm **35%** và nhãn "Chưa phù hợp". Bỏ chọn quần → **40%**. Dép Crocs ở dịp Tết → **45%**. Kiểm tra **cả nam lẫn nữ**.
3. **AI Remix:** gõ "mình thích váy ngắn" khi đang mặc quần đùi → AI phân tích bối cảnh, đưa lựa chọn phù hợp hơn kèm điểm trước/sau.
4. **Trang Việt look:** thẻ Lookbook bên trái, Style Match và Color Harmony có số, có đoạn nhận xét + dòng *Recommend* in nghiêng, nút **Checklist & Lookbook** mở hộp thoại ở giữa và có nút đóng.
5. **Studio 3D:** hai khung ngang nhau; 4 tab tủ đồ; chọn nón lá, xoay 4 góc.
6. **Giao diện chung:** logo cặp đôi ở đầu/chân trang, favicon trên tab, dòng bản quyền, dải ✳ ở trang chủ.

---

## 9. Quy ước làm việc từ giờ (đề xuất)

- **Không push thẳng vào `main`.** Mỗi người một nhánh (`thang/ten-viec`, `khai/ten-viec`), mở **Pull Request** vào `main`, người kia duyệt.
- **Migration:** mỗi thay đổi DB là một file mới `V15__…sql`, `V16__…sql`. Không sửa file đã có. Viết SQL chạy được cả PostgreSQL và H2.
- **Luật chấm điểm / quiz / prompt** sửa trong `ai-service/data/*.json` và `ai-service/prompts/*.txt`, kèm test; đọc `ai-service/README.md` mục "Chấm điểm phối đồ trong tủ đồ".
- **Không commit khoá API**, `.env`, hoặc file build. Nếu lỡ commit khoá thì **đổi khoá ngay**, không chỉ xoá file.
- **Trước khi push:** chạy cả ba bộ test ở mục 8.1.
- Commit message nên mô tả việc đã làm; không cần dòng đồng tác giả (`Co-Authored-By`).

### Việc còn mở (chưa xử lý, để Thắng và Khai thống nhất)

0. **Ảnh nguồn `assets/` (587 MB, 1151 file) lưu ở đâu?** Đưa thẳng vào `main` làm repo rất nặng (GitHub khuyến nghị dưới 1 GB, mỗi file dưới 100 MB, và mọi lần clone đều tải hết). Ba hướng, chọn một:
   a. Giữ trên nhánh `vietfit` / máy Thắng, `main` chỉ chứa ảnh đã dùng (`frontend/public/figure/`) — **đang là cách này**;
   b. Dùng **Git LFS** cho `assets/` (cần cài LFS cho cả nhóm);
   c. Nén thành một file và đưa vào **GitHub Release** / ổ đĩa chung, README chỉ ghi đường dẫn.

1. **Chưa có luật theo giới tính cho trang phục.** Dữ liệu `garments.json` ghi áo tứ thân và nhật bình là trang phục nữ, nhưng tủ đồ nam vẫn cho chọn và chấm không trừ điểm. Tương tự: nam đeo hoa cài tóc/kiềng bạc, nữ đội khăn xếp cũng không bị trừ (hiện chỉ có luật cho khăn xếp với nam). Đây là nội dung văn hoá nên cần nguồn trước khi thêm luật.
2. **Gemini đôi khi không viết được nhận xét** (kết quả không qua bước kiểm tra), khi đó dùng câu dự phòng viết sẵn; chưa tìm ra nguyên nhân từng lần.
3. **Dữ liệu có hai nơi** (file JSON và seed SQL) nên có thể lệch nhau nếu chỉ sửa một nơi.
4. **Tủ đồ nữ ít kiểu quần** (trắng ngà, đen, váy dài), nên đôi khi cả 3 gợi ý cùng quần trắng ngà. Muốn đa dạng hơn cần thêm ảnh quần/váy và mã `BOTTOM` mới (theo mẫu `V14`).
5. **Nhóm phụ kiện hiện đại** (tai nghe, kính, ba lô…) có trong tủ đồ nhưng chưa nằm trong danh mục 17 món của stylist, nên stylist chưa gợi ý chúng.
6. **Repo** nên để chế độ **Private** nếu chưa muốn công khai; thêm `.gitattributes`, `CODEOWNERS` và mẫu Pull Request nếu hai bạn đồng ý.

---

*Tài liệu viết từ trạng thái `main` tại `cd5647e` (và bản sửa nhỏ chưa push ở mục 1). Cần hỏi gì thêm, cứ nhắn Khai.*
