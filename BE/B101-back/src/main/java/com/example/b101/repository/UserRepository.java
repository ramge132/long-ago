package com.example.b101.repository;

import com.example.b101.domain.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

//Long: @Id 필드의 데이터 타입
public interface UserRepository extends JpaRepository<User,Long> {

    //닉네임으로 사용자 검색
    Optional<User> findByNickname(String nickname);

    //소셜 이메일로 사용자 검색
    Optional<User> findByEmail(String email);

}
