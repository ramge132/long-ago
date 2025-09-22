package com.example.b101.dto;

import com.example.b101.domain.StoryCard;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class CardExchangeResponse {
    private String status;        // "success", "failed"
    private String message;       // 결과 메시지
    private StoryCard newCard;    // 교환받은 새로운 카드 (성공시)
    private int remainingExchangeCount; // 남은 교환 횟수
}