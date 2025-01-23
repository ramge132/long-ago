package com.example.b101.service;

import com.example.b101.domain.EndingCard;
import com.example.b101.repository.EndingCardRepository;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;

@Service
public class CardService {

    private final EndingCardRepository endingCardRepository;
    private List<EndingCard> cardList;

    public CardService(EndingCardRepository endingCardRepository){
        this.endingCardRepository = endingCardRepository;
        this.cardList = endingCardRepository.findAll();
    }


    public void shuffleCard(HttpServletRequest request) {
        System.out.println("기존 카드리스트 : "+cardList);
        Collections.shuffle(cardList);
        System.out.println("셔플 후 카드리스트 : "+cardList);
    }



}
