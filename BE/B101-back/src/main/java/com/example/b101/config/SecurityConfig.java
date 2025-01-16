package com.example.b101.config;

import com.example.b101.dto.CustomUserDetails;
import com.example.b101.response.ApiResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

import java.util.Map;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final ObjectMapper objectMapper = new ObjectMapper(); // JSON 변환을 위한 ObjectMapper

    @Bean
    public BCryptPasswordEncoder bCryptPasswordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {

        http
                .authorizeHttpRequests((auth) -> auth
                        .requestMatchers("/", "/api/user/**", "/swagger-ui/**", "/v3/api-docs/**").permitAll() // Swagger 허용
                        .anyRequest().authenticated()
                )
                .formLogin()
                .loginProcessingUrl("/api/user/login") // 로그인 처리 URL
                .successHandler((request, response, authentication) -> {
                    response.setContentType("application/json");
                    response.setCharacterEncoding("UTF-8");

                    // 인증된 사용자 정보 가져오기
                    CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();

                    // ApiResponse 객체 생성
                    ApiResponse<?> apiResponse = ApiResponse.builder()
                            .success(true)
                            .status(HttpServletResponse.SC_OK)
                            .message("로그인 성공")
                            .data(Map.of("nickname", userDetails.getNickname()))
                            .timestamp(java.time.LocalDateTime.now().toString())
                            .path(request.getRequestURI()) // 요청 경로 추가
                            .build();

                    // JSON 응답 작성
                    response.getWriter().write(objectMapper.writeValueAsString(apiResponse));
                })
                .failureHandler((request, response, exception) -> {
                    response.setContentType("application/json");
                    response.setCharacterEncoding("UTF-8");
                    response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);

                    // ApiResponse 객체 생성
                    ApiResponse<?> apiResponse = ApiResponse.builder()
                            .success(false)
                            .status(HttpServletResponse.SC_UNAUTHORIZED)
                            .message("로그인 실패: " + exception.getMessage())
                            .data(null)
                            .timestamp(java.time.LocalDateTime.now().toString())
                            .path(request.getRequestURI()) // 요청 경로 추가
                            .build();

                    // JSON 응답 작성
                    response.getWriter().write(objectMapper.writeValueAsString(apiResponse));
                });

        http.csrf().disable(); // REST API에서 CSRF 비활성화

        return http.build();
    }
}
