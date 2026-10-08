package com.vietphuc.remix.dto.request;
import jakarta.validation.constraints.*;
public record RecommendationRequest(
    @NotBlank @Size(max=2000) String prompt,
    @NotBlank @Size(max=100) String city,
    @NotBlank @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String eventCode,
    @NotBlank @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String styleCode
) {}
