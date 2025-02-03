package com.example.b101.domain;

import lombok.*;
import org.springframework.data.redis.core.RedisHash;
import org.springframework.data.redis.core.TimeToLive;

import java.io.Serializable;
import java.util.List;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@RedisHash("Game") // Redis keyspace 이름을 정의
public class Game implements Serializable {

    private String gameId; // Redis 키로 사용할 필드

    private List<EndingCard> endingCardlist;

    private List<PlayerStatus> playerStatuses;

    private int tension;

    private List<Scene> scenes;

    @TimeToLive // TTL을 설정할 필드
    private Long ttl; // TTL 값 (초 단위)
}
