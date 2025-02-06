package com.example.b101.dto;

import com.example.b101.domain.PlayerStatus;
import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GameResponse {

    String gameId;

    PlayerStatus status;
}
