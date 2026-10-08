package com.vietphuc.remix.entity;
import jakarta.persistence.*;
import lombok.*;
@Getter @Setter @Entity @Table(name="accessories")
public class Accessory extends BaseEntity {
    @Column(nullable=false, unique=true, length=40) private String code;
    @Column(nullable=false, length=100) private String name;
    @Column(nullable=false, length=40) private String type;
    @Column(columnDefinition="text") private String description;
    private String imageUrl;
    @Column(nullable=false) private Integer layerOrder;
}
