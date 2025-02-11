package com.example.b101.dto;

import lombok.Builder;
import lombok.Data;

@Builder
@Data
//GPU 서버에 이미지 생성 요청을 위한 dto
public class GenerateSceneRequest {

    //게임 아이디
    String session_id;

    //작화 스타일
    int game_mode;

    //사용자 프롬포트
    String user_sentence;

    // 0 : 진행 중 -> 삽화 생성
    // 1 : 종료 -> 표지 생성
    // 2 : 전원 패배 -> 생성 안함
    int status;

}
