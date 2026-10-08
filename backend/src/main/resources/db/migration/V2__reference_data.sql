INSERT INTO outfits(code,name) VALUES
 ('AO_DAI','Áo dài'),('AO_TU_THAN','Áo tứ thân'),('AO_NGU_THAN','Áo ngũ thân'),
 ('NHAT_BINH','Nhật bình'),('AO_BA_BA','Áo bà ba');
INSERT INTO colors(code,name,hex_code) VALUES
 ('RED','Đỏ','#D32F2F'),('DARK_RED','Đỏ sẫm','#8B0000'),('WHITE','Trắng','#FFFFFF'),
 ('BLUE','Xanh dương','#1976D2'),('YELLOW','Vàng','#FBC02D'),('BLACK','Đen','#000000'),
 ('CREAM','Kem','#FFFDD0');
INSERT INTO styles(code,name) VALUES
 ('TRADITIONAL','Truyền thống'),('GEN_Z','Gen Z'),('MINIMAL','Tối giản'),
 ('ELEGANT','Thanh lịch'),('VINTAGE','Hoài cổ');
INSERT INTO events(code,name) VALUES
 ('TET','Tết'),('FESTIVAL','Lễ hội'),('GRADUATION','Tốt nghiệp'),
 ('PHOTOSHOOT','Chụp ảnh'),('CULTURAL_EVENT','Sự kiện văn hóa');
INSERT INTO accessories(code,name,type,layer_order) VALUES
 ('NON_LA','Nón lá','HEADWEAR',30),('FAN','Quạt','HANDHELD',40),
 ('MINIMAL_BAG','Túi tối giản','BAG',50),('WHITE_SNEAKERS','Giày thể thao trắng','FOOTWEAR',10);
-- Technical availability in MVP only; NULL compatibility_score is not a cultural assessment.
INSERT INTO outfit_accessories(outfit_id,accessory_id)
 SELECT o.id,a.id FROM outfits o CROSS JOIN accessories a;
-- No invented cultural sources, rules, scores or image assets.
