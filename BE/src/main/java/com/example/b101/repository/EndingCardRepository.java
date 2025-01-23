package com.example.b101.repository;

import com.example.b101.domain.EndingCard;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface EndingCardRepository extends JpaRepository<EndingCard, Integer> {

    List<EndingCard> findAll();

    EndingCard findById(int id);
}
