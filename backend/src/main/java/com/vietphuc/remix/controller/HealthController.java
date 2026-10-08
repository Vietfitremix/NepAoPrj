package com.vietphuc.remix.controller;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
@RestController @RequiredArgsConstructor
public class HealthController {
    private final JdbcTemplate jdbc;
    @GetMapping("/api/health") public ResponseEntity<Map<String,String>> health() {
        try {
            jdbc.queryForObject("SELECT 1",Integer.class);
            return ResponseEntity.ok(Map.of("status","UP"));
        } catch(org.springframework.dao.DataAccessException e) {
            return ResponseEntity.status(503).body(Map.of("status","DOWN"));
        }
    }
}
