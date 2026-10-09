package com.vietphuc.remix.controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.vietphuc.remix.service.DataCatalogService;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api/data") @RequiredArgsConstructor
public class DataCatalogController {
    private final DataCatalogService data;
    @GetMapping("/bootstrap") public JsonNode bootstrap() { return data.bootstrap(); }
    @GetMapping("/documents/{key}") public JsonNode document(@PathVariable String key) { return data.document(key); }
    @GetMapping("/assets") public List<Map<String,Object>> assets(@RequestParam(defaultValue="frontend/public/figure/") String prefix) {
        return data.assetManifest(prefix);
    }
}
