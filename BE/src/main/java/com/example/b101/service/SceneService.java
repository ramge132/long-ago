package com.example.b101.service;

import com.example.b101.cache.Game;
import com.example.b101.cache.SceneRedis;
import com.example.b101.common.ApiResponseUtil;
import com.example.b101.dto.GenerateSceneRequest;
import com.example.b101.dto.SceneRequest;
import com.example.b101.dto.GenerateSceneResponse;
import com.example.b101.repository.GameRepository;
import com.example.b101.repository.RedisSceneRepository;
import jakarta.servlet.http.HttpServletRequest;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;
import java.util.UUID;

@Service
@AllArgsConstructor
public class SceneService {

    private final RedisSceneRepository redisSceneRepository;
    private final GameRepository gameRepository;
    private final WebClient webClient;

    public ResponseEntity<?> createScene(SceneRequest sceneRequest, HttpServletRequest request) {

        //gameId를 통해 게임 데이터 조회
        Game game = gameRepository.findById(sceneRequest.getGameId());

        //게임 데이터가 없다면 fail
        if (game == null) {
            return ApiResponseUtil.failure("존재하지 않는 gameId입니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        //해당 게임 데이터의 저장된 플에이어 중의 userId가 없다면 fail
        if (game.getPlayerStatuses().stream()
                .noneMatch(player -> player.getUserId().equals(sceneRequest.getUserId()))) {
            return ApiResponseUtil.failure("해당 게임에 존재하지 않는 userId입니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }


        //GPU 서버에 요청을 보내기 위한 객체 생성
        GenerateSceneRequest generateSceneRequest = GenerateSceneRequest.builder()
                .drawingStyle(game.getDrawingStyle())
                .userPrompt(sceneRequest.getUserPrompt())
                .build();


        // GPU 서버와 통신하여 데이터 받기
        GenerateSceneResponse generateSceneResponse;
        try {

            generateSceneResponse = webClient.post()  //post형식으로 webClient의 요청을 보냄.
                    .uri("/generate") //endpoint는 /generate
                    .bodyValue(generateSceneRequest) //RequestBody로 보낼 객체
                    .retrieve()
                    .onStatus(
                            status -> status.value() == 422,
                            clientResponse -> {
                                throw new CustomException(ApiResponseUtil.failure("prompt가 누락되었습니다.",
                                        HttpStatus.BAD_REQUEST,
                                        request.getRequestURI()));
                            }
                    )
                    .bodyToMono(GenerateSceneResponse.class) // 바이너리 데이터를 받음
                    .block();
        } catch (CustomException e) {
            return e.getApiResponse();
        } catch (Exception e) {
            return ApiResponseUtil.failure("GPU 서버 통신 중 에러 발생",
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        }

        // Redis에 Scene 데이터 저장
        List<SceneRedis> scenes = redisSceneRepository.findAllByGameId(sceneRequest.getGameId());
        int maxOrder = scenes.size();

        SceneRedis scene = SceneRedis.builder()
                .id(UUID.randomUUID().toString())
                .gameId(sceneRequest.getGameId())
                .prompt(sceneRequest.getUserPrompt())
                .image(generateSceneResponse.getImage()) // 바이너리 이미지 저장
                .sceneOrder(maxOrder + 1)
                .userId(sceneRequest.getUserId())
                .build();

        redisSceneRepository.save(scene);

        return ApiResponseUtil.success(scene,
                "Scene 저장 완료",
                HttpStatus.CREATED,
                request.getRequestURI());
    }


    // CustomException 정의
    @Getter
    @AllArgsConstructor
    public static class CustomException extends RuntimeException {
        private final ResponseEntity<?> apiResponse;
    }
}
