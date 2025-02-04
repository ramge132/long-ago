package com.example.b101.controller;

import com.example.b101.dto.CreateGame;
import com.example.b101.service.GameService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.AllArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/game")
@AllArgsConstructor
public class GameController{

    private final GameService gameService;

    @PostMapping
    public ResponseEntity<?> createGame(@RequestBody CreateGame createGame, HttpServletRequest request) {
        return gameService.save(createGame, request);
    }


    @DeleteMapping
    public ResponseEntity<?> deleteGame(@RequestParam String gameId, HttpServletRequest request) {
        return gameService.delete(gameId,request);
    }

    @PatchMapping("/shuffle/{gameId}")
    public ResponseEntity<?> shuffleEndingCard(@PathVariable String gameId, @RequestParam String userId, HttpServletRequest request) {
        return gameService.shuffleEndingCard(gameId, userId, request);
    }


    @GetMapping("/{gameId}")
    public ResponseEntity<?> getPlayerStatus(@PathVariable String gameId, @RequestParam String userId, HttpServletRequest request) {
        return gameService.playStatusFindById(gameId, userId, request);
    }
}
