package com.example.b101.controller;

import com.example.b101.dto.FilteringRequest;
import com.example.b101.dto.SceneRequest;
import com.example.b101.service.FilteringService;
import com.example.b101.service.SceneService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/scene")
public class SceneController {

    private final SceneService sceneService;
    private final FilteringService filteringService;

    @PostMapping("/storyCard")
    public ResponseEntity<?> addSceneStoryCard(@RequestBody SceneRequest sceneRequest, HttpServletRequest request) {
        return sceneService.createScene(sceneRequest, request);
    }


    @PostMapping("/endingCard")
    public ResponseEntity<?> addSceneEndingCard(@RequestBody SceneRequest sceneRequest, HttpServletRequest request) {
        return sceneService.createScene(sceneRequest, request);
    }

    @PostMapping("/filtering")
    public ResponseEntity<?> filterPrompt(@RequestBody FilteringRequest filteringRequest, HttpServletRequest request) {
        return filteringService.findCardVariantsByCardId(filteringRequest,request);
    }


    @GetMapping
    public ResponseEntity<?> getAllScene(@RequestParam String gameId,HttpServletRequest request) {
        return sceneService.getScenesByGameId(gameId,request);
    }


    @DeleteMapping
    public ResponseEntity<?> deleteScene(@RequestParam String gameId,HttpServletRequest request) {
        return sceneService.deleteScene(gameId,request);
    }

}
