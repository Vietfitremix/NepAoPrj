package com.vietphuc.remix.controller;
import com.vietphuc.remix.service.RecommendationService;
import com.vietphuc.remix.dto.request.RecommendationRequest;
import com.vietphuc.remix.dto.response.AiDtos.RecommendationResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/api/recommendations") @RequiredArgsConstructor
public class RecommendationController {
    private final RecommendationService recommendations;
    @PostMapping public RecommendationResponse recommend(@Valid @RequestBody RecommendationRequest request) {
        return recommendations.recommend(request);
    }
}
