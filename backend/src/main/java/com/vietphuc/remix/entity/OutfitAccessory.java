package com.vietphuc.remix.entity;
import jakarta.persistence.*;
import lombok.*;
@Getter @Setter @Entity @Table(name="outfit_accessories")
public class OutfitAccessory {
    @EmbeddedId private OutfitAccessoryId id;
    @MapsId("outfitId") @ManyToOne(fetch=FetchType.LAZY,optional=false) @JoinColumn(name="outfit_id")
    private Outfit outfit;
    @MapsId("accessoryId") @ManyToOne(fetch=FetchType.LAZY,optional=false) @JoinColumn(name="accessory_id")
    private Accessory accessory;
    private Integer compatibilityScore;
}
