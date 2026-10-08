package com.vietphuc.remix.controller;
import com.vietphuc.remix.service.CulturalScoreService;
import com.vietphuc.remix.dto.request.LookSelection;
import com.vietphuc.remix.dto.response.CulturalScoreResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/api/cultural-score") @RequiredArgsConstructor
public class CulturalScoreController {
    private final CulturalScoreService culture;
    @PostMapping public CulturalScoreResponse evaluate(@Valid @RequestBody LookSelection request) { return culture.evaluate(request); }
}
