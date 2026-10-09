-- Bốn màu có trong bảng màu tủ đồ và bảng màu của AI nhưng chưa có trong danh mục tham chiếu:
-- stylist chưa thể gợi ý hồng đào, xanh ngọc/rêu, nâu đất, tím Huế dù người dùng chọn đúng các màu này.
-- Viết bằng INSERT ... SELECT ... WHERE NOT EXISTS để chạy được cả trên PostgreSQL lẫn H2 của bộ test.
INSERT INTO colors(code,name,hex_code)
SELECT v.code,v.name,v.hex_code FROM (
  SELECT 'GREEN' AS code,'Xanh lá' AS name,'#39705B' AS hex_code
  UNION ALL SELECT 'PINK','Hồng','#DE91AA'
  UNION ALL SELECT 'PURPLE','Tím','#765A94'
  UNION ALL SELECT 'BROWN','Nâu','#876044'
) v WHERE NOT EXISTS (SELECT 1 FROM colors c WHERE c.code=v.code);
