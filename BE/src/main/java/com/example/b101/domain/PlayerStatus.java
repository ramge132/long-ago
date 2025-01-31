package com.example.b101.domain;

import lombok.*;

import java.util.List;

@AllArgsConstructor
@Builder
@Getter
public class PlayerStatus{

    String userId;

    List<StoryCard> storyCards;

    int life;

    int score;

    EndingCard endingCard;
}
