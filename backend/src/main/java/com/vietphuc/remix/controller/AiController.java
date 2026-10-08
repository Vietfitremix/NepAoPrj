package com.vietphuc.remix.controller;
import com.vietphuc.remix.service.AiService;
import com.vietphuc.remix.dto.request.RemixRequest;
import com.vietphuc.remix.dto.response.AiDtos.RemixResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/api/remix") @RequiredArgsConstructor
public class AiController {
    private final AiService ai;
    @PostMapping public RemixResponse remix(@Valid @RequestBody RemixRequest request) { return ai.remix(request); }
}
