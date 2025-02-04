package com.example.b101.cache;

import lombok.*;
import org.springframework.data.redis.core.RedisHash;
import org.springframework.data.annotation.Id;
import java.io.Serializable;

@Getter
@Setter
@Builder
@AllArgsConstructor
@NoArgsConstructor
@RedisHash(value = "scene", timeToLive = 3600) // TTL 1시간 설정
/**
 *  Scene은 투표로 반대가 나오면 영구적으로 저장할 필요도 없고
 *  실시간으로 보여줄 때도 인메모리 방식인 redis가 속도가 빠르기 때문에
 *  실시간 게임중에는 redis에서 scene을 관리하고
 *  게임이 끝난 뒤에는 db에 scene을 저장함.
 */
public class SceneRedis implements Serializable {

    @Id
    private String id;

    private String gameId;
    private int sceneOrder;
    private String prompt;
    private String imageUrl;
    private String userId;
}
