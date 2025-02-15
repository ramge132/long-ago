package com.example.b101.service;

import com.example.b101.domain.User;
import com.example.b101.dto.SignUpRequest;
import com.example.b101.repository.UserRepository;
import com.example.b101.common.ApiResponseUtil;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;


@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final BCryptPasswordEncoder encoder;

    //닉네임 사용 가능 여부
    public ResponseEntity<?> findByNickname(String nickname, HttpServletRequest request) {
        if (usedNickname(nickname)) {
            return ApiResponseUtil.failure("이미 사용중인 닉네임입니다.",
                    HttpStatus.CONFLICT,
                    request.getRequestURI());
        }

        return ApiResponseUtil.success(nickname, "닉네임 사용가능",
                HttpStatus.OK,
                request.getRequestURI());
    }


    //회원가입
    public ResponseEntity<?> saveUser(SignUpRequest signUpRequest, HttpServletRequest request) {
        if (usedEmail(signUpRequest.getEmail())) {
            return ApiResponseUtil.failure("이미 사용중인 이메일입니다.",
                    HttpStatus.CONFLICT,
                    request.getRequestURI());
        }

        User newUser = new User();
        newUser.setEmail(signUpRequest.getEmail());
        newUser.setPassword(encoder.encode(signUpRequest.getPassword())); //비밀번호 암호화 후 저장
        userRepository.save(newUser);

        return ApiResponseUtil.success(null, "회원가입 성공", HttpStatus.CREATED, request.getRequestURI());
    }

    //이메일 중복 체크
    public boolean usedEmail(String email) {
        return userRepository.findByEmail(email).isPresent();
    }

    //닉네임 중복 체크
    public boolean usedNickname(String nickname) {return userRepository.findByNickname(nickname).isPresent();}


}
