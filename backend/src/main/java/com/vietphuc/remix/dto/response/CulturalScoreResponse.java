package com.vietphuc.remix.dto.response;
import java.util.List;
import com.vietphuc.remix.enums.*;
public record CulturalScoreResponse(Integer score,String level,Breakdown breakdown,List<Warning> warnings,
                                    List<ScoreCategory> missingCategories,String explanation) {
    public record Breakdown(Integer structure,Integer garmentCharacteristics,Integer accessories,
                            Integer context,Integer modernRemix) {}
    public record Warning(Severity severity,ScoreCategory category,String message,String suggestion,
                          String sourceName,String sourceUrl,boolean sourceVerified,String sourceNote) {}
}
