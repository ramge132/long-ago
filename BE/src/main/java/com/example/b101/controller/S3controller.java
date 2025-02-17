package com.example.b101.controller;

import com.example.b101.service.S3service;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


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

    // 2) upload ( 클라이언트와 소통을 하지 않기 때문에 Service에 만 있습니다.)
    //

    // 3) download
    // imageUrl 세부 조정은 나중에...
    @GetMapping("/downloadFromS3")
    public  ResponseEntity<?> downloadFromS3(@RequestParam String objectKey, HttpServletRequest request) {

        return s3service.downloadFromS3(objectKey, request);
    }
}

