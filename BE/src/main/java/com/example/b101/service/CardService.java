package com.example.b101.service;

import com.example.b101.domain.EndingCard;
import com.example.b101.domain.StoryCard;
import com.example.b101.repository.EndingCardRepository;
import com.example.b101.repository.StoryCardRepository;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

@Service
@AllArgsConstructor
public class CardService {

    private final EndingCardRepository endingCardRepository;
    private final StoryCardRepository storyCardRepository;


    public List<EndingCard> shuffleEndingCard() {
        List<EndingCard> cardList = endingCardRepository.findAll();
        Collections.shuffle(cardList);

        return cardList;
    }


    public List<List<StoryCard>> shuffleStoryCard(int playerCnt) {
        List<List<StoryCard>> shuffledCards = new ArrayList<>();

        // "인물" 카테고리 카드 가져와서 셔플 후 사람 수 만큼 저장
        shuffledCards.add(fetchAndShuffleCards("인물",playerCnt));

        // 나머지 속성 리스트 섞기
        List<String> attributes = Arrays.asList("사물", "장소", "사건", "상태");

        // 나머지 속성 카테고리별 카드 가져와서 셔플 후 저장.
        for (String attribute : attributes) {
            shuffledCards.add(fetchAndShuffleCards(attribute,playerCnt));
        }

        return shuffledCards;
    }

    private List<StoryCard> fetchAndShuffleCards(String attribute,int playerCnt) {
        List<StoryCard> cards = new ArrayList<>(storyCardRepository.findStoryCardsByAttribute(attribute));
        Collections.shuffle(cards);
        return cards.subList(0, playerCnt);
    }

}
