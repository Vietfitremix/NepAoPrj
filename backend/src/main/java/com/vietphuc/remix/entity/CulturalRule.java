package com.vietphuc.remix.entity;
import jakarta.persistence.*;
import java.time.Instant;
import lombok.*;
import com.vietphuc.remix.enums.*;
@Getter @Setter @Entity @Table(name="cultural_rules")
public class CulturalRule extends BaseEntity {
    @ManyToOne(fetch=FetchType.LAZY, optional=false) @JoinColumn(name="outfit_id") private Outfit outfit;
    @Enumerated(EnumType.STRING) @Column(nullable=false,length=40) private ScoreCategory category;
    @Enumerated(EnumType.STRING) @Column(nullable=false,length=40) private TargetType targetType;
    @Column(nullable=false,length=40) private String targetCode;
    @Enumerated(EnumType.STRING) @Column(nullable=false,length=40) private RuleType ruleType;
    @Column(nullable=false) private Integer scoreModifier;
    @Enumerated(EnumType.STRING) @Column(nullable=false,length=40) private Severity severity;
    @Column(nullable=false,columnDefinition="text") private String message;
    @Column(columnDefinition="text") private String suggestion;
    @Column(nullable=false) private String sourceName;
    @Column(nullable=false,columnDefinition="text") private String sourceUrl;
    @Column(nullable=false,updatable=false) private Instant createdAt;
    @PrePersist void create() { if(createdAt == null) createdAt = Instant.now(); }
}
