-- Look lưu theo định dạng AI Nếp Áo (state + bối cảnh + thẻ điểm), tách khỏi bảng looks cũ của bản phối 1 áo + màu.
CREATE TABLE shared_looks (
    id UUID PRIMARY KEY,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
