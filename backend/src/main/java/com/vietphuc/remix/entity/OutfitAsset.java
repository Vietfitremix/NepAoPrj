package com.vietphuc.remix.entity;
import jakarta.persistence.*;
import lombok.*;
@Getter @Setter @Entity @Table(name="outfit_assets")
public class OutfitAsset extends BaseEntity {
    @ManyToOne(fetch=FetchType.LAZY, optional=false) @JoinColumn(name="outfit_id") private Outfit outfit;
    @ManyToOne(fetch=FetchType.LAZY, optional=false) @JoinColumn(name="color_id") private Color color;
    @Column(nullable=false, length=40) private String assetType;
    @Column(nullable=false, length=40) private String variantCode;
    private String imageUrl;
    @Column(nullable=false) private Integer layerOrder;
}
