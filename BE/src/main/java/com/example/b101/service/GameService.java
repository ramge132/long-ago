package com.example.b101.service;

import com.example.b101.cache.Game;
import com.example.b101.common.ApiResponseUtil;
import com.example.b101.domain.EndingCard;
import com.example.b101.domain.PlayerStatus;
import com.example.b101.domain.StoryCard;
import com.example.b101.dto.GameRequest;
import com.example.b101.dto.GameResponse;
import com.example.b101.repository.GameRepository;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor // 생성자 자동 주입
public class GameService {

    private final GameRepository gameRepository;
    private final CardService cardService;


    /**
     * 게임을 생성하고 Redis에 저장
     */
    public ResponseEntity<?> save(GameRequest gameRequest, HttpServletRequest request) {
        int playerCount = gameRequest.getPlayer().size();

        if (playerCount < 2) {
            return ApiResponseUtil.failure("플레이어 수가 2명 미만입니다..",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        // 카드 셔플
        List<EndingCard> endingCards = cardService.shuffleEndingCard();
        List<List<StoryCard>> storyCardList = cardService.shuffleStoryCard(playerCount);

        // 플레이어 상태 생성
        List<PlayerStatus> playerStatuses = assignCardsToPlayers(gameRequest, endingCards, storyCardList);

        // Game 객체 생성
        Game game = Game.builder()
                .gameId(UUID.randomUUID().toString())
                .endingCardlist(endingCards)
                .playerStatuses(playerStatuses)
                .drawingStyle(gameRequest.getDrawingStyle())
                .build();

        // 게임 초기 데이터 Redis에 저장
        gameRepository.save(game);

        GameResponse gameResponse = GameResponse.builder()
                .gameId(game.getGameId())
                .status(gameRepository.getPlayerStatus(game.getGameId(), gameRequest.getBossId()))
                .build();


        return ApiResponseUtil.success(gameResponse, "게임 생성", HttpStatus.CREATED, request.getRequestURI());
    }

    /**
     * 각 플레이어에게 카드를 배정하여 PlayerStatus 생성
     */
    private List<PlayerStatus> assignCardsToPlayers(GameRequest gameRequest, List<EndingCard> endingCards, List<List<StoryCard>> storyCardList) {
        //플레이어 상태를 저장할 list
        List<PlayerStatus> playerStatuses = new ArrayList<>();

        //플레이어 수만큼 카드를 분배함.
        for (int i = 0; i < gameRequest.getPlayer().size(); i++) {

            String userId = gameRequest.getPlayer().get(i);

            List<StoryCard> storyCards = new ArrayList<>(); //플레이어가 가진 이야기 카드 리스트

            Set<Integer> usedAttributes = new HashSet<>(); // 이미 받은 속성을 Set의 저장.

            // 인물 카드 1장 배분
            // 1장을 갖자마자 이 게임의 이야기 카드 리스트에서는 삭제
            // 다른 사람과 카드가 중복되면 안되므로
            storyCards.add(storyCardList.get(0).remove(0));

            usedAttributes.add(0); // 인물 카드 사용 표시


            // (사물, 장소, 사건, 상태) 인덱스로 구분
            List<Integer> attributeIndices = Arrays.asList(1, 2, 3, 4);

            // 속성을 랜덤하게 섞음.
            Collections.shuffle(attributeIndices);

            // 중복 속성을 방지하며 3장 배분
            for (int j = 0; j < 3; j++) {

                for (int index : attributeIndices) {

                    //ArrayList의 contains 연산은 시간 복잡도 O(N)
                    //HashSet의 contains 연산은 시간 복잡도 O(1)
                    if (!usedAttributes.contains(index)) {

                        //storyCardList가 2차원 배열이기 때문에 get(index)를 하면 해당 index 속성을 가진 카드리스트들을 받아옴.
                        //remove는 값을 삭제하면서 삭제된 값을 반환함.
                        storyCards.add(storyCardList.get(index).remove(0));

                        usedAttributes.add(index); // 속성 사용 표시

                        break; // 한 개의 속성을 추가했으면 다음 속성으로 이동
                    }
                }
            }

            //빌더패턴을 이용해서 플레이어 상태 객체 생성
            playerStatuses.add(PlayerStatus.builder()
                    .userId(userId)
                    .storyCards(storyCards)
                    .endingCard(endingCards.get(i))
                    .build());

        }

        return playerStatuses;
    }



    public ResponseEntity<?> delete(String gameId, HttpServletRequest request) {
        //해당 gameId의 게임을 조회
        Game game = gameRepository.findById(gameId);
        
        if (game == null) {
            return ApiResponseUtil.failure("해당 gameId는 존재하지 않습니다."
                    , HttpStatus.BAD_REQUEST, request.getRequestURI());
        }

        //게임 데이터 삭제
        gameRepository.delete(game);
        
        return ApiResponseUtil.success(null,
                "게임 데이터 삭제 성공",
                HttpStatus.OK,
                request.getRequestURI());
    }


    //엔딩카드 리롤
    public ResponseEntity<?> shuffleEndingCard(String gameId, String userId, HttpServletRequest request) {
        //해당 gameId를 가진 게임을 찾는다.
        Game game = gameRepository.findById(gameId);

        if (game == null) {
            return ApiResponseUtil.failure("해당 gameId는 존재하지 않습니다."
                    , HttpStatus.BAD_REQUEST, request.getRequestURI());
        }

        List<PlayerStatus> playerStatuses = game.getPlayerStatuses();

        
        for (PlayerStatus playerStatus : playerStatuses) {
            //게임 플레이어 중의 userId가 있다면
            if (playerStatus.getUserId().equals(userId)) {
                
                //이 게임에서 사용되는 엔딩카드 리스트에서 한장을 뽑는다.
                playerStatus.setEndingCard(game.getEndingCardlist().get(0));
                
                //뽑은 카드는 엔딩카드 리스트에서 삭제한다.
                game.getEndingCardlist().remove(0);
                
                //game data를 업데이트 한다.
                gameRepository.update(game);

                return ApiResponseUtil.success(playerStatus,
                        "EndingCard 리롤 성공",
                        HttpStatus.OK,
                        request.getRequestURI());
            }
        }

        return ApiResponseUtil.failure("해당 userId는 존재하지 않습니다.",
                HttpStatus.BAD_REQUEST, request.getRequestURI());
    }

    
    //플레이어 상태 조회 (플레이어가 소유한 카드 조회)
    public ResponseEntity<?> playStatusFindById(String gameId, String userId, HttpServletRequest request) {
        
        //해당 gameId를 가진 게임이 없을 때
        if(gameRepository.findById(gameId) == null) {
            return ApiResponseUtil.failure("잘못된 gameId입니다.",
                    HttpStatus.BAD_REQUEST, request.getRequestURI());
        }

        //해당 userId를 가진 플레이어가 소유한 카드 조회
        PlayerStatus playerStatus = gameRepository.getPlayerStatus(gameId, userId);
        
        //null이라면 해당 userId가 없다는 것.
        if (playerStatus == null) {
            return ApiResponseUtil.failure("해당 userId는 게임에 존재 하지 않습니다.",
                    HttpStatus.BAD_REQUEST, request.getRequestURI());
        }


        return ApiResponseUtil.success(playerStatus,
                "플레이어 카드 상태 반환 성공",
                HttpStatus.OK,
                request.getRequestURI());
    }
}

