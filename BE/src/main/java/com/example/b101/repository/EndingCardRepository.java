package com.example.b101.repository;

import com.example.b101.domain.EndingCard;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;


@Repository
public interface EndingCardRepository extends JpaRepository<EndingCard, Integer> {

    List<EndingCard> findAll(); //초기에 DB에서 카드정보들을 가져오기 위함.

    EndingCard findById(int id);


}
