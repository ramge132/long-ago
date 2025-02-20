package com.example.b101.cache;

import lombok.*;
import java.io.Serializable;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
/**
 *  Scene은 투표로 반대가 나오면 영구적으로 저장할 필요도 없고
 *  실시간으로 보여줄 때도 인메모리 방식인 redis가 속도가 빠르기 때문에
 *  실시간 게임중에는 redis에서 scene을 관리하고
 *  게임이 끝난 뒤에는 db에 scene을 저장함.
 */
public class SceneRedis implements Serializable {

    private String id; //sceneId (같은 게임 안에서 scene들을 구분하기 위함.)

    private String gameId; //이 scene을 생성한 gameId

    private String userId; //scene을 생성한 userId

    private int sceneOrder; //scene의 순서

    private String prompt; //사용자가 생성한 프롬포트

    private byte[] image; //바이너리 형태로 저장된 이미지

}
