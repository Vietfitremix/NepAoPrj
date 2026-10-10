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
        var result=ai.recommend(request,currentWeather);
        var analysis=result.analysis();
        return new RecommendationResponse(new Analysis(analysis.event(),currentWeather,
            result.concepts().stream().map(Concept::styleCode).distinct().toList(),analysis.understanding(),
            analysis.character(),analysis.context(),analysis.source()),result.concepts());
    }
}
