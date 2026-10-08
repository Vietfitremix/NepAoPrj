package com.vietphuc.remix.dto.request;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
public record RemixRequest(@NotNull @Valid LookSelection currentLook,
                           @NotBlank @Size(max=2000) String prompt) {}
