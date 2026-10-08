package com.vietphuc.remix.dto.response;
import java.util.List;
public final class CatalogDtos {
    private CatalogDtos() {}
    public record OutfitSummary(String code,String name,String description,String origin,
                                String culturalMeaning,String thumbnailUrl) {}
    public record ColorView(String code,String name,String hexCode) {}
    public record AccessoryView(String code,String name,String type,String description,String imageUrl,Integer layerOrder) {}
    public record ReferenceView(String code,String name,String description) {}
    public record AssetView(String colorCode,String assetType,String variantCode,String imageUrl,Integer layerOrder) {}
    public record KnowledgeView(String category,String title,String content,String sourceName,String sourceUrl) {}
    public record OutfitDetail(OutfitSummary outfit,List<ColorView> colors,List<AssetView> assets,
                               List<AccessoryView> accessories) {}
    public record ReferenceData(List<OutfitDetail> outfits,List<ColorView> colors,List<ReferenceView> styles,
                                List<ReferenceView> events,List<AccessoryView> accessories) {}
}
