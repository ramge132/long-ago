package com.example.b101.service;

import com.example.b101.cache.Game;
import com.example.b101.cache.SceneRedis;
import com.example.b101.common.ApiResponseUtil;
import com.example.b101.config.WebClientConfig;
import com.example.b101.domain.PlayerStatus;
import com.example.b101.dto.DeleteSceneRequest;
import com.example.b101.dto.GenerateSceneRequest;
import com.example.b101.dto.SceneRequest;
import com.example.b101.repository.GameRepository;
import com.example.b101.repository.RedisSceneRepository;
import com.example.b101.repository.StoryCardRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientException;

import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Slf4j
@Service
@AllArgsConstructor
public class SceneService {

    private final RedisSceneRepository redisSceneRepository;
    private final GameRepository gameRepository;
    @Qualifier("runpodWebClient")
    private final WebClient runpodWebClient;
    @Qualifier("webClient")
    private final WebClient webClient;
    @Qualifier("openaiWebClient")
    private final WebClient openaiWebClient;
    @Qualifier("geminiWebClient")
    private final WebClient geminiWebClient;
    private final StoryCardRepository storyCardRepository;
    private final WebClientConfig webClientConfig;
    private final ObjectMapper objectMapper = new ObjectMapper();


    public ResponseEntity<?> createScene(SceneRequest sceneRequest, HttpServletRequest request) {
        log.info("=== 이미지 생성 요청 시작 ===");
        log.info("게임ID: {}, 사용자ID: {}, 턴: {}", sceneRequest.getGameId(), sceneRequest.getUserId(), sceneRequest.getTurn());
        log.info("사용자 입력: [{}] (길이: {}자)", sceneRequest.getUserPrompt(), sceneRequest.getUserPrompt().length());

        // 게임 데이터 조회 및 유효성 검사
        Game game = gameRepository.findById(sceneRequest.getGameId());
        if (game == null) {
            log.error("존재하지 않는 게임ID: {}", sceneRequest.getGameId());
            return ApiResponseUtil.failure("존재하지 않는 gameId입니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        boolean userExists = game.getPlayerStatuses()
                .stream()
                .anyMatch(playerStatus -> playerStatus.getUserId().equals(sceneRequest.getUserId()));
        if (!userExists) {
            log.error("게임 {}에 존재하지 않는 사용자ID: {}", sceneRequest.getGameId(), sceneRequest.getUserId());
            return ApiResponseUtil.failure("해당 게임에 존재하지 않는 userId입니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        log.info("게임 유효성 검사 통과. 그림체 모드: {}", game.getDrawingStyle());

        // 새로운 API 시스템: OpenAI GPT + Gemini
        byte[] generateImage = null;
        try {
            // 결말카드인지 확인 (턴이 높고 결말카드 내용으로 추정)
            boolean isEndingCard = sceneRequest.getTurn() > 5 && 
                    (sceneRequest.getUserPrompt().contains("결말") || 
                     sceneRequest.getUserPrompt().contains("끝") ||
                     sceneRequest.getUserPrompt().length() > 30); // 결말카드는 보통 길다
            
            log.info("=== 결말카드 탐지 결과 ===");
            log.info("턴 > 5: {}, '결말' 포함: {}, '끝' 포함: {}, 길이 > 30: {}", 
                    sceneRequest.getTurn() > 5,
                    sceneRequest.getUserPrompt().contains("결말"),
                    sceneRequest.getUserPrompt().contains("끝"),
                    sceneRequest.getUserPrompt().length() > 30);
            log.info("최종 판정: {} 카드", isEndingCard ? "결말" : "일반");
            
            String enhancedPrompt;
            if (isEndingCard) {
                log.info("=== 결말카드 GPT 프롬프트 생성 시작 ===");
                enhancedPrompt = generateEndingPromptWithGPT(sceneRequest.getUserPrompt(), game.getDrawingStyle());
                log.info("결말카드용 GPT 프롬프트 생성 완료: [{}]", enhancedPrompt);
            } else {
                log.info("=== 일반카드 GPT 프롬프트 생성 시작 ===");
                enhancedPrompt = generatePromptWithGPT(sceneRequest.getUserPrompt(), game.getDrawingStyle());
                log.info("일반카드용 GPT 프롬프트 생성 완료: [{}]", enhancedPrompt);
            }
            
            // 2단계: Gemini로 이미지 생성
            log.info("=== Gemini 이미지 생성 시작 ===");
            generateImage = generateImageWithGemini(enhancedPrompt);
            log.info("=== Gemini 이미지 생성 성공 ===");
            log.info("생성된 이미지 크기: {} bytes", generateImage.length);
            
        } catch (WebClientException e) {
            log.error("=== API 서버 통신 에러 ===");
            log.error("WebClientException 발생: {}", e.getMessage());
            log.error("에러 상세:", e);
            return ApiResponseUtil.failure("이미지 생성 API 통신 중 오류 발생: " + e.getMessage(),
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        } catch (RuntimeException e) {
            log.error("=== Runtime 에러 ===");
            log.error("RuntimeException 발생: {}", e.getMessage());
            log.error("에러 상세:", e);
            return ApiResponseUtil.failure("이미지 생성 중 런타임 오류 발생: " + e.getMessage(),
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        } catch (Exception e) {
            log.error("=== 일반 에러 ===");
            log.error("Exception 발생: {}", e.getMessage());
            log.error("에러 상세:", e);
            return ApiResponseUtil.failure("이미지 생성 중 오류 발생: " + e.getMessage(),
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        }

        if (generateImage == null || generateImage.length == 0) {
            log.error("=== 이미지 생성 실패 ===");
            log.error("생성된 이미지가 null이거나 크기가 0입니다. generateImage: {}", 
                    generateImage == null ? "null" : "empty(" + generateImage.length + " bytes)");
            return ApiResponseUtil.failure("이미지 받기 실패",
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        }

        log.info("=== Redis 저장 시작 ===");

        // Redis 등 저장소에 이미지 데이터와 함께 Scene 정보 저장
        String id = UUID.randomUUID().toString();
        SceneRedis scene = SceneRedis.builder()
                .id(id)
                .gameId(sceneRequest.getGameId())
                .prompt(sceneRequest.getUserPrompt())
                .image(generateImage)  // 바이너리 이미지 데이터 저장
                .sceneOrder(sceneRequest.getTurn())
                .userId(sceneRequest.getUserId())
                .build();

        redisSceneRepository.save(scene);

        log.info("Redis에 저장된 scene 개수 : {}", redisSceneRepository.findAllByGameId(sceneRequest.getGameId()).size());
        log.info("새로운 API에서 생성된 이미지 크기 : {}", generateImage.length);
        log.info("Redis에 저장된 이미지 크기 : {}", redisSceneRepository.findById(id).getImage().length);

        // 이미지 바이너리 데이터를 PNG 미디어 타입으로 반환
        return ResponseEntity.status(HttpStatus.CREATED)
                .contentType(MediaType.IMAGE_PNG)
                .body(generateImage);
    }


    public ResponseEntity<?> deleteScene(DeleteSceneRequest deleteSceneRequest, HttpServletRequest request) {
        log.info("투표 요청 왔습니다.");
        List<SceneRedis> scenes = redisSceneRepository.findAllByGameId(deleteSceneRequest.getGameId());
        if(scenes.isEmpty()) {
            log.error("저장된 scene이 없습니다.");
            return ApiResponseUtil.failure("아직 저장된 scene이 없습니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        log.info("투표 결과 : {}",deleteSceneRequest.isAccepted());
        if(!deleteSceneRequest.isAccepted()){
            log.info("투표 결과 반대");
            //scene 데이터 삭제
            SceneRedis lastScene = scenes.get(scenes.size() - 1);
            redisSceneRepository.delete(lastScene);

            // 새로운 API 시스템에서는 삭제 알림이 필요하지 않음
            log.info("장면 삭제됨 - 새로운 API 시스템에서는 별도 알림 불필요");

            return ApiResponseUtil.success(lastScene, "투표 결과에 따라 삭제됨", HttpStatus.OK, request.getRequestURI());
        }

        //사용한 카드 삭제해야함
        PlayerStatus playerStatus = gameRepository.getPlayerStatus(deleteSceneRequest.getGameId(), deleteSceneRequest.getUserId());

        storyCardRepository.findById(deleteSceneRequest.getCardId())
                .ifPresent(playerStatus.getStoryCards()::remove);

        Game game = gameRepository.findById(deleteSceneRequest.getGameId());
        
        game.getPlayerStatuses().stream()
                .filter(ps -> ps.getUserId().equals(playerStatus.getUserId()))
                .findFirst()
                .ifPresent(ps -> ps.setStoryCards(playerStatus.getStoryCards()));

        gameRepository.update(game);
        
        log.info("투표 결과 찬성");

        return ApiResponseUtil.failure("투표 결과 찬성으로 삭제되지 않음",HttpStatus.CONFLICT,request.getRequestURI());
    }


    public ResponseEntity<?> deleteSceneTest(DeleteSceneRequest deleteSceneRequest, HttpServletRequest request) {

        log.info("시연용 장면 삭제");
        if(!deleteSceneRequest.isAccepted()){
            log.info("투표 반대가 나오면 카드 사용 취소");
            return ApiResponseUtil.success(null, "투표 결과에 따라 삭제됨", HttpStatus.OK, request.getRequestURI());
        }

        log.info("투표 찬성이 나오면 카드 사용됨");
        //사용한 카드 삭제해야함
        PlayerStatus playerStatus = gameRepository.getPlayerStatus(deleteSceneRequest.getGameId(), deleteSceneRequest.getUserId());

        storyCardRepository.findById(deleteSceneRequest.getCardId())
                .ifPresent(playerStatus.getStoryCards()::remove);

        Game game = gameRepository.findById(deleteSceneRequest.getGameId());

        game.getPlayerStatuses().stream()
                .filter(ps -> ps.getUserId().equals(playerStatus.getUserId()))
                .findFirst()
                .ifPresent(ps -> ps.setStoryCards(playerStatus.getStoryCards()));

        gameRepository.update(game);

        return ApiResponseUtil.failure("투표 결과 찬성으로 삭제되지 않음",HttpStatus.CONFLICT,request.getRequestURI());
    }

    /**
     * OpenAI GPT를 사용하여 프롬프트 생성
     */
    private String generatePromptWithGPT(String userSentence, int gameMode) {
        log.info("=== 일반카드 GPT API 호출 시작 ===");
        log.info("입력 문장: [{}], 게임모드: {}", userSentence, gameMode);
        
        try {
            // 그림체 모드에 따른 스타일 정의
            String[] styles = {
                "애니메이션 스타일", "3D 카툰 스타일", "코믹 스트립 스타일", "클레이메이션 스타일",
                "크레용 드로잉 스타일", "픽셀 아트 스타일", "미니멀리스트 일러스트", "수채화 스타일", "스토리북 일러스트"
            };
            
            String style = gameMode < styles.length ? styles[gameMode] : "애니메이션 스타일";
            log.info("선택된 스타일: {}", style);
            
            // OpenAI GPT API 요청 구조
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("model", "gpt-5-nano");
            requestBody.put("max_tokens", 200);
            requestBody.put("temperature", 0.7);
            
            // 메시지 구조
            Map<String, Object> systemMessage = new HashMap<>();
            systemMessage.put("role", "system");
            systemMessage.put("content", "당신은 이미지 생성을 위한 프롬프트를 만드는 전문가입니다. 사용자의 한국어 문장을 받아서 " + style + " 스타일의 이미지 생성에 적합한 영어 프롬프트로 변환해주세요. 간결하고 명확하게 작성해주세요.");
            
            Map<String, Object> userMessage = new HashMap<>();
            userMessage.put("role", "user");
            userMessage.put("content", "다음 한국어 문장을 " + style + " 스타일의 이미지 생성 프롬프트로 변환해주세요: " + userSentence);
            
            requestBody.put("messages", List.of(systemMessage, userMessage));
            
            log.info("OpenAI API 요청 전송 중... (model: gpt-5-nano, temperature: 0.7)");
            
            // OpenAI API 호출
            String response = openaiWebClient.post()
                    .uri("https://api.openai.com/v1/chat/completions")
                    .bodyValue(requestBody)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();
            
            log.info("OpenAI API 응답 수신: {}", response != null ? "응답 있음" : "응답 없음");
            
            // 응답 파싱
            JsonNode responseJson = objectMapper.readTree(response);
            log.info("응답 JSON 구조: {}", responseJson.toString());
            
            if (responseJson.has("choices") && responseJson.get("choices").size() > 0) {
                String generatedPrompt = responseJson.get("choices").get(0).get("message").get("content").asText().trim();
                log.info("=== 일반카드 GPT API 성공 ===");
                log.info("생성된 프롬프트: [{}]", generatedPrompt);
                return generatedPrompt;
            }
            
            log.warn("=== 일반카드 GPT API 응답 파싱 실패 ===");
            log.warn("choices 필드가 없거나 비어있음. 원본 문장 반환: [{}]", userSentence);
            return userSentence;
            
        } catch (Exception e) {
            log.error("=== 일반카드 GPT API 호출 실패 ===");
            log.error("GPT API 호출 중 예외 발생: {}", e.getMessage());
            log.error("상세 에러:", e);
            log.info("원본 문장으로 대체: [{}]", userSentence);
            return userSentence; // 실패시 원본 문장 반환
        }
    }
    
    /**
     * 결말카드 전용 OpenAI GPT 프롬프트 생성
     */
    private String generateEndingPromptWithGPT(String endingCardContent, int gameMode) {
        log.info("=== 결말카드 GPT API 호출 시작 ===");
        log.info("결말카드 내용: [{}], 게임모드: {}", endingCardContent, gameMode);
        
        try {
            // 그림체 모드에 따른 스타일 정의
            String[] styles = {
                "애니메이션 스타일", "3D 카툰 스타일", "코믹 스트립 스타일", "클레이메이션 스타일",
                "크레용 드로잉 스타일", "픽셀 아트 스타일", "미니멀리스트 일러스트", "수채화 스타일", "스토리북 일러스트"
            };
            
            String style = gameMode < styles.length ? styles[gameMode] : "애니메이션 스타일";
            log.info("선택된 스타일: {}", style);
            
            // OpenAI GPT API 요청 구조
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("model", "gpt-5-nano");
            requestBody.put("max_tokens", 200);
            requestBody.put("temperature", 0.8); // 결말은 더 창의적으로
            
            log.warn("⚠️ 결말카드는 높은 temperature(0.8) 사용 - API 불안정성 증가 가능");
            
            // 메시지 구조
            Map<String, Object> systemMessage = new HashMap<>();
            systemMessage.put("role", "system");
            String systemContent = "당신은 스토리의 결말 장면을 위한 이미지 생성 프롬프트를 만드는 전문가입니다. 결말카드의 내용을 바탕으로 " + style + " 스타일의 감동적이고 인상적인 결말 장면 이미지 생성에 적합한 영어 프롬프트로 변환해주세요. 결말의 드라마틱한 느낌을 강조해주세요.";
            systemMessage.put("content", systemContent);
            
            Map<String, Object> userMessage = new HashMap<>();
            userMessage.put("role", "user");
            String userContent = "다음 결말카드 내용을 " + style + " 스타일의 감동적인 결말 장면 이미지 생성 프롬프트로 변환해주세요: " + endingCardContent;
            userMessage.put("content", userContent);
            
            requestBody.put("messages", List.of(systemMessage, userMessage));
            
            log.info("시스템 메시지 길이: {} 글자", systemContent.length());
            log.info("사용자 메시지 길이: {} 글자", userContent.length());
            log.info("OpenAI API 요청 전송 중... (model: gpt-5-nano, temperature: 0.8)");
            
            // OpenAI API 호출
            String response = openaiWebClient.post()
                    .uri("https://api.openai.com/v1/chat/completions")
                    .bodyValue(requestBody)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();
            
            log.info("OpenAI API 응답 수신: {}", response != null ? "응답 있음" : "응답 없음");
            
            // 응답 파싱
            JsonNode responseJson = objectMapper.readTree(response);
            log.info("응답 JSON 구조: {}", responseJson.toString());
            
            if (responseJson.has("choices") && responseJson.get("choices").size() > 0) {
                String generatedPrompt = responseJson.get("choices").get(0).get("message").get("content").asText().trim();
                log.info("=== 결말카드 GPT API 성공 ===");
                log.info("생성된 프롬프트: [{}]", generatedPrompt);
                return generatedPrompt;
            }
            
            log.warn("=== 결말카드 GPT API 응답 파싱 실패 ===");
            log.warn("choices 필드가 없거나 비어있음. 원본 내용 반환: [{}]", endingCardContent);
            return endingCardContent;
            
        } catch (Exception e) {
            log.error("=== 결말카드 GPT API 호출 실패 ===");
            log.error("결말 GPT API 호출 중 예외 발생: {}", e.getMessage());
            log.error("상세 에러:", e);
            log.info("원본 결말카드 내용으로 대체: [{}]", endingCardContent);
            return endingCardContent; // 실패시 원본 결말카드 내용 반환
        }
    }
    
    /**
     * Gemini 2.5 Flash Image Preview를 사용하여 이미지 생성
     */
    private byte[] generateImageWithGemini(String prompt) {
        log.info("=== Gemini 2.5 Flash Image Preview API 호출 시작 ===");
        log.info("입력 프롬프트: [{}] (길이: {}자)", prompt, prompt.length());
        
        try {
            // Gemini 2.5 Flash Image Preview API 요청 구조
            Map<String, Object> requestBody = new HashMap<>();
            
            // contents 배열 구성
            Map<String, Object> content = new HashMap<>();
            Map<String, Object> part = new HashMap<>();
            String fullPrompt = "Generate an image: " + prompt + " portrait orientation, 9:16 aspect ratio, vertical format, 720x1280 resolution";
            part.put("text", fullPrompt);
            content.put("parts", List.of(part));
            requestBody.put("contents", List.of(content));
            
            log.info("Gemini API 전송 프롬프트: [{}] (길이: {}자)", fullPrompt, fullPrompt.length());
            
            // Gemini 2.5 Flash Image Preview API 호출
            String apiUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key=" + webClientConfig.getGeminiApiKey();
            
            log.info("Gemini API URL: {}", apiUrl.substring(0, apiUrl.lastIndexOf("key=") + 4) + "***");
            log.info("Gemini API 요청 전송 중...");
            
            String response = geminiWebClient.post()
                    .uri(apiUrl)
                    .bodyValue(requestBody)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();
            
            log.info("=== Gemini API 응답 수신 ===");
            log.info("응답 상태: {}", response != null ? "응답 있음" : "응답 없음");
            
            if (response == null) {
                log.error("Gemini API에서 null 응답 수신");
                throw new RuntimeException("Gemini API null 응답");
            }
            
            // 응답 파싱
            JsonNode responseJson = objectMapper.readTree(response);
            log.info("=== Gemini API 응답 JSON 분석 ===");
            log.info("전체 응답 JSON: {}", responseJson.toString());
            
            // candidates 확인
            if (!responseJson.has("candidates")) {
                log.error("❌ CRITICAL: Gemini API 응답에 'candidates' 필드 없음!");
                log.error("사용 가능한 필드들: {}", responseJson.fieldNames());
                
                // 에러 정보 확인
                if (responseJson.has("error")) {
                    log.error("Gemini API 에러: {}", responseJson.get("error").toString());
                }
                
                throw new RuntimeException("Gemini API candidates 필드 누락");
            }
            
            JsonNode candidates = responseJson.get("candidates");
            if (candidates.size() == 0) {
                log.error("❌ CRITICAL: candidates 배열이 비어있음!");
                throw new RuntimeException("Gemini API candidates 배열 비어있음");
            }
            
            log.info("candidates 개수: {}", candidates.size());
            JsonNode candidate = candidates.get(0);
            log.info("첫 번째 candidate: {}", candidate.toString());
            
            // content 및 parts 확인
            if (!candidate.has("content")) {
                log.error("❌ candidate에 'content' 필드 없음!");
                throw new RuntimeException("Gemini API candidate content 누락");
            }
            
            JsonNode candidateContent = candidate.get("content");
            if (!candidateContent.has("parts")) {
                log.error("❌ content에 'parts' 필드 없음!");
                log.error("content 구조: {}", candidateContent.toString());
                throw new RuntimeException("Gemini API content parts 누락");
            }
            
            JsonNode parts = candidateContent.get("parts");
            log.info("parts 개수: {}", parts.size());
            
            // 각 part 검사
            for (int i = 0; i < parts.size(); i++) {
                JsonNode currentPart = parts.get(i);
                log.info("=== Part {} 분석 ===", i);
                log.info("Part {} 구조: {}", i, currentPart.toString());
                
                // inlineData 방식 확인
                if (currentPart.has("inlineData")) {
                    JsonNode inlineData = currentPart.get("inlineData");
                    log.info("inlineData 발견: {}", inlineData.toString());
                    
                    if (inlineData.has("data")) {
                        String base64Data = inlineData.get("data").asText();
                        log.info("✅ SUCCESS: Base64 이미지 데이터 발견!");
                        log.info("Base64 데이터 길이: {} 글자", base64Data.length());
                        log.info("Base64 데이터 미리보기: {}...", base64Data.substring(0, Math.min(50, base64Data.length())));
                        
                        byte[] imageBytes = Base64.getDecoder().decode(base64Data);
                        log.info("=== Gemini API 성공 ===");
                        log.info("최종 이미지 크기: {} bytes", imageBytes.length);
                        return imageBytes;
                    } else {
                        log.warn("inlineData에 'data' 필드 없음: {}", inlineData.toString());
                    }
                }
                
                // 다른 가능한 이미지 데이터 형식 확인
                if (currentPart.has("image")) {
                    log.info("'image' 필드 발견: {}", currentPart.get("image").toString());
                }
                if (currentPart.has("imageUrl")) {
                    log.info("'imageUrl' 필드 발견: {}", currentPart.get("imageUrl").toString());
                }
                if (currentPart.has("text")) {
                    log.info("'text' 필드 발견: {}", currentPart.get("text").toString());
                }
            }
            
            log.error("❌ CRITICAL: 모든 parts를 검사했지만 이미지 데이터를 찾을 수 없음!");
            throw new RuntimeException("Gemini에서 이미지 데이터를 찾을 수 없음");
            
        } catch (Exception e) {
            log.error("=== Gemini 2.5 Flash Image Preview API 호출 실패 ===");
            log.error("Gemini API 예외: {}", e.getMessage());
            log.error("상세 스택 트레이스:", e);
            throw new RuntimeException("이미지 생성 실패: " + e.getMessage(), e);
        }
    }
}
