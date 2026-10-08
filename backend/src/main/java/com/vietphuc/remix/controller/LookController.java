package com.vietphuc.remix.controller;
import com.vietphuc.remix.service.LookService;
import com.vietphuc.remix.dto.request.SaveLookRequest;
import com.vietphuc.remix.dto.response.LookResponse;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Positive;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.net.URI;
@RestController @RequestMapping("/api/looks") @RequiredArgsConstructor
public class LookController {
    private final LookService looks;
    @PostMapping public ResponseEntity<LookResponse> save(@Valid @RequestBody SaveLookRequest request) {
        var saved=looks.save(request);
        return ResponseEntity.created(URI.create("/api/looks/"+saved.id())).body(saved);
    }
    @GetMapping("/{id}") public LookResponse get(@PathVariable @Positive Long id) { return looks.get(id); }
}
