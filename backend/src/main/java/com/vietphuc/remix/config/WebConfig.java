package com.vietphuc.remix.config;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
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
        registry.addMapping("/ai/**").allowedOrigins(properties.corsAllowedOrigins().toArray(String[]::new))
                .allowedMethods("GET", "POST").allowedHeaders("Content-Type");
        registry.addMapping("/figure/**").allowedOrigins(properties.corsAllowedOrigins().toArray(String[]::new))
                .allowedMethods("GET");
    }
    /** Serve the existing React build when WEB_ROOT points to frontend/dist. */
    @Override public void addResourceHandlers(ResourceHandlerRegistry registry) {
        if (webRoot == null || webRoot.isBlank()) return;
        Resource root = new FileSystemResource(webRoot.endsWith("/") ? webRoot : webRoot + "/");
        registry.addResourceHandler("/**").addResourceLocations(root).resourceChain(true)
            .addResolver(new PathResourceResolver() {
                @Override protected Resource getResource(String path, Resource location) throws java.io.IOException {
                    Resource resource = super.getResource(path, location);
                    if (resource != null) return resource;
                    // API and missing asset URLs must keep their normal 404 response.
                    if (path.equals("api") || path.startsWith("api/") || path.equals("ai") || path.startsWith("ai/")
                        || path.startsWith("figure/") || path.startsWith("assets/") || path.contains(".")) return null;
                    return super.getResource("index.html", location);
                }
            });
    }
    @Override public void addViewControllers(ViewControllerRegistry registry) {
        if (webRoot != null && !webRoot.isBlank()) registry.addViewController("/").setViewName("forward:/index.html");
    }
}
