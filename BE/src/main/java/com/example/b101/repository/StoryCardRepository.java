package com.example.b101.repository;

import com.example.b101.domain.StoryCard;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;



@Repository
public interface StoryCardRepository extends JpaRepository<StoryCard, Integer> {

}
