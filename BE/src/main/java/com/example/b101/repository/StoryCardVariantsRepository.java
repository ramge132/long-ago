package com.example.b101.repository;

import com.example.b101.domain.StoryCardVariants;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface StoryCardVariantsRepository extends JpaRepository<StoryCardVariants, Integer> {

    //해당 카드 id의 모든 변형어들을 가져옴.
    List<StoryCardVariants> findByStoryCardId(int storyCardId);


    //해당하는 카드 id들의 모든 변형어들을 가져옴.
    List<StoryCardVariants> findAllByStoryCardIdIn(List<Integer> storyCardIds);


}
