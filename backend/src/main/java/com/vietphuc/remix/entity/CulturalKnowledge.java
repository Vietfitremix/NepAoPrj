package com.vietphuc.remix.entity;
import jakarta.persistence.*;
import java.time.Instant;
import lombok.*;
@Getter @Setter @Entity @Table(name="cultural_knowledge")
public class CulturalKnowledge extends BaseEntity {
    @ManyToOne(fetch=FetchType.LAZY, optional=false) @JoinColumn(name="outfit_id") private Outfit outfit;
    @Column(nullable=false,length=40) private String category;
    @Column(nullable=false) private String title;
    @Column(nullable=false,columnDefinition="text") private String content;
    @Column(nullable=false) private String sourceName;
    @Column(nullable=false,columnDefinition="text") private String sourceUrl;
    @Column(nullable=false,updatable=false) private Instant createdAt;
    @PrePersist void create() { if(createdAt == null) createdAt = Instant.now(); }
}
