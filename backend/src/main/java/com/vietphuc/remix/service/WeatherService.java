package com.vietphuc.remix.service;
import com.vietphuc.remix.client.WeatherClient;
import com.vietphuc.remix.dto.response.WeatherResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
@Service @RequiredArgsConstructor
public class WeatherService {
    private final WeatherClient weather;
    public WeatherResponse current(String city) { return weather.current(city.strip()); }
}
