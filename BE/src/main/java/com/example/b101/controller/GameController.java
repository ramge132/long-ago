package com.example.b101.controller;

import com.example.b101.domain.EndingCard;
import com.example.b101.domain.Game;
import com.example.b101.domain.PlayerStatus;
import com.example.b101.dto.CreateGame;
import com.example.b101.service.CardService;
import com.example.b101.service.GameService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

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

    @GetMapping
    public ResponseEntity<?> getGame(@RequestParam String gameId, HttpServletRequest request) {
        return gameService.findById(gameId,request);
    }

    @GetMapping("/{roomId}")
    public ResponseEntity<?> getGameByUserId(@PathVariable String roomId, @RequestParam String userId, HttpServletRequest request) {
        return gameService.shuffleEndingCard(roomId, userId, request);
    }
}
