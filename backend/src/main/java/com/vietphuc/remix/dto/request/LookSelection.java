package com.vietphuc.remix.dto.request;
import jakarta.validation.constraints.*;
import java.util.List;
public record LookSelection(
    @NotBlank @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String outfitCode,
    @NotBlank @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String colorCode,
    @NotBlank @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String styleCode,
    @NotBlank @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String eventCode,
    @NotNull @Size(max=10) List<@NotBlank @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String> accessories,
    com.fasterxml.jackson.databind.JsonNode wardrobe,
    @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    com.fasterxml.jackson.databind.JsonNode context
) {
    public LookSelection(String outfitCode,String colorCode,String styleCode,String eventCode,List<String> accessories,com.fasterxml.jackson.databind.JsonNode wardrobe) {
        this(outfitCode,colorCode,styleCode,eventCode,accessories,wardrobe,null);
    }
    public LookSelection(String outfitCode,String colorCode,String styleCode,String eventCode,List<String> accessories) {
        this(outfitCode,colorCode,styleCode,eventCode,accessories,null);
    }
}
