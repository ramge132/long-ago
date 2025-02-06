package com.example.b101.service;

import com.example.b101.cache.Game;
import com.example.b101.cache.SceneRedis;
import com.example.b101.common.ApiResponseUtil;
import com.example.b101.dto.CreateSceneDto;
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

    public ResponseEntity<?> createScene(CreateSceneDto createSceneDto, HttpServletRequest request) {

        Game game = gameRepository.findById(createSceneDto.getGameId());

        if (game == null) {
            return ApiResponseUtil.failure("존재하지 않는 gameId입니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        if (game.getPlayerStatuses().stream()
                .noneMatch(player -> player.getUserId().equals(createSceneDto.getUserId()))) {
            return ApiResponseUtil.failure("해당 게임에 존재하지 않는 userId입니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        // GPU 서버와 통신하여 바이너리 데이터 받기
        byte[] imageBytes;
        try {
            imageBytes = webClient.post()
                    .uri("/generate")
                    .bodyValue(createSceneDto)
                    .retrieve()
                    .onStatus(
                            status -> status.value() == 422,
                            clientResponse -> {
                                throw new CustomException(ApiResponseUtil.failure("prompt가 누락되었습니다.",
                                        HttpStatus.BAD_REQUEST,
                                        request.getRequestURI()));
                            }
                    )
                    .bodyToMono(byte[].class) // 바이너리 데이터를 받음
                    .block();
        } catch (CustomException e) {
            return e.getApiResponse();
        } catch (Exception e) {
            return ApiResponseUtil.failure("GPU 서버 통신 중 에러 발생",
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        }

        // Redis에 Scene 데이터 저장
        List<SceneRedis> scenes = redisSceneRepository.findAllByGameId(createSceneDto.getGameId());
        int maxOrder = scenes.size();

        SceneRedis scene = SceneRedis.builder()
                .id(UUID.randomUUID().toString())
                .gameId(createSceneDto.getGameId())
                .prompt(createSceneDto.getPromptText())
                .image(imageBytes) // 바이너리 이미지 저장
                .sceneOrder(maxOrder + 1)
                .userId(createSceneDto.getUserId())
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
