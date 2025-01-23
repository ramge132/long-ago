package com.example.b101.repository;

import com.example.b101.domain.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Integer> {

    /**
     * Optional 타입은 nullpointerException을 방지합니다.
     */
    Optional<User> findByNickname(String nickname);

    //소셜 이메일로 사용자 검색
    Optional<User> findByEmail(String email);


}
