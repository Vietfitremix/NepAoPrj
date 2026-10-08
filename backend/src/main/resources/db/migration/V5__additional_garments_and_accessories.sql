-- V5__additional_garments_and_accessories.sql
-- Bổ sung đầy đủ các thể loại váy, quần, khăn, nón, trang sức và giày dép để mix cùng 5 trang phục chính

-- 1. Thêm danh mục món đồ phối mới vào bảng ACCESSORIES
DELETE FROM outfit_accessories;
DELETE FROM accessories WHERE code IN (
 'VAY_DUP', 'VAY_XEP_LY', 'QUAN_LUA', 'NON_QUAI_THAO', 'KHAN_MO_QUA',
 'KHAN_VAN', 'KHAN_XEP', 'HOA_CAI_TOC', 'KIENG_BAC', 'TRANG_SUC',
 'GUOC', 'HAI_THEU', 'GIAY_BUP_BE'
);

INSERT INTO accessories (code, name, type, description, image_url, layer_order) VALUES
 ('VAY_DUP', 'Váy đụp truyền thống', 'BOTTOM', 'Váy xòe lụa đen cổ truyền Bắc Bộ, tôn vinh nét bình dị dân gian khi phối cùng Áo tứ thân hoặc Áo bà ba.', '/figure/bottom/vay_nu.svg', 15),
 ('VAY_XEP_LY', 'Chân váy xếp ly cách tân', 'BOTTOM', 'Chân váy xếp ly hiện đại mang phong cách trẻ trung Gen Z, tạo điểm nhấn phá cách cho Áo dài hoặc Áo tứ thân.', '/figure/bottom/vay_xep_ly_nu.svg', 15),
 ('QUAN_LUA', 'Quần lụa suông truyền thống', 'BOTTOM', 'Quần lụa ống suông mềm mại buông rủ thướt tha, chuẩn mực phối cùng Áo dài, Áo ngũ thân, Nhật bình và Áo bà ba.', '/figure/bottom/quan_nu.svg', 15),
 ('NON_QUAI_THAO', 'Nón quai thao', 'HEADWEAR', 'Nón ba tầm quai thao dệt tơ tằm, biểu tượng văn hóa Kinh Bắc của các liền chị quan họ.', '/figure/accessory/non_quai_thao.svg', 30),
 ('KHAN_MO_QUA', 'Khăn mỏ quạ', 'HEADWEAR', 'Khăn lụa đen xếp nếp mỏ quạ ôm khéo gương mặt, gắn liền với hình tượng người phụ nữ đồng bằng Bắc Bộ.', '/figure/accessory/khan_mo_qua.svg', 28),
 ('KHAN_VAN', 'Khăn vấn truyền thống', 'HEADWEAR', 'Khăn nhung vấn tròn quanh đầu tôn vinh vẻ đài các, quý phái cho Áo dài và Nhật bình.', '/figure/accessory/khan_van.svg', 28),
 ('KHAN_XEP', 'Khăn xếp', 'HEADWEAR', 'Khăn xếp nếp cổ truyền trang nghiêm, tạo phong thái đĩnh đạc khi phối cùng Áo ngũ thân và Áo dài.', '/figure/accessory/khan_xep.svg', 28),
 ('HOA_CAI_TOC', 'Hoa cài tóc', 'HEADWEAR', 'Điểm xuyết nhành hoa tươi hoặc trâm hoa lên mái tóc thiếu nữ thanh xuân.', '/figure/accessory/hoa_cai_toc.svg', 29),
 ('KIENG_BAC', 'Kiềng bạc cổ truyền', 'JEWELRY', 'Vòng kiềng bạc nguyên khối chạm khắc hoa văn tinh xảo, phụ kiện sang trọng khi trẩy hội xuân.', '/figure/accessory/kieng_bac.svg', 25),
 ('TRANG_SUC', 'Trang sức (Vòng tay & Bông tai)', 'JEWELRY', 'Bộ trang sức ngọc bích, vòng tay ngọc thanh nhã tăng thêm nét quý phái.', '/figure/accessory/trang_suc.svg', 26),
 ('GUOC', 'Guốc mộc truyền thống', 'FOOTWEAR', 'Guốc gỗ quai nhung mộc mạc ngân vang nhịp bước cổ truyền trên đường làng ngõ xóm.', '/figure/accessory/guoc.svg', 10),
 ('HAI_THEU', 'Hài thêu hoa cổ trang', 'FOOTWEAR', 'Hài vải nhung thêu hoa văn tinh xảo mũi cong cung đình trang nhã.', '/figure/accessory/hai_theu.svg', 10),
 ('GIAY_BUP_BE', 'Giày búp bê', 'FOOTWEAR', 'Giày búp bê đế bệt nhẹ nhàng, tiện lợi cho phong cách tối giản và dạo phố.', '/figure/accessory/giay_bup_be.svg', 10);

-- 2. Thiết lập liên kết phối đồ trong bảng OUTFIT_ACCESSORIES

-- Áo dài (AO_DAI)
INSERT INTO outfit_accessories (outfit_id, accessory_id)
SELECT o.id, a.id FROM outfits o CROSS JOIN accessories a
WHERE o.code = 'AO_DAI' AND a.code IN (
 'QUAN_LUA', 'VAY_XEP_LY', 'NON_LA', 'KHAN_VAN', 'KHAN_XEP',
 'HOA_CAI_TOC', 'KIENG_BAC', 'TRANG_SUC', 'FAN', 'MINIMAL_BAG',
 'GUOC', 'HAI_THEU', 'GIAY_BUP_BE', 'WHITE_SNEAKERS'
);

-- Áo tứ thân (AO_TU_THAN)
INSERT INTO outfit_accessories (outfit_id, accessory_id)
SELECT o.id, a.id FROM outfits o CROSS JOIN accessories a
WHERE o.code = 'AO_TU_THAN' AND a.code IN (
 'VAY_DUP', 'VAY_XEP_LY', 'QUAN_LUA', 'NON_QUAI_THAO', 'NON_LA',
 'KHAN_MO_QUA', 'KHAN_VAN', 'HOA_CAI_TOC', 'KIENG_BAC', 'FAN',
 'MINIMAL_BAG', 'GUOC', 'HAI_THEU', 'WHITE_SNEAKERS'
);

-- Áo ngũ thân (AO_NGU_THAN)
INSERT INTO outfit_accessories (outfit_id, accessory_id)
SELECT o.id, a.id FROM outfits o CROSS JOIN accessories a
WHERE o.code = 'AO_NGU_THAN' AND a.code IN (
 'QUAN_LUA', 'VAY_DUP', 'KHAN_XEP', 'KHAN_VAN', 'NON_LA',
 'KIENG_BAC', 'TRANG_SUC', 'FAN', 'MINIMAL_BAG', 'GUOC',
 'HAI_THEU', 'WHITE_SNEAKERS'
);

-- Nhật bình (NHAT_BINH)
INSERT INTO outfit_accessories (outfit_id, accessory_id)
SELECT o.id, a.id FROM outfits o CROSS JOIN accessories a
WHERE o.code = 'NHAT_BINH' AND a.code IN (
 'QUAN_LUA', 'KHAN_VAN', 'HOA_CAI_TOC', 'KIENG_BAC', 'TRANG_SUC',
 'FAN', 'HAI_THEU', 'GUOC', 'NON_LA'
);

-- Áo bà ba (AO_BA_BA)
INSERT INTO outfit_accessories (outfit_id, accessory_id)
SELECT o.id, a.id FROM outfits o CROSS JOIN accessories a
WHERE o.code = 'AO_BA_BA' AND a.code IN (
 'QUAN_LUA', 'VAY_DUP', 'NON_LA', 'MINIMAL_BAG', 'GUOC',
 'GIAY_BUP_BE', 'WHITE_SNEAKERS', 'FAN', 'HOA_CAI_TOC'
);

-- 3. Nạp quy tắc chấm điểm và đánh giá văn hóa cho các phụ kiện mới trong CULTURAL_RULES

-- Nón quai thao + Áo tứ thân
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'NON_QUAI_THAO', 'RECOMMENDED', 0, 'LOW',
       'Nón quai thao (nón ba tầm) là biểu tượng văn hóa kinh điển của liền chị quan họ khi mặc cùng áo tứ thân.',
       'Cầm nón nghiêng hoặc đội quai thao duyên dáng khi trẩy hội xuân Kinh Bắc.',
       'Viện Văn hóa Nghệ thuật Quốc gia', 'https://vicas.org.vn/ao-tu-than-dong-bang-bac-bo'
FROM outfits o WHERE o.code = 'AO_TU_THAN';

-- Khăn mỏ quạ + Áo tứ thân
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'KHAN_MO_QUA', 'RECOMMENDED', 0, 'LOW',
       'Khăn mỏ quạ đen tuyền gấp nếp ôm gọn khuôn trăng đầy đặn của phụ nữ Bắc Bộ xưa.',
       'Thắt nút khăn khéo léo dưới cằm, để lộ phần trán thanh tú.',
       'Bảo tàng Phụ nữ Việt Nam', 'https://baotangphunu.org.vn/ao-tu-than-va-y-nghia-dao-hieu/'
FROM outfits o WHERE o.code = 'AO_TU_THAN';

-- Váy đụp + Áo tứ thân
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'VAY_DUP', 'RECOMMENDED', 0, 'LOW',
       'Váy đụp lụa đen dài chấm gót là phục sức dân gian chuẩn mực nhất đi cùng áo tứ thân bốn vạt.',
       'Mặc cùng yếm thắm và thắt lưng lụa đào tạo nét duyên thôn dã tuyệt đẹp.',
       'Bảo tàng Lịch sử Quốc gia', 'https://baotanglichsu.vn/vi/Articles/3097/15432/trang-phuc-dan-gian-viet-nam.html'
FROM outfits o WHERE o.code = 'AO_TU_THAN';

-- Chân váy xếp ly + Áo tứ thân
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'VAY_XEP_LY', 'RECOMMENDED', 0, 'LOW',
       'Chân váy xếp ly mang hơi thở hiện đại phá cách cho áo tứ thân trong các bộ ảnh thời trang sáng tạo.',
       'Chọn chân váy độ dài vừa phải để giữ nét mềm mại của tà áo tứ thân.',
       'Tạp chí Thời trang Di sản', 'https://vietnamheritage.com.vn/gen-z-viet-phuc/'
FROM outfits o WHERE o.code = 'AO_TU_THAN';

-- Kiềng bạc + Áo tứ thân
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'KIENG_BAC', 'RECOMMENDED', 0, 'LOW',
       'Kiềng bạc sáng lấp lánh trên nền áo yếm thắm tạo điểm nhấn quý phái cho thiếu nữ Kinh Bắc.',
       'Đeo kiềng ôm vừa vặn quanh cổ, kết hợp áo cánh khoác ngoài.',
       'Bảo tàng Phụ nữ Việt Nam', 'https://baotangphunu.org.vn/ao-tu-than-va-y-nghia-dao-hieu/'
FROM outfits o WHERE o.code = 'AO_TU_THAN';

-- Chân váy xếp ly + Áo dài
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'VAY_XEP_LY', 'RECOMMENDED', 0, 'LOW',
       'Áo dài cách tân phối chân váy xếp ly là trào lưu rất được các bạn trẻ Gen Z yêu thích.',
       'Nên chọn tông màu chân váy đồng điệu hoặc tương phản nhẹ nhàng với tà áo dài.',
       'Tạp chí Thời trang Di sản', 'https://vietnamheritage.com.vn/gen-z-viet-phuc/'
FROM outfits o WHERE o.code = 'AO_DAI';

-- Quần lụa + Áo dài
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'QUAN_LUA', 'RECOMMENDED', 0, 'LOW',
       'Quần lụa suông rộng ống mềm mại là chuẩn mực tuyệt đối đi cùng tà áo dài truyền thống.',
       'Ống quần dài vừa phủ mu bàn chân, màu trắng ngà hoặc đen tạo vẻ thanh lịch nhất.',
       'Bảo tàng Phụ nữ Việt Nam', 'https://baotangphunu.org.vn/ao-dai-di-san-van-hoa-viet-nam/'
FROM outfits o WHERE o.code = 'AO_DAI';

-- Khăn vấn + Áo dài
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'KHAN_VAN', 'RECOMMENDED', 0, 'LOW',
       'Khăn vấn nhung tôn nét kiêu sa, đài các của phụ nữ Hà thành xưa khi mặc áo dài.',
       'Vấn tóc gọn gàng trước khi đội khăn để tôn trọn vẹn gương mặt thanh tú.',
       'Bảo tàng Phụ nữ Việt Nam', 'https://baotangphunu.org.vn/ao-dai-di-san-van-hoa-viet-nam/'
FROM outfits o WHERE o.code = 'AO_DAI';

-- Kiềng bạc + Áo dài
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'KIENG_BAC', 'RECOMMENDED', 0, 'LOW',
       'Kiềng bạc tròn thanh mảnh đeo trước cổ áo dài tạo phong thái tao nhã, hoài cổ.',
       'Rất phù hợp cho các dịp lễ Tết, cưới hỏi hoặc chụp ảnh kỷ niệm.',
       'Ngàn năm áo mũ', 'https://baotanglichsu.vn/vi/Articles/3096/13364/ngan-nam-ao-mu.html'
FROM outfits o WHERE o.code = 'AO_DAI';

-- Hài thêu + Áo dài
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'HAI_THEU', 'RECOMMENDED', 0, 'LOW',
       'Hài thêu hoa văn cổ truyền hoàn thiện phong cách cổ điển duyên dáng cho tà áo dài.',
       'Bước đi nhẹ nhàng khoan thai để tà áo bay tự nhiên.',
       'Bảo tàng Lịch sử Quốc gia', 'https://baotanglichsu.vn/vi/Articles/3097/15432/trang-phuc-dan-gian-viet-nam.html'
FROM outfits o WHERE o.code = 'AO_DAI';

-- Khăn xếp + Áo ngũ thân
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'KHAN_XEP', 'RECOMMENDED', 0, 'LOW',
       'Khăn xếp (khăn đóng) là phụ kiện chuẩn mực theo điển chế triều Nguyễn đi cùng áo ngũ thân.',
       'Khăn xếp nếp gọn gàng tạo phong thái nghiêm trang, đĩnh đạc.',
       'Trung tâm Bảo tồn Di tích Cố đô Huế', 'https://hueworldheritage.org.vn/ao-ngu-than-trieu-nguyen'
FROM outfits o WHERE o.code = 'AO_NGU_THAN';

-- Hài thêu + Áo ngũ thân
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'HAI_THEU', 'RECOMMENDED', 0, 'LOW',
       'Hài thêu cổ trang rất ăn nhập với phom dáng áo ngũ thân lập lĩnh.',
       'Tạo nét quý phái chuẩn mực của văn nhân xưa.',
       'Ngàn năm áo mũ', 'https://baotanglichsu.vn/vi/Articles/3096/13364/ngan-nam-ao-mu.html'
FROM outfits o WHERE o.code = 'AO_NGU_THAN';

-- Khăn vấn + Nhật bình
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'KHAN_VAN', 'RECOMMENDED', 0, 'LOW',
       'Khăn vấn hoàng cung (vành khăn) là phục sức kinh điển tôn vinh sự quyền quý của áo Nhật bình.',
       'Đội khăn vành thẳng thớm, có thể cài trâm ngọc quý phái.',
       'Bảo tàng Mỹ thuật Cung đình Huế', 'https://baotanglichsu.vn/vi/Articles/3096/my-thuat-trang-phuc-trieu-nguyen.html'
FROM outfits o WHERE o.code = 'NHAT_BINH';

-- Hài thêu + Nhật bình
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'HAI_THEU', 'RECOMMENDED', 0, 'LOW',
       'Hài thêu hoa văn phượng vũ cung đình là lựa chọn hoàn hảo nhất cho lễ phục Nhật bình.',
       'Đảm bảo sự trang nghiêm và nét đẹp hoàng tộc.',
       'Trung tâm Bảo tồn Di tích Cố đô Huế', 'https://hueworldheritage.org.vn/le-phuc-cung-dinh'
FROM outfits o WHERE o.code = 'NHAT_BINH';

-- Trang sức ngọc + Nhật bình
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'TRANG_SUC', 'RECOMMENDED', 0, 'LOW',
       'Bông tai ngọc và chuỗi ngọc đeo cổ tôn lên sự đài các và quyền quý của lễ phục cung đình.',
       'Hài hòa với màu sắc hoa văn cổ áo Nhật bình.',
       'Khâm định Đại Nam hội điển sự lệ', 'https://baotanglichsu.vn/vi/Articles/3096/nhat-binh-cung-dinh-hue.html'
FROM outfits o WHERE o.code = 'NHAT_BINH';

-- Guốc mộc + Áo bà ba
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'GUOC', 'RECOMMENDED', 0, 'LOW',
       'Guốc mộc truyền thống đi cùng áo bà ba tạo cảm giác bình dị, mộc mạc và gần gũi.',
       'Gợi nhắc nét sinh hoạt sông nước phương Nam hiền hòa.',
       'Bảo tàng Phụ nữ Nam Bộ', 'https://baotangphununambo.vn/chiec-ao-ba-ba-nam-bo/'
FROM outfits o WHERE o.code = 'AO_BA_BA';

-- Váy đụp + Áo bà ba
INSERT INTO cultural_rules (outfit_id, category, target_type, target_code, rule_type, score_modifier, severity, message, suggestion, source_name, source_url)
SELECT o.id, 'ACCESSORIES', 'ACCESSORY', 'VAY_DUP', 'RECOMMENDED', 0, 'LOW',
       'Áo bà ba phối váy lụa là một biến tấu nhẹ nhàng, thoải mái cho thiếu nữ khi dạo chơi miệt vườn.',
       'Tạo sự nữ tính, phóng khoáng tự nhiên.',
       'Viện Nghiên cứu Văn hóa Nam Bộ', 'https://vicas.org.vn/ao-ba-ba-bieu-tuong-mien-tay'
FROM outfits o WHERE o.code = 'AO_BA_BA';
