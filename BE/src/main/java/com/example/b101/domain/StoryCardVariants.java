package com.example.b101.domain;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

@Entity
@Data
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
