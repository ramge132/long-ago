package com.example.b101.service;

import com.example.b101.cache.Game;
import com.example.b101.cache.SceneRedis;
import com.example.b101.common.ApiResponseUtil;
import com.example.b101.domain.PlayerStatus;
import com.example.b101.domain.StoryCard;
import com.example.b101.dto.DeleteSceneRequest;
import com.example.b101.dto.GenerateSceneRequest;
import com.example.b101.dto.SceneRequest;
import com.example.b101.repository.GameRepository;
import com.example.b101.repository.RedisSceneRepository;
import jakarta.servlet.http.HttpServletRequest;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientException;

import java.util.List;
import java.util.UUID;

@Slf4j
@Service
@AllArgsConstructor
public class SceneService {

    private final RedisSceneRepository redisSceneRepository;
    private final GameRepository gameRepository;
    private final WebClient webClient;



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


        // GPU 서버 요청을 위한 객체 생성
        GenerateSceneRequest generateSceneRequest = GenerateSceneRequest.builder()
                .session_id(sceneRequest.getGameId())            // 게임 아이디 (세션 식별자)
                .game_mode(game.getDrawingStyle())                    // 작화 스타일 (예: 1: 기본 모드)
                .user_sentence(sceneRequest.getUserPrompt()) // 사용자 프롬프트
                .status(0)                       // 진행 상태 (0: 진행 중)
                .build();

        log.info(generateSceneRequest.toString()+"GPU 서버로 보낼 객체 생성");

        // GPU 서버와 통신하여 이미지 바이너리 데이터 수신
        byte[] generateImage;
        try {
            log.info("이미지 서버에 요청 보냄.");
            generateImage = webClient.post()
                    .uri("/generate")
                    .contentType(MediaType.APPLICATION_JSON)
                    .accept(MediaType.IMAGE_PNG)
                    .bodyValue(generateSceneRequest)
                    .retrieve()
                    .bodyToMono(byte[].class)
                    .block();
        } catch (WebClientException e) {
            log.error("GPU 서버 에러 발생");
            return ApiResponseUtil.failure("GPU 서버 통신 중 오류 발생",
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        }

        if (generateImage == null || generateImage.length == 0) {
            return ApiResponseUtil.failure("이미지 받기 실패",
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        }

        // Redis 등 저장소에 이미지 데이터와 함께 Scene 정보 저장
        SceneRedis scene = SceneRedis.builder()
                .id(UUID.randomUUID().toString())
                .gameId(sceneRequest.getGameId())
                .prompt(sceneRequest.getUserPrompt())
                .image(generateImage)  // 바이너리 이미지 데이터 저장
                .sceneOrder(sceneRequest.getTurn())
                .userId(sceneRequest.getUserId())
                .build();


        redisSceneRepository.save(scene);


        // 이미지 바이너리 데이터를 PNG 미디어 타입으로 반환
        return ResponseEntity.status(HttpStatus.CREATED)
                .contentType(MediaType.IMAGE_PNG)
                .body(generateImage);
    }


    public ResponseEntity<?> deleteScene(DeleteSceneRequest deleteSceneRequest, HttpServletRequest request) {

        List<SceneRedis> scenes = redisSceneRepository.findAllByGameId(deleteSceneRequest.getGameId());
        if(scenes.isEmpty()) {
            return ApiResponseUtil.failure("아직 저장된 scene이 없습니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        if(!deleteSceneRequest.isAccepted()){

            //sceene 데이터 삭제
            SceneRedis lastScene = scenes.get(scenes.size() - 1);
            redisSceneRepository.delete(lastScene);
            return ApiResponseUtil.success(lastScene, "투표 결과에 따라 삭제됨", HttpStatus.OK, request.getRequestURI());
        }

        //사용한 카드 삭제해야함
        PlayerStatus playerStatus = gameRepository.getPlayerStatus(deleteSceneRequest.getGameId(), deleteSceneRequest.getUserId());

        StoryCard storyCard = playerStatus.getStoryCards().stream().filter(storyCard1 -> storyCard1.getId() == deleteSceneRequest.getCardId()).findFirst().orElse(null);

        // 🔹 카드 삭제
        playerStatus.getStoryCards().remove(storyCard);

        Game game = gameRepository.findById(deleteSceneRequest.getGameId());

        game.getPlayerStatuses().stream()
                .filter(ps -> ps.getUserId().equals(playerStatus.getUserId()))
                .findFirst()
                .ifPresent(ps -> ps.setStoryCards(playerStatus.getStoryCards()));

        gameRepository.update(game);

        return ApiResponseUtil.failure("투표 결과 찬성으로 삭제되지 않음",HttpStatus.CONFLICT,request.getRequestURI());

    }
}