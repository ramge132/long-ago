package com.example.b101.repository;

import com.example.b101.cache.Game;
import com.example.b101.domain.PlayerStatus;

public interface GameRepository {

    void save(Game game);

    void delete(Game game);

    void update(Game game);

    Game findById(String gameId);

    PlayerStatus getPlayerStatus(String gameId,String playerId);

}
