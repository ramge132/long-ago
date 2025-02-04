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
@RedisHash(value = "Game", timeToLive = 3600) //TTL 1시간 설정
public class Game implements Serializable {

    @Id  // edis에서 Key 역할을 할 필드
    private String gameId;

    private List<EndingCard> endingCardlist;

    private List<PlayerStatus> playerStatuses;


}
