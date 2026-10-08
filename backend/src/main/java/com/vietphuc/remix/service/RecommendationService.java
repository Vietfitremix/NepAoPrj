package com.vietphuc.remix.service;
import com.vietphuc.remix.dto.request.RecommendationRequest;
import com.vietphuc.remix.dto.response.AiDtos.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
@Service @RequiredArgsConstructor
public class RecommendationService {
    private final SelectionService selections;
    private final WeatherService weather;
    private final AiService ai;
    public RecommendationResponse recommend(RecommendationRequest request) {
        selections.validateContext(request.eventCode(),request.styleCode());
        var currentWeather=weather.current(request.city());
        var concepts=ai.recommend(request,currentWeather);
        return new RecommendationResponse(new Analysis(request.eventCode(),currentWeather,
            concepts.stream().map(Concept::styleCode).distinct().toList()),concepts);
    }
}
