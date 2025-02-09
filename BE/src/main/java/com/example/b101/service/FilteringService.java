package com.example.b101.service;

import com.example.b101.cache.Game;
import com.example.b101.common.ApiResponseUtil;
import com.example.b101.domain.PlayerStatus;
import com.example.b101.domain.StoryCard;
import com.example.b101.domain.StoryCardVariants;
import com.example.b101.dto.FilteringRequest;
import com.example.b101.repository.GameRepository;
import com.example.b101.repository.StoryCardVariantsRepository;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class FilteringService {

    private final StoryCardVariantsRepository storyCardVariantsRepository;
    private final GameRepository gameRepository;

    public ResponseEntity<?> findCardVariantsByCardId(FilteringRequest filteringRequest, HttpServletRequest request) {
        // 게임 존재 여부 확인
        Game game = gameRepository.findById(filteringRequest.getGameId());
        if (game == null) {
            return ApiResponseUtil.failure("해당 gameId는 존재하지 않습니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        // 사용자 상태 확인
        PlayerStatus playerStatus = game.getPlayerStatuses().stream()
                .filter(player -> player.getUserId().equals(filteringRequest.getUserId()))
                .findFirst()
                .orElse(null);

        if (playerStatus == null) {
            return ApiResponseUtil.failure("해당 userId는 게임에 존재하지 않습니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }


        // 카드 id로 변형어 가져오기
        List<String> variants = storyCardVariantsRepository.findByStoryCardId(filteringRequest.getCardId()).stream()
                .map(StoryCardVariants::getVariant)
                .toList();

        // 플레이어 상태의 모든 StoryCard id 가져오기
        List<Integer> playerStoryCardIds = playerStatus.getStoryCards().stream()
                .map(StoryCard::getId)
                .toList();


        // 플레이어가 가진 모든 카드의 변형어들을 가져옴.
        List<String> allVariants = storyCardVariantsRepository.findAllByStoryCardIdIn(playerStoryCardIds).stream()
                .map(StoryCardVariants::getVariant)
                .toList();


        // prompt가 사용자가 낸 card의 변형어를 포함하고 있는지 확인
        boolean isOk = variants.stream().anyMatch(variant -> filteringRequest.getUserPrompt().contains(variant));

        if (!isOk) {
            return ApiResponseUtil.failure("Prompt에 선택한 카드가 사용되지 않았습니다..",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        // prompt에 사용자가 낸 card 외에 소지하고 있는 card의 변형어들을 포함하고 있는지 확인
        boolean isNotOk = allVariants.stream().anyMatch(variant -> !variants.contains(variant) && filteringRequest.getUserPrompt().contains(variant));

        if (isNotOk) {
            return ApiResponseUtil.failure("Prompt에 중복된 카드가 사용되었습니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        // 성공 응답
        return ApiResponseUtil.success(true,"Prompt 필터링 성공",
                HttpStatus.OK,
                request.getRequestURI());
    }
}
