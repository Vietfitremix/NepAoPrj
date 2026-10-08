package com.vietphuc.remix.client;
import com.fasterxml.jackson.databind.JsonNode;
import com.vietphuc.remix.config.AppProperties;
import com.vietphuc.remix.dto.response.WeatherResponse;
import com.vietphuc.remix.exception.ApiException;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.client.*;
import java.util.Map;
@Component
public class WeatherClient {
    private final RestClient client;
    private final String apiKey;
    public WeatherClient(AppProperties properties) {
        client=ClientSupport.create(properties.weather().baseUrl(),properties,properties.weatherTimeout());
        apiKey=properties.weather().apiKey();
    }
    public WeatherResponse current(String city) {
        if(apiKey==null || apiKey.isBlank())
            throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE,"WEATHER_NOT_CONFIGURED","Chưa cấu hình Weather API key.");
        try {
            var data=client.get().uri(b -> b.path("/data/2.5/weather")
                .queryParam("q","{city}").queryParam("appid","{key}").queryParam("units","metric")
                .build(Map.of("city",city,"key",apiKey))).retrieve().body(JsonNode.class);
            if(data==null || !data.path("main").path("temp").isNumber() ||
               !data.path("main").path("humidity").isIntegralNumber() ||
               !data.path("weather").path(0).path("id").isIntegralNumber())
                throw ApiException.upstream("Weather API trả dữ liệu không hợp lệ.");
            double temperature=data.path("main").path("temp").doubleValue();
            int humidity=data.path("main").path("humidity").intValue();
            int id=data.path("weather").path(0).path("id").intValue();
            if(!Double.isFinite(temperature) || humidity<0 || humidity>100)
                throw ApiException.upstream("Weather API trả dữ liệu ngoài giới hạn.");
            return new WeatherResponse(city,temperature,condition(id),humidity);
        } catch(RestClientResponseException e) {
            if(e.getStatusCode().value()==404) throw ApiException.invalid("Không tìm thấy thành phố.");
            throw ApiException.upstream("Không thể lấy thời tiết từ nhà cung cấp.");
        } catch(RestClientException e) {
            throw ApiException.upstream("Weather API không phản hồi hoặc trả dữ liệu không hợp lệ.");
        }
    }
    private String condition(int id) {
        if(id>=200 && id<300) return "THUNDERSTORM";
        if(id>=300 && id<600) return "RAIN";
        if(id>=600 && id<700) return "SNOW";
        if(id>=700 && id<800) return "FOG";
        if(id==800) return "CLEAR";
        if(id>800 && id<=804) return "CLOUDS";
        return "OTHER";
    }
}
