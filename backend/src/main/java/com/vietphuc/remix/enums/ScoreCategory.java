package com.vietphuc.remix.enums;
public enum ScoreCategory {
    STRUCTURE(30), GARMENT_CHARACTERISTICS(25), ACCESSORIES(20), CONTEXT(15), MODERN_REMIX(10);
    public final int weight;
    ScoreCategory(int weight) { this.weight=weight; }
}
