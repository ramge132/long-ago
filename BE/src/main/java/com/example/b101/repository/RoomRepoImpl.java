package com.example.b101.repository;

import com.example.b101.cache.Room;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.stream.Collectors;

@Repository
public class RoomRepoImpl implements RoomRepository {

    private static final String KEY = "Room"; // 키 값은 Room으로 고정

    private final RedisTemplate<String, Room> redisTemplate;

    public RoomRepoImpl(RedisTemplate<String, Room> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    @Override
    public void create(Room room) {
        redisTemplate.opsForHash().put(KEY, room.getId(), room);
    }

    @Override
    public Room findById(String id) {
        return (Room) redisTemplate.opsForHash().get(KEY, String.valueOf(id));
    }

    @Override
    public List<Room> findAll() {
        return redisTemplate.opsForHash().values(KEY)
                .stream()
                .map(obj -> (Room) obj)
                .collect(Collectors.toList());
    }

    @Override
    public void delete(String id) {
        redisTemplate.opsForHash().delete(KEY, id);
    }

    @Override
    public void put(Room room) {
        redisTemplate.opsForHash().put(KEY, room.getId(), room);
    }


}
