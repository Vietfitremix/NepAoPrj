package com.vietphuc.remix;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.sun.net.httpserver.HttpServer;
import com.vietphuc.remix.client.*;
import com.vietphuc.remix.config.AppProperties;
import com.vietphuc.remix.exception.ApiException;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
class ClientContractTest {
    private HttpServer server;
    private AppProperties properties;
    @BeforeEach void start() throws Exception {
        server=HttpServer.create(new InetSocketAddress(InetAddress.getLoopbackAddress(),0),0);
        server.start();
        String url="http://localhost:"+server.getAddress().getPort();
        properties=new AppProperties(new AppProperties.Weather(url,"secret-test-key"),new AppProperties.Ai(url),
            Duration.ofSeconds(1),Duration.ofMillis(250),Duration.ofMillis(250),List.of("http://localhost:5173"));
    }
    @AfterEach void stop() { server.stop(0); }
    private void respond(String path,int status,String body,AtomicReference<String> captured) {
        server.createContext(path,e -> {
            if(captured!=null) captured.set(new String(e.getRequestBody().readAllBytes(),StandardCharsets.UTF_8));
            byte[] bytes=body.getBytes(StandardCharsets.UTF_8);
            e.getResponseHeaders().add("Content-Type","application/json");
            e.sendResponseHeaders(status,bytes.length); e.getResponseBody().write(bytes); e.close();
        });
    }
    @Test void weatherMappingAndEncodedQuery() {
        var query=new AtomicReference<String>();
        server.createContext("/data/2.5/weather",e -> {
            query.set(e.getRequestURI().getRawQuery());
            byte[] b="{\"main\":{\"temp\":30.5,\"humidity\":82},\"weather\":[{\"id\":500}]}".getBytes(StandardCharsets.UTF_8);
            e.getResponseHeaders().add("Content-Type","application/json"); e.sendResponseHeaders(200,b.length);
            e.getResponseBody().write(b); e.close();
        });
        var result=new WeatherClient(properties).current("Hanoi&appid=attacker");
        assertEquals(30.5,result.temperature()); assertEquals("RAIN",result.condition());
        assertTrue(query.get().contains("Hanoi%26appid%3Dattacker")); assertTrue(query.get().contains("units=metric"));
        assertEquals(1,query.get().split("appid=", -1).length-1);
    }
    @Test void missingWeatherKeyFailsWithoutNetwork() {
        var p=new AppProperties(new AppProperties.Weather(properties.weather().baseUrl(),""),properties.ai(),
            properties.connectTimeout(),properties.weatherTimeout(),properties.aiTimeout(),properties.corsAllowedOrigins());
        assertEquals("WEATHER_NOT_CONFIGURED",assertThrows(ApiException.class,() -> new WeatherClient(p).current("Hanoi")).getCode());
    }
    @Test void invalidWeatherPayloadIsRejected() {
        respond("/data/2.5/weather",200,"{\"main\":{\"temp\":30,\"humidity\":150},\"weather\":[{\"id\":800}]}",null);
        assertEquals(502,assertThrows(ApiException.class,() -> new WeatherClient(properties).current("Hanoi")).getStatus().value());
    }
    @Test void malformedWeatherJsonIsRejected() {
        respond("/data/2.5/weather",200,"not-json",null);
        assertThrows(ApiException.class,() -> new WeatherClient(properties).current("Hanoi"));
    }
    @Test void unknownCityBecomesBadRequest() {
        respond("/data/2.5/weather",404,"{}",null);
        assertEquals(400,assertThrows(ApiException.class,() -> new WeatherClient(properties).current("Unknown")).getStatus().value());
    }
    @Test void upstreamErrorNeverLeaksSecretOrBody() {
        respond("/data/2.5/weather",401,"{\"message\":\"secret-test-key\"}",null);
        var error=assertThrows(ApiException.class,() -> new WeatherClient(properties).current("Hanoi"));
        assertFalse(error.getMessage().contains("secret-test-key")); assertEquals(502,error.getStatus().value());
    }
    @Test void aiPostsJsonContract() throws Exception {
        var captured=new AtomicReference<String>();
        respond("/ai/recommendations",200,"{\"concepts\":[]}",captured);
        var result=new AiClient(properties).recommendations(Map.of("prompt","Đi lễ hội","referenceData",Map.of()));
        assertTrue(result.path("concepts").isArray());
        assertEquals("Đi lễ hội",new ObjectMapper().readTree(captured.get()).path("prompt").asText());
    }
    @Test void aiHandlesMalformedPayloadAndUpstreamFailures() {
        respond("/ai/remix",200,"[]",null);
        assertThrows(ApiException.class,() -> new AiClient(properties).remix(Map.of()));
    }
    @Test void aiStatusErrorIsSanitized() {
        respond("/ai/recommendations",503,"{\"detail\":\"provider-secret\"}",null);
        assertFalse(assertThrows(ApiException.class,() -> new AiClient(properties).recommendations(Map.of())).getMessage().contains("provider-secret"));
    }
    @Test void slowAiIsBoundedByTimeout() {
        server.createContext("/ai/remix",e -> {
            try { Thread.sleep(800); } catch(InterruptedException ignored) { Thread.currentThread().interrupt(); }
            e.close();
        });
        assertThrows(ApiException.class,() -> new AiClient(properties).remix(Map.of()));
    }
}
