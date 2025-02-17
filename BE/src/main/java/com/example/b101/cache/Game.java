package com.example.b101.cache;

import com.example.b101.domain.EndingCard;
import com.example.b101.domain.PlayerStatus;
import lombok.*;
import org.springframework.data.annotation.Id;
import org.springframework.data.redis.core.RedisHash;

import java.io.Serializable;
import java.util.List;

@Builder
@Data
@NoArgsConstructor
@AllArgsConstructor
@RedisHash(value = "Game")
public class Game implements Serializable {

    @Id  // redis에서 Key 역할을 할 필드
    private String gameId;

    //게임에서 쓰이는 게임 개별 endingCardList
    private List<EndingCard> endingCardlist;

    //플에이어들의 게임데이터 정보
    private List<PlayerStatus> playerStatuses;

    //작화 스타일
    private int drawingStyle;




}
