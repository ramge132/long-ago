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
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

import java.io.IOException;
import java.util.Map;
import java.util.Optional;

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
                        .anyRequest().permitAll()
                )
                .formLogin(form -> form
                        .loginProcessingUrl("/api/user/login") // 로그인 처리 URL
                        .successHandler(this::onLoginSuccess)  // 로그인 성공 시 처리할 메서드
                        .failureHandler(this::onLoginFailure)  // 로그인 실패 시 처리할 메서드
                )
                .csrf(csrf -> csrf.disable());

        return http.build();
    }

    // 로그인 성공 시 처리할 메서드
    public void onLoginSuccess(HttpServletRequest request, HttpServletResponse response, Authentication authentication) throws IOException {
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");

        // 인증된 사용자 정보 가져오기
        CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();

        // ApiResponse 객체 생성
        ApiResponse<?> apiResponse = ApiResponse.builder()
                .success(true)
                .status(HttpServletResponse.SC_OK)
                .message("로그인 성공")
                .data(Map.of("nickname", Optional.ofNullable(userDetails.getNickname()).orElse("익명 사용자")))
                .timestamp(java.time.LocalDateTime.now().toString())
                .path(request.getRequestURI()) // 요청 경로 추가
                .build();

        // JSON 응답 작성
        response.getWriter().write(objectMapper.writeValueAsString(apiResponse));
    }

    // 로그인 실패 시 처리할 메서드
    public void onLoginFailure(HttpServletRequest request, HttpServletResponse response, Exception exception) throws IOException {
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
    }
}
