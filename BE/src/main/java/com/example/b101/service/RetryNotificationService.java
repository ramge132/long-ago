package com.example.b101.service;

import com.example.b101.dto.RetryNotificationRequest;
import com.example.b101.common.ApiResponseUtil;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
public class RetryNotificationService {

    /**
     * AI 서버로부터 재시도 알림을 받아서 처리
     * 현재는 단순히 로깅만 하고 성공 응답을 반환
     * 향후 WebSocket이나 Server-Sent Events를 통해 실시간으로 프론트엔드에 전달할 수 있음
     */
    public ResponseEntity<?> handleRetryNotification(
            RetryNotificationRequest request,
            HttpServletRequest httpRequest
    ) {
        try {
            log.info("=== 재시도 알림 처리 시작 ===");
            log.info("메시지: {}", request.getMessage());
            log.info("진행 상황: {}/{} 재시도", request.getAttempt(), request.getMaxAttempts());
            log.info("타임스탬프: {}", request.getTimestamp());

            // 현재는 로깅만 수행
            // 향후 개선점:
            // 1. WebSocket을 통해 실시간으로 프론트엔드에 전달
            // 2. Redis에 임시 저장하여 프론트엔드가 폴링으로 확인
            // 3. Server-Sent Events (SSE) 활용

            // 응답 데이터 구성
            Map<String, Object> responseData = new HashMap<>();
            responseData.put("received", true);
            responseData.put("message", "재시도 알림 수신 완료");
            responseData.put("timestamp", System.currentTimeMillis());

            log.info("=== 재시도 알림 처리 완료 ===");

            return ApiResponseUtil.success(
                    responseData,
                    "재시도 알림이 성공적으로 처리되었습니다.",
                    HttpStatus.OK,
                    httpRequest.getRequestURI()
            );

        } catch (Exception e) {
            log.error("=== 재시도 알림 처리 중 오류 ===");
            log.error("오류 내용: {}", e.getMessage(), e);

            return ApiResponseUtil.failure(
                    "재시도 알림 처리 중 오류가 발생했습니다.",
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    httpRequest.getRequestURI()
            );
        }
    }
}