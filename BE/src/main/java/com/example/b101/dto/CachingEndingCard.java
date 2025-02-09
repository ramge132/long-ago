package com.example.b101.dto;

import com.example.b101.domain.EndingCard;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@Builder
@AllArgsConstructor
public class CachingEndingCard {

    List<EndingCard> endingCards;
}
