package com.example.b101.dto;

import lombok.Data;

@Data
public class CardExchangeRequest {
    private String gameId;
    private String fromUserId;    // 교환 신청자
    private String toUserId;      // 교환 대상자
    private int fromCardId;       // 신청자가 제공할 카드 ID
    private int toCardId;         // 대상자가 제공할 카드 ID (응답시 설정)
    private String status;        // "pending", "accepted", "rejected"
}