package com.vietphuc.remix.config;
import java.time.Duration;
import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;
@ConfigurationProperties(prefix = "app")
public record AppProperties(Weather weather, Ai ai, Duration connectTimeout, Duration weatherTimeout,
                            Duration aiTimeout, List<String> corsAllowedOrigins) {
    public record Weather(String baseUrl, String apiKey) {}
    public record Ai(String baseUrl) {}
}
