// SceneService.java 수정 방안

@Service
@AllArgsConstructor
public class SceneService {

    // 기존 RunPod WebClient는 유지 (하위 호환성)
    @Qualifier("runpodWebClient")
    private final WebClient runpodWebClient;
    
    // 새로운 API 시스템용 WebClient 추가
    @Qualifier("newApiWebClient")
    private final WebClient newApiWebClient;
    
    @Value("${USE_NEW_API_SYSTEM:false}")
    private boolean useNewApiSystem;
    
    @Value("${NEW_API_SYSTEM_URL:http://localhost:8190}")
    private String newApiSystemUrl;

    public ResponseEntity<?> createScene(SceneRequest sceneRequest, HttpServletRequest request) {
        log.info("게임 턴: {}", sceneRequest.getTurn());

        // 게임 데이터 조회 및 유효성 검사 (기존과 동일)
        Game game = gameRepository.findById(sceneRequest.getGameId());
        if (game == null) {
            return ApiResponseUtil.failure("존재하지 않는 gameId입니다.",
                    HttpStatus.BAD_REQUEST, request.getRequestURI());
        }

        boolean userExists = game.getPlayerStatuses()
                .stream()
                .anyMatch(playerStatus -> playerStatus.getUserId().equals(sceneRequest.getUserId()));
        if (!userExists) {
            return ApiResponseUtil.failure("해당 게임에 존재하지 않는 userId입니다.",
                    HttpStatus.BAD_REQUEST, request.getRequestURI());
        }

        byte[] generateImage = null;
        
        if (useNewApiSystem) {
            // 새로운 API 시스템 사용
            generateImage = callNewApiSystem(sceneRequest, game, request);
        } else {
            // 기존 RunPod 시스템 사용 (기존 로직 유지)
            generateImage = callRunPodSystem(sceneRequest, game, request);
        }

        // 나머지 로직은 동일 (Redis 저장 등)
        if (generateImage == null || generateImage.length == 0) {
            return ApiResponseUtil.failure("이미지 생성에 실패했습니다.",
                    HttpStatus.INTERNAL_SERVER_ERROR, request.getRequestURI());
        }

        // Redis 저장 로직 (기존과 동일)
        // ... 기존 코드 유지
    }
    
    private byte[] callNewApiSystem(SceneRequest sceneRequest, Game game, HttpServletRequest request) {
        try {
            // 새로운 API 시스템 요청 객체 생성
            Map<String, Object> newApiRequest = new HashMap<>();
            newApiRequest.put("session_id", sceneRequest.getGameId());          // gameId → session_id 매핑
            newApiRequest.put("game_mode", game.getDrawingStyle());             // drawingStyle → game_mode 매핑
            newApiRequest.put("user_sentence", sceneRequest.getUserPrompt());   // userPrompt → user_sentence 매핑
            newApiRequest.put("status", 0); // 진행 중
            
            log.info("새로운 API 시스템 요청: {}", newApiRequest);
            
            // 새로운 API 시스템 호출
            byte[] imageBytes = newApiWebClient.post()
                    .uri(newApiSystemUrl + "/generate")
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(newApiRequest)
                    .retrieve()
                    .bodyToMono(byte[].class)
                    .block();
            
            log.info("새로운 API 시스템 응답 받음");
            return imageBytes;
            
        } catch (Exception e) {
            log.error("새로운 API 시스템 호출 실패: {}", e.getMessage());
            return null;
        }
    }
    
    private byte[] callRunPodSystem(SceneRequest sceneRequest, Game game, HttpServletRequest request) {
        // 기존 RunPod 호출 로직 그대로 유지
        // ... 기존 코드
        return null; // 기존 로직 결과 반환
    }
}