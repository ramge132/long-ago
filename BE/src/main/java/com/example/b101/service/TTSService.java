package com.example.b101.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class TTSService {

    private final WebClient.Builder webClientBuilder;
    private final ObjectMapper objectMapper;

    @Value("${gemini.api.key}")
    private String googleApiKey;

    private static final String GOOGLE_TTS_URL = "https://texttospeech.googleapis.com/v1beta1/text:synthesize";

    public byte[] synthesizeSpeech(String text) {
        try {
            // Google Cloud TTS API 요청 페이로드 구성 (v1beta1, Chirp3-HD)
            Map<String, Object> input = new HashMap<>();
            input.put("text", text);

            Map<String, Object> voice = new HashMap<>();
            voice.put("languageCode", "ko-KR");
            voice.put("name", "ko-KR-Chirp3-HD-Aoede"); // 고품질 Chirp3 HD 음성 (여성)

            Map<String, Object> audioConfig = new HashMap<>();
            audioConfig.put("audioEncoding", "MP3");
            audioConfig.put("pitch", 0);
            audioConfig.put("speakingRate", 0.8); // 말하기 속도

            Map<String, Object> payload = new HashMap<>();
            payload.put("input", input);
            payload.put("voice", voice);
            payload.put("audioConfig", audioConfig);

            // WebClient로 Google TTS API 호출
            WebClient webClient = webClientBuilder.build();
            
            String response = webClient.post()
                    .uri(GOOGLE_TTS_URL + "?key=" + googleApiKey)
                    .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                    .bodyValue(payload)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();

            // 응답에서 오디오 데이터 추출
            JsonNode jsonNode = objectMapper.readTree(response);
            String audioContent = jsonNode.get("audioContent").asText();
            
            // Base64 디코딩하여 바이트 배열 반환
            return Base64.getDecoder().decode(audioContent);

        } catch (Exception e) {
            log.error("Google TTS API 호출 실패: {}", e.getMessage(), e);
            throw new RuntimeException("TTS 생성 중 오류 발생", e);
        }
    }
}