package com.example.b101.dto;

import lombok.Data;

import java.util.List;

@Data
public class GameRequest {

    String bossId;
    int drawingStyle;
    List<String> player;
}
