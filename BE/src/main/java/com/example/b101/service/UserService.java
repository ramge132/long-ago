package com.example.b101.service;

import com.example.b101.domain.User;
import com.example.b101.dto.SignUpDto;
import com.example.b101.repository.UserRepository;
import com.example.b101.response.ApiResponse;
import com.example.b101.response.ApiResponseUtil;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class UserService {

    private final UserRepository userRepository;
    private final BCryptPasswordEncoder encoder;


    public UserService(UserRepository userRepository, BCryptPasswordEncoder encoder) {
        this.userRepository = userRepository;
        this.encoder = encoder;
    }

    //이메일로 사용자 조회
    public Optional<User> findByEmail(String email) {
        return userRepository.findByEmail(email);
    }

    //닉네임으로 사용자 조회
    public ResponseEntity<?> findByNicKname(String nickname, HttpServletRequest request) {
        if(userRepository.findByNickname(nickname).isPresent()) {
            return ApiResponseUtil.failure("이미 사용중인 닉네임입니다.",
                    HttpStatus.CONFLICT,
                    request.getRequestURI());
        }

        return ApiResponseUtil.success(nickname,"닉네임 사용가능",
                HttpStatus.OK,
                request.getRequestURI());
    }

    //회원가입
    public ResponseEntity<?> saveUser(SignUpDto signUpDto, HttpServletRequest request) {
        if (usedEmail(signUpDto.getEmail())) {
            return ApiResponseUtil.failure("이미 사용중인 이메일입니다.",
                    HttpStatus.CONFLICT,
                    request.getRequestURI());
        }

        User newUser = new User();
        newUser.setEmail(signUpDto.getEmail());
        newUser.setPassword(encoder.encode(signUpDto.getPassword())); //비밀번호 암호화 후 저장
        userRepository.save(newUser);

        return ApiResponseUtil.success(null,"회원가입 성공",HttpStatus.CREATED,request.getRequestURI());
    }

    public boolean usedEmail(String email){
        return userRepository.findByEmail(email).isPresent();
    }


}
