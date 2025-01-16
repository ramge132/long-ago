package com.example.b101.domain;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Getter
@Setter
@Entity
@NoArgsConstructor // 기본 생성자 생성
@EntityListeners(AuditingEntityListener.class)
@Table(name = "USERS") // 테이블 이름
public class User {

    @Id // PK
    @GeneratedValue
    @Schema(hidden = true)
    private Long id; // 사용자 고유 ID

    @Column(name="user_email") //일반 회원가입 유저는 null 가능?
    private String email;

    @Column(name = "USER_PASSWORD", length = 255)
    private String password; // 사용자 비밀번호

    @Column(name = "USER_NICKNAME", nullable = false, unique = true, length = 50)
    private String nickname; // 사용자 닉네임

    @Column(name = "CREATED_AT", updatable = false)
    @CreatedDate
    private LocalDateTime createdAt; // 생성일

    @Column(name = "UPDATED_AT")
    @LastModifiedDate
    private LocalDateTime updatedAt; // 수정일
}
