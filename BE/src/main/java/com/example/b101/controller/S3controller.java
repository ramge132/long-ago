package com.example.b101.controller;

import com.example.b101.service.S3service;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;

@RestController
@RequestMapping("/s3")
@RequiredArgsConstructor
public class S3controller {

    private final S3service s3service;

    // #1. presignedURL 생성
    @GetMapping("/presignedUrl")
    public ResponseEntity<?> getPresignedUrl(
            @RequestParam String bookNum, @RequestParam String fileName, HttpServletRequest request) {

        return s3service.generatePresignedUrl(bookNum, fileName, request);
    }

    // 2) upload
    // 어떤 파라미터를 받아야하는지 모르겠당... 이미지 자체가 들어가야할 듯?
    @PostMapping("/upload")
    public ResponseEntity<?> uploadToS3(String gameId, HttpServletRequest request) throws IOException {

        return s3service.uploadToS3(gameId, request);
    }

    // 3) download
    // imageUrl 세부 조정은 나중에...
    @GetMapping("/downloadFromS3/{objectKey}")
    public  ResponseEntity<?> downloadFromS3(@PathVariable String objectKey, HttpServletRequest request) {

        return s3service.downloadFromS3(objectKey, request);
    }
}

