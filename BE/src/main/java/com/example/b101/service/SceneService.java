package com.example.b101.service;

import com.example.b101.cache.Game;
import com.example.b101.cache.SceneRedis;
import com.example.b101.common.ApiResponseUtil;
import com.example.b101.dto.CreateSceneDto;
import com.example.b101.repository.GameRepository;
import com.example.b101.repository.RedisSceneRepository;
import jakarta.servlet.http.HttpServletRequest;
import lombok.AllArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
@AllArgsConstructor
public class SceneService {

    private final RedisSceneRepository redisSceneRepository;
    private final GameRepository gameRepository;

    public ResponseEntity<?> createScene(CreateSceneDto createSceneDto,HttpServletRequest request) {

        try {
        /**
         *  GPU 서버와 API 통신후 이미지 받아오는 로직
         *
         *
         *
         *
         */



            List<SceneRedis> scenes = redisSceneRepository.findAllByGameId(createSceneDto.getGameId());

            int maxOrder = scenes.size();


            SceneRedis scene = SceneRedis.builder()
                    .gameId(createSceneDto.getGameId())
                    .id(UUID.randomUUID().toString())
                    .prompt(createSceneDto.getPromptText())
                    .sceneOrder(maxOrder + 1)
                    .userId(createSceneDto.getUserId())
                    .build();

            redisSceneRepository.save(scene);

            return ApiResponseUtil.success(scene,
                    "Scene 저장 완료",
                    HttpStatus.CREATED,
                    request.getRequestURI());
        } catch (Exception e) {
            return ApiResponseUtil.failure("Scene 저장 중 오류 발생: " + e.getMessage(),
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        }

    }


}
