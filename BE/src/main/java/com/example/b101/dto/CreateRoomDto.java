package com.example.b101.dto;

import lombok.Data;

@Data
public class CreateRoomDto {

    String name;
    int maxCapacity;
    String password;
    String link;
    String ownerId;
}
