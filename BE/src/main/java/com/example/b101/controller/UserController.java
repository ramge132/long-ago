package com.example.b101.controller;

import com.example.b101.dto.SignUpRequest;
import com.example.b101.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.AllArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
@AllArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping("/signup")
    public ResponseEntity<?> signup(@RequestBody SignUpRequest signUpRequest, HttpServletRequest request) {
        return userService.saveUser(signUpRequest, request);
    }


    @GetMapping("/check-nickname")
    public ResponseEntity<?> checkNickname(@RequestParam("nickname") String nickname, HttpServletRequest request) {
        return userService.findByNickname(nickname, request);
    }

}
