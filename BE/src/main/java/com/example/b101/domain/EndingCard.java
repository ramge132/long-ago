package com.example.b101.domain;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Data
public class EndingCard {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    @Column(nullable = false)
    private String content;
}
