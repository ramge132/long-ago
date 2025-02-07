package com.example.b101.service;

import com.example.b101.cache.Game;
import com.example.b101.cache.SceneRedis;
import com.example.b101.common.ApiResponseUtil;
import com.example.b101.domain.PlayerStatus;
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
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

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
        Set<String> playerUserIds = game.getPlayerStatuses()
                .stream()
                .map(PlayerStatus::getUserId)
                .collect(Collectors.toSet());

        if (!playerUserIds.contains(sceneRequest.getUserId())) {
            return ApiResponseUtil.failure("해당 게임에 존재하지 않는 userId입니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }



        //GPU 서버에 요청을 보내기 위한 객체 생성
        //작화, 직전에 저장된 요약된 스토리, 사용자 프롬포트, 직전의 생성된 이미지 프롬포트
        GenerateSceneRequest generateSceneRequest = GenerateSceneRequest.builder()
                .drawingStyle(game.getDrawingStyle()) //작화
                .userPrompt(sceneRequest.getUserPrompt()) //사용자 프롬포트
                .build();


        // GPU 서버와 통신하여 데이터 받기
        byte[] generateImage;
        try {
            generateImage = webClient.post()  //post형식으로 webClient의 요청을 보냄.
                    .uri("/generate").accept(MediaType.APPLICATION_JSON) //JSON 타입을 받겠다.
                    .bodyValue(generateSceneRequest) //RequestBody로 보낼 객체
                    .retrieve()
                    .onStatus(HttpStatusCode::is4xxClientError, response ->
                            response.createException().flatMap(Mono::error))
                    .bodyToMono(byte[].class) //응답의 본문(body)만 가져옴.
                    .block(); //이미지를 다 받고 프론트에 보내야 하므로 동기방식 채택
        } catch (WebClientResponseException e) { //GPU 서버에서 에러 반환 시
            log.error(e.getResponseBodyAsString());
            return ApiResponseUtil.failure("GPU 서버 통신 중 data 누락 발생",
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


        BufferedImage bufferedImage;
        try{
            ByteArrayInputStream inputStream = new ByteArrayInputStream(generateImage);
            bufferedImage = ImageIO.read(inputStream);
        } catch (IOException e){
            return ApiResponseUtil.failure("이미지 전송 실패",
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        }


        return ApiResponseUtil.success(bufferedImage,
                "Scene 저장 완료",
                HttpStatus.CREATED,
                request.getRequestURI());
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
