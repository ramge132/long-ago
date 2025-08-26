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
    private final StoryCardRepository storyCardRepository;
    private final WebClientConfig webClientConfig;
    private final ObjectMapper objectMapper = new ObjectMapper();


    public ResponseEntity<?> createScene(SceneRequest sceneRequest, HttpServletRequest request) {
        log.info("게임 턴: {}", sceneRequest.getTurn());

        // 게임 데이터 조회 및 유효성 검사
        Game game = gameRepository.findById(sceneRequest.getGameId());
        if (game == null) {
            return ApiResponseUtil.failure("존재하지 않는 gameId입니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        boolean userExists = game.getPlayerStatuses()
                .stream()
                .anyMatch(playerStatus -> playerStatus.getUserId().equals(sceneRequest.getUserId()));
        if (!userExists) {
            return ApiResponseUtil.failure("해당 게임에 존재하지 않는 userId입니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        // RunPod API를 위한 요청 객체 생성
        Map<String, Object> runpodRequest = new HashMap<>();
        Map<String, Object> inputData = new HashMap<>();
        inputData.put("session_id", sceneRequest.getGameId());
        inputData.put("game_mode", game.getDrawingStyle());
        inputData.put("user_sentence", sceneRequest.getUserPrompt());
        inputData.put("status", 0);
        inputData.put("character_cards", List.of()); // 캐릭터 카드 리스트 (필요시 추가)
        runpodRequest.put("input", inputData);

        log.info("RunPod API 요청 객체 생성: {}", runpodRequest);

        // RunPod API 호출
        byte[] generateImage = null;
        try {
            log.info("RunPod 서버에 요청 보냄.");
            
            // RunPod URL 사용 (baseUrl0이 RunPod URL)
            String runpodUrl = webClientConfig.getBaseUrls().get(0);
            
            // RunPod API는 Authorization 헤더가 이미 runpodWebClient에 설정되어 있음
            String responseBody = runpodWebClient.post()
                    .uri(runpodUrl)
                    .bodyValue(runpodRequest)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();
            
            log.info("RunPod 응답 받음");
            
            // RunPod 응답 파싱
            if (responseBody != null) {
                JsonNode responseJson = objectMapper.readTree(responseBody);
                
                // 비동기 처리 확인
                if (responseJson.has("status") && "IN_QUEUE".equals(responseJson.get("status").asText())) {
                    // 비동기 작업인 경우 job_id로 상태 확인 필요
                    String jobId = responseJson.get("id").asText();
                    log.info("RunPod 작업이 큐에 있음. Job ID: {}", jobId);
                    
                    // 상태 확인 (최대 5분 대기)
                    int maxAttempts = 60; // 5초 간격으로 60번 시도 = 5분
                    for (int i = 0; i < maxAttempts; i++) {
                        Thread.sleep(5000); // 5초 대기
                        
                        String statusResponse = runpodWebClient.get()
                                .uri(runpodUrl.replace("/run", "/status/" + jobId))
                                .retrieve()
                                .bodyToMono(String.class)
                                .block();
                        
                        JsonNode statusJson = objectMapper.readTree(statusResponse);
                        String status = statusJson.get("status").asText();
                        
                        if ("COMPLETED".equals(status)) {
                            responseJson = statusJson.get("output");
                            break;
                        } else if ("FAILED".equals(status)) {
                            log.error("RunPod 작업 실패");
                            return ApiResponseUtil.failure("이미지 생성 실패",
                                    HttpStatus.INTERNAL_SERVER_ERROR,
                                    request.getRequestURI());
                        }
                    }
                }
                
                // output에서 이미지 데이터 추출
                if (responseJson.has("output")) {
                    responseJson = responseJson.get("output");
                }
                
                if (responseJson.has("image")) {
                    String base64Image = responseJson.get("image").asText();
                    generateImage = Base64.getDecoder().decode(base64Image);
                    log.info("Base64 이미지 디코딩 완료. 크기: {} bytes", generateImage.length);
                } else if (responseJson.has("s3_url")) {
                    // S3 URL이 있는 경우 직접 다운로드 (선택적)
                    String s3Url = responseJson.get("s3_url").asText();
                    log.info("S3 URL 받음: {}", s3Url);
                    
                    // S3에서 이미지 다운로드
                    generateImage = webClient.get()
                            .uri(s3Url)
                            .retrieve()
                            .bodyToMono(byte[].class)
                            .block();
                }
            }
            
        } catch (WebClientException e) {
            log.error("RunPod 서버 통신 에러: {}", e.getMessage());
            return ApiResponseUtil.failure("RunPod 서버 통신 중 오류 발생",
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        } catch (Exception e) {
            log.error("이미지 처리 중 에러: {}", e.getMessage());
            return ApiResponseUtil.failure("이미지 처리 중 오류 발생",
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        }

        if (generateImage == null || generateImage.length == 0) {
            return ApiResponseUtil.failure("이미지 받기 실패",
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        }

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
        log.info("RunPod에서 온 이미지 크기 : {}", generateImage.length);
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

            // RunPod API를 위한 요청 객체 생성 (status 3 = 삭제)
            Map<String, Object> runpodRequest = new HashMap<>();
            Map<String, Object> inputData = new HashMap<>();
            inputData.put("session_id", deleteSceneRequest.getGameId());
            inputData.put("game_mode", 1);
            inputData.put("user_sentence", "");
            inputData.put("status", 3);
            inputData.put("character_cards", List.of());
            runpodRequest.put("input", inputData);

            // RunPod URL 사용
            String runpodUrl = webClientConfig.getBaseUrls().get(0);
            
            runpodWebClient.post()
                    .uri(runpodUrl)
                    .bodyValue(runpodRequest)
                    .retrieve()
                    .bodyToMono(Void.class)
                    .subscribe();

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
}
