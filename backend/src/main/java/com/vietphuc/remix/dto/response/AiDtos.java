package com.vietphuc.remix.dto.response;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.util.List;
public final class AiDtos {
    private AiDtos() {}
    public record Concept(
        @NotBlank @Size(max=100) String conceptName,
        @NotBlank String outfitCode, @NotBlank String colorCode, @NotBlank String styleCode,
        @NotNull @Size(max=10) List<@NotBlank String> accessories,
        @NotNull @Min(0) @Max(100) Integer matchScore,
        @NotBlank @Size(max=2000) String reason
    ) {}
    public record Analysis(String event,WeatherResponse weather,List<String> styles) {}
    public record RecommendationResponse(Analysis analysis,List<Concept> concepts) {}
    public record Changes(
        @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String colorCode,
        @Pattern(regexp="[A-Z][A-Z0-9_]{0,39}") String styleCode,
        @NotNull @Size(max=10) List<@NotBlank String> removeAccessories,
        @NotNull @Size(max=10) List<@NotBlank String> addAccessories
    ) {}
    public record RemixResponse(@NotNull @Valid Changes changes,
                                @NotBlank @Size(max=2000) String explanation) {}
}
