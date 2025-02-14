package com.example.b101.repository;

import com.example.b101.cache.Game;
import com.example.b101.domain.PlayerStatus;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Repository;

import java.util.concurrent.TimeUnit;

@Repository
public class GameRepoImpl implements GameRepository {

    private static final String KEY = "game";

    private final RedisTemplate<String, Game> redisTemplate;

    public GameRepoImpl(RedisTemplate<String, Game> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    @Override
    public void save(Game game) {
        redisTemplate.opsForHash().put(KEY, game.getGameId(), game);

        // Key에 TTL 설정
        redisTemplate.expire(KEY, 30, TimeUnit.MINUTES );
    }

    @Override
    public void delete(Game game) {
        redisTemplate.opsForHash().delete(KEY, game.getGameId());
    }

    @Override
    public void update(Game game) {
        redisTemplate.opsForHash().put(KEY, game.getGameId(), game);
    }

    @Override
    public Game findById(String id) {
        return (Game) redisTemplate.opsForHash().get(KEY,id);
    }

    public PlayerStatus getPlayerStatus(String gameId, String playerId) {
        Game game = findById(gameId);

        return game.getPlayerStatuses().stream().filter(playerStatus -> playerStatus.getUserId().equals(playerId)).findFirst().orElse(null);
    }
}
