package com.vietphuc.remix.entity;
import jakarta.persistence.*;
import lombok.*;
import java.util.*;
@Getter @Setter @Entity @Table(name="looks")
public class Look extends TimedEntity {
    @ManyToOne(fetch=FetchType.LAZY, optional=false) @JoinColumn(name="outfit_id") private Outfit outfit;
    @ManyToOne(fetch=FetchType.LAZY, optional=false) @JoinColumn(name="color_id") private Color color;
    @ManyToOne(fetch=FetchType.LAZY, optional=false) @JoinColumn(name="style_id") private Style style;
    @ManyToOne(fetch=FetchType.LAZY, optional=false) @JoinColumn(name="event_id") private Event event;
    @Column(columnDefinition="text") private String originalPrompt;
    private Integer styleMatchScore;
    private Integer culturalScore;
    private Integer colorHarmonyScore;
    @Column(length=2048) private String previewImageUrl;
}
