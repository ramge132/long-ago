package com.example.b101.dto.room;

import lombok.Data;

@Data
public class CreateRoomDto {

    String id;
    String name;
    int maxCapacity;
    String password;
    String link;
    String ownerId;
}
