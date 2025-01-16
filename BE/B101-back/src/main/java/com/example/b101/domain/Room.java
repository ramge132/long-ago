package com.example.b101.domain;


import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.springframework.data.annotation.CreatedDate;

import java.time.LocalDateTime;

@Entity
@Getter
@Setter
public class Room {

    @Id
    @GeneratedValue
    @Column(name="ROOM_ID")
    private int id;

    private String name;

    private int capacity;

    private int maxCapacity;

    @Enumerated(EnumType.STRING)
    private RoomStatus roomStatus;

    private String roomPassword;

    private String roomLink;

    @CreatedDate
    private LocalDateTime createdAt;


}
