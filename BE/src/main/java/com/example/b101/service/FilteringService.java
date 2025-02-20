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
import kr.co.shineware.nlp.komoran.constant.DEFAULT_MODEL;
import kr.co.shineware.nlp.komoran.core.Komoran;
import kr.co.shineware.nlp.komoran.model.KomoranResult;
import kr.co.shineware.nlp.komoran.model.Token;
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
            log.error("[findCardVariantsByCardId] 게임을 찾을 수 없음 - gameId: {}", filteringRequest.getGameId());
            return ApiResponseUtil.failure("해당 gameId는 존재하지 않습니다.", HttpStatus.BAD_REQUEST, request.getRequestURI());
        }

        // 사용자 상태 확인
        PlayerStatus playerStatus = game.getPlayerStatuses().stream()
                .filter(player -> player.getUserId().equals(filteringRequest.getUserId()))
                .findFirst()
                .orElse(null);

        if (playerStatus == null) {
            log.error("[findCardVariantsByCardId] 플레이어를 찾을 수 없음 - userId: {}", filteringRequest.getUserId());
            return ApiResponseUtil.failure("해당 userId는 게임에 존재하지 않습니다.", HttpStatus.BAD_REQUEST, request.getRequestURI());
        }

        // 스토리 카드 변형어 데이터 로드
        List<StoryCardVariants> storyCardVariantsList = cachingService.getCardVariantsAll().getStoryCardVariants();
        if (storyCardVariantsList == null || storyCardVariantsList.isEmpty()) {
            log.warn("[findCardVariantsByCardId] 스토리 카드 변형어 데이터 없음");
        }

        // 플레이어가 가진 모든 StoryCard ID 가져오기
        List<Integer> playerStoryCardIds = playerStatus.getStoryCards().stream()
                .map(StoryCard::getId)
                .toList();

        if (playerStoryCardIds.isEmpty()) {
            log.warn("[findCardVariantsByCardId] 플레이어가 가진 StoryCard가 없음 - userId: {}", filteringRequest.getUserId());
        }

        // 플레이어가 가진 모든 카드의 변형어들을 가져옴.
        List<String> allVariants = storyCardVariantsList.stream()
                .filter(variant -> playerStoryCardIds.contains(variant.getStoryCard().getId()))
                .map(StoryCardVariants::getVariant)
                .toList();

        log.info("[findCardVariantsByCardId] 플레이어가 가진 카드 변형어 리스트: {}", allVariants);


        // 사용자 입력값(프롬프트)에서 욕설 필터링
        boolean isBadWord = badWordFiltering.check(filteringRequest.getUserPrompt());

        String changeStr = badWordFiltering.change(filteringRequest.getUserPrompt(), new String[] {
                "*", ".", ",", "-", "_", "+", "=", "~", "!", "@", "#", "$", "%", "^", "&", "(", ")", "[", "]", "{", "}",
                "|", "/", ":", ";", "'", "<", ">", "?", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
        });

        if (isBadWord || changeStr.contains("*")) {
            log.warn("[findCardVariantsByCardId] 욕설 감지됨 - 변환된 문자열: {}", changeStr);
            return ApiResponseUtil.failure("욕설이 사용되었습니다.", HttpStatus.BAD_REQUEST, request.getRequestURI());
        }


        Komoran komoran = new Komoran(DEFAULT_MODEL.LIGHT);

        KomoranResult analyzeResultList = komoran.analyze(filteringRequest.getUserPrompt());

        List<Token> tokenList = analyzeResultList.getTokenList();

        for (Token token : tokenList) {
            log.info(token.getMorph());
        }

        long keywordCnt = allVariants.stream()
                .filter(variant -> tokenList.stream().anyMatch(token -> token.getMorph().contains(variant)))
                .count();

        if (keywordCnt > 1) {
            return ApiResponseUtil.failure("중복된 카드가 사용되었습니다.", HttpStatus.BAD_REQUEST, request.getRequestURI());
        } else if (keywordCnt < 1) {
            return ApiResponseUtil.failure("플레이어가 소유한 카드가 사용되지 않았습니다.", HttpStatus.BAD_REQUEST, request.getRequestURI());
        }

        // 사용한 카드 찾기
        Integer userCardId = storyCardVariantsList.stream()
                .filter(variant -> playerStoryCardIds.contains(variant.getStoryCard().getId()) && tokenList.stream().anyMatch(token -> token.getMorph().contains(variant.getVariant())))
                .map(storyCardVariants -> storyCardVariants.getStoryCard().getId())
                .findFirst()
                .orElse(null);

        if (userCardId == null) {
            return ApiResponseUtil.failure("사용한 카드가 정확하지 않습니다.", HttpStatus.BAD_REQUEST, request.getRequestURI());
        }

        log.info("[findCardVariantsByCardId] 사용자가 사용한 카드 ID: {}", userCardId);

        return ApiResponseUtil.success(userCardId, "필터링 성공", HttpStatus.OK, request.getRequestURI());

    }
}
