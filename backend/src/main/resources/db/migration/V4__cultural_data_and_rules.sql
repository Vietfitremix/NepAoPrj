-- V4__cultural_data_and_rules.sql
-- Nạp đầy đủ dữ liệu văn hóa, lịch sử và quy tắc chấm điểm cho 5 trang phục Việt cổ truyền

DELETE FROM cultural_rules;
DELETE FROM cultural_knowledge;

-- 1. Cập nhật thông tin nguồn gốc và ý nghĩa văn hóa trong bảng OUTFITS
UPDATE outfits
SET description = 'Áo dài truyền thống với tà áo thướt tha, cổ đứng thanh lịch, biểu tượng vượt thời gian của trang phục Việt Nam.',
    origin = 'Phát triển từ áo ngũ thân lập lĩnh thời Nguyễn, được cách tân vào những năm 1930 bởi họa sĩ Cát Tường (Lemur) và Lê Phổ tại Hà Nội, dần định hình thành tà áo dài duyên dáng ngày nay.',
    cultural_meaning = 'Biểu trưng cho vẻ đẹp thuần khiết, kín đáo mà trang nhã của người Việt. Tà áo ôm sát nhẹ nhàng tôn vinh nét đẹp thanh tao và khí chất nhã nhặn trong đời sống văn hóa dân tộc.'
WHERE code = 'AO_DAI';

UPDATE outfits
SET description = 'Áo tứ thân bốn vạt duyên dáng, đi kèm dải yếm thắm và thắt lưng lụa, gắn liền với làn điệu dân ca quan họ Bắc Ninh.',
    origin = 'Xuất hiện từ thời kỳ phong kiến trung đại (thế kỷ 12-14), phát triển rực rỡ và trở thành trang phục thường nhật lẫn lễ hội tiêu biểu của phụ nữ đồng bằng Bắc Bộ vào thế kỷ 18-19.',
    cultural_meaning = 'Bốn vạt áo tượng trưng cho tứ thân phụ mẫu (cha mẹ mình và cha mẹ chồng). Hai vạt trước buộc thắt biểu trưng cho nghĩa tình phu thê bền chặt. Dải yếm thắm và thắt lưng thể hiện nét đẹp thùy mị, chịu thương chịu khó.'
WHERE code = 'AO_TU_THAN';

UPDATE outfits
SET description = 'Áo ngũ thân cài khuy nghi lễ, may từ 5 thân vải ghép lại với cổ đứng lập lĩnh nghiêm trang và đường khuy chéo.',
    origin = 'Được định hình từ sắc lệnh cải cách y phục năm 1744 của Chúa Nguyễn Phúc Khoát tại Đàng Trong, sau đó được Hoàng đế Minh Mạng chuẩn hóa thành quốc phục toàn quốc vào năm 1827.',
    cultural_meaning = 'Năm thân áo tượng trưng cho tứ thân phụ mẫu và thân con ở trong lòng che chở. Năm chiếc khuy cài biểu trưng cho Ngũ thường: Nhân, Lễ, Nghĩa, Trí, Tín - chuẩn mực đạo đức của người quân tử.'
WHERE code = 'AO_NGU_THAN';

UPDATE outfits
SET description = 'Cung phục hoàng gia triều Nguyễn nổi bật với cổ áo hình chữ nhật bản rộng trước ngực, viền hoa văn tinh xảo.',
    origin = 'Được điển chế hóa dưới triều đại nhà Nguyễn (1802-1945), quy định làm thường phục cao quý của Hoàng thái hậu, Hoàng hậu, Công chúa và lễ phục của các mệnh phụ quý tộc.',
    cultural_meaning = 'Thể hiện trật tự phẩm hàm, sự trang nghiêm vương giả và nghệ thuật thêu tay đỉnh cao của chốn hoàng cung Huế; mang đậm giá trị di sản cung đình Việt Nam.'
WHERE code = 'NHAT_BINH';

UPDATE outfits
SET description = 'Trang phục mộc mạc, phóng khoáng của miền Tây Nam Bộ với thiết kế cổ tròn, xẻ hai tà và túi tiện lợi.',
    origin = 'Xuất hiện phổ biến tại đồng bằng sông Cửu Long từ thế kỷ 19, lấy cảm hứng cải biên nhằm thích ứng hoàn hảo với khí hậu nhiệt đới gió mùa và đời sống sông nước phù sa.',
    cultural_meaning = 'Tượng trưng cho vẻ đẹp hồn hậu, chân chất, kiên cường và hiếu khách của người dân phương Nam; gắn liền với hình ảnh người mẹ, người chị trong lao động và bảo vệ quê hương.'
WHERE code = 'AO_BA_BA';

-- 2. Nạp dữ liệu chi tiết vào bảng CULTURAL_KNOWLEDGE
-- Áo dài (AO_DAI)
INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'ORIGIN', 'Tiến trình lịch sử Áo Dài',
       'Áo dài có cội nguồn sâu xa từ áo ngũ thân tay chẽn thời Nguyễn. Vào thập niên 1930, phong trào cách tân y phục của nhóm Tự Lực Văn Đoàn, đứng đầu là họa sĩ Cát Tường (Lemur) và Lê Phổ, đã kết hợp cấu trúc phương Tây để làm áo ôm sát cơ thể, tạo nên vóc dáng áo dài hiện đại.',
       'Ngàn năm áo mũ (Trần Quang Đức - NXB Thế Giới)', 'https://baotanglichsu.vn/vi/Articles/3096/13364/ngan-nam-ao-mu.html'
FROM outfits WHERE code = 'AO_DAI';

INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'MEANING', 'Ý nghĩa biểu tượng văn hóa',
       'Áo dài không chỉ tôn vinh vóc dáng mà còn biểu thị nếp sống thanh nhã, tôn ti trật tự và phẩm hạnh kín đáo. Tà áo dài là biểu tượng văn hóa trường tồn của người Việt trong các nghi lễ trang trọng, học đường và giao lưu quốc tế.',
       'Bảo tàng Phụ nữ Việt Nam', 'https://baotangphunu.org.vn/ao-dai-di-san-van-hoa-viet-nam/'
FROM outfits WHERE code = 'AO_DAI';

INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'CHARACTERISTICS', 'Cấu trúc và phom dáng',
       'Áo dài gồm thân trước và thân sau may dài quá gối, xẻ tà từ eo xuống. Cổ áo truyền thống cao từ 2-4cm hoặc cổ tròn cách tân. Áo thường được mặc cùng quần lụa suông rộng, kết hợp hài hòa cùng nón lá hoặc khăn đóng.',
       'Hội Di sản Văn hóa Việt Nam', 'https://vietnamheritage.com.vn/trang-phuc-truyen-thong/'
FROM outfits WHERE code = 'AO_DAI';

-- Áo tứ thân (AO_TU_THAN)
INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'ORIGIN', 'Nguồn gốc áo tứ thân Kinh Bắc',
       'Áo tứ thân là trang phục cổ truyền của phụ nữ Bắc Bộ, gắn liền với lịch sử ngàn năm văn hiến và hội Lim quan họ. Trước thế kỷ 20, áo tứ thân là trang phục phổ biến của phụ nữ nông thôn cũng như thành thị trong sinh hoạt và lễ hội.',
       'Viện Văn hóa Nghệ thuật Quốc gia', 'https://vicas.org.vn/ao-tu-than-dong-bang-bac-bo'
FROM outfits WHERE code = 'AO_TU_THAN';

INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'MEANING', 'Ý nghĩa bốn vạt và đạo hiếu',
       'Bốn vạt áo mang ý niệm sâu sắc về tứ thân phụ mẫu (cha mẹ đẻ, cha mẹ chồng). Hai vạt trước buộc lại thể hiện tình nghĩa vợ chồng son sắt, thắt lưng lụa buộc chặt ngoài cùng vừa giữ tà áo kín đáo vừa tượng trưng cho sự bao bọc yêu thương gia đình.',
       'Bảo tàng Phụ nữ Việt Nam', 'https://baotangphunu.org.vn/ao-tu-than-va-y-nghia-dao-hieu/'
FROM outfits WHERE code = 'AO_TU_THAN';

INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'CHARACTERISTICS', 'Cấu trúc đa lớp dân gian',
       'Áo gồm 4 vạt dài, 2 vạt sau may liền giữa sống lưng, 2 vạt trước thả tự do để buộc vạt. Bên trong mặc yếm lụa cổ xây hoặc cổ xẻ, ngoài khoác áo cánh mỏng rồi đến áo tứ thân, đầu đội khăn mỏ quạ hoặc nón quai thao.',
       'Bảo tàng Lịch sử Quốc gia', 'https://baotanglichsu.vn/vi/Articles/3097/15432/trang-phuc-dan-gian-viet-nam.html'
FROM outfits WHERE code = 'AO_TU_THAN';

-- Áo ngũ thân (AO_NGU_THAN)
INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'ORIGIN', 'Chuẩn mực quốc phục thời Nguyễn',
       'Áo ngũ thân được Chúa Nguyễn Phúc Khoát định hình năm 1744 nhằm xây dựng bản sắc riêng cho Đàng Trong. Đến năm 1827-1837, vua Minh Mạng ban hành sắc lệnh toàn quốc áp dụng thống nhất, đưa áo ngũ thân trở thành quốc phục chung của cả nam và nữ.',
       'Trung tâm Bảo tồn Di tích Cố đô Huế', 'https://hueworldheritage.org.vn/ao-ngu-than-trieu-nguyen'
FROM outfits WHERE code = 'AO_NGU_THAN';

INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'MEANING', 'Đạo làm người và ngũ thường',
       'Năm thân áo tượng trưng cho tứ thân phụ mẫu che chở đứa con ở giữa. Năm cúc áo làm bằng kim loại, ngọc hoặc gỗ quý tượng trưng cho năm đức tính của người quân tử: Nhân, Lễ, Nghĩa, Trí, Tín.',
       'Ngàn năm áo mũ (Trần Quang Đức)', 'https://baotanglichsu.vn/vi/Articles/3096/13364/ngan-nam-ao-mu.html'
FROM outfits WHERE code = 'AO_NGU_THAN';

INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'CHARACTERISTICS', 'Đặc trưng cổ đứng và vạt chẽn',
       'Áo ngũ thân có cổ đứng cao thẳng (cổ lập lĩnh), vạt áo uốn lượn hình cánh cung, 5 cúc cài bên sườn phải kín đáo. Đường may thẳng thắn, kín cổ thể hiện tính trang nghiêm, đĩnh đạc của người mặc.',
       'Hội Di sản Văn hóa Việt Nam', 'https://vietnamheritage.com.vn/ao-ngu-than-phuc-dung/'
FROM outfits WHERE code = 'AO_NGU_THAN';

-- Nhật bình (NHAT_BINH)
INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'ORIGIN', 'Cung phục điển chế triều Nguyễn',
       'Áo Nhật bình là lễ phục của bậc hậu phi, công chúa và mệnh phụ triều Nguyễn. Tên gọi bắt nguồn từ dải cổ áo to bản đối khâm tạo thành một hình chữ nhật phẳng phiu trước ngực.',
       'Khâm định Đại Nam hội điển sự lệ', 'https://baotanglichsu.vn/vi/Articles/3096/nhat-binh-cung-dinh-hue.html'
FROM outfits WHERE code = 'NHAT_BINH';

INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'MEANING', 'Đỉnh cao mỹ thuật cung đình',
       'Mỗi màu sắc và hoa văn thêu trên áo Nhật bình tượng trưng cho vị thế và phẩm tước trong hoàng tộc (Hoàng hậu mặc vàng hoặc đỏ, công chúa mặc đỏ, cung tần mặc tím hoặc lam). Áo mang ý nghĩa tôn nghiêm và uy quyền quý tộc.',
       'Trung tâm Bảo tồn Di tích Cố đô Huế', 'https://hueworldheritage.org.vn/le-phuc-cung-dinh'
FROM outfits WHERE code = 'NHAT_BINH';

INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'CHARACTERISTICS', 'Cổ áo nhật bình và tay áo ngũ hành',
       'Điểm nổi bật nhất là cổ áo viền chữ nhật chạy dọc xuống ngực, tay áo đính dải vải ngũ sắc đại diện ngũ hành (kim, mộc, thủy, hỏa, thổ). Khi mặc thường cài trâm, đội khăn vành và mang hài phượng.',
       'Bảo tàng Mỹ thuật Cung đình Huế', 'https://baotanglichsu.vn/vi/Articles/3096/my-thuat-trang-phuc-trieu-nguyen.html'
FROM outfits WHERE code = 'NHAT_BINH';

-- Áo bà ba (AO_BA_BA)
INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'ORIGIN', 'Dấu ấn phương Nam khẩn hoang',
       'Áo bà ba xuất hiện phổ biến vào thế kỷ 19 tại Nam Bộ. Với thiết kế tối giản, áo giúp người dân thuận tiện trong việc làm nông, chèo xuồng và thích ứng tốt với thời tiết nắng gió sông nước đồng bằng Cửu Long.',
       'Bảo tàng Phụ nữ Nam Bộ', 'https://baotangphununambo.vn/chiec-ao-ba-ba-nam-bo/'
FROM outfits WHERE code = 'AO_BA_BA';

INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'MEANING', 'Tâm hồn hào sảng phương Nam',
       'Áo bà ba gắn liền với đức tính kiên nhẫn, chịu thương chịu khó nhưng luôn lạc quan, hào sảng và mến khách của người dân Nam Bộ qua nhiều thế hệ.',
       'Viện Nghiên cứu Văn hóa Nam Bộ', 'https://vicas.org.vn/ao-ba-ba-bieu-tuong-mien-tay'
FROM outfits WHERE code = 'AO_BA_BA';

INSERT INTO cultural_knowledge (outfit_id, category, title, content, source_name, source_url)
SELECT id, 'CHARACTERISTICS', 'Đường nét mộc mạc và tiện dụng',
       'Áo không có cổ, thân trước xẻ giữa cài hàng nút bấm hoặc nút nhựa, xẻ tà hai bên hông. Áo may nhấn eo nhẹ, hai túi to ở vạt trước rất tiện dụng, thường phối cùng nón lá và khăn rằn.',
       'Bảo tàng Lịch sử TP. Hồ Chí Minh', 'https://baotanglichsutphcm.com.vn/ao-ba-ba-truyen-thong.html'
FROM outfits WHERE code = 'AO_BA_BA';

-- 3. Nạp bộ quy tắc CULTURAL_RULES cho cả 5 trang phục (đảm bảo đủ 5 danh mục ScoreCategory: STRUCTURE, GARMENT_CHARACTERISTICS, ACCESSORIES, CONTEXT, MODERN_REMIX)

-- Macro nạp quy tắc cho Áo Dài (AO_DAI)
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'STRUCTURE', 'OUTFIT', 'AO_DAI', 'RECOMMENDED', 0, 'LOW',
       'Cấu trúc tà áo dài chuẩn mực, cân đối và thướt tha.', 'Giữ tà áo phẳng phiu và dáng đứng thanh tao.',
       'Bảo tàng Phụ nữ Việt Nam', 'https://baotangphunu.org.vn/ao-dai-di-san-van-hoa-viet-nam/'
FROM outfits o WHERE o.code = 'AO_DAI';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'GARMENT_CHARACTERISTICS', 'COLOR', 'WHITE', 'RECOMMENDED', 0, 'LOW',
       'Sắc trắng tinh khôi biểu trưng cho nét đẹp thanh tao, thuần khiết.', 'Rất hợp cho dịp lễ trường lớp, tốt nghiệp hoặc dạo phố.',
       'Hội Di sản Văn hóa Việt Nam', 'https://vietnamheritage.com.vn/trang-phuc-truyen-thong/'
FROM outfits o WHERE o.code = 'AO_DAI';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'GARMENT_CHARACTERISTICS', 'COLOR', 'RED', 'RECOMMENDED', 0, 'LOW',
       'Sắc đỏ son rực rỡ mang ý nghĩa may mắn, hỷ sự và cát tường.', 'Tuyệt vời cho dịp Tết Nguyên Đán, lễ hội truyền thống hoặc đám cưới.',
       'Ngàn năm áo mũ', 'https://baotanglichsu.vn/vi/Articles/3096/13364/ngan-nam-ao-mu.html'
FROM outfits o WHERE o.code = 'AO_DAI';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'NON_LA', 'RECOMMENDED', 0, 'LOW',
       'Nón lá là phụ kiện đồng hành kinh điển cùng tà áo dài Việt Nam.', 'Đội nghiêng hoặc cầm tay nhẹ nhàng tạo dáng duyên dáng.',
       'Bảo tàng Phụ nữ Việt Nam', 'https://baotangphunu.org.vn/ao-dai-di-san-van-hoa-viet-nam/'
FROM outfits o WHERE o.code = 'AO_DAI';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'WHITE_SNEAKERS', 'CAUTION', -10, 'LOW',
       'Giày thể thao trắng mang nét phá cách hiện đại cho áo dài.', 'Nên chọn sneaker phom thon gọn, đơn sắc để giữ nét thanh lịch của tà áo.',
       'Tạp chí Thời trang Di sản', 'https://vietnamheritage.com.vn/remix-ao-dai-sneakers/'
FROM outfits o WHERE o.code = 'AO_DAI';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'CONTEXT', 'EVENT', 'TET', 'RECOMMENDED', 0, 'LOW',
       'Áo dài là trang phục hoàn hảo nhất cho dịp du xuân, lễ Tết.', 'Kết hợp cùng phụ kiện nhẹ nhàng tạo không khí tết truyền thống.',
       'Viện Văn hóa Nghệ thuật Quốc gia', 'https://vicas.org.vn/ao-dai-tet/'
FROM outfits o WHERE o.code = 'AO_DAI';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'CONTEXT', 'EVENT', 'GRADUATION', 'RECOMMENDED', 0, 'LOW',
       'Áo dài trắng là dấu ấn thanh xuân kỷ yếu trường học Việt Nam.', 'Phối cùng bó hoa tươi hoặc quạt lụa nhẹ nhàng.',
       'Bảo tàng Phụ nữ Việt Nam', 'https://baotangphunu.org.vn/ao-dai-ky-yeu/'
FROM outfits o WHERE o.code = 'AO_DAI';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'MODERN_REMIX', 'STYLE', 'TRADITIONAL', 'RECOMMENDED', 0, 'LOW',
       'Phong cách truyền thống giữ trọn tinh hoa chuẩn mực của áo dài.', 'Tôn trọng chiều dài tà áo và kiểu cổ truyền thống.',
       'Hội Di sản Văn hóa Việt Nam', 'https://vietnamheritage.com.vn/trang-phuc-truyen-thong/'
FROM outfits o WHERE o.code = 'AO_DAI';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'MODERN_REMIX', 'STYLE', 'GEN_Z', 'RECOMMENDED', 0, 'LOW',
       'Cách tân Gen Z trẻ trung, năng động mà vẫn giữ được hồn cốt dân tộc.', 'Có thể phối cùng túi xách mini hoặc giày hiện đại.',
       'Tạp chí Thiết kế Sáng tạo', 'https://vietnamheritage.com.vn/gen-z-viet-phuc/'
FROM outfits o WHERE o.code = 'AO_DAI';

-- Áo tứ thân (AO_TU_THAN)
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'STRUCTURE', 'OUTFIT', 'AO_TU_THAN', 'RECOMMENDED', 0, 'LOW',
       'Phom dáng áo tứ thân bốn vạt buông rủ mang đậm chất văn hóa Bắc Bộ.', 'Hai vạt trước buộc eo tự nhiên, bên trong phối yếm thắm kín đáo.',
       'Bảo tàng Phụ nữ Việt Nam', 'https://baotangphunu.org.vn/ao-tu-than-va-y-nghia-dao-hieu/'
FROM outfits o WHERE o.code = 'AO_TU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'GARMENT_CHARACTERISTICS', 'COLOR', 'RED', 'RECOMMENDED', 0, 'LOW',
       'Tông đỏ rực rỡ gợi không khí lễ hội mùa xuân Kinh Bắc.', 'Thích hợp phối cùng thắt lưng lụa xanh tạo độ tương phản duyên dáng.',
       'Viện Văn hóa Nghệ thuật Quốc gia', 'https://vicas.org.vn/ao-tu-than-dong-bang-bac-bo'
FROM outfits o WHERE o.code = 'AO_TU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'GARMENT_CHARACTERISTICS', 'COLOR', 'CREAM', 'RECOMMENDED', 0, 'LOW',
       'Sắc kem nhã nhặn tôn nét đằm thắm mộc mạc của phụ nữ xưa.', 'Hài hòa với khăn mỏ quạ và guốc mộc.',
       'Bảo tàng Lịch sử Quốc gia', 'https://baotanglichsu.vn/vi/Articles/3097/15432/trang-phuc-dan-gian-viet-nam.html'
FROM outfits o WHERE o.code = 'AO_TU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'NON_LA', 'RECOMMENDED', 0, 'LOW',
       'Nón lá hài hòa với nét bình dị, duyên dáng của áo tứ thân.', 'Có thể thử kết hợp thêm nón quai thao khi đi trẩy hội.',
       'Bảo tàng Phụ nữ Việt Nam', 'https://baotangphunu.org.vn/ao-tu-than-va-y-nghia-dao-hieu/'
FROM outfits o WHERE o.code = 'AO_TU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'FAN', 'RECOMMENDED', 0, 'LOW',
       'Quạt tay lụa hoặc quạt giấy là điểm nhấn trang nhã của liền chị.', 'Cầm quạt trước ngực hoặc cài thắt lưng khi không dùng.',
       'Viện Văn hóa Nghệ thuật Quốc gia', 'https://vicas.org.vn/ao-tu-than-dong-bang-bac-bo'
FROM outfits o WHERE o.code = 'AO_TU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'CONTEXT', 'EVENT', 'FESTIVAL', 'RECOMMENDED', 0, 'LOW',
       'Áo tứ thân là linh hồn của các lễ hội dân gian và hội xuân đồng bằng Bắc Bộ.', 'Phù hợp nhất cho các buổi giao lưu văn hóa, biểu diễn nghệ thuật.',
       'Bảo tàng Lịch sử Quốc gia', 'https://baotanglichsu.vn/vi/Articles/3097/15432/trang-phuc-dan-gian-viet-nam.html'
FROM outfits o WHERE o.code = 'AO_TU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'CONTEXT', 'EVENT', 'TET', 'RECOMMENDED', 0, 'LOW',
       'Áo tứ thân mang lại không khí Tết hoài cổ, ấm cúng và độc đáo.', 'Nên chọn tông màu tươi sáng như đỏ, vàng để đón chào năm mới.',
       'Viện Văn hóa Nghệ thuật Quốc gia', 'https://vicas.org.vn/ao-tu-than-dong-bang-bac-bo'
FROM outfits o WHERE o.code = 'AO_TU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'MODERN_REMIX', 'STYLE', 'TRADITIONAL', 'RECOMMENDED', 0, 'LOW',
       'Phong cách truyền thống gìn giữ trọn vẹn nét văn hóa Kinh Bắc.', 'Mặc đủ lớp áo cánh, yếm và thắt lưng lụa.',
       'Bảo tàng Phụ nữ Việt Nam', 'https://baotangphunu.org.vn/ao-tu-than-va-y-nghia-dao-hieu/'
FROM outfits o WHERE o.code = 'AO_TU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'MODERN_REMIX', 'STYLE', 'GEN_Z', 'RECOMMENDED', 0, 'LOW',
       'Phối đồ tứ thân cách tân Gen Z tạo sự nổi bật và cá tính riêng biệt.', 'Giữ kết cấu 4 vạt và phối phụ kiện nhẹ nhàng.',
       'Tạp chí Thiết kế Sáng tạo', 'https://vietnamheritage.com.vn/gen-z-viet-phuc/'
FROM outfits o WHERE o.code = 'AO_TU_THAN';

-- Áo ngũ thân (AO_NGU_THAN)
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'STRUCTURE', 'OUTFIT', 'AO_NGU_THAN', 'RECOMMENDED', 0, 'LOW',
       'Cấu trúc cổ lập lĩnh đứng thẳng và năm hàng khuy cài mẫu mực.', 'Cài đủ 5 khuy để giữ nét uy nghiêm, lịch lãm.',
       'Trung tâm Bảo tồn Di tích Cố đô Huế', 'https://hueworldheritage.org.vn/ao-ngu-than-trieu-nguyen'
FROM outfits o WHERE o.code = 'AO_NGU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'GARMENT_CHARACTERISTICS', 'COLOR', 'BLUE', 'RECOMMENDED', 0, 'LOW',
       'Màu xanh lam quý phái mang cốt cách thanh tao của văn nhân triều Nguyễn.', 'Hài hòa với quần trắng lụa hoặc đen truyền thống.',
       'Ngàn năm áo mũ', 'https://baotanglichsu.vn/vi/Articles/3096/13364/ngan-nam-ao-mu.html'
FROM outfits o WHERE o.code = 'AO_NGU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'GARMENT_CHARACTERISTICS', 'COLOR', 'DARK_RED', 'RECOMMENDED', 0, 'LOW',
       'Tông đỏ sẫm trầm ấm, đĩnh đạc và sang trọng cho lễ nghi.', 'Rất hợp cho các dịp trang trọng hoặc lễ hội truyền thống.',
       'Trung tâm Bảo tồn Di tích Cố đô Huế', 'https://hueworldheritage.org.vn/ao-ngu-than-trieu-nguyen'
FROM outfits o WHERE o.code = 'AO_NGU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'NON_LA', 'RECOMMENDED', 0, 'LOW',
       'Nón lá phối cùng áo ngũ thân tạo phong thái nho nhã.', 'Có thể đội nón chuông hoặc nón chóp khi dạo phố.',
       'Trung tâm Bảo tồn Di tích Cố đô Huế', 'https://hueworldheritage.org.vn/ao-ngu-than-trieu-nguyen'
FROM outfits o WHERE o.code = 'AO_NGU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'WHITE_SNEAKERS', 'CAUTION', -10, 'LOW',
       'Sneaker trắng phối cùng áo ngũ thân là một nét thử nghiệm của giới trẻ.', 'Nên giữ cổ áo đứng thẳng và cài đủ 5 khuy để không mất phom dáng.',
       'Hội Di sản Văn hóa Việt Nam', 'https://vietnamheritage.com.vn/ao-ngu-than-phuc-dung/'
FROM outfits o WHERE o.code = 'AO_NGU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'CONTEXT', 'EVENT', 'CULTURAL_EVENT', 'RECOMMENDED', 0, 'LOW',
       'Áo ngũ thân là trang phục danh giá trong các sự kiện văn hóa, ngoại giao.', 'Tôn vinh bản sắc dân tộc trang trọng và đường bệ.',
       'Trung tâm Bảo tồn Di tích Cố đô Huế', 'https://hueworldheritage.org.vn/ao-ngu-than-trieu-nguyen'
FROM outfits o WHERE o.code = 'AO_NGU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'CONTEXT', 'EVENT', 'TET', 'RECOMMENDED', 0, 'LOW',
       'Mặc áo ngũ thân du xuân đón Tết đang là xu hướng phục dựng văn hóa mạnh mẽ.', 'Tạo nên những khung hình đón xuân đậm chất truyền thống.',
       'Bảo tàng Lịch sử Quốc gia', 'https://baotanglichsu.vn/vi/Articles/3097/15432/trang-phuc-dan-gian-viet-nam.html'
FROM outfits o WHERE o.code = 'AO_NGU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'MODERN_REMIX', 'STYLE', 'TRADITIONAL', 'RECOMMENDED', 0, 'LOW',
       'Phong cách truyền thống giữ nguyên quy chuẩn ngũ thân thời Nguyễn.', 'Đảm bảo cổ lập lĩnh ôm khít cổ vừa vặn.',
       'Trung tâm Bảo tồn Di tích Cố đô Huế', 'https://hueworldheritage.org.vn/ao-ngu-than-trieu-nguyen'
FROM outfits o WHERE o.code = 'AO_NGU_THAN';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'MODERN_REMIX', 'STYLE', 'ELEGANT', 'RECOMMENDED', 0, 'LOW',
       'Phong cách thanh lịch mang hơi thở đương đại nhẹ nhàng cho ngũ thân.', 'Phối màu tối giản tinh tế.',
       'Hội Di sản Văn hóa Việt Nam', 'https://vietnamheritage.com.vn/ao-ngu-than-phuc-dung/'
FROM outfits o WHERE o.code = 'AO_NGU_THAN';

-- Áo Nhật bình (NHAT_BINH)
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'STRUCTURE', 'OUTFIT', 'NHAT_BINH', 'RECOMMENDED', 0, 'LOW',
       'Cổ áo Nhật bình bản rộng và dải ngũ sắc tay áo mang đậm điển chế cung đình.', 'Giữ tà áo thẳng buông tự nhiên, cài trâm giữ nếp.',
       'Trung tâm Bảo tồn Di tích Cố đô Huế', 'https://hueworldheritage.org.vn/le-phuc-cung-dinh'
FROM outfits o WHERE o.code = 'NHAT_BINH';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'GARMENT_CHARACTERISTICS', 'COLOR', 'YELLOW', 'RECOMMENDED', 0, 'LOW',
       'Sắc vàng hoàng gia rực rỡ, màu sắc cao quý nhất của chốn cung đình.', 'Tôn vinh nét uy nghiêm, cao nhã của cổ phục.',
       'Khâm định Đại Nam hội điển sự lệ', 'https://baotanglichsu.vn/vi/Articles/3096/nhat-binh-cung-dinh-hue.html'
FROM outfits o WHERE o.code = 'NHAT_BINH';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'GARMENT_CHARACTERISTICS', 'COLOR', 'RED', 'RECOMMENDED', 0, 'LOW',
       'Sắc đỏ son đại diện cho hỷ phục và lễ phục công chúa thời Nguyễn.', 'Rất thích hợp cho ảnh kỷ niệm trang trọng hoặc sự kiện trọng đại.',
       'Bảo tàng Mỹ thuật Cung đình Huế', 'https://baotanglichsu.vn/vi/Articles/3096/my-thuat-trang-phuc-trieu-nguyen.html'
FROM outfits o WHERE o.code = 'NHAT_BINH';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'FAN', 'RECOMMENDED', 0, 'LOW',
       'Quạt lụa hoặc quạt lông là phụ kiện đồng điệu tuyệt đối cùng Nhật bình.', 'Cầm nhẹ tay trước ngực để tôn lên vẻ kiêu sa.',
       'Trung tâm Bảo tồn Di tích Cố đô Huế', 'https://hueworldheritage.org.vn/le-phuc-cung-dinh'
FROM outfits o WHERE o.code = 'NHAT_BINH';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'NON_LA', 'CAUTION', -10, 'LOW',
       'Nhật bình vốn là cung phục vương giả, phối cùng nón lá dân gian mang nét ngẫu hứng.', 'Nếu muốn chuẩn lễ phục hoàng gia, có thể cân nhắc đội khăn vành.',
       'Bảo tàng Mỹ thuật Cung đình Huế', 'https://baotanglichsu.vn/vi/Articles/3096/my-thuat-trang-phuc-trieu-nguyen.html'
FROM outfits o WHERE o.code = 'NHAT_BINH';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'CONTEXT', 'EVENT', 'CULTURAL_EVENT', 'RECOMMENDED', 0, 'LOW',
       'Nhật bình là tâm điểm trong các lễ hội văn hóa và triển lãm di sản.', 'Tôn vinh trang phục cung đình Việt Nam một cách trọn vẹn nhất.',
       'Trung tâm Bảo tồn Di tích Cố đô Huế', 'https://hueworldheritage.org.vn/le-phuc-cung-dinh'
FROM outfits o WHERE o.code = 'NHAT_BINH';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'CONTEXT', 'EVENT', 'PHOTOSHOOT', 'RECOMMENDED', 0, 'LOW',
       'Lựa chọn hàng đầu cho các bộ ảnh nghệ thuật, cổ phục và chụp kỷ niệm.', 'Không gian kiến trúc cổ kính sẽ làm nổi bật vẻ đẹp cung đình.',
       'Hội Di sản Văn hóa Việt Nam', 'https://vietnamheritage.com.vn/trang-phuc-truyen-thong/'
FROM outfits o WHERE o.code = 'NHAT_BINH';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'MODERN_REMIX', 'STYLE', 'TRADITIONAL', 'RECOMMENDED', 0, 'LOW',
       'Bảo tồn nguyên vẹn quy chuẩn lễ phục cung đình thời Nguyễn.', 'Tôn trọng chi tiết viền cổ và thứ tự màu tay áo.',
       'Khâm định Đại Nam hội điển sự lệ', 'https://baotanglichsu.vn/vi/Articles/3096/nhat-binh-cung-dinh-hue.html'
FROM outfits o WHERE o.code = 'NHAT_BINH';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'MODERN_REMIX', 'STYLE', 'ELEGANT', 'RECOMMENDED', 0, 'LOW',
       'Phong cách thanh lịch sang trọng, quý phái.', 'Hài hòa các chi tiết trang sức và phụ kiện đi kèm.',
       'Bảo tàng Mỹ thuật Cung đình Huế', 'https://baotanglichsu.vn/vi/Articles/3096/my-thuat-trang-phuc-trieu-nguyen.html'
FROM outfits o WHERE o.code = 'NHAT_BINH';

-- Áo bà ba (AO_BA_BA)
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'STRUCTURE', 'OUTFIT', 'AO_BA_BA', 'RECOMMENDED', 0, 'LOW',
       'Dáng áo bà ba xẻ hai tà hông phóng khoáng, thoải mái và năng động.', 'Tà áo buông nhẹ tôn dáng người mặc một cách tự nhiên.',
       'Bảo tàng Phụ nữ Nam Bộ', 'https://baotangphununambo.vn/chiec-ao-ba-ba-nam-bo/'
FROM outfits o WHERE o.code = 'AO_BA_BA';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'GARMENT_CHARACTERISTICS', 'COLOR', 'CREAM', 'RECOMMENDED', 0, 'LOW',
       'Tông màu kem mộc mạc mang hơi thở miệt vườn Nam Bộ.', 'Phối cùng quần lụa đen tạo phong thái thanh thoát.',
       'Bảo tàng Lịch sử TP. Hồ Chí Minh', 'https://baotanglichsutphcm.com.vn/ao-ba-ba-truyen-thong.html'
FROM outfits o WHERE o.code = 'AO_BA_BA';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'GARMENT_CHARACTERISTICS', 'COLOR', 'BLACK', 'RECOMMENDED', 0, 'LOW',
       'Màu đen truyền thống của nông dân Nam Bộ, bền bỉ và chất phác.', 'Có thể điểm thêm khăn rằn sọc để hoàn thiện bản phối.',
       'Bảo tàng Phụ nữ Nam Bộ', 'https://baotangphununambo.vn/chiec-ao-ba-ba-nam-bo/'
FROM outfits o WHERE o.code = 'AO_BA_BA';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'NON_LA', 'RECOMMENDED', 0, 'LOW',
       'Nón lá là biểu tượng bất hủ đi cùng chiếc áo bà ba Nam Bộ.', 'Đội hoặc cầm tay đều tạo cảm giác bình dị, thân thương.',
       'Bảo tàng Phụ nữ Nam Bộ', 'https://baotangphununambo.vn/chiec-ao-ba-ba-nam-bo/'
FROM outfits o WHERE o.code = 'AO_BA_BA';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'MINIMAL_BAG', 'RECOMMENDED', 0, 'LOW',
       'Túi tối giản tiện lợi, hài hòa với sự gọn gàng của áo bà ba.', 'Thích hợp cho dạo phố hoặc đi chợ quê.',
       'Viện Nghiên cứu Văn hóa Nam Bộ', 'https://vicas.org.vn/ao-ba-ba-bieu-tuong-mien-tay'
FROM outfits o WHERE o.code = 'AO_BA_BA';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'CONTEXT', 'EVENT', 'FESTIVAL', 'RECOMMENDED', 0, 'LOW',
       'Rất phù hợp cho các lễ hội miệt vườn, ngày hội văn hóa sông nước.', 'Tạo sự gần gũi, thoải mái trong mọi hoạt động.',
       'Bảo tàng Lịch sử TP. Hồ Chí Minh', 'https://baotanglichsutphcm.com.vn/ao-ba-ba-truyen-thong.html'
FROM outfits o WHERE o.code = 'AO_BA_BA';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'CONTEXT', 'EVENT', 'PHOTOSHOOT', 'RECOMMENDED', 0, 'LOW',
       'Áo bà ba tạo nên những khung hình đồng quê nên thơ, giản dị.', 'Không gian bến sông, vườn cây sẽ làm nổi bật vẻ đẹp của áo.',
       'Bảo tàng Phụ nữ Nam Bộ', 'https://baotangphununambo.vn/chiec-ao-ba-ba-nam-bo/'
FROM outfits o WHERE o.code = 'AO_BA_BA';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'MODERN_REMIX', 'STYLE', 'MINIMAL', 'RECOMMENDED', 0, 'LOW',
       'Phong cách tối giản tôn vinh sự mộc mạc tự nhiên của áo bà ba.', 'Không cần cầu kỳ, vẻ đẹp toát lên từ sự chân phương.',
       'Viện Nghiên cứu Văn hóa Nam Bộ', 'https://vicas.org.vn/ao-ba-ba-bieu-tuong-mien-tay'
FROM outfits o WHERE o.code = 'AO_BA_BA';

INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'MODERN_REMIX', 'STYLE', 'TRADITIONAL', 'RECOMMENDED', 0, 'LOW',
       'Giữ trọn nét truyền thống Nam Bộ với quần lụa đen và nón lá.', 'Tái hiện vẹn nguyên hình ảnh con người miền Tây hào sảng.',
       'Bảo tàng Phụ nữ Nam Bộ', 'https://baotangphununambo.vn/chiec-ao-ba-ba-nam-bo/'
FROM outfits o WHERE o.code = 'AO_BA_BA';
