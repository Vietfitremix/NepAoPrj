package com.vietphuc.remix.service;
import com.vietphuc.remix.dto.response.CatalogDtos.*;
import com.vietphuc.remix.mapper.CatalogMapper;
import com.vietphuc.remix.repository.*;
import com.vietphuc.remix.exception.ApiException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.*;
@Service @RequiredArgsConstructor @Transactional(readOnly=true)
public class OutfitService {
    private final OutfitRepository outfits;
    private final ColorRepository colors;
    private final AccessoryRepository accessories;
    private final StyleRepository styles;
    private final EventRepository events;
    private final OutfitAssetRepository assets;
    private final OutfitAccessoryRepository supported;
    private final CulturalKnowledgeRepository knowledge;
    public List<OutfitSummary> list() { return outfits.findAllByOrderByIdAsc().stream().map(CatalogMapper::outfit).toList(); }
    public OutfitDetail detail(String code) {
        var outfit = outfits.findByCode(code).orElseThrow(() -> ApiException.notFound("Không tìm thấy trang phục: "+code));
        return new OutfitDetail(CatalogMapper.outfit(outfit),colors.findAllByOrderByIdAsc().stream().map(CatalogMapper::color).toList(),
            assets.findByOutfitCodeOrderByLayerOrderAsc(code).stream().map(CatalogMapper::asset).toList(),
            supported.findByOutfitCodeOrderByAccessoryCodeAsc(code).stream().map(a -> CatalogMapper.accessory(a.getAccessory())).toList());
    }
    public List<KnowledgeView> knowledge(String code) {
        if(!outfits.findByCode(code).isPresent()) throw ApiException.notFound("Không tìm thấy trang phục: "+code);
        return knowledge.findByOutfitCodeOrderByIdAsc(code).stream().map(CatalogMapper::knowledge).toList();
    }
    public ReferenceData references() {
        return new ReferenceData(list().stream().map(o -> detail(o.code())).toList(),
            colors.findAllByOrderByIdAsc().stream().map(CatalogMapper::color).toList(),
            styles.findAllByOrderByIdAsc().stream().map(CatalogMapper::style).toList(),
            events.findAllByOrderByIdAsc().stream().map(CatalogMapper::event).toList(),
            accessories.findAllByOrderByIdAsc().stream().map(CatalogMapper::accessory).toList());
    }
    public Map<String,List<KnowledgeView>> culturalContext() {
        Map<String,List<KnowledgeView>> result=new LinkedHashMap<>();
        for(var outfit:list()) result.put(outfit.code(),knowledge(outfit.code()));
        return result;
    }
}
