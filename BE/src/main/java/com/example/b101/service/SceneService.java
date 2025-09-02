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
import java.time.Duration;

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
    @Qualifier("pythonImageServiceClient")
    private final WebClient pythonImageServiceClient;
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

        // Python 통합 이미지 생성 서비스 호출
        String imageUrl = null;
        try {
            // 결말카드인지 확인 (기존 로직과 동일)
            boolean isEndingCard = sceneRequest.getTurn() > 5 && 
                    (sceneRequest.getUserPrompt().contains("결말") || 
                     sceneRequest.getUserPrompt().contains("끝") ||
                     sceneRequest.getUserPrompt().length() > 30);
            
            log.info("=== Python 이미지 생성 서비스 호출 시작 ===");
            log.info("결말카드 여부: {}, 그림체 모드: {}", isEndingCard, game.getDrawingStyle());
            
            imageUrl = callPythonImageService(sceneRequest, game.getDrawingStyle(), isEndingCard);
            log.info("=== Python 이미지 생성 성공 ===");
            log.info("생성된 이미지 URL: {}", imageUrl);
            
        } catch (WebClientException e) {
            log.error("=== API 서버 통신 에러 ===");
            log.error("WebClientException 발생: {}", e.getMessage());
            log.error("에러 상세:", e);
            return ApiResponseUtil.failure("AI 이미지 생성 서비스 일시 장애. 잠시 후 다시 시도해주세요.",
                    HttpStatus.SERVICE_UNAVAILABLE, // 503
                    request.getRequestURI());
        } catch (RuntimeException e) {
            log.error("=== Runtime 에러 ===");
            log.error("RuntimeException 발생: {}", e.getMessage());
            log.error("에러 상세:", e);
            
            // Gemini API 최종 실패의 경우 재시도 안내
            if (e.getMessage() != null && e.getMessage().contains("이미지 생성 최종 실패")) {
                return ApiResponseUtil.failure("AI 이미지 생성이 일시적으로 불안정합니다. 잠시 후 다시 시도해주세요.",
                        HttpStatus.SERVICE_UNAVAILABLE, // 503
                        request.getRequestURI());
            }
            
            return ApiResponseUtil.failure("이미지 생성 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    HttpStatus.SERVICE_UNAVAILABLE, // 503
                    request.getRequestURI());
        } catch (Exception e) {
            log.error("=== 일반 에러 ===");
            log.error("Exception 발생: {}", e.getMessage());
            log.error("에러 상세:", e);
            return ApiResponseUtil.failure("예상치 못한 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    HttpStatus.SERVICE_UNAVAILABLE, // 503
                    request.getRequestURI());
        }

        // Python 서비스에서 이미지가 성공적으로 생성되어 S3에 저장되었으므로 별도 검증 불필요
        log.info("=== Python 서비스를 통한 이미지 생성 및 S3 저장 완료 ===");

        log.info("=== Redis 저장 시작 ===");

        // Redis에 Scene 정보 저장 (이미지는 이미 S3에 저장됨)
        String id = UUID.randomUUID().toString();
        SceneRedis scene = SceneRedis.builder()
                .id(id)
                .gameId(sceneRequest.getGameId())
                .prompt(sceneRequest.getUserPrompt())
                .image(null)  // Python 서비스에서 S3에 직접 저장하므로 바이너리 데이터는 저장하지 않음
                .sceneOrder(sceneRequest.getTurn())
                .userId(sceneRequest.getUserId())
                .build();

        redisSceneRepository.save(scene);

        log.info("Redis에 저장된 scene 개수: {}", redisSceneRepository.findAllByGameId(sceneRequest.getGameId()).size());
        log.info("Python 서비스에서 생성된 이미지 URL: {}", imageUrl);

        // 성공 응답 반환 (이미지 URL 포함)
        return ApiResponseUtil.success(imageUrl, "이미지 생성 성공", HttpStatus.CREATED, request.getRequestURI());
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

        return ApiResponseUtil.success(null, "투표 결과 찬성으로 장면이 승인됨", HttpStatus.OK, request.getRequestURI());
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

        return ApiResponseUtil.success(null, "투표 결과 찬성으로 장면이 승인됨", HttpStatus.OK, request.getRequestURI());
    }

    /**
     * OpenAI GPT를 사용하여 프롬프트 생성
     */
    private String generatePromptWithGPT(String userSentence, int gameMode) {
        return callGPTWithRetry(userSentence, gameMode, 1, false); // 1회 재시도 (총 2번)
    }
    
    /**
     * 재시도 로직이 포함된 GPT API 호출
     */
    private String callGPTWithRetry(String userSentence, int gameMode, int maxRetries, boolean isEndingCard) {
        String cardType = isEndingCard ? "결말카드" : "일반카드";
        log.info("=== {} GPT API 호출 시작 (최대 {}회 시도) ===", cardType, maxRetries + 1);
        log.info("입력 문장: [{}], 게임모드: {}", userSentence, gameMode);
        
        for (int attempt = 1; attempt <= maxRetries + 1; attempt++) {
            try {
                log.info("🔄 {} GPT API 시도 {}/{}", cardType, attempt, maxRetries + 1);
                
                // 그림체 모드에 따른 스타일 정의
                String[] styles = {
                    "애니메이션 스타일", "3D 카툰 스타일", "코믹 스트립 스타일", "클레이메이션 스타일",
                    "크레용 드로잉 스타일", "픽셀 아트 스타일", "미니멀리스트 일러스트", "수채화 스타일", "스토리북 일러스트"
                };
                
                String style = gameMode < styles.length ? styles[gameMode] : "애니메이션 스타일";
                log.info("선택된 스타일: {}", style);
                
                // GPT-5 Responses API 요청 구조
                Map<String, Object> requestBody = new HashMap<>();
                requestBody.put("model", "gpt-5-nano");
                
                String promptInstruction = isEndingCard ?
                    "결말: " + userSentence + ". 이 문장을 " + style + " 스타일의 이미지로 만들기 위한 핵심 영어 키워드를 나열해줘." :
                    "문장: " + userSentence + ". 이 문장을 " + style + " 스타일의 이미지로 만들기 위한 핵심 영어 키워드를 나열해줘.";
                requestBody.put("input", promptInstruction);

                Map<String, String> reasoning = new HashMap<>();
                reasoning.put("effort", "low");
                requestBody.put("reasoning", reasoning);

                Map<String, String> text = new HashMap<>();
                text.put("verbosity", "low");
                requestBody.put("text", text);
                
                log.info("GPT-5 Responses API 요청 전송 중... (시도 {})", attempt);
                
                // OpenAI Responses API 호출
                String response = openaiWebClient.post()
                        .uri("https://api.openai.com/v1/responses")
                        .bodyValue(requestBody)
                        .retrieve()
                        .onStatus(
                            status -> status.is4xxClientError() || status.is5xxServerError(),
                            clientResponse -> clientResponse.bodyToMono(String.class)
                                .map(errorBody -> {
                                    log.error("🚨 OpenAI API 에러 응답 본문: {}", errorBody);
                                    return new RuntimeException("OpenAI API 에러: " + errorBody);
                                })
                        )
                        .bodyToMono(String.class)
                        .block();
                
                log.info("OpenAI API 응답 수신: {}", response != null ? "응답 있음" : "응답 없음");
                
                // 응답 파싱
                JsonNode responseJson = objectMapper.readTree(response);
                log.info("응답 JSON 구조: {}", responseJson.toString());

                if (responseJson.has("output") && responseJson.get("output").isArray()) {
                    for (JsonNode outputNode : responseJson.get("output")) {
                        if ("message".equals(outputNode.path("type").asText()) && outputNode.has("content")) {
                            JsonNode contentArray = outputNode.get("content");
                            if (contentArray.isArray() && !contentArray.isEmpty()) {
                                JsonNode firstContent = contentArray.get(0);
                                if ("output_text".equals(firstContent.path("type").asText())) {
                                    String generatedPrompt = firstContent.path("text").asText().trim();
                                    log.info("✅ {} GPT API 성공 (시도 {}) ===", cardType, attempt);
                                    log.info("생성된 프롬프트: [{}]", generatedPrompt);
                                    return generatedPrompt;
                                }
                            }
                        }
                    }
                }
                
                log.warn("⚠️ {} GPT API 응답 파싱 실패 (시도 {})", cardType, attempt);
                log.warn("choices 필드가 없거나 비어있음");
                
                // 마지막 시도가 아니면 예외를 던져서 재시도 로직으로 이동
                if (attempt < maxRetries + 1) {
                    throw new RuntimeException("GPT API 응답 구조 오류");
                }
                
            } catch (Exception e) {
                log.error("❌ {} GPT API 시도 {} 실패: {}", cardType, attempt, e.getMessage());
                
                if (attempt == maxRetries + 1) {
                    log.error("🚨 {} GPT API 최종 실패 - 원본 문장 사용", cardType);
                    log.error("상세 에러:", e);
                    return userSentence; // 최종 실패시 원본 문장 반환
                }
                
                // 짧은 대기 (500ms, 1초)
                long waitTime = 500L * attempt; 
                log.info("⏰ {}ms 대기 후 재시도...", waitTime);
                
                try {
                    Thread.sleep(waitTime);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    log.error("대기 중 인터럽트 발생");
                    return userSentence;
                }
            }
        }
        
        return userSentence; // fallback
    }
    
    /**
     * 결말카드 전용 OpenAI GPT 프롬프트 생성
     */
    private String generateEndingPromptWithGPT(String endingCardContent, int gameMode) {
        return callGPTWithRetry(endingCardContent, gameMode, 1, true); // 1회 재시도, 결말카드
    }
    
    /**
     * Gemini 2.5 Flash Image Preview를 사용하여 이미지 생성
     */
    private byte[] generateImageWithGemini(String prompt) {
        return callGeminiWithRetry(prompt, 1); // 1회 재시도 (총 2번)
    }
    
    /**
     * 재시도 로직이 포함된 Gemini API 호출
     */
    private byte[] callGeminiWithRetry(String prompt, int maxRetries) {
        log.info("=== Gemini 2.5 Flash Image Preview API 호출 시작 (최대 {}회 시도) ===", maxRetries + 1);
        log.info("입력 프롬프트: [{}] (길이: {}자)", prompt, prompt.length());
        
        for (int attempt = 1; attempt <= maxRetries + 1; attempt++) {
            try {
                log.info("🔄 Gemini API 시도 {}/{}", attempt, maxRetries + 1);
                
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
                    log.error("❌ Gemini API 응답에 'candidates' 필드 없음! (시도 {})", attempt);
                    log.error("사용 가능한 필드들: {}", responseJson.fieldNames());
                    
                    // 에러 정보 상세 분석
                    if (responseJson.has("error")) {
                        JsonNode error = responseJson.get("error");
                        String errorCode = error.has("code") ? error.get("code").asText() : "UNKNOWN";
                        String errorMessage = error.has("message") ? error.get("message").asText() : "No message";
                        String errorStatus = error.has("status") ? error.get("status").asText() : "UNKNOWN_STATUS";
                        
                        log.error("🚨 Gemini API 에러 상세 정보:");
                        log.error("  - 에러 코드: {}", errorCode);
                        log.error("  - 에러 메시지: {}", errorMessage);
                        log.error("  - 상태: {}", errorStatus);
                        log.error("  - 전체 에러: {}", error.toString());
                        
                        // 필터링 관련 에러 감지
                        if (errorMessage.toLowerCase().contains("blocked") || 
                            errorMessage.toLowerCase().contains("filter") ||
                            errorMessage.toLowerCase().contains("safety") ||
                            errorMessage.toLowerCase().contains("inappropriate") ||
                            errorMessage.toLowerCase().contains("policy")) {
                            
                            log.error("🔒 콘텐츠 필터링으로 인한 생성 거부 감지!");
                            log.error("사용자 입력 프롬프트: [{}]", prompt);
                            throw new RuntimeException("콘텐츠 필터링으로 인한 이미지 생성 거부: " + errorMessage);
                        }
                    }
                    
                    throw new RuntimeException("Gemini API candidates 필드 누락");
                }
                
                JsonNode candidates = responseJson.get("candidates");
                if (candidates.size() == 0) {
                    log.error("❌ candidates 배열이 비어있음! (시도 {})", attempt);
                    log.error("🔍 빈 candidates 배열 원인 분석:");
                    
                    // promptFeedback 확인 (필터링 정보)
                    if (responseJson.has("promptFeedback")) {
                        JsonNode promptFeedback = responseJson.get("promptFeedback");
                        log.error("  - promptFeedback: {}", promptFeedback.toString());
                        
                        if (promptFeedback.has("blockReason")) {
                            String blockReason = promptFeedback.get("blockReason").asText();
                            log.error("🔒 프롬프트가 안전 필터에 의해 차단됨!");
                            log.error("  - 차단 이유 (blockReason): {}", blockReason);
                            
                            // blockReason 종류별 설명 추가
                            String reasonDescription = getBlockReasonDescription(blockReason);
                            log.error("  - 차단 설명: {}", reasonDescription);
                            
                            log.error("사용자 입력 프롬프트: [{}]", prompt);
                            throw new RuntimeException("프롬프트 안전 필터 차단: " + blockReason + " (" + reasonDescription + ")");
                        }
                        
                        if (promptFeedback.has("safetyRatings")) {
                            log.error("  - 안전성 등급: {}", promptFeedback.get("safetyRatings").toString());
                        }
                    }
                    
                    log.error("사용자 입력 프롬프트: [{}]", prompt);
                    throw new RuntimeException("Gemini API candidates 배열 비어있음 - 필터링 가능성");
                }
                
                log.info("candidates 개수: {}", candidates.size());
                JsonNode candidate = candidates.get(0);
                log.info("첫 번째 candidate: {}", candidate.toString());
                
                // candidate의 필터링 상태 확인
                if (candidate.has("finishReason")) {
                    String finishReason = candidate.get("finishReason").asText();
                    log.info("finishReason: {}", finishReason);
                    
                    // 필터링으로 인한 중단 감지 (공식 API 문서 기준)
                    if ("SAFETY".equals(finishReason)) {
                        log.error("🔒 콘텐츠가 안전 필터에 의해 차단됨!");
                        log.error("finishReason: SAFETY - 유해 콘텐츠로 분류됨");
                        
                        if (candidate.has("safetyRatings")) {
                            JsonNode safetyRatings = candidate.get("safetyRatings");
                            log.error("📊 상세 안전성 등급:");
                            for (JsonNode rating : safetyRatings) {
                                String category = rating.has("category") ? rating.get("category").asText() : "UNKNOWN";
                                String probability = rating.has("probability") ? rating.get("probability").asText() : "UNKNOWN";
                                log.error("  - 카테고리: {}, 확률: {}", category, probability);
                            }
                        }
                        
                        log.error("사용자 입력 프롬프트: [{}]", prompt);
                        throw new RuntimeException("SAFETY 필터 차단 - 유해 콘텐츠 감지: " + finishReason);
                    }
                    
                    // 기타 중단 이유들도 로깅
                    if ("RECITATION".equals(finishReason)) {
                        log.warn("⚠️ RECITATION 감지 - 저작권 위험 콘텐츠");
                        log.warn("사용자 입력 프롬프트: [{}]", prompt);
                    } else if ("MAX_TOKENS".equals(finishReason)) {
                        log.warn("⚠️ MAX_TOKENS - 최대 토큰 수 도달");
                    } else if ("OTHER".equals(finishReason)) {
                        log.warn("⚠️ OTHER - 기타 중단 이유: {}", finishReason);
                    }
                }
                
                // content 및 parts 확인
                if (!candidate.has("content")) {
                    log.error("❌ candidate에 'content' 필드 없음!");
                    
                    // content가 없는 이유 분석
                    if (candidate.has("finishReason")) {
                        String finishReason = candidate.get("finishReason").asText();
                        log.error("content 없음의 원인 - finishReason: {}", finishReason);
                    }
                    
                    log.error("전체 candidate 구조: {}", candidate.toString());
                    throw new RuntimeException("Gemini API candidate content 누락 - 필터링 가능성");
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
                            log.info("✅ Gemini API 성공 (시도 {}) ===", attempt);
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
                
                log.error("❌ 모든 parts를 검사했지만 이미지 데이터를 찾을 수 없음! (시도 {})", attempt);
                throw new RuntimeException("Gemini에서 이미지 데이터를 찾을 수 없음");
                
            } catch (Exception e) {
                log.error("❌ Gemini API 시도 {} 실패: {}", attempt, e.getMessage());
                
                if (attempt == maxRetries + 1) {
                    log.error("🚨 Gemini API 최종 실패 - RuntimeException 던짐");
                    log.error("상세 스택 트레이스:", e);
                    throw new RuntimeException("이미지 생성 최종 실패: " + e.getMessage(), e);
                }
                
                // 짧은 대기 (500ms, 1초)
                long waitTime = 500L * attempt; 
                log.info("⏰ {}ms 대기 후 재시도...", waitTime);
                
                try {
                    Thread.sleep(waitTime);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    log.error("대기 중 인터럽트 발생");
                    throw new RuntimeException("이미지 생성 인터럽트: " + ie.getMessage(), ie);
                }
            }
        }
        
        throw new RuntimeException("Gemini API 재시도 로직 오류"); // fallback
    }
    
    /**
     * blockReason 코드에 대한 설명을 반환
     */
    private String getBlockReasonDescription(String blockReason) {
        switch (blockReason) {
            case "BLOCK_REASON_UNSPECIFIED":
                return "특정되지 않은 차단 이유";
            case "SAFETY":
                return "안전성 우려로 인한 차단";
            case "OTHER":
                return "기타 이유로 인한 차단";
            default:
                return "알 수 없는 차단 이유: " + blockReason;
        }
    }
    
    /**
     * Python 통합 이미지 생성 서비스 호출
     */
    private String callPythonImageService(SceneRequest sceneRequest, int drawingStyle, boolean isEnding) {
        try {
            // Python 서비스 요청 데이터 구성
            HashMap<String, Object> requestBody = new HashMap<>();
            requestBody.put("gameId", sceneRequest.getGameId());
            requestBody.put("userId", sceneRequest.getUserId());
            requestBody.put("userPrompt", sceneRequest.getUserPrompt());
            requestBody.put("turn", sceneRequest.getTurn());
            requestBody.put("drawingStyle", drawingStyle);
            requestBody.put("isEnding", isEnding);
            
            log.info("Python 서비스 호출 요청: {}", requestBody);
            
            // Python 서비스 호출 (재시도 로직 포함)
            String response = pythonImageServiceClient
                .post()
                .uri("/generate-scene")
                .bodyValue(requestBody)
                .retrieve()
                .onStatus(
                    status -> status.is4xxClientError() || status.is5xxServerError(),
                    clientResponse -> clientResponse.bodyToMono(String.class)
                        .map(errorBody -> new RuntimeException("Python 서비스 에러: " + errorBody))
                )
                .bodyToMono(String.class)
                .timeout(Duration.ofMinutes(5))  // 5분 타임아웃
                .block();
            
            // 응답 파싱
            JsonNode responseNode = objectMapper.readTree(response);
            
            if (responseNode.get("success").asBoolean()) {
                String imageUrl = responseNode.get("imageUrl").asText();
                String gptPrompt = responseNode.has("gptPrompt") ? responseNode.get("gptPrompt").asText() : "";
                
                log.info("Python 이미지 생성 성공. URL: {}, GPT 프롬프트: {}", imageUrl, gptPrompt);
                return imageUrl;
            } else {
                String errorMessage = responseNode.get("message").asText();
                log.error("Python 이미지 생성 실패: {}", errorMessage);
                throw new RuntimeException(errorMessage);
            }
            
        } catch (Exception e) {
            log.error("Python 이미지 서비스 호출 실패: {}", e.getMessage());
            throw new RuntimeException("이미지 생성 서비스 호출 실패: " + e.getMessage(), e);
        }
    }
}
