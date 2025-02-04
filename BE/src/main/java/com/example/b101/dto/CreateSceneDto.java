package com.example.b101.dto;

import lombok.Data;

@Data
public class CreateSceneDto {

    String gameId;

    String userId;

    String promptText;

    int cardId;
}
