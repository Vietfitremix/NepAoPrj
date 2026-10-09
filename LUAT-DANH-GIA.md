# Bộ quy tắc đánh giá chi tiết

80 luật tham khảo chia theo cấu trúc, đặc trưng áo và màu, phụ kiện, bối cảnh, cách tân. Luật quyết định điểm; AI chỉ diễn giải.

## Cách tính và giới hạn

- Cộng/trừ điểm bên dưới tác động vào tiêu chí tương ứng, không cộng trực tiếp vào điểm tổng. Trọng số: cấu trúc 20%, đặc trưng 25%, phụ kiện 15%, bối cảnh 30%, cách tân 10%. Điểm tiêu chí giới hạn 0–100.
- Các luật cùng nhóm chỉ tính một lần: ưu tiên mức rủi ro cao, sau đó mức cụ thể và độ lớn tác động. Phong cách tối giản/đường phố giảm tác động cân nhắc theo hệ số trong scoring.json. Mô hình hài hòa màu và phong cách vẫn có điểm nền riêng; các luật màu chi tiết bổ sung tín hiệu vào tiêu chí đặc trưng.
- Quần ngắn/váy ngắn chặn tổng ở 35; thiếu lớp dưới ở 40; dép trong dịp trang trọng ở 45.
- Chỉ áp dụng luật ngữ cảnh khi có câu trả lời phù hợp. Không trả lời không bị coi là lỗi; kết quả liệt kê phần ngữ cảnh còn thiếu.
- Màu dùng RGB gốc hoặc RGB tùy chỉnh, quy đổi OKLCH; ngưỡng là lựa chọn của ứng dụng, không phải chuẩn văn hóa. Không đánh giá màu lớp dưới khi chưa chọn lớp dưới.
- Chưa có dữ liệu để xác nhận chất liệu, độ dày, số khuy, cổ áo, kích cỡ, độ bám giày, nhiệt độ hay ánh sáng thực tế. Không suy diễn những đặc điểm này từ tên hoặc ảnh.
- Nguồn lịch sử dùng để tham khảo hình thức và ngữ cảnh trang phục. Điểm số và gợi ý thẩm mỹ đều chưa được nguồn xác nhận; không áp dụng phẩm cấp triều Nguyễn hay các điều cấm màu sắc cho người mặc hiện đại.

## Danh sách luật

Tác động luật đặc trưng áo được nhân 0,4 trong công thức `0,6 × điểm màu + 0,4 × (75 + tổng tác động luật)`. Chỉ các luật cân nhắc thuộc tiêu chí cách tân được giảm còn khoảng 1/3 khi cấu hình phong cách có `softConsider`. Trần điểm chỉ áp dụng khi luật mức risk khớp.

### R01 — Bộ trang phục gắn với vùng Kinh Bắc

- Tiêu chí: cau_truc; nhóm: cultural_accessory_set; tác động: +8.
- Điều kiện: `{"all":[{"garment":["ao_tu_than"]},{"hasAccessory":"non_quai_thao"}]}`.
- Nhận xét: Bộ trang phục gắn với vùng Kinh Bắc
- Gợi ý: Đội thêm khăn mỏ quạ bên dưới nón, đeo kiềng bạc để trọn bộ quan họ
- Nguồn: [Tham khảo](https://dsvh.gov.vn/dan-ca-quan-ho-bac-ninh-482) Nguồn giới thiệu lịch sử và đặc trưng trang phục. Gợi ý phối đồ và điểm số là quy tắc tham khảo của ứng dụng, chưa được nguồn này xác nhận toàn bộ.

### R07 — Cách tân chấp nhận được, nên giữ cổ đứng và 5 khuy

- Tiêu chí: cach_tan; nhóm: sneaker_style; tác động: -10.
- Điều kiện: `{"all":[{"garment":["ao_ngu_than"]},{"hasAccessory":"sneaker"}]}`.
- Nhận xét: Cách tân chấp nhận được, nên giữ cổ đứng và 5 khuy
- Gợi ý: Chọn sneaker trắng trơn, giữ cổ đứng và đủ 5 khuy
- Nguồn: [Tham khảo](https://visithue.vn/Tinh-te-ao-dai-ngu-than.html/?pid=MjA1MjR8Y3NkbGRs0) Nguồn giới thiệu lịch sử và đặc trưng trang phục. Gợi ý phối đồ và điểm số là quy tắc tham khảo của ứng dụng, chưa được nguồn này xác nhận toàn bộ.

### R12 — Phối đơn sắc trắng trong dịp Tết hoặc cưới

- Tiêu chí: boi_canh; nhóm: R12; tác động: -10.
- Điều kiện: `{"all":[{"occasion":["dam_cuoi","tet"]},{"allColorsIn":["trang_nga","trang_tinh"]},{"hasAccessory":"khan_van"}]}`.
- Nhận xét: Áo và lớp dưới cùng thuộc nhóm trắng, kèm khăn vấn, tạo một hướng phối đơn sắc trong dịp Tết hoặc cưới; nên đối chiếu dress code cụ thể.
- Gợi ý: Nếu muốn tổng thể có điểm nhấn vui tươi, thêm màu ở áo hoặc phụ kiện. Không thể kết luận tang phục chỉ từ cặp màu và loại khăn.
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R15 — Nhật Bình khi đi dạo theo hướng truyền thống

- Tiêu chí: boi_canh; nhóm: R15; tác động: -10.
- Điều kiện: `{"all":[{"all":[{"garment":["nhat_binh"]},{"occasion":["dao_pho"]}]},{"style":["truyen_thong"]},{"role":["khach","nhan_vat_chinh","be_trap","nhom"]}]}`.
- Nhận xét: Nhật Bình có dáng lễ phục rõ nét; khi đi dạo với mục tiêu phối truyền thống, tổng thể có thể trang trọng hơn hoạt động đã chọn.
- Gợi ý: Giữ Nhật Bình nếu mục đích là chụp ảnh cổ phục; nếu cần di chuyển gọn, cân nhắc áo dài hoặc bà ba. Đây là lựa chọn theo mục đích mặc.
- Nguồn: [Tham khảo](https://khamphahue.com.vn/Hue-24h/Thong-bao/tid/Ao-Nhat-Binh-Mot-di-san-van-hoa-quy-cua-Co-do-Hue.html/pid/11533/cid/28) Nguồn giới thiệu lịch sử và đặc trưng trang phục. Gợi ý phối đồ và điểm số là quy tắc tham khảo của ứng dụng, chưa được nguồn này xác nhận toàn bộ.

### R20 — Trời mưa, guốc gỗ dễ trơn trượt và thấm nước

- Tiêu chí: boi_canh; nhóm: wet_footwear; tác động: -10.
- Điều kiện: `{"all":[{"weather":["mua"]},{"hasAccessory":"guoc"}]}`.
- Nhận xét: Trời mưa, guốc gỗ dễ trơn trượt và thấm nước
- Gợi ý: Đi giày kín mũi hoặc dép có đế bám thay cho guốc gỗ
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R21 — Áo nhiều lớp, mặc lâu ngoài trời nắng nóng dễ bí và ra mồ hôi

- Tiêu chí: boi_canh; nhóm: R21; tác động: -10.
- Điều kiện: `{"all":[{"weather":["nang_nong"]},{"setting":["ngoai_troi","ca_hai"]},{"garment":["nhat_binh","ao_tu_than","ao_ngu_than"]}]}`.
- Nhận xét: Áo nhiều lớp, mặc lâu ngoài trời nắng nóng dễ bí và ra mồ hôi
- Gợi ý: Chọn áo dài hoặc áo bà ba vải mỏng, hoặc hẹn chụp lúc sáng sớm, chiều muộn
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R22 — Màu tối hấp nắng, mặc ngoài trời lúc nắng nóng sẽ nóng hơn

- Tiêu chí: boi_canh; nhóm: R22; tác động: -10.
- Điều kiện: `{"all":[{"weather":["nang_nong"]},{"setting":["ngoai_troi","ca_hai"]},{"mainColorIn":["den_tuyen","xanh_lam","nau_dat","tim_hue"]}]}`.
- Nhận xét: Màu tối hấp nắng, mặc ngoài trời lúc nắng nóng sẽ nóng hơn
- Gợi ý: Đổi màu chính sang màu sáng như trắng ngà hoặc be kem
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R23 — Áo nhiều lớp, may dày, hợp với tiết trời se lạnh

- Tiêu chí: boi_canh; nhóm: R23; tác động: +8.
- Điều kiện: `{"all":[{"weather":["lanh"]},{"garment":["ao_ngu_than","nhat_binh","ao_tu_than"]}]}`.
- Nhận xét: Áo nhiều lớp, may dày, hợp với tiết trời se lạnh
- Gợi ý: Có thể mặc thêm áo lót giữ nhiệt bên trong
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R24 — Áo màu trắng gặp mưa dễ ướt, lộ và bám bẩn

- Tiêu chí: boi_canh; nhóm: R24; tác động: -10.
- Điều kiện: `{"all":[{"weather":["mua"]},{"mainColorIn":["trang_nga","trang_tinh"]}]}`.
- Nhận xét: Áo màu trắng gặp mưa dễ ướt, lộ và bám bẩn
- Gợi ý: Chọn màu đậm hơn như hồng đào hoặc xanh lam
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R25 — Nhật bình là lễ phục rất trang trọng, khách dự cưới mặc dễ nổi bật hơn cô dâu

- Tiêu chí: boi_canh; nhóm: wedding_role_attention; tác động: -10.
- Điều kiện: `{"all":[{"role":["khach"]},{"occasion":["dam_cuoi"]},{"garment":["nhat_binh"]}]}`.
- Nhận xét: Nhật bình là lễ phục rất trang trọng, khách dự cưới mặc dễ nổi bật hơn cô dâu
- Gợi ý: Khách nên chọn áo dài hoặc áo ngũ thân
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R26 — Màu đỏ thường dành cho cô dâu, khách mặc đỏ dễ trùng với nhân vật chính

- Tiêu chí: boi_canh; nhóm: wedding_role_attention; tác động: -10.
- Điều kiện: `{"all":[{"role":["khach"]},{"occasion":["dam_cuoi"]},{"mainColorIn":["do_son"]}]}`.
- Nhận xét: Màu đỏ thường dành cho cô dâu, khách mặc đỏ dễ trùng với nhân vật chính
- Gợi ý: Đổi sang hồng đào hoặc xanh lam
- Nguồn: [Tham khảo](https://vietnam.travel/things-to-do/ao-dai-vietnam) Nguồn giới thiệu lịch sử và đặc trưng trang phục. Gợi ý phối đồ và điểm số là quy tắc tham khảo của ứng dụng, chưa được nguồn này xác nhận toàn bộ.

### R27 — Đỏ và vàng là sắc màu quen thuộc của lễ cưới truyền thống

- Tiêu chí: boi_canh; nhóm: R27; tác động: +8.
- Điều kiện: `{"all":[{"role":["nhan_vat_chinh"]},{"occasion":["dam_cuoi"]},{"mainColorIn":["do_son","vang_hoang"]}]}`.
- Nhận xét: Đỏ và vàng là sắc màu quen thuộc của lễ cưới truyền thống
- Gợi ý: Có thể thêm khăn vấn cùng tông để trọn bộ
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R28 — Hoạ tiết chấm bi, kẻ sọc mang nét hiện đại, khác tinh thần truyền thống bạn chọn

- Tiêu chí: cach_tan; nhóm: pattern_style; tác động: -10.
- Điều kiện: `{"all":[{"occasion":["dam_cuoi","le_hoi_chua"]},{"pattern":["cham_bi","ke_soc"]},{"style":["truyen_thong"]}]}`.
- Nhận xét: Hoạ tiết chấm bi, kẻ sọc mang nét hiện đại, khác tinh thần truyền thống bạn chọn
- Gợi ý: Đổi sang vải trơn hoặc hoa văn tròn
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R30 — Khăn xếp đi cùng áo dài, áo ngũ thân là bộ lễ phục quen thuộc của nam giới

- Tiêu chí: cau_truc; nhóm: cultural_accessory_set; tác động: +8.
- Điều kiện: `{"all":[{"gender":["nam"]},{"garment":["ao_ngu_than","ao_dai"]},{"hasAccessory":"khan_xep"}]}`.
- Nhận xét: Khăn xếp đi cùng áo dài, áo ngũ thân là bộ lễ phục quen thuộc của nam giới
- Gợi ý: Chọn khăn cùng tông màu sẫm (đen, xanh lam) để tổng thể trang nhã
- Nguồn: [Tham khảo](https://visithue.vn/Tinh-te-ao-dai-ngu-than.html/?pid=MjA1MjR8Y3NkbGRs0) Nguồn giới thiệu lịch sử và đặc trưng trang phục. Gợi ý phối đồ và điểm số là quy tắc tham khảo của ứng dụng, chưa được nguồn này xác nhận toàn bộ.

### R31 — Nhật bình là lễ phục, giày hiện đại làm giảm vẻ trang trọng

- Tiêu chí: phu_kien; nhóm: sneaker_style; tác động: -10.
- Điều kiện: `{"all":[{"garment":["nhat_binh"]},{"any":[{"hasAccessory":"sneaker"},{"hasAccessory":"giay_bup_be"}]}]}`.
- Nhận xét: Nhật bình là lễ phục, giày hiện đại làm giảm vẻ trang trọng
- Gợi ý: Đổi sang hài thêu hoặc guốc gỗ
- Nguồn: [Tham khảo](https://khamphahue.com.vn/Du-lich/Chi-tiet/tid/Giu-ao-dai-Nhat-Binh-cho-Hue.html/pid/10926/cid/28) Nguồn giới thiệu lịch sử và đặc trưng trang phục. Gợi ý phối đồ và điểm số là quy tắc tham khảo của ứng dụng, chưa được nguồn này xác nhận toàn bộ.

### R32 — Hài thêu hợp với lễ phục và không khí lễ cưới

- Tiêu chí: phu_kien; nhóm: cultural_accessory_set; tác động: +8.
- Điều kiện: `{"all":[{"hasAccessory":"hai_theu"},{"any":[{"garment":["nhat_binh","ao_ngu_than"]},{"occasion":["dam_cuoi"]}]}]}`.
- Nhận xét: Hài thêu hợp với lễ phục và không khí lễ cưới
- Gợi ý: Chọn màu hài trùng màu điểm nhấn của khăn để đồng bộ
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R33 — Nón quai thao gắn với áo tứ thân của liền chị quan họ, đi với áo dài hay bà ba dễ lệch tinh thần

- Tiêu chí: phu_kien; nhóm: R33; tác động: -10.
- Điều kiện: `{"all":[{"hasAccessory":"non_quai_thao"},{"garment":["ao_dai","ao_ba_ba"]}]}`.
- Nhận xét: Nón quai thao gắn với áo tứ thân của liền chị quan họ, đi với áo dài hay bà ba dễ lệch tinh thần
- Gợi ý: Đổi sang nón lá, hoặc đổi áo sang áo tứ thân
- Nguồn: [Tham khảo](https://dsvh.gov.vn/dan-ca-quan-ho-bac-ninh-482) Nguồn giới thiệu lịch sử và đặc trưng trang phục. Gợi ý phối đồ và điểm số là quy tắc tham khảo của ứng dụng, chưa được nguồn này xác nhận toàn bộ.

### R34 — Khăn mỏ quạ, kiềng bạc là phụ kiện quen thuộc đi cùng áo tứ thân

- Tiêu chí: phu_kien; nhóm: cultural_accessory_set; tác động: +8.
- Điều kiện: `{"all":[{"garment":["ao_tu_than"]},{"any":[{"hasAccessory":"khan_mo_qua"},{"hasAccessory":"kieng_bac"}]}]}`.
- Nhận xét: Khăn mỏ quạ, kiềng bạc là phụ kiện quen thuộc đi cùng áo tứ thân
- Gợi ý: Đi lễ hội có thể thêm nón quai thao; chụp ảnh trong nhà thì khăn mỏ quạ là đủ
- Nguồn: [Tham khảo](https://dsvh.gov.vn/dan-ca-quan-ho-bac-ninh-482) Nguồn giới thiệu lịch sử và đặc trưng trang phục. Gợi ý phối đồ và điểm số là quy tắc tham khảo của ứng dụng, chưa được nguồn này xác nhận toàn bộ.

### R35 — Quạt giấy gặp mưa dễ ướt, rách

- Tiêu chí: boi_canh; nhóm: fan_weather; tác động: -10.
- Điều kiện: `{"all":[{"weather":["mua"]},{"hasAccessory":"quat_giay"}]}`.
- Nhận xét: Quạt giấy gặp mưa dễ ướt, rách
- Gợi ý: Thay bằng túi cói hoặc để quạt cho buổi chụp trong nhà
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R36 — Phượng hoàng thường là hoạ tiết áo cưới của cô dâu, khách mặc dễ trùng nhân vật chính

- Tiêu chí: boi_canh; nhóm: wedding_role_attention; tác động: -10.
- Điều kiện: `{"all":[{"role":["khach"]},{"occasion":["dam_cuoi"]},{"pattern":["phuong_hoang"]}]}`.
- Nhận xét: Phượng hoàng thường là hoạ tiết áo cưới của cô dâu, khách mặc dễ trùng nhân vật chính
- Gợi ý: Khách dự cưới nên chọn cành đào, sen hoặc hạc và mai
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R37 — Sen, hồi văn, hạc và mai là hoạ tiết truyền thống, hợp không khí lễ hội, ngày Tết

- Tiêu chí: dac_trung; nhóm: garment_pattern; tác động: +8.
- Điều kiện: `{"all":[{"pattern":["sen","hoi_van","hac_mai"]},{"occasion":["le_hoi_chua","tet"]}]}`.
- Nhận xét: Sen, hồi văn, hạc và mai là hoạ tiết truyền thống, hợp không khí lễ hội, ngày Tết
- Gợi ý: Giữ nền trơn một màu để hoạ tiết nổi bật
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R38 — Tùng, trúc, rồng, sóng nước là hoạ tiết quen thuộc trên áo nam, gợi khí chất vững vàng

- Tiêu chí: dac_trung; nhóm: garment_pattern; tác động: +8.
- Điều kiện: `{"all":[{"gender":["nam"]},{"pattern":["tung","truc","rong_may","song_nuoc"]}]}`.
- Nhận xét: Tùng, trúc, rồng, sóng nước là hoạ tiết quen thuộc trên áo nam, gợi khí chất vững vàng
- Gợi ý: Chọn nền xanh lam hoặc nâu đất để hoạ tiết vàng nổi bật
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R39 — Mai vàng, hoa đào là hoa ngày Tết, hợp không khí du xuân

- Tiêu chí: dac_trung; nhóm: garment_pattern; tác động: +8.
- Điều kiện: `{"all":[{"pattern":["mai_vang","canh_dao"]},{"occasion":["tet"]}]}`.
- Nhận xét: Mai vàng, hoa đào là hoa ngày Tết, hợp không khí du xuân
- Gợi ý: Kết hợp khăn vấn hoặc khăn xếp cùng tông với hoa
- Nguồn: Quy tắc của ứng dụng. Gợi ý phối đồ hoặc sử dụng của ứng dụng; chưa có nguồn đối chiếu cho nhận định này.

### R40 — Lớp quần ngắn dưới áo truyền thống

- Tiêu chí: cau_truc; nhóm: bottom_length; tác động: -40; trần tổng 35.
- Điều kiện: `{"all":[{"garment":["ao_dai","ao_ngu_than","ao_tu_than","nhat_binh","ao_ba_ba"]},{"bottom":["quan_ngan"]}]}`.
- Nhận xét: Quần đùi / quần ngắn không đi cùng áo truyền thống: tà áo dài phủ lên quần ngắn làm mất cấu trúc và dáng của bộ đồ
- Gợi ý: Đổi sang quần ống suông hoặc ống rộng, hoặc váy dài
- Nguồn: Quy tắc của ứng dụng. Quy ước phối đồ của ứng dụng (tổng hợp từ cách mặc phổ biến), chưa phải quy định văn hoá bắt buộc.

### R41 — Lớp váy ngắn dưới áo truyền thống

- Tiêu chí: cau_truc; nhóm: bottom_length; tác động: -40; trần tổng 35.
- Điều kiện: `{"all":[{"garment":["ao_dai","ao_ngu_than","ao_tu_than","nhat_binh","ao_ba_ba"]},{"bottom":["vay_ngan"]}]}`.
- Nhận xét: Váy ngắn không hợp với áo truyền thống: áo cần đi với quần hoặc váy dài tới mắt cá
- Gợi ý: Đổi sang quần ống suông / ống rộng hoặc váy dài
- Nguồn: Quy tắc của ứng dụng. Quy ước phối đồ của ứng dụng (tổng hợp từ cách mặc phổ biến), chưa phải quy định văn hoá bắt buộc.

### R42 — Chưa phối quần hoặc váy: bộ trang phục truyền thống chưa hoàn chỉnh

- Tiêu chí: cau_truc; nhóm: bottom_length; tác động: -40; trần tổng 40.
- Điều kiện: `{"all":[{"garment":["ao_dai","ao_ngu_than","ao_tu_than","nhat_binh","ao_ba_ba"]},{"bottom":["khong"]}]}`.
- Nhận xét: Chưa phối quần hoặc váy: bộ trang phục truyền thống chưa hoàn chỉnh
- Gợi ý: Chọn quần ống suông, ống rộng hoặc váy dài cho bộ đồ
- Nguồn: Quy tắc của ứng dụng. Quy ước phối đồ của ứng dụng (tổng hợp từ cách mặc phổ biến), chưa phải quy định văn hoá bắt buộc.

### R43 — Quần ống bó hoặc quần lửng làm mất độ buông của tà áo; áo dài hợp quần ống suông hoặc ống rộng hơn

- Tiêu chí: cau_truc; nhóm: bottom_shape; tác động: -10.
- Điều kiện: `{"all":[{"garment":["ao_dai","ao_ngu_than","ao_tu_than","nhat_binh"]},{"bottom":["quan_bo","quan_lung"]}]}`.
- Nhận xét: Quần ống bó hoặc quần lửng làm mất độ buông của tà áo; áo dài hợp quần ống suông hoặc ống rộng hơn
- Gợi ý: Đổi sang quần ống suông hoặc ống rộng
- Nguồn: Quy tắc của ứng dụng. Quy ước phối đồ của ứng dụng (tổng hợp từ cách mặc phổ biến), chưa phải quy định văn hoá bắt buộc.

### R44 — Áo bà ba hợp quần ống rộng hoặc quần lửng thoải mái hơn là quần ống bó

- Tiêu chí: cau_truc; nhóm: bottom_shape; tác động: -10.
- Điều kiện: `{"all":[{"garment":["ao_ba_ba"]},{"bottom":["quan_bo"]}]}`.
- Nhận xét: Áo bà ba hợp quần ống rộng hoặc quần lửng thoải mái hơn là quần ống bó
- Gợi ý: Đổi sang quần ống rộng hoặc quần lửng
- Nguồn: Quy tắc của ứng dụng. Quy ước phối đồ của ứng dụng (tổng hợp từ cách mặc phổ biến), chưa phải quy định văn hoá bắt buộc.

### R45 — Dép lê / dép Crocs quá xuề xoà cho dịp trang trọng khi mặc áo truyền thống

- Tiêu chí: boi_canh; nhóm: shoe_formality; tác động: -40; trần tổng 45.
- Điều kiện: `{"all":[{"garment":["ao_dai","ao_ngu_than","ao_tu_than","nhat_binh","ao_ba_ba"]},{"shoes":["dep"]},{"occasion":["tet","ky_yeu","dam_cuoi","le_hoi_chua"]}]}`.
- Nhận xét: Dép lê / dép Crocs quá xuề xoà cho dịp trang trọng khi mặc áo truyền thống
- Gợi ý: Đổi sang hài thêu, giày búp bê hoặc guốc
- Nguồn: Quy tắc của ứng dụng. Quy ước phối đồ của ứng dụng (tổng hợp từ cách mặc phổ biến), chưa phải quy định văn hoá bắt buộc.

### R46 — Dép lê / dép Crocs làm bộ áo truyền thống trông xuề xoà, mất sự chỉn chu

- Tiêu chí: boi_canh; nhóm: shoe_formality; tác động: -10.
- Điều kiện: `{"all":[{"garment":["ao_dai","ao_ngu_than","ao_tu_than","nhat_binh","ao_ba_ba"]},{"shoes":["dep"]},{"occasion":["dao_pho"]}]}`.
- Nhận xét: Dép lê / dép Crocs làm bộ áo truyền thống trông xuề xoà, mất sự chỉn chu
- Gợi ý: Đổi sang giày búp bê hoặc sneaker trắng trơn
- Nguồn: Quy tắc của ứng dụng. Quy ước phối đồ của ứng dụng (tổng hợp từ cách mặc phổ biến), chưa phải quy định văn hoá bắt buộc.

### R47 — Giày thể thao chưa hợp dịp trang trọng như cưới hỏi, đi chùa

- Tiêu chí: boi_canh; nhóm: shoe_formality; tác động: -10.
- Điều kiện: `{"all":[{"garment":["ao_dai","ao_ngu_than","ao_tu_than","nhat_binh","ao_ba_ba"]},{"shoes":["giay_the_thao"]},{"occasion":["dam_cuoi","le_hoi_chua"]}]}`.
- Nhận xét: Giày thể thao chưa hợp dịp trang trọng như cưới hỏi, đi chùa
- Gợi ý: Đổi sang hài thêu, giày búp bê hoặc giày da
- Nguồn: Quy tắc của ứng dụng. Quy ước phối đồ của ứng dụng (tổng hợp từ cách mặc phổ biến), chưa phải quy định văn hoá bắt buộc.

### R48 — Đi chân trần chưa phù hợp dịp trang trọng

- Tiêu chí: boi_canh; nhóm: shoe_formality; tác động: -10.
- Điều kiện: `{"all":[{"garment":["ao_dai","ao_ngu_than","ao_tu_than","nhat_binh","ao_ba_ba"]},{"shoes":["khong"]},{"occasion":["dam_cuoi","le_hoi_chua"]}]}`.
- Nhận xét: Đi chân trần chưa phù hợp dịp trang trọng
- Gợi ý: Thêm hài thêu hoặc giày búp bê
- Nguồn: Quy tắc của ứng dụng. Quy ước phối đồ của ứng dụng (tổng hợp từ cách mặc phổ biến), chưa phải quy định văn hoá bắt buộc.

### R49 — Phụ kiện đường phố (mũ lưỡi trai / cao bồi, tai nghe, ba lô, găng tay, dây xích) lệch tinh thần dịp trang trọng

- Tiêu chí: boi_canh; nhóm: street_formality; tác động: -10.
- Điều kiện: `{"all":[{"garment":["ao_dai","ao_ngu_than","ao_tu_than","nhat_binh","ao_ba_ba"]},{"occasion":["dam_cuoi","le_hoi_chua"]},{"any":[{"hasAccessory":"mu_cao_boi"},{"hasAccessory":"mu_luoi_trai"},{"hasAccessory":"tai_nghe"},{"hasAccessory":"ba_lo"},{"hasAccessory":"gang_tay_ho_ngon"},{"hasAccessory":"day_xich_hong"}]}]}`.
- Nhận xét: Phụ kiện đường phố (mũ lưỡi trai / cao bồi, tai nghe, ba lô, găng tay, dây xích) lệch tinh thần dịp trang trọng
- Gợi ý: Bỏ phụ kiện đường phố, chọn nón lá, khăn vấn hoặc túi cói
- Nguồn: Quy tắc của ứng dụng. Quy ước phối đồ của ứng dụng (tổng hợp từ cách mặc phổ biến), chưa phải quy định văn hoá bắt buộc.

### R50 — Dù chọn phong cách đường phố, quần/váy ngắn vẫn làm tà áo dài mất dáng

- Tiêu chí: cau_truc; nhóm: bottom_length; tác động: -10.
- Điều kiện: `{"all":[{"garment":["ao_dai","ao_ngu_than","ao_tu_than","nhat_binh"]},{"bottom":["quan_ngan","vay_ngan"]},{"style":["duong_pho"]}]}`.
- Nhận xét: Dù chọn phong cách đường phố, quần/váy ngắn vẫn làm tà áo dài mất dáng
- Gợi ý: Giữ quần ống rộng cho cá tính mà vẫn hợp áo dài
- Nguồn: Quy tắc của ứng dụng. Quy ước phối đồ của ứng dụng (tổng hợp từ cách mặc phổ biến), chưa phải quy định văn hoá bắt buộc.

### R51 — Áo dài với quần dài

- Tiêu chí: cau_truc; nhóm: bottom_shape; tác động: +8.
- Điều kiện: `{"all":[{"garment":["ao_dai"]},{"bottom":["quan_dai_suong","quan_ong_rong","quan_dai"]}]}`.
- Nhận xét: Quần dài tạo lớp nền liền mạch dưới hai tà áo dài và giữ cấu trúc áo mặc ngoài quần.
- Gợi ý: Giữ quần dài; cân nhắc độ rộng thực tế để bước đi thoải mái.
- Nguồn: [Tham khảo](https://vietnam.travel/things-to-do/ao-dai-vietnam) Nguồn mô tả trang phục và bối cảnh lịch sử. Điều kiện phối đồ, mức cộng/trừ điểm là quy tắc tham khảo của ứng dụng, không phải điều cấm được nguồn xác nhận.

### R52 — Tứ thân với váy dài

- Tiêu chí: cau_truc; nhóm: bottom_shape; tác động: +8.
- Điều kiện: `{"all":[{"garment":["ao_tu_than"]},{"bottom":["vay_dai"]}]}`.
- Nhận xét: Váy dài tạo tổng thể nhiều lớp phù hợp hướng phối tứ thân dân gian của ứng dụng.
- Gợi ý: Phối khăn mỏ quạ hoặc nón quai thao nếu muốn nhấn mạnh liên hệ Quan họ. Nguồn không quy định mọi kiểu váy.
- Nguồn: [Tham khảo](https://dsvh.gov.vn/dan-ca-quan-ho-bac-ninh-482) Nguồn mô tả trang phục và bối cảnh lịch sử. Điều kiện phối đồ, mức cộng/trừ điểm là quy tắc tham khảo của ứng dụng, không phải điều cấm được nguồn xác nhận.

### R53 — Ngũ thân với quần dài

- Tiêu chí: cau_truc; nhóm: bottom_shape; tác động: +8.
- Điều kiện: `{"all":[{"garment":["ao_ngu_than"]},{"bottom":["quan_dai_suong","quan_ong_rong","quan_dai"]}]}`.
- Nhận xét: Quần dài giúp phần tà áo ngũ thân và lớp dưới có đường nét thống nhất.
- Gợi ý: Giữ chiều dài quần, điều chỉnh độ rộng theo nhu cầu vận động.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R54 — Lớp dưới dài cho Nhật Bình

- Tiêu chí: cau_truc; nhóm: bottom_shape; tác động: +8.
- Điều kiện: `{"all":[{"garment":["nhat_binh"]},{"any":[{"bottom":["quan_dai_suong","quan_ong_rong","quan_dai"]},{"bottom":["vay_dai"]}]}]}`.
- Nhận xét: Quần dài hoặc váy dài giữ dáng nhiều lớp của bản phối Nhật Bình. Tư liệu Huế ghi nhận xiêm và quần trong các giai đoạn khác nhau.
- Gợi ý: Nếu muốn tái hiện một giai đoạn cụ thể, đối chiếu kiểu xiêm/quần và khăn; bản phối hiện đại có thể linh hoạt.
- Nguồn: [Tham khảo](https://khamphahue.com.vn/Hue-24h/Thong-bao/tid/Ao-Nhat-Binh-Mot-di-san-van-hoa-quy-cua-Co-do-Hue.html/pid/11533/cid/28) Nguồn mô tả trang phục và bối cảnh lịch sử. Điều kiện phối đồ, mức cộng/trừ điểm là quy tắc tham khảo của ứng dụng, không phải điều cấm được nguồn xác nhận.

### R55 — Bà ba với quần thoải mái

- Tiêu chí: cau_truc; nhóm: bottom_shape; tác động: +6.
- Điều kiện: `{"all":[{"garment":["ao_ba_ba"]},{"bottom":["quan_dai_suong","quan_ong_rong","quan_dai","quan_lung"]}]}`.
- Nhận xét: Phom quần suông hoặc lửng tạo hướng phối bà ba gọn, thiên về sinh hoạt.
- Gợi ý: Trong dịp lễ hoặc trời lạnh, ưu tiên quần dài thay cho quần lửng.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R56 — Váy dài với áo dài hoặc ngũ thân

- Tiêu chí: cau_truc; nhóm: bottom_shape; tác động: -8.
- Điều kiện: `{"all":[{"garment":["ao_dai","ao_ngu_than"]},{"bottom":["vay_dai"]}]}`.
- Nhận xét: Váy dài thay lớp quần tạo một biến thể cách tân; tổng thể khác cấu trúc áo mặc ngoài quần thường gặp.
- Gợi ý: Giữ váy nếu chủ đích là cách tân; chọn quần dài để trở về hướng phối truyền thống. Không coi mọi biến thể là sai.
- Nguồn: [Tham khảo](https://vietnam.travel/things-to-do/ao-dai-vietnam) Nguồn mô tả trang phục và bối cảnh lịch sử. Điều kiện phối đồ, mức cộng/trừ điểm là quy tắc tham khảo của ứng dụng, không phải điều cấm được nguồn xác nhận.

### R57 — Chưa chọn giày cho dịp lễ

- Tiêu chí: boi_canh; nhóm: shoe_formality; tác động: -8.
- Điều kiện: `{"all":[{"occasion":["tet","ky_yeu"]},{"shoes":["khong"]}]}`.
- Nhận xét: Bản phối cho Tết hoặc kỷ yếu chưa có giày dép; phần đánh giá mới phản ánh lựa chọn trên màn hình.
- Gợi ý: Chọn giày bệt, hài hoặc giày kín phù hợp hoạt động thực tế.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R58 — Nón lá trong không gian trong nhà

- Tiêu chí: boi_canh; nhóm: head_setting; tác động: -6.
- Điều kiện: `{"all":[{"setting":["trong_nha"]},{"hasAccessory":"non_la"}]}`.
- Nhận xét: Nón lá có thể chiếm diện tích trong chỗ ngồi hoặc khung hình trong nhà.
- Gợi ý: Giữ nón khi chụp ảnh; cầm hoặc tháo nón khi ngồi, tùy quy định của địa điểm.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R59 — Nón lá trong bản phối ngoài trời

- Tiêu chí: boi_canh; nhóm: head_setting; tác động: +4.
- Điều kiện: `{"all":[{"setting":["ngoai_troi","ca_hai"]},{"hasAccessory":"non_la"},{"any":[{"occasion":["tet","dao_pho"]},{"role":["chup_anh"]}]}]}`.
- Nhận xét: Nón lá tạo điểm nhận diện trong bản phối ngoài trời và ảnh lưu niệm.
- Gợi ý: Kiểm tra độ vừa và cách giữ nón khi di chuyển; ứng dụng không suy ra khả năng chống nắng từ hình ảnh.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R60 — Quạt giấy khi trời nóng trong nhà

- Tiêu chí: boi_canh; nhóm: fan_weather; tác động: +4.
- Điều kiện: `{"all":[{"weather":["nang_nong"]},{"setting":["trong_nha"]},{"hasAccessory":"quat_giay"}]}`.
- Nhận xét: Quạt giấy là phụ kiện cầm tay phù hợp mục đích tạo dáng hoặc quạt nhẹ trong bối cảnh nóng đã khai báo.
- Gợi ý: Cầm quạt khi cần và cất khi phải sử dụng hai tay.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R61 — Guốc trong hoạt động ngoài trời mưa

- Tiêu chí: boi_canh; nhóm: wet_footwear; tác động: -12.
- Điều kiện: `{"all":[{"weather":["mua"]},{"setting":["ngoai_troi","ca_hai"]},{"hasAccessory":"guoc"}]}`.
- Nhận xét: Guốc đang được chọn cho hoạt động ngoài trời có mưa; cần kiểm tra đế và mặt đường thực tế.
- Gợi ý: Cân nhắc giày kín dễ di chuyển. Không thể kết luận độ bám của đế chỉ từ ảnh tủ đồ.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R62 — Dép trong hoạt động ngoài trời mưa

- Tiêu chí: boi_canh; nhóm: wet_footwear; tác động: -10.
- Điều kiện: `{"all":[{"weather":["mua"]},{"setting":["ngoai_troi","ca_hai"]},{"shoes":["dep"]}]}`.
- Nhận xét: Dép có phần chân hở trong bối cảnh mưa ngoài trời, dễ làm bản phối bất tiện khi di chuyển.
- Gợi ý: Chọn giày phù hợp nền đường thực tế và chuẩn bị cách giữ tà áo khỏi ướt.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R63 — Quần lửng khi trời lạnh ngoài trời

- Tiêu chí: boi_canh; nhóm: cold_coverage; tác động: -8.
- Điều kiện: `{"all":[{"weather":["lanh"]},{"setting":["ngoai_troi","ca_hai"]},{"bottom":["quan_lung"]}]}`.
- Nhận xét: Quần lửng để hở một phần chân trong bối cảnh lạnh ngoài trời đã chọn.
- Gợi ý: Cân nhắc quần dài hoặc lớp giữ ấm phù hợp; ứng dụng chưa biết nhiệt độ và chất liệu thực tế.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R64 — Lớp dưới ngắn khi trời lạnh

- Tiêu chí: boi_canh; nhóm: cold_coverage; tác động: -12.
- Điều kiện: `{"all":[{"weather":["lanh"]},{"setting":["ngoai_troi","ca_hai"]},{"bottom":["quan_ngan","vay_ngan"]}]}`.
- Nhận xét: Quần hoặc váy ngắn có độ che phủ thấp trong bối cảnh lạnh ngoài trời.
- Gợi ý: Ưu tiên lớp dưới dài hơn nếu cần giữ ấm và di chuyển lâu.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R65 — Tai nghe trong hoạt động nghi lễ

- Tiêu chí: boi_canh; nhóm: street_formality; tác động: -12.
- Điều kiện: `{"all":[{"occasion":["dam_cuoi","le_hoi_chua"]},{"hasAccessory":"tai_nghe"}]}`.
- Nhận xét: Tai nghe tạo điểm nhấn sinh hoạt hiện đại trong bản phối cho cưới hoặc lễ chùa.
- Gợi ý: Cất tai nghe trong phần nghi lễ nếu muốn tổng thể trang trọng và dễ tương tác.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R66 — Túi lớn khi bê tráp

- Tiêu chí: boi_canh; nhóm: carried_bag_load; tác động: -10.
- Điều kiện: `{"all":[{"role":["be_trap"]},{"accessoryCount":{"items":["ba_lo","tui_tote"],"min":1}}]}`.
- Nhận xét: Ba lô hoặc túi tote tạo thêm phần đồ mang theo khi vai trò đã chọn là bê tráp.
- Gợi ý: Gửi túi hoặc chọn túi nhỏ; kiểm tra khả năng vận động thực tế trước buổi lễ.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R67 — Nhiều phụ kiện cầm tay khi bê tráp

- Tiêu chí: boi_canh; nhóm: free_hands; tác động: -10.
- Điều kiện: `{"all":[{"role":["be_trap"]},{"accessoryCount":{"items":["tui","quat_giay","tui_tote","tui_deo_cheo","tui_xach_thoi_trang"],"min":2}}]}`.
- Nhận xét: Ít nhất hai phụ kiện túi/quạt đang được chọn trong vai trò cần cầm tráp.
- Gợi ý: Giảm phụ kiện cầm tay trong phần bê tráp, dùng lại khi chụp ảnh.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R68 — Nhiều trang sức trong ảnh nhóm

- Tiêu chí: boi_canh; nhóm: jewelry_density; tác động: -6.
- Điều kiện: `{"all":[{"occasion":["ky_yeu"]},{"role":["nhom"]},{"accessoryCount":{"items":["trang_suc","bong_tai","vong_tay","kieng_bac","day_xich_hong"],"min":3}}]}`.
- Nhận xét: Từ ba loại trang sức trở lên có thể làm điểm nhấn cá nhân nổi hơn tổng thể ảnh nhóm.
- Gợi ý: Thống nhất một hoặc hai điểm nhấn với nhóm nếu muốn ảnh đồng đều.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R69 — Khách cưới phối nhiều điểm nhấn

- Tiêu chí: boi_canh; nhóm: wedding_role_attention; tác động: -12.
- Điều kiện: `{"all":[{"occasion":["dam_cuoi"]},{"role":["khach"]},{"garment":["nhat_binh"]},{"accessoryCount":{"items":["trang_suc","bong_tai","vong_tay","kieng_bac","day_xich_hong"],"min":2}}]}`.
- Nhận xét: Nhật Bình cùng nhiều loại trang sức tạo tổng thể nổi bật cho vai trò khách dự cưới.
- Gợi ý: Đối chiếu dress code, giảm trang sức nếu buổi lễ muốn dành điểm nhấn cho nhân vật chính.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R70 — Nhật Bình cho nhân vật chính lễ cưới

- Tiêu chí: boi_canh; nhóm: dress_occasion; tác động: +5.
- Điều kiện: `{"all":[{"occasion":["dam_cuoi"]},{"role":["nhan_vat_chinh"]},{"garment":["nhat_binh"]}]}`.
- Nhận xét: Vai trò nhân vật chính phù hợp mục đích chọn Nhật Bình làm điểm nhấn lễ phục hiện đại.
- Gợi ý: Phối lớp dưới dài và chọn phụ kiện theo mức trang trọng của buổi lễ.
- Nguồn: [Tham khảo](https://khamphahue.com.vn/Hue-24h/Thong-bao/tid/Ao-Nhat-Binh-Mot-di-san-van-hoa-quy-cua-Co-do-Hue.html/pid/11533/cid/28) Nguồn mô tả trang phục và bối cảnh lịch sử. Điều kiện phối đồ, mức cộng/trừ điểm là quy tắc tham khảo của ứng dụng, không phải điều cấm được nguồn xác nhận.

### R71 — Nhật Bình cho mục đích chụp ảnh

- Tiêu chí: boi_canh; nhóm: dress_occasion; tác động: +5.
- Điều kiện: `{"all":[{"role":["chup_anh"]},{"garment":["nhat_binh"]}]}`.
- Nhận xét: Nhật Bình có thể được chọn có chủ đích cho ảnh cổ phục; tư liệu Huế cũng mô tả việc mặc chụp ảnh tham quan hiện nay.
- Gợi ý: Ưu tiên phụ kiện hỗ trợ bố cục ảnh và thuận tiện di chuyển giữa các điểm chụp.
- Nguồn: [Tham khảo](https://khamphahue.com.vn/Hue-24h/Thong-bao/tid/Ao-Nhat-Binh-Mot-di-san-van-hoa-quy-cua-Co-do-Hue.html/pid/11533/cid/28) Nguồn mô tả trang phục và bối cảnh lịch sử. Điều kiện phối đồ, mức cộng/trừ điểm là quy tắc tham khảo của ứng dụng, không phải điều cấm được nguồn xác nhận.

### R72 — Giày và lớp dưới gọn khi bê tráp

- Tiêu chí: boi_canh; nhóm: role_footwear; tác động: +6.
- Điều kiện: `{"all":[{"role":["be_trap"]},{"bottom":["quan_dai_suong","quan_ong_rong","quan_dai"]},{"shoes":["giay_bet","giay_truyen_thong"]}]}`.
- Nhận xét: Quần dài và giày bệt/truyền thống tạo hướng phối gọn cho vai trò bê tráp.
- Gợi ý: Kiểm tra kích cỡ, độ dài gấu quần và độ bám đế ngoài thực tế; hình ảnh không xác nhận được các đặc tính này.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R73 — Bản phối kỷ yếu ít điểm nhấn

- Tiêu chí: boi_canh; nhóm: dress_occasion; tác động: +5.
- Điều kiện: `{"all":[{"occasion":["ky_yeu"]},{"pattern":["tron","hoa_sen","hoi_van"]},{"shoes":["giay_bet","giay_truyen_thong"]},{"metric":{"name":"bottomChroma","max":0.04}}]}`.
- Nhận xét: Họa tiết ít hoặc theo mô típ nhẹ cùng quần màu trung tính tạo nền rõ cho ảnh kỷ yếu.
- Gợi ý: Giữ một phụ kiện nổi bật để bản phối dễ hòa vào bố cục ảnh lớp.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R74 — Áo và lớp dưới gần nhau về độ sáng

- Tiêu chí: dac_trung; nhóm: color_contrast; tác động: -8.
- Điều kiện: `{"metric":{"name":"lightnessContrast","max":0.1}}`.
- Nhận xét: Độ sáng OKLCH của áo và quần/váy chênh không quá 0,10; đường phân lớp có thể ít rõ trên ảnh.
- Gợi ý: Tăng chênh lệch sáng tối nếu muốn rõ hai lớp; phối đồng màu vẫn có thể là chủ đích.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R75 — Phân lớp sáng tối rõ

- Tiêu chí: dac_trung; nhóm: color_contrast; tác động: +5.
- Điều kiện: `{"metric":{"name":"lightnessContrast","min":0.25,"max":0.65}}`.
- Nhận xét: Độ sáng áo và quần/váy chênh 0,25–0,65, giúp phân lớp màu rõ trong mô hình đánh giá.
- Gợi ý: Giữ cặp màu nếu phù hợp mục đích ảnh và ánh sáng thực tế.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R76 — Hai mảng màu cùng đậm

- Tiêu chí: dac_trung; nhóm: color_saturation; tác động: -10.
- Điều kiện: `{"metric":{"name":"saturatedCount","min":2}}`.
- Nhận xét: Cả áo và quần/váy đều có độ chroma OKLCH trên 0,18; hai mảng cùng cạnh tranh điểm nhấn.
- Gợi ý: Giảm độ đậm của một mảng hoặc dùng quần/váy trung tính nếu muốn tổng thể dịu hơn.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R77 — Màu áo nổi trên nền trung tính

- Tiêu chí: dac_trung; nhóm: color_saturation; tác động: +5.
- Điều kiện: `{"all":[{"metric":{"name":"mainChroma","min":0.18}},{"metric":{"name":"bottomChroma","max":0.04}}]}`.
- Nhận xét: Áo có độ chroma cao, trong khi lớp dưới gần trung tính, tạo một trọng tâm màu.
- Gợi ý: Giữ phụ kiện đơn giản để tập trung vào áo.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R78 — Cặp màu đạt hài hòa cao

- Tiêu chí: dac_trung; nhóm: color_harmony; tác động: +4.
- Điều kiện: `{"metric":{"name":"colorHarmony","min":80}}`.
- Nhận xét: Cặp màu đạt ít nhất 80/100 theo mô hình tương phản và sắc độ của ứng dụng.
- Gợi ý: Có thể giữ cặp màu; điểm màu không xác nhận cấu trúc hay xuất xứ trang phục.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R79 — Cặp màu cần cân nhắc

- Tiêu chí: dac_trung; nhóm: color_harmony; tác động: -8.
- Điều kiện: `{"metric":{"name":"colorHarmony","max":45}}`.
- Nhận xét: Cặp màu đạt không quá 45/100 theo mô hình màu hiện tại; cần xem cùng mục đích phối.
- Gợi ý: Thử một lớp dưới trung tính hoặc thay đổi độ sáng trước khi đổi cả áo.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R80 — Hai mảng tối cho ảnh ngoài trời buổi tối

- Tiêu chí: boi_canh; nhóm: color_night; tác động: -5.
- Điều kiện: `{"all":[{"setting":["ngoai_troi","ca_hai"]},{"timeOfDay":["buoi_toi"]},{"metric":{"name":"mainLightness","max":0.34}},{"metric":{"name":"bottomLightness","max":0.34}}]}`.
- Nhận xét: Cả hai mảng có độ sáng OKLCH thấp trong bối cảnh ảnh ngoài trời buổi tối; chi tiết có thể khó tách nếu thiếu ánh sáng.
- Gợi ý: Tăng sáng một mảng hoặc kiểm tra ánh sáng tại điểm chụp; ứng dụng không đo ánh sáng môi trường.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R81 — Màu áo nhẹ theo phong cách pastel

- Tiêu chí: cach_tan; nhóm: style_color; tác động: +4.
- Điều kiện: `{"all":[{"style":["pastel"]},{"metric":{"name":"mainLightness","min":0.7}},{"metric":{"name":"mainChroma","max":0.12}}]}`.
- Nhận xét: Màu áo sáng và chroma thấp phù hợp hướng pastel đã chọn.
- Gợi ý: Duy trì phụ kiện ít tương phản mạnh nếu muốn giữ cảm giác nhẹ.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R82 — Nhiều loại trang sức cùng lúc

- Tiêu chí: phu_kien; nhóm: jewelry_density; tác động: -10.
- Điều kiện: `{"accessoryCount":{"items":["trang_suc","bong_tai","vong_tay","kieng_bac","day_xich_hong"],"min":3}}`.
- Nhận xét: Ít nhất ba loại trang sức đang được chọn; nhiều điểm phản chiếu có thể làm tổng thể khó có trọng tâm.
- Gợi ý: Chọn một điểm nhấn chính, cân nhắc bỏ bớt vòng tay, bông tai hoặc kiềng.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R83 — Nhiều phụ kiện quanh đầu

- Tiêu chí: phu_kien; nhóm: head_density; tác động: -8.
- Điều kiện: `{"accessoryCount":{"items":["non_la","non_quai_thao","khan_van","khan_mo_qua","khan_xep","hoa_cai_toc","mu_luoi_trai","mu_cao_boi"],"min":3}}`.
- Nhận xét: Ít nhất ba loại nón, khăn hoặc hoa cài đang được chọn cùng lúc.
- Gợi ý: Giữ bộ khăn và nón có chủ đích; giảm món còn lại nếu che mặt hoặc chồng lớp khó nhìn.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R84 — Nhiều túi trong một bản phối

- Tiêu chí: phu_kien; nhóm: carried_bag_load; tác động: -8.
- Điều kiện: `{"accessoryCount":{"items":["tui","ba_lo","tui_tote","tui_deo_cheo","tui_xach_thoi_trang"],"min":2}}`.
- Nhận xét: Từ hai loại túi hoặc ba lô trở lên tạo nhiều lớp phụ kiện mang theo.
- Gợi ý: Giữ một túi theo hoạt động chính, kiểm tra cách mang thực tế.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R85 — Móc khóa chưa có túi đi kèm

- Tiêu chí: phu_kien; nhóm: bag_charm; tác động: -6.
- Điều kiện: `{"all":[{"hasAccessory":"moc_khoa_bong"},{"not":{"accessoryCount":{"items":["tui","ba_lo","tui_tote","tui_deo_cheo","tui_xach_thoi_trang"],"min":1}}}]}`.
- Nhận xét: Móc khóa bông được chọn nhưng không có túi hoặc ba lô trong bộ đồ để thể hiện điểm gắn.
- Gợi ý: Chọn túi phù hợp hoặc bỏ móc khóa; ứng dụng chưa biết bạn có gắn vào vị trí khác hay không.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R86 — Họa tiết nổi cùng nhiều trang sức

- Tiêu chí: phu_kien; nhóm: pattern_density; tác động: -10.
- Điều kiện: `{"all":[{"pattern":["rong_may","phuong","ke_soc","cham_bi"]},{"accessoryCount":{"items":["trang_suc","bong_tai","vong_tay","kieng_bac","day_xich_hong"],"min":2}}]}`.
- Nhận xét: Họa tiết nổi và ít nhất hai loại trang sức tạo nhiều điểm hút mắt.
- Gợi ý: Giảm một loại trang sức hoặc đổi họa tiết đơn giản để tạo trọng tâm.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R87 — Phụ kiện dày với phong cách tối giản

- Tiêu chí: phu_kien; nhóm: accessory_density; tác động: -8.
- Điều kiện: `{"all":[{"style":["toi_gian"]},{"accessoryCount":{"items":["trang_suc","bong_tai","vong_tay","kieng_bac","day_xich_hong","tui","ba_lo","tui_tote","tui_deo_cheo","tui_xach_thoi_trang","non_la","non_quai_thao","khan_van","khan_mo_qua","khan_xep","hoa_cai_toc","mu_luoi_trai","mu_cao_boi","quat_giay","tai_nghe","kinh_ram","moc_khoa_bong","gang_tay_ho_ngon"],"min":5}}]}`.
- Nhận xét: Từ năm loại phụ kiện ngoài giày trở lên khác mục tiêu ít chi tiết của phong cách tối giản.
- Gợi ý: Giữ hai hoặc ba món cần thiết, chọn một món tạo điểm nhấn.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R88 — Nhiều món hiện đại trong hướng truyền thống

- Tiêu chí: cach_tan; nhóm: modern_density; tác động: -10.
- Điều kiện: `{"all":[{"style":["truyen_thong"]},{"accessoryCount":{"items":["sneaker","giay_bup_be","giay_the_thao","dep_crocs","dep_le","tai_nghe","mu_luoi_trai","moc_khoa_bong","ba_lo","tui_tote","tui_deo_cheo","kinh_ram","day_xich_hong","gang_tay_ho_ngon","mu_cao_boi","tui_xach_thoi_trang"],"min":3}}]}`.
- Nhận xét: Ít nhất ba loại phụ kiện hiện đại cùng xuất hiện khi hướng phối đã chọn là truyền thống.
- Gợi ý: Giảm phụ kiện hiện đại hoặc đổi phong cách sang đường phố nếu đây là chủ đích.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R89 — Một đến hai điểm nhấn đường phố

- Tiêu chí: cach_tan; nhóm: modern_density; tác động: +6.
- Điều kiện: `{"all":[{"style":["duong_pho"]},{"occasion":["dao_pho"]},{"accessoryCount":{"items":["sneaker","giay_bup_be","giay_the_thao","dep_crocs","dep_le","tai_nghe","mu_luoi_trai","moc_khoa_bong","ba_lo","tui_tote","tui_deo_cheo","kinh_ram","day_xich_hong","gang_tay_ho_ngon","mu_cao_boi","tui_xach_thoi_trang"],"min":1,"max":2}}]}`.
- Nhận xét: Một đến hai điểm nhấn hiện đại phù hợp mục tiêu cách tân cho hoạt động dạo phố.
- Gợi ý: Giữ cấu trúc áo và lớp dưới rõ, tránh tăng nhiều điểm nhấn cùng lúc.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R90 — Bản phối tối giản ít chi tiết

- Tiêu chí: cach_tan; nhóm: minimalist_balance; tác động: +5.
- Điều kiện: `{"all":[{"style":["toi_gian"]},{"pattern":["tron"]},{"accessoryCount":{"items":["trang_suc","bong_tai","vong_tay","kieng_bac","day_xich_hong","tui","ba_lo","tui_tote","tui_deo_cheo","tui_xach_thoi_trang","non_la","non_quai_thao","khan_van","khan_mo_qua","khan_xep","hoa_cai_toc","mu_luoi_trai","mu_cao_boi","quat_giay","tai_nghe","kinh_ram","moc_khoa_bong","gang_tay_ho_ngon"],"max":2}}]}`.
- Nhận xét: Áo trơn cùng không quá hai loại phụ kiện ngoài giày phù hợp hướng tối giản.
- Gợi ý: Giữ đường nét và cặp màu làm trọng tâm.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R91 — Họa tiết hiện đại trong hướng truyền thống

- Tiêu chí: cach_tan; nhóm: pattern_style; tác động: -8.
- Điều kiện: `{"all":[{"style":["truyen_thong"]},{"pattern":["ke_soc","cham_bi"]}]}`.
- Nhận xét: Kẻ sọc hoặc chấm bi tạo hướng đồ họa hiện đại trong bản phối đã chọn truyền thống.
- Gợi ý: Chọn áo trơn hoặc mô típ truyền thống nếu muốn sát hướng phối; họa tiết hiện đại có thể giữ trong cách tân.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R92 — Màu áo đậm trong hướng pastel

- Tiêu chí: cach_tan; nhóm: style_color; tác động: -8.
- Điều kiện: `{"all":[{"style":["pastel"]},{"metric":{"name":"mainChroma","min":0.18}}]}`.
- Nhận xét: Độ chroma áo từ 0,18 trở lên khác hướng màu nhẹ thường dùng cho pastel.
- Gợi ý: Giảm độ đậm, tăng độ sáng hoặc chọn phong cách khác phù hợp màu đang thích.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R93 — Ngũ thân trơn trong dịp trang trọng

- Tiêu chí: dac_trung; nhóm: garment_pattern; tác động: +5.
- Điều kiện: `{"all":[{"garment":["ao_ngu_than"]},{"pattern":["tron"]},{"occasion":["tet","ky_yeu","dam_cuoi","le_hoi_chua"]}]}`.
- Nhận xét: Áo ngũ thân trơn giữ đường nét áo làm điểm nhấn trong hướng phối trang trọng của ứng dụng.
- Gợi ý: Có thể thêm khăn xếp hoặc một món trang sức; ứng dụng chưa kiểm tra cổ áo, số khuy hay chất liệu.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R94 — Nhật Bình với họa tiết đồ họa hiện đại

- Tiêu chí: cach_tan; nhóm: pattern_style; tác động: -8.
- Điều kiện: `{"all":[{"garment":["nhat_binh"]},{"pattern":["ke_soc","cham_bi"]},{"style":["truyen_thong"]}]}`.
- Nhận xét: Kẻ sọc hoặc chấm bi phủ trên Nhật Bình tạo cách tân rõ khi mục tiêu đã chọn là truyền thống.
- Gợi ý: Đổi họa tiết nếu muốn nhấn mạnh dáng cổ phục; không áp dụng quy định phẩm cấp lịch sử cho người mặc hiện nay.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R95 — Nhiều điểm nhấn trong bản phối đường phố

- Tiêu chí: cach_tan; nhóm: visual_focus; tác động: -6.
- Điều kiện: `{"all":[{"style":["duong_pho"]},{"pattern":["rong_may","phuong","ke_soc","cham_bi"]},{"accessoryCount":{"items":["sneaker","giay_bup_be","giay_the_thao","dep_crocs","dep_le","tai_nghe","mu_luoi_trai","moc_khoa_bong","ba_lo","tui_tote","tui_deo_cheo","kinh_ram","day_xich_hong","gang_tay_ho_ngon","mu_cao_boi","tui_xach_thoi_trang"],"min":2}}]}`.
- Nhận xét: Họa tiết nổi kết hợp nhiều món hiện đại có thể làm bản phối đường phố thiếu trọng tâm.
- Gợi ý: Giữ một mảng họa tiết hoặc một phụ kiện hiện đại làm điểm nhấn chính.
- Nguồn: Quy tắc của ứng dụng. Quy tắc phối đồ của ứng dụng, dựa trên các món đã chọn và bối cảnh đã cung cấp; không phải quy định văn hóa bắt buộc.

### R96 — Tứ thân với khăn và nón quai thao

- Tiêu chí: phu_kien; nhóm: cultural_accessory_set; tác động: +10.
- Điều kiện: `{"all":[{"garment":["ao_tu_than"]},{"hasAccessory":"non_quai_thao"},{"hasAccessory":"khan_mo_qua"}]}`.
- Nhận xét: Khăn mỏ quạ và nón quai thao tạo hướng phối tứ thân gắn với hình ảnh Quan họ của ứng dụng.
- Gợi ý: Giữ tổng thể nhiều lớp gọn; tham khảo tư liệu địa phương nếu cần phục dựng đúng một hình thức trình diễn.
- Nguồn: [Tham khảo](https://dsvh.gov.vn/dan-ca-quan-ho-bac-ninh-482) Nguồn mô tả trang phục và bối cảnh lịch sử. Điều kiện phối đồ, mức cộng/trừ điểm là quy tắc tham khảo của ứng dụng, không phải điều cấm được nguồn xác nhận.
