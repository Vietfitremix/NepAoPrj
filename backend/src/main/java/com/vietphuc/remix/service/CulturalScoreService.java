package com.vietphuc.remix.service;
import com.vietphuc.remix.dto.request.LookSelection;
import com.vietphuc.remix.dto.response.CulturalScoreResponse;
import com.vietphuc.remix.dto.response.CulturalScoreResponse.*;
import com.vietphuc.remix.entity.CulturalRule;
import com.vietphuc.remix.enums.*;
import com.vietphuc.remix.repository.CulturalRuleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.*;
@Service @RequiredArgsConstructor @Transactional(readOnly=true)
public class CulturalScoreService {
    private final CulturalRuleRepository rules;
    private final SelectionService selections;
    private final com.vietphuc.remix.client.AiClient ai;
    private final com.fasterxml.jackson.databind.ObjectMapper mapper;
    public CulturalScoreResponse evaluate(LookSelection look) {
        selections.validate(look);
        if(look.wardrobe()!=null && !look.wardrobe().isNull()) {
            try {
                var result=mapper.treeToValue(ai.culturalScore(look),CulturalScoreResponse.class);
                if(result==null || result.level()==null || result.warnings()==null ||
                    (result.score()!=null && (result.score()<0 || result.score()>100)))
                    throw com.vietphuc.remix.exception.ApiException.upstream("Kết quả kiểm tra bản phối không hợp lệ.");
                return result;
            } catch(com.fasterxml.jackson.core.JsonProcessingException e) {
                throw com.vietphuc.remix.exception.ApiException.upstream("Kết quả kiểm tra bản phối không hợp lệ.");
            }
        }
        var configured=rules.findByOutfitCodeOrderByIdAsc(look.outfitCode());
        EnumMap<ScoreCategory,Integer> dimensions=new EnumMap<>(ScoreCategory.class);
        configured.forEach(r -> dimensions.put(r.getCategory(),100));
        List<Warning> warnings=new ArrayList<>();
        for(var r:configured) if(matches(r,look)) {
            dimensions.merge(r.getCategory(),r.getScoreModifier(),Integer::sum);
            if(r.getRuleType()!=RuleType.RECOMMENDED)
                warnings.add(new Warning(r.getSeverity(),r.getCategory(),r.getMessage(),r.getSuggestion(),r.getSourceName(),r.getSourceUrl(),r.isSourceVerified(),r.getSourceNote()));
        }
        dimensions.replaceAll((category,value) -> Math.max(0,Math.min(100,value)));
        var missing=Arrays.stream(ScoreCategory.values()).filter(c -> !dimensions.containsKey(c)).toList();
        var breakdown=new Breakdown(dimensions.get(ScoreCategory.STRUCTURE),dimensions.get(ScoreCategory.GARMENT_CHARACTERISTICS),
            dimensions.get(ScoreCategory.ACCESSORIES),dimensions.get(ScoreCategory.CONTEXT),dimensions.get(ScoreCategory.MODERN_REMIX));
        warnings.sort(Comparator.comparing(Warning::severity).reversed());
        if(!missing.isEmpty()) return new CulturalScoreResponse(null,"INSUFFICIENT_DATA",breakdown,List.copyOf(warnings),missing,
            "Chưa đủ quy tắc tham khảo cho cả 5 tiêu chí; chưa thể tính điểm tổng.");
        int score=(int)Math.round(dimensions.entrySet().stream().mapToDouble(e -> e.getValue()*e.getKey().weight/100.0).sum());
        String level=score>=90?"WELL_PRESERVED":score>=75?"SUITABLE":score>=60?"WARNING":"HIGH_RISK";
        return new CulturalScoreResponse(score,level,breakdown,List.copyOf(warnings),List.of(),
            "Điểm tương thích theo rule và trọng số định hướng; không phải phán quyết tuyệt đối về văn hóa.");
    }
    private boolean matches(CulturalRule r,LookSelection l) {
        return switch(r.getTargetType()) {
            case OUTFIT -> r.getTargetCode().equals(l.outfitCode());
            case COLOR -> r.getTargetCode().equals(l.colorCode());
            case STYLE -> r.getTargetCode().equals(l.styleCode());
            case EVENT -> r.getTargetCode().equals(l.eventCode());
            case ACCESSORY -> l.accessories().contains(r.getTargetCode());
        };
    }
}
