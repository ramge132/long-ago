package com.example.b101.domain;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.io.Serializable;
import java.time.LocalDateTime;

@Builder
@Getter
@Setter
@Entity
@NoArgsConstructor // 기본 생성자 생성
@AllArgsConstructor
@EntityListeners(AuditingEntityListener.class)
@Table(name = "USERS") // 테이블 이름
public class User implements Serializable {

    @Id // PK
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id; // 사용자 고유 ID

    @Column(name="USER_EMAIL",unique = true)
    private String email;

    @Column(name = "USER_PASSWORD", length = 255)
    private String password; // 사용자 비밀번호

    @Column(name = "USER_NICKNAME", length = 50)
    private String nickname; // 사용자 닉네임

    @Column(name = "CREATED_AT", updatable = false)
    @CreatedDate
    private LocalDateTime createdAt; // 생성일

    @Column(name = "UPDATED_AT")
    @LastModifiedDate
    private LocalDateTime updatedAt; // 수정일
}
