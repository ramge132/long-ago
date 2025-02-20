package com.example.b101.domain;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Data
public class StoryCard{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    @Column(nullable = false)
    private String keyword;

    @Column(nullable = false)
    private String attribute;
}
