package com.example.b101.domain;

import jakarta.persistence.*;
import lombok.*;



@Entity
@Getter
@Setter
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
    private String imageUrl; //책 표지


    public Scene(int sceneOrder, String userPrompt, String imageUrl) {
        this.sceneOrder = sceneOrder;
        this.userPrompt = userPrompt;
        this.imageUrl = imageUrl;
    }
}
