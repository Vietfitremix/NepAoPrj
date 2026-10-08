package com.vietphuc.remix.client;
import com.vietphuc.remix.config.AppProperties;
import java.net.http.HttpClient;
import java.time.Duration;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.web.client.RestClient;
final class ClientSupport {
    private ClientSupport() {}
    static RestClient create(String url,AppProperties properties,Duration timeout) {
        var http=HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1)
                .connectTimeout(properties.connectTimeout())
                .followRedirects(HttpClient.Redirect.NEVER).build();
        var factory=new JdkClientHttpRequestFactory(http);
        factory.setReadTimeout(timeout);
        return RestClient.builder().baseUrl(url).requestFactory(factory).build();
    }
}
