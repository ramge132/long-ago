# 🔄 이미지 생성 Python 통합 마이그레이션 가이드

## 📋 준비 단계

### 1. 환경 설정
```bash
cd AI
pip install -r requirements.txt

# 새로운 의존성 추가
pip install fastapi uvicorn openai google-generativeai boto3 pillow
```

### 2. 환경변수 설정 (.env)
```bash
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=your_s3_bucket_name
AWS_REGION=ap-northeast-2
```

## 🔧 Java 코드 수정 사항

### SceneService.java 수정

#### AS-IS (현재 코드)
```java
// 현재: 직접 GPT + Gemini API 호출
String gptPrompt = generatePromptWithGPT(userSentence, gameMode);
byte[] imageData = generateImageWithGemini(gptPrompt, gameMode);
String imageUrl = uploadImageToS3(imageData, objectKey);
```

#### TO-BE (수정할 코드)
```java
// 변경: Python 서비스 호출
String imageUrl = callPythonImageService(sceneRequest);

private String callPythonImageService(SceneRequest sceneRequest) {
    try {
        // Python 서비스 요청 구조
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("gameId", sceneRequest.getGameId());
        requestBody.put("userId", sceneRequest.getUserId());
        requestBody.put("userPrompt", sceneRequest.getUserPrompt());
        requestBody.put("turn", sceneRequest.getTurn());
        requestBody.put("drawingStyle", game.getDrawingStyle());
        requestBody.put("isEnding", usedCard.isEnding());
        
        // Python 서비스 호출
        String response = WebClient.create("http://localhost:8190")
            .post()
            .uri("/generate-scene")
            .bodyValue(requestBody)
            .retrieve()
            .bodyToMono(String.class)
            .block();
            
        // 응답 파싱
        ObjectMapper mapper = new ObjectMapper();
        JsonNode responseNode = mapper.readTree(response);
        
        if (responseNode.get("success").asBoolean()) {
            return responseNode.get("imageUrl").asText();
        } else {
            throw new RuntimeException(responseNode.get("message").asText());
        }
    } catch (Exception e) {
        log.error("Python 이미지 서비스 호출 실패: {}", e.getMessage());
        throw new RuntimeException("이미지 생성 실패", e);
    }
}
```

### GameService.java 수정

#### AS-IS (현재 코드)
```java
// 현재: 직접 GPT + Gemini API 호출
String bookTitle = generateBookTitle(sceneRedisList);
byte[] coverImageBytes = generateCoverImage(bookTitle, game.getDrawingStyle());
```

#### TO-BE (수정할 코드)
```java
// 변경: Python 서비스 호출
BookCoverResponse coverResponse = callPythonCoverService(sceneRedisList, game);

private BookCoverResponse callPythonCoverService(List<SceneRedis> sceneRedisList, Game game) {
    try {
        // 스토리 내용 구성
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
        
        String response = WebClient.create("http://localhost:8190")
            .post()
            .uri("/generate-cover")
            .bodyValue(requestBody)
            .retrieve()
            .bodyToMono(String.class)
            .block();
            
        // 응답 파싱
        ObjectMapper mapper = new ObjectMapper();
        JsonNode responseNode = mapper.readTree(response);
        
        if (responseNode.get("success").asBoolean()) {
            return new BookCoverResponse(
                responseNode.get("title").asText(),
                responseNode.get("imageUrl").asText()
            );
        } else {
            throw new RuntimeException(responseNode.get("message").asText());
        }
    } catch (Exception e) {
        log.error("Python 표지 서비스 호출 실패: {}", e.getMessage());
        throw new RuntimeException("표지 생성 실패", e);
    }
}

// 응답 데이터 클래스
@Data
@AllArgsConstructor
public static class BookCoverResponse {
    private String title;
    private String imageUrl;
}
```

## 🚀 마이그레이션 실행 단계

### Phase 1: Python 서비스 준비
1. `unified_image_service.py` 실행
2. 헬스체크 확인: `http://localhost:8190/health`
3. 테스트 요청으로 동작 확인

### Phase 2: Java 코드 수정
1. `SceneService.java`에서 이미지 생성 로직을 Python 호출로 변경
2. `GameService.java`에서 책 표지 생성 로직을 Python 호출로 변경
3. 기존 GPT/Gemini 관련 메서드들을 주석 처리 또는 제거

### Phase 3: 기존 Java 코드 정리
**제거할 메서드들:**
- `SceneService.java`:
  - `generatePromptWithGPT()`
  - `callGPTWithRetry()`
  - `generateImageWithGemini()`
  - `callGeminiWithRetry()`
  - `generateEndingPromptWithGPT()`
  - `uploadImageToS3()`
  
- `GameService.java`:
  - `generateBookTitle()`
  - `generateCoverImage()`
  - `callGeminiWithRetryForCover()`

**제거할 의존성:**
```xml
<!-- 기존 WebClient 설정에서 OpenAI/Gemini 관련 부분 제거 -->
```

### Phase 4: 설정 업데이트
**application.properties**에서 제거:
```properties
# 더 이상 필요없는 설정들
#OPENAI_API_KEY=
#GEMINI_API_KEY=
```

**추가할 설정:**
```properties
# Python 이미지 서비스 URL
python.image.service.url=http://localhost:8190
```

## 🔍 테스트 방법

### 1. 개별 API 테스트
```bash
# 장면 이미지 생성 테스트
curl -X POST "http://localhost:8190/generate-scene" \
  -H "Content-Type: application/json" \
  -d '{
    "gameId": "test-game",
    "userId": "test-user", 
    "userPrompt": "아름다운 숲속 풍경",
    "turn": 1,
    "drawingStyle": 0,
    "isEnding": false
  }'

# 책 표지 생성 테스트
curl -X POST "http://localhost:8190/generate-cover" \
  -H "Content-Type: application/json" \
  -d '{
    "storyContent": "옛날 옛적에 용감한 기사가 있었습니다.",
    "drawingStyle": 0
  }'
```

### 2. 통합 테스트
1. Python 서비스 시작
2. Java 백엔드 시작
3. 프론트엔드에서 게임 플레이 테스트
4. 이미지 생성 및 표지 생성 확인

## ⚠️ 주의사항

1. **서비스 순서**: Python 서비스를 먼저 시작한 후 Java 서비스 시작
2. **포트 충돌**: 8190 포트가 사용 중인지 확인
3. **환경변수**: Python과 Java 모두에서 동일한 AWS 설정 필요
4. **에러 처리**: Python 서비스 다운 시 Java에서 적절한 에러 처리
5. **성능**: 네트워크 호출로 인한 지연 시간 고려

## 🔄 롤백 계획

문제 발생 시 기존 Java 코드로 빠르게 롤백할 수 있도록:
1. 기존 메서드들을 주석 처리만 하고 완전히 삭제하지 않기
2. 설정 파일에 rollback 플래그 추가
3. 조건부로 Python/Java 중 선택할 수 있는 구조 구현

## 📊 예상 효과

### 장점
- ✅ AI 로직 통합 및 관리 용이성
- ✅ Python AI 라이브러리 생태계 활용
- ✅ 코드 중복 제거
- ✅ 독립적인 AI 서비스로 확장 가능

### 단점  
- ❌ 네트워크 통신 오버헤드 (~50-100ms 추가)
- ❌ 서비스 의존성 증가
- ❌ 배포 복잡도 증가