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
    private long id;

    @Column(name = "BOOK_TITLE",nullable = true)
    private String title;

    @OneToMany(mappedBy = "book")
    private List<Author> authors = new ArrayList<>();

    private int viewCnt;

    private int likeCnt;

    @CreatedDate
    private LocalDateTime createdAt;


}
