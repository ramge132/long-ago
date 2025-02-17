package com.example.b101.controller;

import com.example.b101.dto.DeleteGameRequest;
import com.example.b101.dto.GameRequest;
import com.example.b101.service.GameService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/game")
@AllArgsConstructor
public class GameController{

    private final GameService gameService;

    //게임 생성
    @PostMapping
    public ResponseEntity<?> createGame(@RequestBody GameRequest gameRequest, HttpServletRequest request) {
        return gameService.saveGame(gameRequest, request);
    }

    //시연용 게임 생성
    @PostMapping("/test")
    public ResponseEntity<?> createGameTest(@RequestBody GameRequest gameRequest, HttpServletRequest request) {
        return gameService.createGame(gameRequest, request);
    }

    //게임 삭제
    @DeleteMapping
    public ResponseEntity<?> deleteGame(@RequestBody DeleteGameRequest deleteGameRequest, HttpServletRequest request) {
        return gameService.finishGame(deleteGameRequest,request);
    }

    //엔딩 카드 리롤
    @PatchMapping("/shuffle")
    public ResponseEntity<?> shuffleEndingCard(@RequestParam String gameId, @RequestParam String userId, HttpServletRequest request) {
        return gameService.shuffleEndingCard(gameId, userId, request);
    }

    //플레이어 카드 정보 조회
    @GetMapping
    public ResponseEntity<?> getPlayerStatus(@RequestParam String gameId, @RequestParam String userId, HttpServletRequest request) {
        return gameService.playStatusFindById(gameId, userId, request);
    }

}
