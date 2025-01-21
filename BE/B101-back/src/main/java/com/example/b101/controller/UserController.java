package com.example.b101.controller;

import com.example.b101.domain.User;
import com.example.b101.dto.SignUpDto;
import com.example.b101.response.ApiResponseUtil;
import com.example.b101.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class UserController {

    private final UserService userService;
    private final BCryptPasswordEncoder encoder;

    public UserController(UserService userService) {
        this.userService = userService;
        this.encoder = new BCryptPasswordEncoder();
    }


    @PostMapping("/signup")
    public ResponseEntity<?> signup(@RequestBody SignUpDto signUpDto, HttpServletRequest request) {


        if (userService.usedEmail(signUpDto.getEmail())) {
            return ApiResponseUtil.failure("이미 사용중인 이메일입니다.",
                    HttpStatus.CONFLICT,
                    request.getRequestURI());
        }

        User newUser = new User();
        newUser.setEmail(signUpDto.getEmail());
        newUser.setPassword(encoder.encode(signUpDto.getPassword())); //비밀번호 암호화 후 저장
        userService.saveUser(newUser);



        return ApiResponseUtil.success(null,"회원가입 성공",HttpStatus.CREATED,request.getRequestURI());
    }


    @GetMapping("/check-nickname")
    public ResponseEntity<?> checkNickname(@RequestParam("nickname") String nickname,HttpServletRequest request) {
        if(userService.findByEmail(nickname).isPresent()) {
            return ApiResponseUtil.failure("이미 사용중인 닉네임입니다.",
                    HttpStatus.CONFLICT,
                    request.getRequestURI());
        }

        return ApiResponseUtil.success(nickname,"닉네임 사용가능",
                HttpStatus.OK,
                request.getRequestURI());
    }

}
