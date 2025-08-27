package com.example.b101.service;

import com.example.b101.cache.Game;
import com.example.b101.cache.SceneRedis;
import com.example.b101.common.ApiResponseUtil;
import com.example.b101.config.WebClientConfig;
import com.example.b101.domain.*;
import com.example.b101.dto.*;
import com.example.b101.repository.BookRepository;
import com.example.b101.repository.GameRepository;
import com.example.b101.repository.RedisSceneRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientException;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor // 생성자 자동 주입
public class GameService {

    private final GameRepository gameRepository;
    private final CardService cardService;
    private final RedisSceneRepository sceneRepository;
    private final WebClient webClient;
    @Qualifier("openaiWebClient")
    private final WebClient openaiWebClient;
    @Qualifier("geminiWebClient")
    private final WebClient geminiWebClient;
    private final S3service s3service;
    private final BookRepository bookRepository;
    private final WebClientConfig webClientConfig;
    private final ObjectMapper objectMapper = new ObjectMapper();


    //시연용
    public ResponseEntity<?> createGame(GameRequest gameRequest,HttpServletRequest request) {
        int playerCnt = gameRequest.getPlayer().size();

        if(playerCnt < 2) {
            return ApiResponseUtil.failure("플레이어 수가 2인 미만입니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        List<EndingCard> endingCards = cardService.getEndingCards();
        List<List<StoryCard>> storyCards = cardService.getStoryCards(playerCnt);


        List<PlayerStatus> playerStatuses = getPlayerStatuses(gameRequest,storyCards,endingCards,playerCnt);

        Game game = Game.builder()
                .gameId(UUID.randomUUID().toString())
                .endingCardlist(endingCards)
                .playerStatuses(playerStatuses)
                .drawingStyle(gameRequest.getDrawingStyle())
                .build();

        gameRepository.save(game);

        GameResponse gameResponse = GameResponse.builder()
                .gameId(game.getGameId())
                .status(game.getPlayerStatuses().stream().filter(player -> player.getUserId().equals(gameRequest.getBossId())).findFirst().orElse(null))
                .build();

        return ApiResponseUtil.success(gameResponse, "게임 생성", HttpStatus.CREATED, request.getRequestURI());
    }


    //시연용 카드 분배 로직
    public List<PlayerStatus> getPlayerStatuses(GameRequest gameRequest,List<List<StoryCard>> storyCards, List<EndingCard> endingCards, int playerCnt) {
        List<PlayerStatus> playerStatuses = new ArrayList<>();
        for(int i=0; i<playerCnt; i++) {
            PlayerStatus playerStatus = new PlayerStatus();
            playerStatus.setUserId(gameRequest.getPlayer().get(i)); //userId 설정

            List<StoryCard> storyCardList = new ArrayList<>();
            for(int j=0; j<4; j++){
                StoryCard storyCard = storyCards.get(j).get(i);
                storyCardList.add(storyCard);

            }

            EndingCard endingCard = endingCards.remove(0);

            playerStatus.setEndingCard(endingCard);
            playerStatus.setStoryCards(storyCardList);

            playerStatuses.add(playerStatus);
        }

        return playerStatuses;
    }

    /**
     * 게임을 생성하고 Redis에 저장
     */
    public ResponseEntity<?> saveGame(GameRequest gameRequest, HttpServletRequest request) {
        int playerCount = gameRequest.getPlayer().size();

        if (playerCount < 2) {
            return ApiResponseUtil.failure("플레이어 수가 2명 미만입니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        // 카드 셔플
        List<EndingCard> endingCards = cardService.shuffleEndingCard();
        List<List<StoryCard>> storyCardList = cardService.shuffleStoryCard(playerCount);

        // 플레이어 상태 생성
        List<PlayerStatus> playerStatuses = assignCardsToPlayers(gameRequest, endingCards, storyCardList);

        // Game 객체 생성
        String gameId = UUID.randomUUID().toString();
        Game game = Game.builder()
                .gameId(gameId)
                .endingCardlist(endingCards)
                .playerStatuses(playerStatuses)
                .drawingStyle(gameRequest.getDrawingStyle())
                .build();

        // 게임 초기 데이터 Redis에 저장 (비동기 가능)
        gameRepository.save(game);



        GameResponse gameResponse = GameResponse.builder()
                .gameId(game.getGameId())
                .status(game.getPlayerStatuses().stream().filter(player -> player.getUserId().equals(gameRequest.getBossId())).findFirst().orElse(null))
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
                    .endingCard(endingCards.remove(0))
                    .build());

        }

        return playerStatuses;
    }



    public ResponseEntity<?> finishGame(DeleteGameRequest deleteGameRequest, HttpServletRequest request) {
        //해당 gameId의 게임을 조회
        Game game = gameRepository.findById(deleteGameRequest.getGameId());

        if (game == null) {
            return ApiResponseUtil.failure("해당 gameId는 존재하지 않습니다."
                    , HttpStatus.BAD_REQUEST, request.getRequestURI());
        }

        List<SceneRedis> sceneRedisList = sceneRepository.findAllByGameId(deleteGameRequest.getGameId());


        int status = deleteGameRequest.isForceStopped() ? 2 : 1;

        GenerateSceneRequest generateSceneRequest = GenerateSceneRequest.builder()
                .session_id(deleteGameRequest.getGameId())
                .game_mode(game.getDrawingStyle())
                .user_sentence("")
                .status(status)
                .build();

        //정상적인 게임 종료 시 책 표지를 반환
        if(!deleteGameRequest.isForceStopped()){

            // 새로운 API 시스템: OpenAI GPT + Gemini로 표지 생성
            String bookTitle;
            byte[] coverImageBytes;
            
            try {
                // 1단계: 스토리 요약 및 제목 생성
                bookTitle = generateBookTitle(sceneRedisList);
                log.info("GPT로 생성된 책 제목: {}", bookTitle);
                
                // 2단계: 표지 이미지 생성 
                coverImageBytes = generateCoverImage(bookTitle, game.getDrawingStyle());
                log.info("Gemini로 생성된 표지 이미지 크기: {} bytes", coverImageBytes.length);
                
            } catch (Exception e) {
                log.error("표지 생성 중 오류: {}", e.getMessage());
                return ApiResponseUtil.failure("표지 생성 중 오류 발생: " + e.getMessage(),
                        HttpStatus.INTERNAL_SERVER_ERROR,
                        request.getRequestURI());
            }


            //정상적인 게임 종료 시 책표지 생성
            SceneRedis scene = SceneRedis.builder()
                    .id(UUID.randomUUID().toString())
                    .gameId(deleteGameRequest.getGameId())
                    .image(coverImageBytes)  // 새 API로 생성된 바이너리 이미지 데이터 저장
                    .sceneOrder(0) //책 표지는 순서가 0
                    .build();

            sceneRepository.save(scene); //책 표지를 0번으로 저장

            Book book = Book.builder()
                    .bookId(UUID.randomUUID().toString())
                    .title(bookTitle)
                    .build();

            //S3에 업로드
            boolean result = s3service.uploadToS3(deleteGameRequest.getGameId(),book.getBookId()); //s3에 이미지들 저장

            if (!result) {
                log.error("s3 이미지 저장 실패");
                sceneRepository.deleteAllByGameId(deleteGameRequest.getGameId());
                return ApiResponseUtil.failure("s3에 이미지 저장 중 에러 발생",
                        HttpStatus.INTERNAL_SERVER_ERROR,
                        request.getRequestURI());
            }

            String baseUrl = ServletUriComponentsBuilder.fromRequestUri(request)
                    .replacePath(null)
                    .build()
                    .toUriString();


            List<Scene> sceneList = sceneRedisList.stream()
                    .filter(sceneRedis -> sceneRedis.getSceneOrder() != 0)
                    .map(sceneRedis -> {
                        Scene scene1 = new Scene(
                                sceneRedis.getSceneOrder(),
                                sceneRedis.getPrompt(),
                                baseUrl + "/images/s3/downloadFromS3?objectKey=" + book.getBookId() + "/" + sceneRedis.getSceneOrder() + ".png"
                        );
                        scene1.setBook(book);
                        return scene1;
                    })
                    .toList();

            book.setImageUrl(baseUrl+"/images/s3/downloadFromS3?objectKey="+book.getBookId()+"/0.png"); //책 표지 url
            book.setScenes(sceneList);


            bookRepository.save(book);

            //redis에 저장됐던 scene 데이터들 삭제
            sceneRepository.deleteAllByGameId(deleteGameRequest.getGameId());

            //게임 데이터 삭제
            gameRepository.delete(game);


            FinishGameResponse finishGameResponse = FinishGameResponse.builder()
                    .bookId(book.getBookId())
                    .bookCover(book.getImageUrl())
                    .title(book.getTitle())
                    .build();

            return ApiResponseUtil.success(finishGameResponse,"책 생성 완료"
                    ,HttpStatus.CREATED,request.getRequestURI());
        }


        try {
            webClient.post()  //post형식으로 webClient의 요청을 보냄.
                    .uri("/generate").accept(MediaType.APPLICATION_JSON) //json으로 응답받음.
                    .bodyValue(generateSceneRequest) //RequestBody로 보낼 객체
                    .retrieve()
                    .bodyToMono(String.class) //응답의 본문(body)만 가져옴.
                    .block(); //이미지를 다 받고 프론트에 보내야 하므로 동기방식 채택
        } catch (WebClientException e) { //GPU 서버에서 에러 반환 시
            return ApiResponseUtil.failure("GPU 서버 통신 중 오류 발생 : ",
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    request.getRequestURI());
        }

        //redis에 저장됐던 scene 데이터들 삭제
        sceneRepository.deleteAllByGameId(deleteGameRequest.getGameId());

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

                return ApiResponseUtil.success(playerStatus.getEndingCard(),
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
    
    /**
     * OpenAI GPT를 사용하여 스토리를 요약하고 책 제목 생성
     */
    private String generateBookTitle(List<SceneRedis> sceneRedisList) {
        try {
            // 스토리 요약 생성
            String storyContent = sceneRedisList.stream()
                    .filter(scene -> scene.getSceneOrder() > 0) // 표지(0번) 제외
                    .sorted(Comparator.comparingInt(SceneRedis::getSceneOrder))
                    .map(SceneRedis::getPrompt)
                    .collect(Collectors.joining(". "));
            
            // OpenAI GPT API 요청 구조
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("model", "gpt-4o-mini");
            requestBody.put("max_tokens", 50);
            requestBody.put("temperature", 0.7);
            
            // 메시지 구조
            Map<String, Object> systemMessage = new HashMap<>();
            systemMessage.put("role", "system");
            systemMessage.put("content", "당신은 스토리를 요약하고 매력적인 제목을 만드는 전문가입니다. 주어진 스토리 내용을 바탕으로 10자 이내의 간결하고 매력적인 한국어 제목을 만들어주세요. 제목만 답해주세요.");
            
            Map<String, Object> userMessage = new HashMap<>();
            userMessage.put("role", "user");
            userMessage.put("content", "다음 스토리를 요약하여 10자 이내의 제목을 만들어주세요: " + storyContent);
            
            requestBody.put("messages", List.of(systemMessage, userMessage));
            
            // OpenAI API 호출
            String response = openaiWebClient.post()
                    .uri("https://api.openai.com/v1/chat/completions")
                    .bodyValue(requestBody)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();
            
            // 응답 파싱
            JsonNode responseJson = objectMapper.readTree(response);
            if (responseJson.has("choices") && responseJson.get("choices").size() > 0) {
                return responseJson.get("choices").get(0).get("message").get("content").asText().trim();
            }
            
            log.warn("GPT 응답에서 제목 추출 실패, 기본 제목 사용");
            return "우리의 이야기";
            
        } catch (Exception e) {
            log.error("GPT API 호출 실패: {}", e.getMessage());
            return "우리의 이야기"; // 실패시 기본 제목 반환
        }
    }
    
    /**
     * Gemini 2.5 Flash Image Preview를 사용하여 표지 이미지 생성
     */
    private byte[] generateCoverImage(String bookTitle, int drawingStyle) {
        try {
            // 그림체 모드에 따른 스타일 정의
            String[] styles = {
                "애니메이션 스타일", "3D 카툰 스타일", "코믹 스트립 스타일", "클레이메이션 스타일",
                "크레용 드로잉 스타일", "픽셀 아트 스타일", "미니멀리스트 일러스트", "수채화 스타일", "스토리북 일러스트"
            };
            
            String style = drawingStyle < styles.length ? styles[drawingStyle] : "애니메이션 스타일";
            
            // 표지 이미지 프롬프트 생성
            String coverPrompt = "Create a beautiful book cover for a story titled '" + bookTitle + "'. " +
                    "Style: " + style + ". The cover should be artistic, captivating, and suitable for a storybook. " +
                    "Include the title text elegantly integrated into the design.";
            
            // Gemini 2.5 Flash Image Preview API 요청 구조
            Map<String, Object> requestBody = new HashMap<>();
            
            // contents 배열 구성
            Map<String, Object> content = new HashMap<>();
            Map<String, Object> part = new HashMap<>();
            part.put("text", "Generate an image: " + coverPrompt);
            content.put("parts", List.of(part));
            requestBody.put("contents", List.of(content));
            
            // Gemini 2.5 Flash Image Preview API 호출
            String apiUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key=" + webClientConfig.getGeminiApiKey();
            
            log.info("Gemini 표지 이미지 생성 호출: {}", apiUrl);
            
            String response = geminiWebClient.post()
                    .uri(apiUrl)
                    .bodyValue(requestBody)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();
            
            log.info("Gemini 표지 API 응답 받음: {}", response != null ? "응답 있음" : "응답 없음");
            
            // 응답 파싱
            JsonNode responseJson = objectMapper.readTree(response);
            if (responseJson.has("candidates") && responseJson.get("candidates").size() > 0) {
                JsonNode candidate = responseJson.get("candidates").get(0);
                
                if (candidate.has("content") && candidate.get("content").has("parts")) {
                    JsonNode parts = candidate.get("content").get("parts");
                    for (int i = 0; i < parts.size(); i++) {
                        JsonNode currentPart = parts.get(i);
                        
                        // inlineData 방식 확인
                        if (currentPart.has("inlineData") && currentPart.get("inlineData").has("data")) {
                            String base64Data = currentPart.get("inlineData").get("data").asText();
                            log.info("표지 Base64 이미지 데이터 발견, 길이: {}", base64Data.length());
                            return Base64.getDecoder().decode(base64Data);
                        }
                    }
                }
            }
            
            log.error("Gemini에서 표지 이미지 데이터를 찾을 수 없음");
            throw new RuntimeException("Gemini 2.5 Flash Image Preview에서 표지 이미지 생성 실패");
            
        } catch (Exception e) {
            log.error("Gemini 표지 이미지 생성 실패: {}", e.getMessage(), e);
            throw new RuntimeException("표지 이미지 생성 실패: " + e.getMessage());
        }
    }


}