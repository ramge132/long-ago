package com.example.b101.service;

import com.example.b101.domain.EndingCard;
import com.example.b101.domain.StoryCard;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

@Slf4j
@Service
@AllArgsConstructor
public class CardService {

    private final CachingService cachingService;

    //시연용 결말 카드
    public List<EndingCard> getEndingCards() {
        return cachingService.getEndingCardAll().getEndingCards();
    }


    //시연용 이야기 카드
    public List<List<StoryCard>> getStoryCards(int playerCnt) {
        List<List<StoryCard>> cards = new ArrayList<>();

        List<String> attribute = Arrays.asList("인물","사물","장소","상태");

        for(String attributeName : attribute) {
            cards.add(getStoryCardByAttribute(attributeName,playerCnt));
        }

        return cards;
    }


    //시연용 이야기 카드 속성별 분배
    public List<StoryCard> getStoryCardByAttribute(String attribute, int playerCnt) {

        return cachingService.getStoryCardAll().getStoryCards()
                .stream()
                .filter(storyCard -> storyCard.getAttribute().equals(attribute))
                .toList()
                .subList(0, playerCnt);
    }






    // 결말 카드 셔플
    public List<EndingCard> shuffleEndingCard() {
        log.info("[shuffleEndingCard] 결말 카드 데이터를 가져오는 중...");

        List<EndingCard> cardList = cachingService.getEndingCardAll().getEndingCards();
        log.info("[shuffleEndingCard] {}개의 결말 카드 로드 완료", cardList.size());

        Collections.shuffle(cardList);
        log.info("[shuffleEndingCard] 결말 카드 셔플 완료");

        return cardList;
    }

    // 이야기 카드 셔플
    public List<List<StoryCard>> shuffleStoryCard(int playerCnt) {
        log.info("[shuffleStoryCard] 플레이어 수: {}", playerCnt);

        List<List<StoryCard>> shuffledCards = new ArrayList<>();

        // "인물" 카테고리 카드 가져와서 셔플 후 사람 수 만큼 저장
        shuffledCards.add(fetchAndShuffleCards("인물", playerCnt));

        // 나머지 속성 리스트 섞기
        List<String> attributes = Arrays.asList("사물", "장소", "사건", "상태");

        // 나머지 속성 카테고리별 카드 가져와서 셔플 후 저장
        for (String attribute : attributes) {
            shuffledCards.add(fetchAndShuffleCards(attribute, playerCnt));
        }

        log.info("[shuffleStoryCard] 이야기 카드 셔플 완료");
        return shuffledCards;
    }

    // 카테고리별 카드 리스트를 플레이어 수 만큼만 가져옴
    private List<StoryCard> fetchAndShuffleCards(String attribute, int playerCnt) {
        log.info("[fetchAndShuffleCards] '{}' 속성의 이야기 카드 가져오는 중...", attribute);

        List<StoryCard> cards = new ArrayList<>(cachingService.getStoryCardAll().getStoryCards()
                .stream()
                .filter(storyCard -> storyCard.getAttribute().equals(attribute))
                .toList());

        log.info("[fetchAndShuffleCards] '{}' 속성의 이야기 카드 {}개 로드 완료", attribute, cards.size());

        Collections.shuffle(cards);
        log.info("[fetchAndShuffleCards] '{}' 속성의 이야기 카드 셔플 완료", attribute);

        return cards.subList(0, playerCnt);
    }
}
