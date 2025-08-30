package com.example.b101.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class TTSRequest {
    
    private String text;
    private String voiceType; // 음성 타입 (선택사항)
    private String languageCode; // 언어 코드 (기본값: ko-KR)
}