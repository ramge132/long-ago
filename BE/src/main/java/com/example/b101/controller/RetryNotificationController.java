package com.example.b101.controller;

import com.example.b101.dto.RetryNotificationRequest;
import com.example.b101.service.RetryNotificationService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api")
public class RetryNotificationController {

    private final RetryNotificationService retryNotificationService;

    /**
     * AI 서버로부터 재시도 알림을 받아서 프론트엔드로 전달
     */
    @PostMapping("/retry-notification")
    public ResponseEntity<?> handleRetryNotification(
            @RequestBody RetryNotificationRequest request,
            HttpServletRequest httpRequest
    ) {
        log.info("=== AI 서버로부터 재시도 알림 수신 ===");
        log.info("메시지: {}", request.getMessage());
        log.info("재시도 횟수: {}/{}", request.getAttempt(), request.getMaxAttempts());

        return retryNotificationService.handleRetryNotification(request, httpRequest);
    }
}