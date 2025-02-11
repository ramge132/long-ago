package com.example.b101.service;

import com.example.b101.cache.Game;
import com.example.b101.common.ApiResponseUtil;
import com.example.b101.domain.PlayerStatus;
import com.example.b101.domain.StoryCard;
import com.example.b101.domain.StoryCardVariants;
import com.example.b101.dto.FilteringRequest;
import com.example.b101.repository.GameRepository;
import com.vane.badwordfiltering.BadWordFiltering;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class FilteringService {

    private final GameRepository gameRepository;
    private final CachingService cachingService;
    private final BadWordFiltering badWordFiltering = new BadWordFiltering();

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

        List<StoryCardVariants> storyCardVariantsList = cachingService.getCardVariantsAll().getStoryCardVariants();


        // 플레이어 상태의 모든 StoryCard id 가져오기
        List<Integer> playerStoryCardIds = playerStatus.getStoryCards().stream()
                .map(StoryCard::getId)
                .toList();


        // 플레이어가 가진 모든 카드의 변형어들을 가져옴.
        List<String> allVariants = storyCardVariantsList.stream()
                .filter(variant -> playerStoryCardIds.contains(variant.getStoryCard().getId()))
                .map(StoryCardVariants::getVariant)
                .toList();

        log.info(allVariants.toString());


        boolean isBadWord = badWordFiltering.blankCheck(filteringRequest.getUserPrompt());

        String changeStr = badWordFiltering.change(filteringRequest.getUserPrompt(),new String[] {"*", " ", ".", ",", "-", "_", "+", "=", "~", "!", "@", "#", "$", "%", "^", "&", "(", ")", "[", "]", "{", "}",
                "|", "/", ":", ";", "'", "<", ">", "?", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"});


        if(isBadWord || changeStr.contains("*")) {
            return ApiResponseUtil.failure("Prompt에 욕설이 사용되었습니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }


        // prompt에 사용자가 낸 card 외에 소지하고 있는 card의 변형어들을 포함하고 있는지 확인
        long keywordCnt = allVariants.stream()
                .filter(variant -> filteringRequest.getUserPrompt().contains(variant))
                .count();



        if (keywordCnt > 1) {
            return ApiResponseUtil.failure("Prompt에 중복된 카드가 사용되었습니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }
        else if(keywordCnt < 1) {
            return ApiResponseUtil.failure("Prompt에 소유한 카드가 사용되지 않았습니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        String usedKeyword = allVariants.stream()
                .filter(variant -> filteringRequest.getUserPrompt().contains(variant))
                .findFirst()
                .orElse(null);

        int userCardId = storyCardVariantsList.stream()
                .filter(storyCardVariants -> storyCardVariants.getVariant().equals(usedKeyword))
                .map(storyCardVariants -> storyCardVariants.getStoryCard().getId())
                .findFirst()
                .orElse(-1);


        // 성공 응답
        return ApiResponseUtil.success(userCardId,"Prompt 필터링 성공",
                HttpStatus.OK,
                request.getRequestURI());
    }



}
