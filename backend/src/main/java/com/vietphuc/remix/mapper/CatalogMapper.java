package com.vietphuc.remix.mapper;
import com.vietphuc.remix.entity.*;
import com.vietphuc.remix.dto.response.CatalogDtos.*;
public final class CatalogMapper {
    private CatalogMapper() {}
    public static OutfitSummary outfit(Outfit o) {
        return new OutfitSummary(o.getCode(),o.getName(),o.getDescription(),o.getOrigin(),o.getCulturalMeaning(),o.getThumbnailUrl());
    }
    public static ColorView color(Color c) { return new ColorView(c.getCode(),c.getName(),c.getHexCode()); }
    public static AccessoryView accessory(Accessory a) {
        return new AccessoryView(a.getCode(),a.getName(),a.getType(),a.getDescription(),a.getImageUrl(),a.getLayerOrder());
    }
    public static ReferenceView style(Style s) { return new ReferenceView(s.getCode(),s.getName(),s.getDescription()); }
    public static ReferenceView event(Event e) { return new ReferenceView(e.getCode(),e.getName(),e.getDescription()); }
    public static AssetView asset(OutfitAsset a) {
        return new AssetView(a.getColor().getCode(),a.getAssetType(),a.getVariantCode(),a.getImageUrl(),a.getLayerOrder());
    }
    public static KnowledgeView knowledge(CulturalKnowledge k) {
        return new KnowledgeView(k.getCategory(),k.getTitle(),k.getContent(),k.getSourceName(),k.getSourceUrl());
    }
}
