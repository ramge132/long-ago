package com.example.b101.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Setter
@Getter
public class Author {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private long id;

    @ManyToOne
    @JoinColumn(name = "BOOK_ID") // Book과 다대일 관계
    private Book book;

    @ManyToOne
    @JoinColumn(name = "USER_ID") // User와 다대일 관계
    private User user;

}
