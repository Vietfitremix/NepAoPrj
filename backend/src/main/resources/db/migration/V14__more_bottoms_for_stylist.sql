-- Ba kiểu quần có sẵn trong tủ đồ (ống rộng, dài đen, dài xanh navy) nhưng chưa có trong danh mục tham chiếu:
-- stylist chỉ gợi ý được quần lụa suông hoặc váy nên mọi bộ gợi ý đều mặc cùng một kiểu quần.
-- Viết bằng INSERT ... SELECT ... WHERE NOT EXISTS để chạy được cả trên PostgreSQL lẫn H2 của bộ test.
INSERT INTO accessories(code,name,type,description,image_url,layer_order)
SELECT v.code,v.name,v.type,v.description,v.image_url,v.layer_order FROM (
  SELECT 'QUAN_ONG_RONG' AS code,'Quần ống rộng' AS name,'BOTTOM' AS type,
         'Quần ống rộng thoải mái, hợp phong cách trẻ trung khi phối cùng áo dài cách tân hoặc áo ngũ thân.' AS description,
         '/figure/male-layers/pants/wide-charcoal/front.png' AS image_url,15 AS layer_order
  UNION ALL SELECT 'QUAN_DAI_DEN','Quần dài đen','BOTTOM',
         'Quần dài đen gọn gàng, nền trầm giúp áo dài hoặc áo tứ thân nổi bật, hợp dịp trang trọng lẫn dạo phố.',
         '/figure/female-layers/pants/long-black/front.png',15
  UNION ALL SELECT 'QUAN_DAI_XANH','Quần dài xanh navy','BOTTOM',
         'Quần dài xanh navy nhã nhặn, dễ phối với các gam màu ấm của áo dài và áo ngũ thân.',
         '/figure/male-layers/pants/long-navy/front.png',15
) v WHERE NOT EXISTS (SELECT 1 FROM accessories a WHERE a.code=v.code);

INSERT INTO outfit_accessories(outfit_id,accessory_id)
SELECT o.id,a.id FROM outfits o CROSS JOIN accessories a
WHERE a.code IN ('QUAN_ONG_RONG','QUAN_DAI_DEN','QUAN_DAI_XANH')
  AND NOT EXISTS (SELECT 1 FROM outfit_accessories x WHERE x.outfit_id=o.id AND x.accessory_id=a.id);
