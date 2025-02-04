package com.example.b101.dto;

import lombok.Data;
import lombok.Getter;

import java.util.List;

@Data
public class CreateGame {

    String bossId;
    List<String> player;
}
