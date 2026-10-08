package com.vietphuc.remix.service;
import com.vietphuc.remix.dto.request.SaveLookRequest;
import com.vietphuc.remix.dto.response.LookResponse;
import com.vietphuc.remix.entity.*;
import com.vietphuc.remix.repository.*;
import com.vietphuc.remix.exception.ApiException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.*;
@Service @RequiredArgsConstructor
public class LookService {
    private final LookRepository looks;
    private final LookAccessoryRepository links;
    private final SelectionService selections;
    private final CulturalScoreService culture;
    @Transactional
    public LookResponse save(SaveLookRequest request) {
        var selection=selections.validate(request.selection());
        var score=culture.evaluate(request.selection());
        Look look=new Look();
        look.setOutfit(selection.outfit()); look.setColor(selection.color());
        look.setStyle(selection.style()); look.setEvent(selection.event());
        look.setOriginalPrompt(request.originalPrompt()); look.setPreviewImageUrl(request.previewImageUrl());
        look.setCulturalScore(score.score());
        // Style match and color harmony stay NULL until a defined server-side scoring method exists.
        looks.saveAndFlush(look);
        for(var accessory:selection.accessories()) {
            var link=new LookAccessory();
            link.setId(new LookAccessoryId(look.getId(),accessory.getId()));
            link.setLook(look); link.setAccessory(accessory); links.save(link);
        }
        return response(look,request.accessories());
    }
    @Transactional(readOnly=true)
    public LookResponse get(Long id) {
        var look=looks.findById(id).orElseThrow(() -> ApiException.notFound("Không tìm thấy look."));
        return response(look,links.findByLookIdOrderByAccessoryLayerOrderAsc(id).stream()
            .map(l -> l.getAccessory().getCode()).toList());
    }
    private LookResponse response(Look l,List<String> accessories) {
        return new LookResponse(l.getId(),l.getOutfit().getCode(),l.getColor().getCode(),l.getStyle().getCode(),
            l.getEvent().getCode(),List.copyOf(accessories),l.getOriginalPrompt(),l.getStyleMatchScore(),
            l.getCulturalScore(),l.getColorHarmonyScore(),l.getPreviewImageUrl(),l.getCreatedAt(),l.getUpdatedAt());
    }
}
