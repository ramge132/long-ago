package com.example.b101.dto;

import lombok.Data;

@Data
public class DeleteGameRequest {

    String gameId;
    boolean isForceStopped;
}
