package com.example.b101.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

@Builder
@Data
@AllArgsConstructor
public class FilteringRequest {

    private String userId;
    private String gameId;
    private String userPrompt;
}
