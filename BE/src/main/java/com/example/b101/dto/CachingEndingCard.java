package com.example.b101.dto;

import com.example.b101.domain.EndingCard;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CachingEndingCard {

    List<EndingCard> endingCards;
    
    public CachingEndingCard(List<EndingCard> endingCards) {
        this.endingCards = endingCards;
    }
}
