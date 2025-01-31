package com.example.b101.repository;

import com.example.b101.domain.Game;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class GameRepositoryImpl implements GameRepository {

    private static final String KEY = "game";

    private final RedisTemplate<String, Game> redisTemplate;

    public GameRepositoryImpl(RedisTemplate<String, Game> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    @Override
    public void save(Game game) {
        redisTemplate.opsForHash().put(KEY, game.getGameId(), game);
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
    public Game findById(int id) {
        return (Game) redisTemplate.opsForHash().get(KEY,id);
    }
}
