package com.vietphuc.remix.entity;
import jakarta.persistence.*;
import lombok.*;
@Getter @Setter @Entity @Table(name="look_accessories")
public class LookAccessory {
    @EmbeddedId private LookAccessoryId id;
    @MapsId("lookId") @ManyToOne(fetch=FetchType.LAZY,optional=false) @JoinColumn(name="look_id")
    private Look look;
    @MapsId("accessoryId") @ManyToOne(fetch=FetchType.LAZY,optional=false) @JoinColumn(name="accessory_id")
    private Accessory accessory;
}
