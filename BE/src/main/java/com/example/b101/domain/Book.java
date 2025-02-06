package com.example.b101.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Setter
@Getter
@EntityListeners(AuditingEntityListener.class)
public class Book {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    @Column(name = "BOOK_TITLE", nullable = false)
    private String title;

    @OneToMany(mappedBy = "book", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Author> authors = new ArrayList<>();

    //book을 삭제하면 자동으로 자식 scenes도 삭제됨. scene 데이터들이 필요할 때만 데이터를 가져오기 위해 지연 로딩 설(N+1 문제 방지)
    @OneToMany(mappedBy = "book", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<Scene> scenes = new ArrayList<>();

    @Column(name = "VIEW_COUNT", nullable = false)
    private int viewCnt = 0;

    @Column(name = "LIKE_COUNT", nullable = false)
    private int likeCnt = 0;

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

}
