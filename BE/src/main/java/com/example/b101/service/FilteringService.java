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
import kr.co.shineware.nlp.komoran.model.Token;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class FilteringService {

    private final GameRepository gameRepository;
    private final CachingService cachingService;
    private final KomoranService komoranService;
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


        // 형태소 분석 (최적화된 서비스 사용)
        List<Token> tokenList = komoranService.analyze(filteringRequest.getUserPrompt());
        
        // 디버깅용 로그
        for (Token token : tokenList) {
            log.info("형태소: {}, 품사: {}", token.getMorph(), token.getPos());
        }
        
        // 디버깅: 매칭된 변형어들 확인
        List<String> matchedVariants = storyCardVariantsList.stream()
                .filter(variant -> playerStoryCardIds.contains(variant.getStoryCard().getId()) && 
                        isVariantMatched(variant.getVariant(), tokenList, filteringRequest.getUserPrompt()))
                .map(StoryCardVariants::getVariant)
                .toList();
        log.info("[findCardVariantsByCardId] 매칭된 변형어들: {}", matchedVariants);
        
        // 개선된 매칭 알고리즘: 카드별로 그룹핑하여 중복 체크
        Set<Integer> matchedCardIds = storyCardVariantsList.stream()
                .filter(variant -> playerStoryCardIds.contains(variant.getStoryCard().getId()) && 
                        isVariantMatched(variant.getVariant(), tokenList, filteringRequest.getUserPrompt()))
                .map(variant -> variant.getStoryCard().getId())
                .collect(Collectors.toSet());
        
        log.info("[findCardVariantsByCardId] 매칭된 카드 ID들: {}, 개수: {}", matchedCardIds, matchedCardIds.size());

        if (matchedCardIds.size() > 1) {
            return ApiResponseUtil.failure("카드는 1장만 사용해야 합니다.", HttpStatus.BAD_REQUEST, request.getRequestURI());
        } else if (matchedCardIds.size() < 1) {
            return ApiResponseUtil.failure("플레이어가 소유한 카드가 사용되지 않았습니다.", HttpStatus.BAD_REQUEST, request.getRequestURI());
        }

        // 사용한 카드 찾기 (이미 매칭된 카드 ID 사용)
        Integer userCardId = matchedCardIds.iterator().next(); // Set에 하나의 요소가 있음을 보장

        // userCardId가 null일 수 없음 (이미 matchedCardIds.size() == 1 확인함)

        log.info("[findCardVariantsByCardId] 사용자가 사용한 카드 ID: {}", userCardId);

        return ApiResponseUtil.success(userCardId, "필터링 성공", HttpStatus.OK, request.getRequestURI());
    }

    /**
     * 개선된 변형어 매칭 알고리즘
     * 
     * @param variant 카드 변형어
     * @param tokenList 형태소 분석 결과
     * @param originalText 원본 텍스트
     * @return 매칭 여부
     */
    private boolean isVariantMatchedStrict(String variant, List<Token> tokenList, String originalText) {
        if (variant == null || variant.trim().isEmpty()) {
            return false;
        }
        
        // 1. 완전 매칭 (원본 텍스트에서 직접 찾기)
        if (originalText.contains(variant)) {
            log.debug("완전 매칭 성공: {}", variant);
            return true;
        }
        
        // 2. 형태소 완전 매칭 (형태소 분석 결과와 정확히 일치)
        for (Token token : tokenList) {
            if (token.getMorph().equals(variant)) {
                log.debug("형태소 완전 매칭 성공: {} = {}", token.getMorph(), variant);
                return true;
            }
        }
        
        // 3. 부분 매칭 (안전한 경우만)
        for (Token token : tokenList) {
            String morph = token.getMorph();
            
            // 3-1. 변형어가 형태소보다 긴 경우 (예: "들뜬"이 "들뜸"을 포함)
            if (variant.length() > morph.length() && variant.contains(morph)) {
                // 최소 길이 제한 (너무 짧은 부분 매칭 방지)
                if (morph.length() >= 2) {
                    log.debug("역방향 부분 매칭 성공: {} contains {}", variant, morph);
                    return true;
                }
            }
            
            // 3-2. 형태소가 변형어보다 긴 경우 (예: "잘생긴"이 "잘생"을 포함)
            if (morph.length() > variant.length() && morph.contains(variant)) {
                // 안전한 부분 매칭: 변형어가 충분히 길고 어근이 확실한 경우
                if (variant.length() >= 3 && !isSafePartialMatch(variant)) {
                    continue; // 위험한 부분 매칭은 건너뛰기
                }
                log.debug("순방향 부분 매칭 성공: {} contains {}", morph, variant);
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * 안전한 부분 매칭인지 확인
     * 
     * @param variant 변형어
     * @return 안전한 부분 매칭 여부
     */
    private boolean isSafePartialMatch(String variant) {
        // 위험한 부분 매칭 패턴들 (예: "지루" -> "지루하다"의 다른 의미 방지)
        String[] dangerousPatterns = {
                "지루", "무료", "고요", "평온", "차분", "조용",
                "시원", "따뜻", "차가", "뜨거", "새로", "예쁘"
        };
        
        for (String dangerous : dangerousPatterns) {
            if (variant.equals(dangerous)) {
                log.debug("위험한 부분 매칭 차단: {}", variant);
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * 매우 엄격한 변형어 매칭 (디버깅용)
     */
    private boolean isVariantMatched(String variant, List<Token> tokenList, String originalText) {
        if (variant == null || variant.trim().isEmpty()) {
            return false;
        }
        
        log.debug("변형어 매칭 체크: '{}' in '{}'", variant, originalText);
        
        // 1. 완전 매칭 (원본 텍스트에서 직접 찾기)
        if (originalText.contains(variant)) {
            log.info("완전 매칭 성공: '{}' 발견", variant);
            return true;
        }
        
        // 2. 형태소 완전 매칭 (형태소 분석 결과와 정확히 일치)
        for (Token token : tokenList) {
            if (token.getMorph().equals(variant)) {
                log.info("형태소 완전 매칭 성공: '{}' = '{}'", token.getMorph(), variant);
                return true;
            }
        }
        
        log.debug("매칭 실패: '{}'", variant);
        return false;
    }
}
