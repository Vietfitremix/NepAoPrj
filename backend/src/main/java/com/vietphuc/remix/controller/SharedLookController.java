package com.vietphuc.remix.controller;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vietphuc.remix.exception.ApiException;
import java.util.Map;
import java.util.UUID;
import java.nio.charset.StandardCharsets;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;

/**
 * Lưu và chia sẻ look theo định dạng của AI Nếp Áo (state bộ đồ + bối cảnh + thẻ điểm + lời stylist) dưới dạng JSON.
 * Chỉ lưu những gì người dùng bấm "Lưu look"; nội dung được kiểm tra là object và giới hạn kích thước.
 */
@RestController @RequestMapping("/api/shared-looks") @RequiredArgsConstructor
public class SharedLookController {
    private static final int MAX_BYTES = 64 * 1024;
    private final JdbcTemplate jdbc;
    private final ObjectMapper mapper;

    @PostMapping
    public ResponseEntity<Map<String, String>> save(@RequestBody JsonNode payload) throws Exception {
        if (!payload.isObject() || !payload.path("state").isObject()) throw ApiException.invalid("Look phải có trường state.");
        String json = mapper.writeValueAsString(payload);
        if (json.getBytes(StandardCharsets.UTF_8).length > MAX_BYTES) throw ApiException.invalid("Look quá lớn.");
        UUID id = UUID.randomUUID();
        jdbc.update("INSERT INTO shared_looks(id,payload) VALUES (?,?::jsonb)", id, json);
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of("id", id.toString()));
    }

    @GetMapping("/{id}")
    public JsonNode get(@PathVariable UUID id) throws Exception {
        var rows = jdbc.queryForList("SELECT payload::text FROM shared_looks WHERE id=?", String.class, id);
        if (rows.isEmpty()) throw new ApiException(HttpStatus.NOT_FOUND, "NOT_FOUND", "Không tìm thấy look.");
        JsonNode payload = mapper.readTree(rows.get(0));
        // H2's PostgreSQL mode wraps a JSONB string parameter; PostgreSQL returns the object directly.
        return payload.isTextual() ? mapper.readTree(payload.textValue()) : payload;
    }
}
