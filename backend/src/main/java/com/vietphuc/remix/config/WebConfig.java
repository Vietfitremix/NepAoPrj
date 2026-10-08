package com.vietphuc.remix.config;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.*;
import org.springframework.web.servlet.resource.PathResourceResolver;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.*;
@Configuration
@RequiredArgsConstructor
public class WebConfig implements WebMvcConfigurer {
    private final AppProperties properties;
    @Value("${app.web-root:}") private String webRoot;
    @Override public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**").allowedOrigins(properties.corsAllowedOrigins().toArray(String[]::new))
                .allowedMethods("GET", "POST").allowedHeaders("Content-Type");
    }
    /** Chạy một cổng: Spring phục vụ luôn bản build React (frontend/dist) khi đặt WEB_ROOT; đường dẫn không phải file/API rơi về index.html. */
    @Override public void addResourceHandlers(ResourceHandlerRegistry registry) {
        if (webRoot == null || webRoot.isBlank()) return;
        Resource root = new FileSystemResource(webRoot.endsWith("/") ? webRoot : webRoot + "/");
        registry.addResourceHandler("/**").addResourceLocations(root).resourceChain(true).addResolver(new PathResourceResolver() {
            @Override protected Resource getResource(String path, Resource location) throws java.io.IOException {
                Resource r = location.createRelative(path);
                return r.exists() && r.isReadable() ? r : (path.startsWith("api/") ? null : location.createRelative("index.html"));
            }
        });
    }
    @Override public void addViewControllers(ViewControllerRegistry registry) {
        if (webRoot != null && !webRoot.isBlank()) registry.addViewController("/").setViewName("forward:/index.html");
    }
}
