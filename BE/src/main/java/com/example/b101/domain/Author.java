package com.example.b101.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.OnDelete;
import org.hibernate.annotations.OnDeleteAction;

@Entity
@Setter
@Getter
public class Author {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    @ManyToOne
    @JoinColumn(name = "BOOK_ID") // Book과 다대일 관계
    @OnDelete(action = OnDeleteAction.CASCADE) //Book 삭제 시 Author 데이터도 삭제 (DB에서 삭제함)
    private Book book;

    @ManyToOne
    @JoinColumn(name = "USER_ID") // User와 다대일 관계
    @OnDelete(action = OnDeleteAction.CASCADE) //User 데이터 삭제 시 Author 데이터도 삭제됨.
    private User user;

}
