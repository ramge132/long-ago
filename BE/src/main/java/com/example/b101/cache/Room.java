package com.example.b101.cache;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.redis.core.RedisHash;

import java.io.Serializable;
import java.util.List;

@Builder
@Data
@NoArgsConstructor
@AllArgsConstructor
@RedisHash(value = "Room")
public class Room implements Serializable {

    @Id
    private String id;

    private String name;

    private List<String> users; //참가자들 sessionID

    private String owner; //방장 sessionID

    private int maxCapacity;

    private String password;

    private String link;

}
