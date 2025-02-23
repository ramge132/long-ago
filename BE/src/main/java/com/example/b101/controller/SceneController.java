package com.example.b101.controller;

import com.example.b101.dto.DeleteSceneRequest;
import com.example.b101.dto.FilteringRequest;
import com.example.b101.dto.SceneRequest;
import com.example.b101.service.FilteringService;
import com.example.b101.service.SceneService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/scene")
public class SceneController {

    private final SceneService sceneService;
    private final FilteringService filteringService;

    
    //카드로 이미지 생성
    @PostMapping
    public ResponseEntity<?> addSceneByCard(@RequestBody SceneRequest sceneRequest, HttpServletRequest request) {
        return sceneService.createScene(sceneRequest, request);
    }

    //프롬포트 필터링
    @PostMapping("/filtering")
    public ResponseEntity<?> filterPrompt(@RequestBody FilteringRequest filteringRequest, HttpServletRequest request) {
        return filteringService.findCardVariantsByCardId(filteringRequest,request);
    }

    //투표 반대 시 scene 데이터 삭제
    @PostMapping("/vote")
    public ResponseEntity<?> deleteScene(@RequestBody DeleteSceneRequest deleteSceneRequest, HttpServletRequest request) {
        return sceneService.deleteScene(deleteSceneRequest,request);
    }


    //테스트용 투표
    @PostMapping("/vote/test")
    public ResponseEntity<?> deleteSceneTest(@RequestBody DeleteSceneRequest deleteSceneRequest, HttpServletRequest request) {
        return sceneService.deleteSceneTest(deleteSceneRequest,request);
    }

}
