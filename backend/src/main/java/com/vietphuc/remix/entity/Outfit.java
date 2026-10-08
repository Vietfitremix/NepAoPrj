package com.vietphuc.remix.entity;
import jakarta.persistence.*;
import lombok.*;
@Getter @Setter @Entity @Table(name="outfits")
public class Outfit extends TimedEntity {
    @Column(nullable=false, unique=true, length=40) private String code;
    @Column(nullable=false, length=100) private String name;
    @Column(columnDefinition="text") private String description;
    @Column(columnDefinition="text") private String origin;
    @Column(columnDefinition="text") private String culturalMeaning;
    private String thumbnailUrl;
}
