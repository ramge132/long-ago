package com.example.b101.domain;

import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

import java.io.Serializable;
import java.util.List;

@Getter
@Setter
@Builder
public class Game implements Serializable {

    String gameId;

    List<EndingCard> endingCardlist;

    List<PlayerStatus> playerStatuses;

    int tension;

    List<Scene> scenes;

}
