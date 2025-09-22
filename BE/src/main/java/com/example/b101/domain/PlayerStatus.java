package com.example.b101.domain;

import lombok.*;

import java.util.List;

@AllArgsConstructor
@Builder
@Getter
@Setter
@ToString
@NoArgsConstructor
//플레이어 상태 CLASS
public class PlayerStatus{

    String userId;

    List<StoryCard> storyCards;

    EndingCard endingCard;

    // 이야기카드 새로고침 횟수 (기본값 3)
    @Builder.Default
    int refreshCount = 3;

    // 이야기카드 교환 횟수 (기본값 3)
    @Builder.Default
    int exchangeCount = 3;


}
