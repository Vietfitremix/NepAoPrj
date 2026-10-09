package com.vietphuc.remix;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sun.net.httpserver.HttpServer;
import com.vietphuc.remix.config.AppProperties;
import com.vietphuc.remix.controller.AiProxyController;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;
import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest @AutoConfigureMockMvc @ActiveProfiles("test") @Transactional
class NepAoIntegrationTest {
    static final AtomicReference<String> requestBody = new AtomicReference<>();
    static final AtomicReference<String> requestQuery = new AtomicReference<>();
    static final AtomicReference<String> requestIp = new AtomicReference<>();
    static final AtomicInteger calls = new AtomicInteger();
    static final HttpServer upstream = startUpstream();
    @Autowired MockMvc mvc;
    @Autowired ObjectMapper mapper;

    static HttpServer startUpstream() {
        try {
            var server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
            server.createContext("/ai/", exchange -> {
                calls.incrementAndGet();
                requestBody.set(new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8));
                requestQuery.set(exchange.getRequestURI().getRawQuery());
                requestIp.set(exchange.getRequestHeaders().getFirst("X-Forwarded-For"));
                int status = exchange.getRequestURI().getPath().endsWith("evaluate") ? 422 : 200;
                byte[] body = (status == 422 ? "{\"message\":\"Bản phối không hợp lệ\"}" : "[{\"id\":\"occasion\"}]").getBytes(StandardCharsets.UTF_8);
                exchange.getResponseHeaders().set("Content-Type", "application/json");
                exchange.sendResponseHeaders(status, body.length);
                exchange.getResponseBody().write(body);
                exchange.close();
            });
            server.start();
            return server;
        } catch (java.io.IOException e) { throw new IllegalStateException(e); }
    }
    @DynamicPropertySource static void properties(DynamicPropertyRegistry registry) {
        registry.add("app.ai.base-url", () -> "http://127.0.0.1:" + upstream.getAddress().getPort());
    }
    @AfterAll static void stopUpstream() { upstream.stop(0); }

    @Test void proxyPreservesGetQueryAndJsonResponse() throws Exception {
        mvc.perform(get(java.net.URI.create("/ai/quiz?language=vi%20VN")))
            .andExpect(status().isOk()).andExpect(jsonPath("$[0].id").value("occasion"));
        assertEquals("language=vi%20VN", requestQuery.get());
    }
    @Test void proxyPreservesPostBodyAndUpstreamError() throws Exception {
        String body = "{\"state\":{\"garment\":\"không hợp lệ\"}}";
        mvc.perform(post("/ai/evaluate").header("X-Forwarded-For", "203.0.113.1")
            .contentType("application/json").content(body))
            .andExpect(status().isUnprocessableEntity()).andExpect(jsonPath("$.message").value("Bản phối không hợp lệ"));
        assertEquals(body, requestBody.get());
        assertEquals("127.0.0.1", requestIp.get());
    }
    @Test void proxyDoesNotExposeAdminOrDevRoutes() throws Exception {
        int before = calls.get();
        mvc.perform(get("/ai/admin/catalog")).andExpect(status().isForbidden());
        mvc.perform(post("/ai/dev/reset")).andExpect(status().isForbidden());
        assertEquals(before, calls.get());
    }
    @Test void proxyHasAllowedOriginCors() throws Exception {
        for (String origin : List.of("http://localhost:5173", "http://localhost:5176")) {
            for (String path : List.of("/ai/evaluate", "/api/recommendations")) {
                mvc.perform(options(path).header("Origin", origin)
                    .header("Access-Control-Request-Method", "POST"))
                    .andExpect(status().isOk()).andExpect(header().string("Access-Control-Allow-Origin", origin));
            }
        }
        // A browser's actual POST must reach the upstream, not fail with CORS 403.
        mvc.perform(post("/ai/evaluate").header("Origin", "http://localhost:5176")
            .contentType("application/json").content("{}"))
            .andExpect(status().isUnprocessableEntity())
            .andExpect(header().string("Access-Control-Allow-Origin", "http://localhost:5176"));
    }
    @Test void unavailableAiReturnsJsonBadGateway() throws Exception {
        var properties = new AppProperties(null, new AppProperties.Ai("http://127.0.0.1:1"),
            Duration.ofMillis(200), Duration.ofMillis(200), Duration.ofMillis(200), List.of());
        var request = new MockHttpServletRequest("GET", "/ai/quiz");
        var response = new AiProxyController(properties).forward(request, null);
        assertEquals(502, response.getStatusCode().value());
        assertEquals("application/json", response.getHeaders().getFirst("Content-Type"));
        assertEquals("AI_UNAVAILABLE", mapper.readTree(response.getBody()).path("code").asText());
    }
    @Test void sharedLookRoundTripsNestedJsonAndVietnamese() throws Exception {
        var payload = mapper.readTree("""
            {"state":{"garment":"ao_dai","colors":{"main":"do_son"},"accessories":["non_la"]},
             "context":{"occasion":"tet"},"scoreCard":{"total":85},"note":{"title":"Áo dài ngày Tết"}}
            """);
        var response = mvc.perform(post("/api/shared-looks").contentType("application/json").content(payload.toString()))
            .andExpect(status().isCreated()).andExpect(jsonPath("$.id").isString()).andReturn();
        String id = mapper.readTree(response.getResponse().getContentAsByteArray()).path("id").asText();
        java.util.UUID.fromString(id);
        var loaded = mvc.perform(get("/api/shared-looks/" + id)).andExpect(status().isOk()).andReturn();
        assertEquals(payload, mapper.readTree(loaded.getResponse().getContentAsByteArray()));
    }
    @Test void sharedLookRejectsMissingStateAndOversizedUtf8() throws Exception {
        for (String body : List.of("[]", "{}", "{\"state\":[]}"))
            mvc.perform(post("/api/shared-looks").contentType("application/json").content(body)).andExpect(status().isBadRequest());
        var large = mapper.createObjectNode();
        large.set("state", mapper.createObjectNode());
        large.put("note", "á".repeat(32768));
        mvc.perform(post("/api/shared-looks").contentType("application/json").content(large.toString())).andExpect(status().isBadRequest());
    }
    @Test void sharedLookMissingAndMalformedIdsHaveClearErrors() throws Exception {
        mvc.perform(get("/api/shared-looks/00000000-0000-0000-0000-000000000000")).andExpect(status().isNotFound());
        mvc.perform(get("/api/shared-looks/not-a-uuid")).andExpect(status().isBadRequest());
    }
}
