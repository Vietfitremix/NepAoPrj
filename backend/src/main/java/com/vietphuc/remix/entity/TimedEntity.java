package com.vietphuc.remix.entity;
import jakarta.persistence.*;
import lombok.*;
import java.time.Instant;
@Getter @Setter @MappedSuperclass
public abstract class TimedEntity extends BaseEntity {
    @Column(nullable=false, updatable=false) private Instant createdAt;
    @Column(nullable=false) private Instant updatedAt;
    @PrePersist void create() { createdAt = Instant.now(); updatedAt = createdAt; }
    @PreUpdate void update() { updatedAt = Instant.now(); }
}
