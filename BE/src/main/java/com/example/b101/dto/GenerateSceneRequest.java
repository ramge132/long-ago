package com.example.b101.dto;

import lombok.Builder;
import lombok.Data;

@Builder
@Data
//GPU 서버에 이미지 생성 요청을 위한 dto
public class GenerateSceneRequest {

    //작화 스타일
    String drawingStyle;

    //사용자 프롬포트
    String userPrompt;

}
