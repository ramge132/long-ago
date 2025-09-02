/*
SceneService.java 수정 예시
현재 이미지 생성 로직을 Python 서비스 호출로 변경
*/

@Service
@RequiredArgsConstructor
public class SceneService {

    private final WebClient pythonImageServiceClient;
    
    // Python 이미지 서비스 클라이언트 생성 (WebClientConfig에 추가)
    @Bean
    @Qualifier("pythonImageServiceClient") 
    public WebClient pythonImageServiceClient() {
        return WebClient.builder()
            .baseUrl("http://localhost:8190")  // Python 서비스 URL
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
            .build();
    }

    public ResponseEntity<?> createScene(SceneRequest sceneRequest, HttpServletRequest request) {
        // ... 기존 유효성 검사 코드 ...

        try {
            // BEFORE: 기존 Java 로직
            /*
            String gptPrompt = generatePromptWithGPT(sceneRequest.getUserPrompt(), game.getDrawingStyle());
            byte[] imageData = generateImageWithGemini(gptPrompt, game.getDrawingStyle());
            String imageUrl = uploadImageToS3(imageData, objectKey);
            */
            
            // AFTER: Python 서비스 호출
            String imageUrl = callPythonImageService(sceneRequest, game);
            
            // Redis에 장면 저장 (기존과 동일)
            SceneRedis sceneRedis = new SceneRedis(
                sceneRequest.getGameId(),
                sceneRequest.getTurn(),
                sceneRequest.getUserPrompt(),
                null // 이미지 바이트는 더 이상 Redis에 저장하지 않음
            );
            redisSceneRepository.save(sceneRedis);
            
            return ApiResponseUtil.success(imageUrl, "장면 생성 성공", HttpStatus.OK, request.getRequestURI());
            
        } catch (Exception e) {
            log.error("장면 생성 실패: {}", e.getMessage());
            return ApiResponseUtil.failure("장면 생성 실패", HttpStatus.INTERNAL_SERVER_ERROR, request.getRequestURI());
        }
    }
    
    private String callPythonImageService(SceneRequest sceneRequest, Game game) {
        try {
            // Python 서비스 요청 데이터 구성
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("gameId", sceneRequest.getGameId());
            requestBody.put("userId", sceneRequest.getUserId()); 
            requestBody.put("userPrompt", sceneRequest.getUserPrompt());
            requestBody.put("turn", sceneRequest.getTurn());
            requestBody.put("drawingStyle", game.getDrawingStyle());
            
            // 결말 카드 여부 확인 (기존 로직과 동일)
            boolean isEnding = false;
            // ... 결말 카드 확인 로직 ...
            requestBody.put("isEnding", isEnding);
            
            log.info("Python 이미지 서비스 호출: {}", requestBody);
            
            // Python 서비스 호출 (재시도 로직 포함)
            String response = pythonImageServiceClient
                .post()
                .uri("/generate-scene")
                .bodyValue(requestBody)
                .retrieve()
                .onStatus(
                    status -> status.is4xxClientError() || status.is5xxServerError(),
                    clientResponse -> clientResponse.bodyToMono(String.class)
                        .map(errorBody -> new RuntimeException("Python 서비스 에러: " + errorBody))
                )
                .bodyToMono(String.class)
                .timeout(Duration.ofMinutes(3))  // 3분 타임아웃
                .block();
            
            // 응답 파싱
            ObjectMapper mapper = new ObjectMapper();
            JsonNode responseNode = mapper.readTree(response);
            
            if (responseNode.get("success").asBoolean()) {
                String imageUrl = responseNode.get("imageUrl").asText();
                String gptPrompt = responseNode.get("gptPrompt").asText();
                
                log.info("Python 이미지 생성 성공. URL: {}, GPT 프롬프트: {}", imageUrl, gptPrompt);
                return imageUrl;
            } else {
                String errorMessage = responseNode.get("message").asText();
                log.error("Python 이미지 생성 실패: {}", errorMessage);
                throw new RuntimeException(errorMessage);
            }
            
        } catch (Exception e) {
            log.error("Python 이미지 서비스 호출 실패: {}", e.getMessage());
            
            // 폴백: 기존 Java 로직으로 대체 (옵션)
            /*
            log.warn("Python 서비스 실패로 기존 Java 로직으로 폴백");
            return fallbackToJavaImageGeneration(sceneRequest, game);
            */
            
            throw new RuntimeException("이미지 생성 서비스 호출 실패: " + e.getMessage(), e);
        }
    }
    
    // 기존 메서드들을 주석 처리 (롤백을 위해 보존)
    /*
    private String generatePromptWithGPT(String userSentence, int gameMode) {
        // ... 기존 GPT 호출 로직 ...
    }
    
    private byte[] generateImageWithGemini(String prompt, int gameMode) {
        // ... 기존 Gemini 호출 로직 ...
    }
    
    private String uploadImageToS3(byte[] imageData, String objectKey) {
        // ... 기존 S3 업로드 로직 ...
    }
    */
}

/*
GameService.java 수정 예시
책 표지 생성 로직을 Python 서비스 호출로 변경
*/

@Service  
@RequiredArgsConstructor
public class GameService {
    
    private final WebClient pythonImageServiceClient;
    
    public ResponseEntity<?> finishGame(DeleteGameRequest deleteGameRequest, HttpServletRequest request) {
        // ... 기존 게임 종료 로직 ...
        
        try {
            // BEFORE: 기존 Java 로직
            /*
            String bookTitle = generateBookTitle(sceneRedisList);
            byte[] coverImageBytes = generateCoverImage(bookTitle, game.getDrawingStyle());
            */
            
            // AFTER: Python 서비스 호출
            BookCoverResponse coverResponse = callPythonCoverService(sceneRedisList, game);
            
            // 책 저장 (기존과 동일, 단지 Python에서 받은 데이터 사용)
            book.setTitle(coverResponse.getTitle());
            book.setImageUrl(coverResponse.getImageUrl());
            
            // ... 나머지 로직 동일 ...
            
        } catch (Exception e) {
            log.error("게임 종료 처리 실패: {}", e.getMessage());
            return ApiResponseUtil.failure("게임 종료 실패", HttpStatus.INTERNAL_SERVER_ERROR, request.getRequestURI());
        }
    }
    
    private BookCoverResponse callPythonCoverService(List<SceneRedis> sceneRedisList, Game game) {
        try {
            // 스토리 내용 구성 (기존 로직과 동일)
            String storyContent = sceneRedisList.stream()
                .filter(scene -> scene.getSceneOrder() > 0)
                .sorted(Comparator.comparingInt(SceneRedis::getSceneOrder))
                .map(SceneRedis::getPrompt)
                .collect(Collectors.joining(". "));
                
            if (storyContent.length() > 200) {
                storyContent = storyContent.substring(0, 200);
            }
            
            // Python 서비스 요청
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("storyContent", storyContent);
            requestBody.put("drawingStyle", game.getDrawingStyle());
            
            log.info("Python 표지 서비스 호출: {}", requestBody);
            
            String response = pythonImageServiceClient
                .post()
                .uri("/generate-cover") 
                .bodyValue(requestBody)
                .retrieve()
                .bodyToMono(String.class)
                .timeout(Duration.ofMinutes(5))  // 표지 생성은 5분 타임아웃
                .block();
                
            // 응답 파싱
            ObjectMapper mapper = new ObjectMapper();
            JsonNode responseNode = mapper.readTree(response);
            
            if (responseNode.get("success").asBoolean()) {
                String title = responseNode.get("title").asText();
                String imageUrl = responseNode.get("imageUrl").asText();
                
                log.info("Python 표지 생성 성공. 제목: {}, URL: {}", title, imageUrl);
                return new BookCoverResponse(title, imageUrl);
            } else {
                String errorMessage = responseNode.get("message").asText();
                log.error("Python 표지 생성 실패: {}", errorMessage);
                throw new RuntimeException(errorMessage);
            }
            
        } catch (Exception e) {
            log.error("Python 표지 서비스 호출 실패: {}", e.getMessage());
            throw new RuntimeException("표지 생성 서비스 호출 실패: " + e.getMessage(), e);
        }
    }
    
    // 응답 데이터 클래스
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class BookCoverResponse {
        private String title;
        private String imageUrl;
    }
    
    // 기존 메서드들을 주석 처리 (롤백을 위해 보존)
    /*
    private String generateBookTitle(List<SceneRedis> sceneRedisList) {
        // ... 기존 GPT 호출 로직 ...
    }
    
    private byte[] generateCoverImage(String bookTitle, int drawingStyle) {
        // ... 기존 Gemini 호출 로직 ...
    }
    */
}