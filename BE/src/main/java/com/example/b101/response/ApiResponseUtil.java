package com.example.b101.response;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.time.LocalDateTime;

public class ApiResponseUtil {

    // 성공 응답
    public static <T> ResponseEntity<ApiResponse<T>> success(T data, String message, HttpStatus status,String path) {
        ApiResponse<T> response = ApiResponse.<T>builder()
                .success(true)
                .status(status.value())
                .message(message)
                .data(data)
                .timestamp(LocalDateTime.now().toString())
                .path(path)
                .build();

        return ResponseEntity.status(status).body(response);
    }

    // 실패 응답
    public static <T> ResponseEntity<ApiResponse<T>> failure(String message, HttpStatus status, String path) {
        ApiResponse<T> response = ApiResponse.<T>builder()
                .success(false)
                .status(status.value())
                .message(message)
                .data(null)
                .timestamp(LocalDateTime.now().toString())
                .path(path)
                .build();

        return ResponseEntity.status(status).body(response);
    }
}
