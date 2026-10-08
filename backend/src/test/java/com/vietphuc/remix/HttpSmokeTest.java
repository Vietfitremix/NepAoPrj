package com.vietphuc.remix;
import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.http.HttpStatus;
import static org.junit.jupiter.api.Assertions.*;
@SpringBootTest(webEnvironment=SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
class HttpSmokeTest {
    @Autowired TestRestTemplate http;
    @Test void applicationStartsAndServesRealHttp() {
        var health=http.getForEntity("/api/health",JsonNode.class);
        assertEquals(HttpStatus.OK,health.getStatusCode());
        assertEquals("UP",health.getBody().path("status").asText());
        var outfits=http.getForEntity("/api/outfits",JsonNode.class);
        assertEquals(HttpStatus.OK,outfits.getStatusCode());
        assertEquals(5,outfits.getBody().size());
        var missing=http.getForEntity("/api/not-a-route",JsonNode.class);
        assertEquals(HttpStatus.NOT_FOUND,missing.getStatusCode());
    }
}
