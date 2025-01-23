package com.example.b101.controller;

import com.example.b101.common.ApiResponseUtil;
import com.example.b101.service.CardService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/card")
@RequiredArgsConstructor
public class CardController {

    private final CardService cardService;

    @GetMapping
    public ResponseEntity<?> suffleCard(HttpServletRequest request) {
        cardService.shuffleCard(request);
        return ApiResponseUtil.success(null,
                "카드 셔플 완료",
                HttpStatus.OK,
                request.getRequestURI());
    }
}
