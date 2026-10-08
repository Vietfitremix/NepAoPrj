package com.vietphuc.remix.entity;
import jakarta.persistence.*;
import lombok.*;
import java.io.Serializable;
@Getter @Setter @EqualsAndHashCode @NoArgsConstructor @AllArgsConstructor @Embeddable
public class LookAccessoryId implements Serializable {
    @Column(name="look_id") private Long lookId;
    @Column(name="accessory_id") private Long accessoryId;
}
