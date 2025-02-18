package com.example.b101.repository;

import com.example.b101.domain.Book;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface BookRepository extends JpaRepository<Book, Integer> {

    List<Book> findBookByBookId(String bookId);

    int deleteByCreatedAtBefore(LocalDateTime createdAt);  // 삭제된 행 수 반환
}