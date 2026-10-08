package com.vietphuc.remix.entity;
import jakarta.persistence.*;
import lombok.*;
@Getter @Setter @Entity @Table(name="styles")
public class Style extends BaseEntity {
    @Column(nullable=false,unique=true,length=40) private String code;
    @Column(nullable=false,length=100) private String name;
    @Column(columnDefinition="text") private String description;
}
