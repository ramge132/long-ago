package com.example.b101.service;

import com.example.b101.domain.User;
import com.example.b101.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    //이메일로 사용자 검색
    public Optional<User> findByEmail(String email) {
        return userRepository.findByEmail(email);
    }

    //닉네임으로 사용자 검색
    public Optional<User> findByNicKname(String nickname) {
        return userRepository.findByNickname(nickname);
    }

    //회원가입
    public User saveUser(User user) {
        return userRepository.save(user);
    }


}
