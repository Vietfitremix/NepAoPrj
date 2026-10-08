package com.vietphuc.remix.dto.response;
import java.time.Instant;
import java.util.List;
public record LookResponse(Long id,String outfitCode,String colorCode,String styleCode,String eventCode,
                           List<String> accessories,String originalPrompt,Integer styleMatchScore,
                           Integer culturalScore,Integer colorHarmonyScore,String previewImageUrl,
                           Instant createdAt,Instant updatedAt) {}
