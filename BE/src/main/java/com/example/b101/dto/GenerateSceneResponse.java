package com.example.b101.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

@Data
@AllArgsConstructor
@Builder
//GPU 서버에서 이미지 생성 후 반환 해주는 dto
public class GenerateSceneResponse {

    //이미지 데이터
    byte[] image;

    //요약된 스토리
    String storySummary;

    //이미지 생성 시 사용된 LLM이 생성한 프롬포트
    String imagePrompt;
}
