package com.example.b101.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.springframework.data.annotation.CreatedDate;

import java.time.LocalDateTime;

@Entity
@Getter
@Setter
public class Scene {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;


    @ManyToOne
    @JoinColumn(name = "BOOK_ID", nullable = false)
    private Book book;


    private int sceneOrder;

    @Column(columnDefinition = "TEXT")
    private String prompt;


    private String imageUrl;

    @ManyToOne
    @JoinColumn(name = "USER_ID")
    private User user;

    @CreatedDate
    private LocalDateTime createdAt;

}
