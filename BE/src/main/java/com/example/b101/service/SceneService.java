package com.example.b101.service;

import com.example.b101.cache.Game;
import com.example.b101.cache.SceneRedis;
import com.example.b101.common.ApiResponseUtil;
import com.example.b101.dto.GenerateSceneRequest;
import com.example.b101.dto.SceneRequest;
import com.example.b101.repository.GameRepository;
import com.example.b101.repository.RedisSceneRepository;
import jakarta.servlet.http.HttpServletRequest;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientException;
import reactor.core.publisher.Mono;

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

        //gameId를 통해 게임 데이터 조회
        Game game = gameRepository.findById(sceneRequest.getGameId());

        //게임 데이터가 없다면 fail
        if (game == null) {
            return ApiResponseUtil.failure("존재하지 않는 gameId입니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        //해당 게임 데이터의 저장된 플에이어 중의 userId가 없다면 fail
        boolean userExists = game.getPlayerStatuses()
                .stream()
                .anyMatch(playerStatus -> playerStatus.getUserId().equals(sceneRequest.getUserId()));

        if (!userExists) {
            return ApiResponseUtil.failure("해당 게임에 존재하지 않는 userId입니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }




        //GPU 서버에 요청을 보내기 위한 객체 생성
        GenerateSceneRequest generateSceneRequest = GenerateSceneRequest.builder()
                .gameId(sceneRequest.getGameId()) //게임 아이디
                .drawingStyle(game.getDrawingStyle()) //작화 스타일
                .userPrompt(sceneRequest.getUserPrompt()) //사용자 프롬포트
                .build();


        // GPU 서버와 통신하여 데이터 받기
        byte[] generateImage = null;
        try {
            generateImage = webClient.post()  //post형식으로 webClient의 요청을 보냄.
                    .uri("/generate").accept(MediaType.IMAGE_PNG) //이미지 파일로 받는다.
                    .bodyValue(generateSceneRequest) //RequestBody로 보낼 객체
                    .retrieve()
                    .onStatus(HttpStatusCode::is4xxClientError, response ->
                            response.createException().flatMap(Mono::error))    //GPU 서버에서 422에러를 응답하면 PROMPT가 누락
                    .bodyToMono(byte[].class) //응답의 본문(body)만 가져옴.
                    .block(); //이미지를 다 받고 프론트에 보내야 하므로 동기방식 채택
        } catch (WebClientException e) { //GPU 서버에서 에러 반환 시
            return ApiResponseUtil.failure("GPU 서버 통신 중 오류 발생",
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        }

        SceneRedis scene = SceneRedis.builder()
                .id(UUID.randomUUID().toString())
                .gameId(sceneRequest.getGameId())
                .prompt(sceneRequest.getUserPrompt())
                .image(generateImage) // 바이너리 이미지 저장
                .sceneOrder(sceneRequest.getTurn())
                .userId(sceneRequest.getUserId())
                .build();

        redisSceneRepository.save(scene);




        return ResponseEntity.status(HttpStatus.CREATED)
                .contentType(MediaType.IMAGE_PNG) // PNG 형식으로 응답
                .body(generateImage);
    }


    public ResponseEntity<?> deleteScene(String gameId, HttpServletRequest request) {
        List<SceneRedis> scenes = redisSceneRepository.findAllByGameId(gameId);

        if(scenes.isEmpty()) {
            return ApiResponseUtil.failure("아직 저장된 scene이 없습니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        SceneRedis lastScene = scenes.get(scenes.size() - 1);

        redisSceneRepository.delete(lastScene);

        return ApiResponseUtil.success(lastScene,"투표 결과에 따라 삭제됨",HttpStatus.OK,request.getRequestURI());
    }



    //해당 Game에서 생성된 모든 Scene 데이터들 가져오기(디버깅 용)
    public ResponseEntity<?> getScenesByGameId(String gameId, HttpServletRequest request) {
        if(gameRepository.findById(gameId) == null) {
            return ApiResponseUtil.failure("해당 gameId를 가진 game이 없습니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }


        List<SceneRedis> sceneRedisList =  redisSceneRepository.findAllByGameId(gameId);

        if(sceneRedisList.isEmpty()){
            return ApiResponseUtil.failure("만들어진 scene이 없습니다.",
                    HttpStatus.NO_CONTENT,
                    request.getRequestURI());
        }

        return ApiResponseUtil.success(sceneRedisList,
                "해당 game의 모든 scene을 가져왔습니다.",
                HttpStatus.OK,
                request.getRequestURI());
    }
}
