package com.vietphuc.remix.dto.response;
import java.util.List;
import com.vietphuc.remix.enums.*;
public record CulturalScoreResponse(Integer score,String level,Breakdown breakdown,List<Warning> warnings,
                                    List<ScoreCategory> missingCategories,String explanation,
                                    List<Check> checks,Assessment assessment) {
    public CulturalScoreResponse(Integer score,String level,Breakdown breakdown,List<Warning> warnings,
                                 List<ScoreCategory> missingCategories,String explanation) {
        this(score,level,breakdown,warnings,missingCategories,explanation,List.of(),null);
    }
    public record Check(String ruleId,String title,ScoreCategory category,String level,Integer points,String reason,
                        String suggestion,String sourceUrl,boolean sourceVerified,String sourceNote) {}
    public record Assessment(Integer ruleCount,Integer matchedRuleCount,java.util.Map<String,String> contextUsed,
                             List<String> missingContext,java.util.Map<String,Double> colorMetrics) {}
    public record Breakdown(Integer structure,Integer garmentCharacteristics,Integer accessories,
                            Integer context,Integer modernRemix) {}
    public record Warning(Severity severity,ScoreCategory category,String message,String suggestion,
                          String sourceName,String sourceUrl,boolean sourceVerified,String sourceNote) {}
}
