package com.example.b101.service;

import com.example.b101.common.ApiResponseUtil;
import com.example.b101.domain.EndingCard;
import com.example.b101.domain.Game;
import com.example.b101.domain.PlayerStatus;
import com.example.b101.domain.StoryCard;
import com.example.b101.dto.CreateGame;
import com.example.b101.repository.GameRepository;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
@RequiredArgsConstructor // 생성자 자동 주입
public class GameService {

    private final GameRepository gameRepository;
    private final CardService cardService;

    /**
     * 게임을 생성하고 Redis에 저장
     */
    public ResponseEntity<?> save(CreateGame createGame, HttpServletRequest request) {
        int playerCount = createGame.getPlayer().size();

        if (playerCount == 0) {
            return ApiResponseUtil.failure("플레이어 수가 0명입니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        // 카드 셔플
        List<EndingCard> endingCards = cardService.shuffleEndingCard();
        List<List<StoryCard>> storyCardList = cardService.shuffleStoryCard(playerCount);

        // 플레이어 상태 생성
        List<PlayerStatus> playerStatuses = assignCardsToPlayers(createGame, endingCards, storyCardList);

        // Game 객체 생성
        Game game = Game.builder()
                .gameId(UUID.randomUUID().toString())
                .endingCardlist(endingCards)
                .playerStatuses(playerStatuses)
                .ttl(3600L) // 1시간(3600초) 동안 유효
                .build();

        // 게임 초기 데이터 Redis에 저장
        gameRepository.save(game);


        return ApiResponseUtil.success(game, "게임 생성", HttpStatus.CREATED, request.getRequestURI());
    }

    /**
     * 각 플레이어에게 카드를 배정하여 PlayerStatus 생성
     */
    private List<PlayerStatus> assignCardsToPlayers(CreateGame createGame, List<EndingCard> endingCards, List<List<StoryCard>> storyCardList) {
        List<PlayerStatus> playerStatuses = new ArrayList<>();

        for (int i = 0; i < createGame.getPlayer().size(); i++) {
            String userId = createGame.getPlayer().get(i);
            List<StoryCard> playerCards = new ArrayList<>();
            Set<Integer> usedAttributes = new HashSet<>(); // 이미 받은 속성 저장

            // 1) 인물 카드 1장 배분
            playerCards.add(storyCardList.get(0).remove(0));
            usedAttributes.add(0); // 인물 카드 사용 표시


            // 2) 속성 리스트 랜덤 섞기 (사물, 장소, 사건, 상태)
            List<Integer> attributeIndices = Arrays.asList(1, 2, 3, 4);
            Collections.shuffle(attributeIndices);

            // 3) 중복 속성을 방지하며 3장 배분
            for (int j = 0; j < 3; j++) {
                for (int index : attributeIndices) {
                    if (!usedAttributes.contains(index)) {  //set의 contains 연산은 O(1)
                        playerCards.add(storyCardList.get(index).remove(0));
                        usedAttributes.add(index); // 속성 사용 표시
                        break; // 한 개의 속성을 추가했으면 다음 속성으로 이동
                    }
                }
            }

            playerStatuses.add(PlayerStatus.builder()
                    .userId(userId)
                    .storyCards(playerCards)
                    .life(4)
                    .endingCard(endingCards.get(i))
                    .score(0)
                    .build());

        }

        return playerStatuses;
    }


    public ResponseEntity<?> delete(String gameId, HttpServletRequest request) {
        Game game = gameRepository.findById(gameId);
        if (game == null) {
            return ApiResponseUtil.failure("해당 gameId는 존재하지 않습니다."
            , HttpStatus.BAD_REQUEST, request.getRequestURI());
        }

        gameRepository.delete(game);
        return ApiResponseUtil.success(null,
                "게임 데이터 삭제 성공",
                HttpStatus.OK,
                request.getRequestURI());
    }


    public ResponseEntity<?> findById(String gameId, HttpServletRequest request) {
        Game game = gameRepository.findById(gameId);
        if (game == null) {
            return ApiResponseUtil.failure("해당 gameId는 존재하지 않습니다.",
                    HttpStatus.BAD_REQUEST, request.getRequestURI());
        }
        
        return ApiResponseUtil.success(game,
                "게임 데이터 불러오기 성공",
                HttpStatus.OK,
                request.getRequestURI());
    }
}
