package com.example.b101.repository;

import com.example.b101.cache.SceneRedis;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Repository;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Repository
public class RedisSceneRepoImpl implements RedisSceneRepository {

    private static final String KEY = "scene"; // Redis Hash Key

    private final RedisTemplate<String, SceneRedis> redisTemplate;

    public RedisSceneRepoImpl(RedisTemplate<String, SceneRedis> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    @Override
    public void save(SceneRedis sceneRedis) {
        String hashKey = String.format("%s:%s", sceneRedis.getGameId(), sceneRedis.getId());
        redisTemplate.opsForHash().put(KEY, hashKey, sceneRedis);

        redisTemplate.expire(KEY,30, TimeUnit.MINUTES);
    }

    //redis에 저장된 scene 정보 삭제
    @Override
    public void delete(SceneRedis sceneRedis) {
        String hashKey = String.format("%s:%s", sceneRedis.getGameId(), sceneRedis.getId());
        redisTemplate.opsForHash().delete(KEY, hashKey);
    }


    @Override
    public void deleteAllByGameId(String gameId) {
        // Redis Hash에서 모든 엔트리를 가져옴
        Map<Object, Object> entries = redisTemplate.opsForHash().entries(KEY);

        // 특정 gameId에 해당하는 모든 HashKey를 필터링합니다.
        List<Object> keysToDelete = entries.keySet().stream()
                .filter(hashKey -> hashKey.toString().startsWith(gameId + ":")) //startWith는 hashKey가 gameId: 로 시작하는 애들을 찾는다
                .toList();

        // 필터링된 HashKey들을 Redis에서 삭제합니다.
        for (Object hashKey : keysToDelete) {
            redisTemplate.opsForHash().delete(KEY, hashKey);
        }
    }



    @Override
    public SceneRedis findById(String id) {
        // Redis Hash에서 모든 엔트리를 가져옴
        Map<Object, Object> entries = redisTemplate.opsForHash().entries(KEY);

        // HashKey를 순회하여 ID가 일치하는 데이터 찾기
        for (Map.Entry<Object, Object> entry : entries.entrySet()) {
            String hashKey = entry.getKey().toString();
            if (hashKey.endsWith(":" + id)) {
                return (SceneRedis) entry.getValue();
            }
        }

        // 해당 ID가 없으면 null 반환
        return null;
    }

    @Override
    public List<SceneRedis> findAllByGameId(String gameId) {
        // Redis Hash에서 gameId가 같은 모든 데이터를 가져옴.
        // Redis Hash는 .entries에 반환값이 Map<Object, Object> 직렬화 과정에서 Object로 저장됨
        Map<Object, Object> entries = redisTemplate.opsForHash().entries(KEY);

        // 특정 gameId로 시작하는 모든 데이터를 sceneOrder순으로 정렬하여 반환
        return entries.entrySet().stream()
                .filter(entry -> entry.getKey().toString().startsWith(gameId + ":"))
                .map(entry -> (SceneRedis) entry.getValue())
                .sorted(Comparator.comparing(SceneRedis::getSceneOrder)) //sceneOrder 순으로 정렬
                .toList();
    }
}
