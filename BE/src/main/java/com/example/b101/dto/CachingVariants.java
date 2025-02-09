package com.example.b101.dto;

import com.example.b101.domain.StoryCardVariants;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@Builder
@AllArgsConstructor
public class CachingVariants{

    private List<StoryCardVariants> storyCardVariants;

}
