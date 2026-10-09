# Người mẫu giấy – quy ước vẽ

Mọi file SVG trong thư mục này vẽ trên **cùng khung `viewBox="0 0 400 800"`**, cùng tư thế đứng thẳng, trục giữa x = 200.

## Người mẫu mặc định

- `body/body_nu.svg`: người mẫu nữ 2D, tỉ lệ khoảng 7,9 đầu (đầu nhỏ 5%, co quanh tầm mắt y=96), **đã mặc sẵn đồ lót trắng** (áo lót + quần lót). Sinh bằng `tools/gen_body_nu.py`.
- `body/body_nam.svg`: người mẫu nam 2D, cùng khung và **cùng mốc đầu, cằm, mắt cá, bàn chân** với mẫu nữ, **đã mặc sẵn quần lót đùi trắng**. Sinh bằng `tools/gen_body_nam.py`.
- Khăn, nón, giày dùng chung cho cả hai mẫu. **Áo và quần phải vẽ riêng cho từng mẫu** (vai, eo, hông nam khác nữ), đặt tên `..._nu.svg` / `..._nam.svg`.
- Thứ tự lớp: người mẫu → quần/váy → áo → giày → kiềng (cổ) → trang sức → túi/quạt (cầm tay) → khăn/hoa cài (tóc) → nón.
- Phụ kiện sinh bằng `python tools/gen_accessories.py`. Túi và quạt cầm ở tay trái người mẫu, vị trí tay nam/nữ khác nhau nên có file riêng `tui_nu.svg`, `tui_nam.svg` (đánh dấu `byGender` trong `data/accessories.json`).

## Bốn hướng nhìn

Mỗi asset (người mẫu, áo, quần/váy, phụ kiện) có đủ 4 hướng, cùng khung 400×800 và cùng mốc y:

| Hướng | Tên file | Quy ước |
| --- | --- | --- |
| Trước | `ten.svg` | Nhìn thẳng mặt |
| Trái | `ten_trai.svg` | Nhìn từ bên trái người mẫu: người mẫu quay mặt sang **trái** khung hình; tay gần (tay trái) đè lên thân |
| Phải | `ten_phai.svg` | **Sinh tự động** bằng `python tools/mirror_views.py` (lật từ `_trai`). Chi tiết chỉ thấy từ bên phải (vd. đường khuy cài bên phải của áo dài, ngũ thân) vẽ vào `ten_phai_them.svg`, script ghép thêm |
| Sau | `ten_sau.svg` | Nhìn sau lưng; đường bao người mẫu giống hướng trước |

Người mẫu hướng trái và sau sinh bằng `python tools/gen_body_views.py`.

Quần áo, quần/váy, guốc, khăn vấn ở hướng trái, phải, sau sinh bằng `python tools/gen_garment_views.py`:
- Hướng trái dựng theo số đo đọc thẳng từ `body_*_trai.svg` (mép thân, mép tay gần) nên luôn phủ kín người. Lớp nào đè lên tay gần thì có nhóm `ban_tay` vẽ lại phần tay lộ ra, để bàn tay nằm trên quần áo.
- Đường cài khuy chéo của áo dài, ngũ thân nằm trong `*_phai_them.svg`, chỉ hiện ở hướng phải.
- Hướng sau dựng từ bản hướng trước: bỏ khuy, túi, yếm, vạt trước; thêm đường may sống lưng.
- Sửa bản hướng trước của áo thì chạy lại script này để hướng sau cập nhật theo.

## Quy tắc khi vẽ quần áo (bắt buộc)

0. **Đủ 4 hướng nhìn:** người mẫu có hướng nào thì quần áo, phụ kiện cũng phải có hướng đó.
1. **Quần áo phải bám đúng tỉ lệ người mẫu.** Trước khi vẽ, xem bảng số đo bên dưới (hoặc chạy `python tools/body_measure.py nu` / `python tools/body_measure.py nam`).
2. **Mép trong của quần áo phải phủ kín mép cơ thể** ở mọi độ cao nó che: rộng hơn mép người ít nhất 1–2 đơn vị (đồ bó) hoặc nhiều hơn (đồ rộng). Không để da lộ ra ở mép.
3. **Không tràn sang bộ phận khác:** phần thân áo không đè lên cánh tay; ống quần không đè lên tay buông bên cạnh.
4. Tay áo đi theo trục cánh tay: vai (150,178) → khuỷu (~137,318) → cổ tay (~130,430). Gấu tay áo dài phải phủ cổ tay (y ≈ 424–438).
5. Ống quần đi theo trục chân: hông (151–249, y 414) → gối (164–190 và 210–236, y 590) → mắt cá (175–193 và 207–225, y 748).
6. Màu vải dùng màu đánh dấu: `#FF0000` màu chính, `#00FF00` lót/viền, `#0000FF` quần/váy, `#FF00FF` điểm nhấn. Bóng và nếp gấp dùng màu đen trong suốt 12–30%.
7. Viền dùng `stroke="#000" stroke-opacity="0.3" stroke-width="1.3"`, không dùng viền đen đặc.
8. Vẽ xong: chạy `python tools/build_figure_preview.py`, mở `preview.html`, bật lớp mới và soát ở các mốc vai, nách, eo, hông, gối, mắt cá.

## Mốc chính

đỉnh đầu 42 · cằm 140 · vai 178 · nách 222 · ngực 238 · eo 318 · hông 414 · đáy chậu 440 · cổ tay 430 · đầu ngón tay ~492 (bàn tay ≈0,6 chiều cao đầu) · gối 590 · mắt cá 748 · đáy chân 781

## Bảng số đo mép cơ thể

Ở mỗi độ cao y, các đoạn x mà cơ thể chiếm. Có 3 đoạn = tay trái, thân, tay phải; có 4 đoạn = tay trái, chân trái, chân phải, tay phải.

### Người mẫu nữ

| y | Mốc | Các đoạn x thân người chiếm (trái → phải) |
| --- | --- | --- |
| 150 | cổ | 189.0–211.0 |
| 178 | vai | 150.0–250.0 |
| 200 | dưới vai | 139.4–260.6 |
| 222 | nách | 138.0–158.0  158.0–242.0  242.0–262.0 |
| 238 | ngực | 137.3–156.4  159.3–240.7  243.6–262.7 |
| 266 | chân ngực | 134.8–152.5  162.9–237.1  247.5–265.2 |
| 300 | giữa sườn | 130.8–147.3  166.9–233.1  252.7–269.2 |
| 318 | eo / khuỷu tay | 129.0–145.0  168.0–232.0  255.0–271.0 |
| 350 | bụng | 127.0–142.9  163.5–236.5  257.1–273.0 |
| 388 | cạp quần lót | 124.7–140.2  153.9–246.1  259.8–275.3 |
| 414 | hông | 123.5–138.7  151.0–249.0  261.3–276.5 |
| 430 | cổ tay | 122.7–138.1  151.2–248.8  261.9–277.3 |
| 440 | đáy chậu | 121.1–140.0  151.6–200.0  200.0–248.4  260.0–278.9 |
| 470 | gấu quần đùi | 120.6–143.8  153.2–197.1  202.9–246.8  256.2–279.4 |
| 500 | giữa đùi / đầu ngón tay | 131.5–135.0  135.0–138.5  155.6–194.4  205.6–244.4  261.5–265.0  265.0–268.5 |
| 590 | gối | 164.0–190.0  210.0–236.0 |
| 660 | bắp chân | 163.1–190.8  209.2–236.9 |
| 748 | mắt cá | 175.0–193.0  207.0–225.0 |

### Người mẫu nam

| y | Mốc | Các đoạn x thân người chiếm (trái → phải) |
| --- | --- | --- |
| 150 | cổ | 186.0–214.0 |
| 178 | vai | 138.1–261.9 |
| 200 | dưới vai | 129.5–270.5 |
| 222 | nách | 128.0–272.0 |
| 238 | ngực | 127.3–150.6  153.5–246.5  249.4–272.7 |
| 266 | chân ngực | 124.9–146.5  157.9–242.1  253.5–275.1 |
| 300 | giữa sườn | 120.8–141.3  163.2–236.8  258.7–279.2 |
| 318 | eo / khuỷu tay | 119.0–139.0  165.0–235.0  261.0–281.0 |
| 350 | bụng | 117.3–136.9  163.0–237.0  263.1–282.7 |
| 388 | cạp quần lót | 115.7–134.2  158.2–241.8  265.8–284.3 |
| 414 | hông | 115.1–132.7  156.0–244.0  267.3–284.9 |
| 430 | cổ tay | 114.7–132.1  155.9–244.1  267.9–285.3 |
| 440 | đáy chậu | 113.1–134.0  156.0–200.0  200.0–244.0  266.0–286.9 |
| 470 | gấu quần đùi | 112.5–138.0  156.8–197.1  202.9–243.2  262.0–287.5 |
| 500 | giữa đùi / đầu ngón tay | 122.3–133.6  158.3–194.4  205.6–241.7  266.4–277.7 |
| 590 | gối | 164.0–190.0  210.0–236.0 |
| 660 | bắp chân | 162.7–190.8  209.2–237.3 |
| 748 | mắt cá | 175.0–193.0  207.0–225.0 |

## Hoạ tiết

- **Vải in đều** (`data/patterns.json`, `kind: "tile"`): ô lặp thay cho màu chính `#FF0000`.
- **Vẽ / thêu theo bố cục** (`kind: "placement"`, file `motif/{id}.svg`, sinh bằng `python tools/gen_motifs.py`): cụm ở ngực + cụm ở tà, co theo khung thân áo của từng kiểu áo và góc nhìn. Chi tiết cách ghép và nguồn ở `NGUON-THAM-KHAO.md`.
- Soát hình có hoạ tiết: `python tools/render_check.py out.png @sen body/body_nu bottom/quan_nu garment/ao_dai_nu` (cần `pip install resvg-py` vì pymupdf bỏ qua clipPath).

