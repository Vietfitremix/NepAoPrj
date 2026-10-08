package com.vietphuc.remix.controller;
import com.vietphuc.remix.service.WeatherService;
import com.vietphuc.remix.dto.response.WeatherResponse;
import jakarta.validation.constraints.*;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/api/weather") @RequiredArgsConstructor
public class WeatherController {
    private final WeatherService weather;
    @GetMapping public WeatherResponse current(@RequestParam @NotBlank @Size(max=100) String city) {
        return weather.current(city);
    }
}
