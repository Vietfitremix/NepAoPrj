package com.vietphuc.remix.controller;
import com.vietphuc.remix.config.AppProperties;
import jakarta.servlet.http.HttpServletRequest;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.nio.charset.StandardCharsets;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * Chuyển tiếp /ai/** tới AI service (quiz, stylist, evaluate, review, catalog, figure...).
 * Trình duyệt chỉ nói chuyện với một địa chỉ; khoá Gemini vẫn chỉ nằm ở AI service.
 */
@RestController
public class AiProxyController {
    private final HttpClient http;
    private final String base;
    private final Duration timeout;

    public AiProxyController(AppProperties properties) {
        this.http = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1)
                .connectTimeout(properties.connectTimeout()).followRedirects(HttpClient.Redirect.NEVER).build();
        String url = properties.ai().baseUrl();
        this.base = url.endsWith("/") ? url.substring(0, url.length() - 1) : url;
        this.timeout = properties.aiTimeout();
    }

    @RequestMapping("/ai/**")
    public ResponseEntity<byte[]> forward(HttpServletRequest request, @RequestBody(required = false) byte[] body) throws IOException, InterruptedException {
        String path = request.getRequestURI();
        if (path.contains("..") || path.startsWith("/ai/admin") || path.startsWith("/ai/dev")) return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        String query = request.getQueryString() == null ? "" : "?" + request.getQueryString();
        var builder = HttpRequest.newBuilder(URI.create(base + path + query)).timeout(timeout);
        builder.header("X-Forwarded-For", request.getRemoteAddr());
        if (request.getContentType() != null) builder.header("Content-Type", request.getContentType());
        builder.method(request.getMethod(), body == null || body.length == 0 ? HttpRequest.BodyPublishers.noBody() : HttpRequest.BodyPublishers.ofByteArray(body));
        HttpResponse<byte[]> res;
        try {
            res = http.send(builder.build(), HttpResponse.BodyHandlers.ofByteArray());
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY).header("Content-Type", "application/json")
                .body("{\"code\":\"AI_UNAVAILABLE\",\"message\":\"AI service không phản hồi.\"}".getBytes(StandardCharsets.UTF_8));
        }
        var headers = new HttpHeaders();
        res.headers().firstValue("Content-Type").ifPresent(v -> headers.set("Content-Type", v));
        res.headers().firstValue("Cache-Control").ifPresent(v -> headers.set("Cache-Control", v));
        return ResponseEntity.status(res.statusCode()).headers(headers).body(res.body());
    }
}
