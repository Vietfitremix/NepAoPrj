package com.vietphuc.remix.dto.request;
import jakarta.validation.constraints.*;
public record RecommendationRequest(
    @NotBlank @Size(max=2000) String prompt,
    @NotBlank @Size(max=100) String city,
    @NotBlank @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String eventCode,
    @NotBlank @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String styleCode,
    @Pattern(regexp="male|female") String character
) {
    public RecommendationRequest(String prompt,String city,String eventCode,String styleCode) {
        this(prompt,city,eventCode,styleCode,null);
    }
}
