package com.example.b101.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RetryNotificationRequest {

    /**
     * 사용자에게 표시할 메시지
     * 예: "부적절한 이미지가 나왔어요!\n다시 그려볼게요!"
     */
    private String message;

    /**
     * 현재 재시도 번호 (1부터 시작)
     */
    private Integer attempt;

    /**
     * 최대 재시도 횟수
     */
    private Integer maxAttempts;

    /**
     * 알림 발생 시각 (밀리초 타임스탬프)
     */
    private Long timestamp;
}