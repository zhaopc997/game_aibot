package com.gametips.platform.common.config;

import com.gametips.platform.common.ratelimit.RateLimitInterceptor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.nio.file.Path;

/**
 * 静态资源映射 + 限流拦截器。
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    private final Path uploadRoot;
    private final RateLimitInterceptor rateLimitInterceptor;

    public WebConfig(@Value("${app.upload.local-dir:./uploads}") String dir,
                     RateLimitInterceptor rateLimitInterceptor) {
        this.uploadRoot = Path.of(dir).toAbsolutePath().normalize();
        this.rateLimitInterceptor = rateLimitInterceptor;
    }

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/uploads/**")
                .addResourceLocations(uploadRoot.toUri().toString());
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(rateLimitInterceptor)
                .addPathPatterns("/api/v1/**");
    }
}
