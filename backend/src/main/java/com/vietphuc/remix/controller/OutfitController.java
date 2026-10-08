package com.vietphuc.remix.controller;
import com.vietphuc.remix.service.OutfitService;
import com.vietphuc.remix.dto.response.CatalogDtos.*;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.List;
@RestController @RequestMapping("/api") @RequiredArgsConstructor
public class OutfitController {
    private final OutfitService outfits;
    @GetMapping("/outfits") public List<OutfitSummary> list() { return outfits.list(); }
    @GetMapping("/outfits/{code}") public OutfitDetail detail(@PathVariable String code) { return outfits.detail(code); }
    @GetMapping("/outfits/{code}/cultural-knowledge")
    public List<KnowledgeView> knowledge(@PathVariable String code) { return outfits.knowledge(code); }
    @GetMapping("/reference-data") public ReferenceData references() { return outfits.references(); }
}
