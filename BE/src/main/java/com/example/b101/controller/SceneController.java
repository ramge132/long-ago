package com.example.b101.controller;

import com.example.b101.domain.Scene;
import com.example.b101.dto.CreateSceneDto;
import com.example.b101.service.SceneService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/scene")
public class SceneController {

    private final SceneService sceneService;

    @PostMapping
    public ResponseEntity<?> addScene(@RequestBody CreateSceneDto createSceneDto, HttpServletRequest request) {
        return sceneService.createScene(createSceneDto, request);
    }
}
