package com.example.b101.dto;

import lombok.Data;

@Data
public class DeleteSceneRequest {

    String gameId;

    String userId;

    boolean isAccepted;

    int cardId;


}
