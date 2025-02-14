package com.example.b101.domain;

import jakarta.persistence.*;
import lombok.*;



@Entity
@Getter
@Setter
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class Scene {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    @ManyToOne
    @JoinColumn(name = "BOOK_ID", nullable = false)
    private Book book;

    @Column(name = "SCENE_ORDER",nullable = false)
    private int sceneOrder;

    @Column(name="PROMPT",columnDefinition = "TEXT")
    private String userPrompt;

    @Column(name="IMAGE_URL",nullable = false,length = 1000)
    private String imageUrl;

//    @ManyToOne
//    @JoinColumn(name = "USER_ID")
//    private User user;

}
