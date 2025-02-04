package com.example.b101.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

import java.util.List;

@Configuration // 스프링의 설정 클래스로 지정
public class CorsConfig {

    @Bean // CORS 필터를 빈으로 등록
    public CorsFilter corsFilter() {
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        CorsConfiguration config = new CorsConfiguration();

        config.setAllowedOrigins(List.of("*"));

        // 허용할 HTTP 메서드 지정
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));

        // 허용할 요청 헤더 지정
        config.setAllowedHeaders(List.of("Authorization", "Content-Type"));

        // 모든 경로에 대해 CORS 설정 적용
        source.registerCorsConfiguration("/**", config);
        return new CorsFilter(source);
    }
}
