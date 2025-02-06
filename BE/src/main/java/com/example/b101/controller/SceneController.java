package com.example.b101.controller;

import com.example.b101.dto.SceneRequest;
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

    @PostMapping("/storyCard")
    public ResponseEntity<?> addSceneStoryCard(@RequestBody SceneRequest sceneRequest, HttpServletRequest request) {
        return sceneService.createScene(sceneRequest, request);
    }


    @PostMapping("/endingCard")
    public ResponseEntity<?> addSceneEndingCard(@RequestBody SceneRequest sceneRequest, HttpServletRequest request) {
        return sceneService.createScene(sceneRequest, request);
    }


}
