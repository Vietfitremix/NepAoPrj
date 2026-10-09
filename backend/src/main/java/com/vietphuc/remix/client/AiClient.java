package com.vietphuc.remix.client;
import com.fasterxml.jackson.databind.JsonNode;
import com.vietphuc.remix.config.AppProperties;
import com.vietphuc.remix.exception.ApiException;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.*;
@Component
public class AiClient {
    private final RestClient client;
    public AiClient(AppProperties properties) {
        client=ClientSupport.create(properties.ai().baseUrl(),properties,properties.aiTimeout());
    }
    public JsonNode recommendations(Object request) { return post("/ai/recommendations",request); }
    public JsonNode remix(Object request) { return post("/ai/remix",request); }
    public JsonNode culturalScore(Object request) { return post("/ai/wardrobe-score",request); }
    private JsonNode post(String path,Object request) {
        try {
            var data=client.post().uri(path).contentType(MediaType.APPLICATION_JSON).body(request)
                .retrieve().body(JsonNode.class);
            if(data==null || !data.isObject()) throw ApiException.upstream("AI Service trả dữ liệu không hợp lệ.");
            return data;
        } catch(RestClientException e) {
            throw ApiException.upstream("AI Service không phản hồi hoặc trả dữ liệu không hợp lệ.");
        }
    }
}
