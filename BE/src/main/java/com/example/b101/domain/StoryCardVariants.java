package com.example.b101.domain;

import jakarta.persistence.*;
import lombok.*;


@Entity
@Getter
@Setter
@Table(name = "story_card_variants")
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class StoryCardVariants{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    @ManyToOne
    @JoinColumn(name = "story_card_id", nullable = false) // 외래 키 컬럼 이름 정의
    private StoryCard storyCard;

    @Column(nullable = false)
    private String variant;




}
