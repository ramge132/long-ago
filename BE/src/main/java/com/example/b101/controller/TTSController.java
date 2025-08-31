package com.example.b101.controller;

import com.example.b101.dto.TTSRequest;
import com.example.b101.service.TTSService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/tts")
public class TTSController {

    private final TTSService ttsService;

    @PostMapping("/synthesize")
    public ResponseEntity<byte[]> synthesizeSpeech(@RequestBody TTSRequest ttsRequest) {
        try {
            log.info("TTS 요청 받음: {}", ttsRequest.getText());
            
            // 임시: TTS 서비스를 비활성화하고 빈 오디오 데이터 반환
            log.warn("TTS 서비스 임시 비활성화 - 빈 오디오 데이터 반환");
            byte[] emptyAudioData = new byte[0];
            
            return ResponseEntity.ok()
                    .contentType(MediaType.valueOf("audio/mpeg"))
                    .body(emptyAudioData);
                    
        } catch (Exception e) {
            log.error("TTS 생성 실패", e);
            return ResponseEntity.internalServerError().build();
        }
    }
}