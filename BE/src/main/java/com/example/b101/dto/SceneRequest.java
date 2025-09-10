package com.example.b101.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
//사용자가 scene을 만들 때 필요한 requestBody
public class SceneRequest {

    String gameId;

    String userId;

    String userPrompt;

    int turn;
    
    Boolean isEnding;  // boolean을 Boolean으로 변경하여 Jackson 역직렬화 문제 해결
}
