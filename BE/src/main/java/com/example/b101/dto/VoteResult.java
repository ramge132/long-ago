package com.example.b101.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class VoteResult {

    private boolean accepted;
    private String userId;
    private int scoreChange;
    private boolean isEnding;
    private String message;

}