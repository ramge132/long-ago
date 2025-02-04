package com.example.b101.domain;

import lombok.*;

import java.util.List;

@AllArgsConstructor
@Builder
@Getter
@Setter
@NoArgsConstructor
//플레이어 상태 CLASS
public class PlayerStatus{

    String userId;

    List<StoryCard> storyCards;

    EndingCard endingCard;


}
