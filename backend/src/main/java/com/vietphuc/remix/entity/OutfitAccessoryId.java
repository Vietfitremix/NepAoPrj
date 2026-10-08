package com.vietphuc.remix.entity;
import jakarta.persistence.*;
import lombok.*;
import java.io.Serializable;
@Getter @Setter @EqualsAndHashCode @NoArgsConstructor @AllArgsConstructor @Embeddable
public class OutfitAccessoryId implements Serializable {
    @Column(name="outfit_id") private Long outfitId;
    @Column(name="accessory_id") private Long accessoryId;
}
