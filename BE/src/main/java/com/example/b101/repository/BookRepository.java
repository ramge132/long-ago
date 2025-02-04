package com.example.b101.repository;

import com.example.b101.cache.Game;
import com.example.b101.domain.Book;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface BookRepository extends JpaRepository<Book, Integer> {



}
