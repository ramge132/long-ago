package com.example.b101.service;

import com.example.b101.domain.EndingCard;
import com.example.b101.domain.StoryCard;
import com.example.b101.domain.StoryCardVariants;
import com.example.b101.dto.CachingEndingCard;
import com.example.b101.dto.CachingStoryCard;
import com.example.b101.dto.CachingVariants;
import com.example.b101.repository.EndingCardRepository;
import com.example.b101.repository.StoryCardRepository;
import com.example.b101.repository.StoryCardVariantsRepository;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.List;

@Slf4j
@Service
@AllArgsConstructor
public class CachingService {

    private final StoryCardVariantsRepository storyCardVariantsRepository;
    private final EndingCardRepository endingCardRepository;
    private final StoryCardRepository storyCardRepository;


    //결말 카드 데이터 캐싱
    @Cacheable(value = "endingCardCache" , key ="'allEndingCard'")
    public CachingEndingCard getEndingCardAll(){
        log.info("getEndingCardAll called");

        List<EndingCard> entities = endingCardRepository.findAll();

        return new CachingEndingCard(entities);
    }


    //스토리 카드 데이터 캐싱
    @Cacheable(value = "storyCardCache" , key = "'allStoryCard'")
    public CachingStoryCard getStoryCardAll(){
        log.info("getStoryCardAll called");

        List<StoryCard> entities = storyCardRepository.findAll();

        return new CachingStoryCard(entities);
    }


    //캐시 데이터
    @Cacheable(value = "cardVariantsCache", key = "'allVariants'")
    public CachingVariants getCardVariantsAll() {

        log.info("Fetching card variants from database");
        List<StoryCardVariants> entities = storyCardVariantsRepository.findAll();

        return new CachingVariants(entities);
    }

}
