package com.vietphuc.remix.dto.request;
import jakarta.validation.constraints.*;
import java.util.List;
public record LookSelection(
    @NotBlank @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String outfitCode,
    @NotBlank @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String colorCode,
    @NotBlank @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String styleCode,
    @NotBlank @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String eventCode,
    @NotNull @Size(max=10) List<@NotBlank @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String> accessories
) {}
