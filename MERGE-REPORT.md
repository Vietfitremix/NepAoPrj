# Kết quả bổ sung merge theo HUONG-DAN-MERGE.md

Ngày kiểm tra: 10/10/2026. Nhánh làm việc: thang/complete-merge-20261009.
Nền hiện tại: cd5647e (MVP); đã fetch vietfit-target, main remote vẫn ở commit này.
Nhánh vietfit đang ở 240f26e, chưa có commit mới sau mốc đó.

## Phần đã bổ sung

- Màu gốc của 4 quần nam trong wardrobe_score.py: wide-charcoal, slim-black, cropped-olive, shorts-khaki. Màu được đo từ pixel alpha >= 230 của ảnh front; màu tùy chỉnh tiếp tục được ưu tiên.
- 5 ca kiểm thử màu quần, đưa bộ AI từ 113 lên 118 test. Kiểm thử dáng quần bó/ống rộng dùng cùng một màu để không bị điểm hài hòa màu che khuất.
- V16__sync_merged_ai_catalog.sql: bổ sung R40–R50 vào cả tài liệu ai.rules và bảng ai_cultural_rules; đưa DB từ 23 lên 34 luật; cập nhật điểm thưởng màu yêu thích từ 10 lên 20; đồng bộ 4 prompt. Giữ các nguồn URL và ghi chú phạm vi kiểm chứng của V11. Các migration cũ giữ nguyên.
- Kiểm thử backend xác nhận dữ liệu JSON và các hàng luật đồng nhất, đúng trần điểm, nguồn cũ được giữ và prompt mới có hiệu lực.
- Cho phép Git lưu backend/gradle/wrapper/gradle-wrapper.jar để clone mới dùng được gradlew.
- README đã hướng dẫn chạy backend migration trước rồi khởi động lại AI khi dùng PostgreSQL.
- Giữ và kiểm chứng phần tủ đồ theo giới tính đang có trong working tree (V15, backend, frontend và các test), không thêm luật văn hóa mới theo giới tính.

## Kết quả kiểm chứng

| Kiểm tra | Kết quả |
| --- | --- |
| AI pytest | 118 passed |
| Frontend node test | 43 passed, 0 failed |
| TypeScript tsc -b | Thành công |
| Vite production build | Thành công |
| Backend Gradle test | 47 passed, 0 failed |
| Backend bootJar | Thành công |
| Flyway trên PostgreSQL local | V16 đã áp dụng thành công |
| Quần đùi, nam/nữ | 35%, HIGH_RISK |
| Chưa chọn quần, nam/nữ | 40%, HIGH_RISK |
| Crocs dịp Tết, nam/nữ | 45%, HIGH_RISK |
| 4 màu quần nam trên API đang chạy | Khớp màu gốc đã bổ sung |
| 4 prompt trong DB | Khớp nội dung file hiện tại |
| Nón lá nam/nữ, 4 góc | 8 asset trả HTTP 200 |
| Marker xung đột và git diff --check | Không còn lỗi |

Đã sao lưu PostgreSQL trước khi áp dụng migration, tại thư mục .tools/merge-backup-2026-10-09T16-48-41-635Z (database-before-v16.dump).
Đã khởi động lại backend/AI; frontend vẫn truy cập được tại http://localhost:5173.
Kết quả API chi tiết nằm ở .tools/merge-runtime-result.json.

## Phạm vi còn cần kiểm tra bằng trình duyệt

Công cụ hiện không có browser khả dụng. Chưa xác nhận trực tiếp bố cục hai khung Studio, hộp thoại Lookbook, logo/favicon và toàn bộ thao tác quiz → concept → studio → look bằng UI.
Các file tính năng này đã có trong main và đã qua đối chiếu code/build/test; việc kiểm tra asset nón lá qua HTTP chưa thay thế kiểm tra hình nón sau render.
Theo mục 8 của hướng dẫn, chưa mở Pull Request khi chưa hoàn tất kiểm tra UI.

Các công cụ SVG cũ frontend/tools và ai-service/integration là phần tùy chọn/đã áp dụng xong theo tài liệu, không cần cho ứng dụng hiện tại.
Ảnh nguồn vẫn giữ trên máy/nhánh vietfit; các ảnh exports đang có và thay đổi VS Code cá nhân được giữ riêng ngoài commit bổ sung.
