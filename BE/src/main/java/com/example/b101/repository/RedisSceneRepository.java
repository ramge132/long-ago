package com.example.b101.repository;


import com.example.b101.cache.SceneRedis;

import java.util.List;

public interface RedisSceneRepository{

    void save(SceneRedis sceneRedis);

    void delete(SceneRedis sceneRedis);

    SceneRedis findById(String id);

    List<SceneRedis> findAllByGameId(String gameId);

    void deleteAllByGameId(String gameId);

}
