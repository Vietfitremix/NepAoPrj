# Blender cho VIỆT FIT

Blender 4.5.3 LTS portable được đặt trong `.tools/blender/` (không commit vào Git).
Nguồn chính thức: https://download.blender.org/release/Blender4.5/blender-4.5.3-windows-x64.zip

Từ thư mục gốc dự án:

```powershell
npm run character:render
npm run blender
```

`character:render` tạo nhân vật mẫu cách điệu mặc áo dài xanh, lưu cảnh chỉnh sửa
tại `assets/archive/blender/viet-fit-character.blend` và ảnh PNG nền trong suốt tại
`frontend/public/figure/blender/viet-fit-character.png`. Frontend có thể dùng URL
`/figure/blender/viet-fit-character.png`. Đây là asset mẫu, chưa có rig hoạt hình
và chưa được thay vào các lớp SVG của Studio phối đồ.

Đổi màu, hình dáng hoặc camera trong `create_character.py`, rồi render lại.
Lệnh render ghi đè hai file đầu ra trên; lưu bản riêng nếu đã chỉnh cảnh bằng tay.

Để cài lại, tải ZIP từ nguồn trên và giải nén vào `.tools/blender/` sao cho có
`.tools/blender/blender-4.5.3-windows-x64/blender.exe`.
Blender chạy Python trực tiếp nên bước tạo mẫu này không cần plugin MCP.
