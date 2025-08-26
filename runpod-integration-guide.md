# RunPod 서버리스 연동 가이드

## 🔑 필요한 API 키와 정보

### RunPod에서 얻어야 할 정보:
1. **RunPod API Key**: RunPod 대시보드 → Settings → API Keys
2. **Endpoint ID**: RunPod 대시보드 → Serverless → Endpoints → 생성된 엔드포인트 ID
3. **Endpoint URL**: `https://api.runpod.ai/v2/{ENDPOINT_ID}/run`

## 📝 설정해야 할 위치

### 1. 백엔드 application.properties 수정

`BE/src/main/resources/application.properties`에 추가:

```properties
# RunPod 설정 추가
RUNPOD.API.KEY=${RUNPOD_API_KEY}
RUNPOD.ENDPOINT.ID=${RUNPOD_ENDPOINT_ID}
RUNPOD.ENDPOINT.URL=https://api.runpod.ai/v2/${RUNPOD_ENDPOINT_ID}/run

# 기존 WEBCLIENT URL을 RunPod으로 변경 (예시)
WEBCLIENT.BASE.URL_0=${RUNPOD_ENDPOINT_URL:https://api.runpod.ai/v2/${RUNPOD_ENDPOINT_ID}/run}
```

### 2. 로컬 개발용 .env 파일 생성

`BE/.env` 파일 생성:

```env
# Database
DB_URL=jdbc:postgresql://localhost:5432/longago
DB_USERNAME=your_db_user
DB_PASSWORD=your_db_password
DB_DRIVER=org.postgresql.Driver

# Redis
REDIS_HOST=localhost

# RunPod 설정
RUNPOD_API_KEY=your_runpod_api_key_here
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
RUNPOD_ENDPOINT_URL=https://api.runpod.ai/v2/your_endpoint_id_here/run

# S3 (선택)
S3_BUCKET_NAME=long-ago-images
S3_REGION=ap-northeast-2
S3_CREDENTIALS_ACCESS_KEY=your_aws_access_key
S3_CREDENTIALS_SECRET_KEY=your_aws_secret_key
```

### 3. GitLab CI/CD 환경변수 추가

GitLab 프로젝트 → Settings → CI/CD → Variables에 추가:

```yaml
# 추가해야 할 변수들
RUNPOD_API_KEY         # RunPod API 키
RUNPOD_ENDPOINT_ID     # RunPod 엔드포인트 ID
RUNPOD_ENDPOINT_URL    # 전체 RunPod URL
```

### 4. GitLab CI/CD 파일 수정

`.gitlab-ci.yml`의 deploy 섹션에 환경변수 추가:

```yaml
deploy_test:
  stage: deploy
  variables:
    # 기존 변수들...
    RUNPOD_API_KEY: "$RUNPOD_API_KEY"
    RUNPOD_ENDPOINT_ID: "$RUNPOD_ENDPOINT_ID"
    RUNPOD_ENDPOINT_URL: "$RUNPOD_ENDPOINT_URL"
  script:
    # .env 파일 생성 부분에 추가
    - echo "RUNPOD_API_KEY=$RUNPOD_API_KEY" >> .env
    - echo "RUNPOD_ENDPOINT_ID=$RUNPOD_ENDPOINT_ID" >> .env
    - echo "RUNPOD_ENDPOINT_URL=$RUNPOD_ENDPOINT_URL" >> .env

deploy_main:
  stage: deploy
  variables:
    # 기존 변수들...
    RUNPOD_API_KEY: "$RUNPOD_API_KEY"
    RUNPOD_ENDPOINT_ID: "$RUNPOD_ENDPOINT_ID"
    RUNPOD_ENDPOINT_URL: "$RUNPOD_ENDPOINT_URL"
  script:
    # .env 파일 생성 부분에 추가
    - echo "RUNPOD_API_KEY=$RUNPOD_API_KEY" >> .env
    - echo "RUNPOD_ENDPOINT_ID=$RUNPOD_ENDPOINT_ID" >> .env
    - echo "RUNPOD_ENDPOINT_URL=$RUNPOD_ENDPOINT_URL" >> .env
```

### 5. Docker Compose 파일 확인

`docker-compose.yml`에서 환경변수 전달 확인:

```yaml
services:
  backend:
    environment:
      - DB_URL=${DB_URL}
      - DB_USERNAME=${DB_USERNAME}
      - DB_PASSWORD=${DB_PASSWORD}
      - REDIS_HOST=${REDIS_HOST}
      - RUNPOD_API_KEY=${RUNPOD_API_KEY}
      - RUNPOD_ENDPOINT_ID=${RUNPOD_ENDPOINT_ID}
      - RUNPOD_ENDPOINT_URL=${RUNPOD_ENDPOINT_URL}
      - S3_BUCKET_NAME=${S3_BUCKET_NAME}
      - S3_REGION=${S3_REGION}
      - S3_CREDENTIALS_ACCESS_KEY=${S3_CREDENTIALS_ACCESS_KEY}
      - S3_CREDENTIALS_SECRET_KEY=${S3_CREDENTIALS_SECRET_KEY}
```

## 🚀 백엔드 코드 수정 예시

### RunPod 서비스 클래스 생성

`BE/src/main/java/com/longago/service/RunPodService.java`:

```java
@Service
@RequiredArgsConstructor
public class RunPodService {
    
    @Value("${RUNPOD.API.KEY}")
    private String runpodApiKey;
    
    @Value("${RUNPOD.ENDPOINT.URL}")
    private String runpodEndpointUrl;
    
    private final WebClient webClient;
    
    public Mono<ImageResponse> generateImage(SceneRequest request) {
        Map<String, Object> payload = Map.of(
            "input", Map.of(
                "session_id", request.getSessionId(),
                "game_mode", request.getGameMode(),
                "user_sentence", request.getUserSentence(),
                "status", request.getStatus(),
                "character_cards", request.getCharacterCards()
            )
        );
        
        return webClient.post()
            .uri(runpodEndpointUrl)
            .header("Authorization", "Bearer " + runpodApiKey)
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(payload)
            .retrieve()
            .bodyToMono(ImageResponse.class);
    }
}
```

## 📋 체크리스트

### 즉시 필요한 작업:

1. **RunPod 대시보드에서 정보 수집**
   - [ ] API Key 복사
   - [ ] Endpoint ID 확인
   - [ ] Endpoint URL 확인

2. **백엔드 설정**
   - [ ] application.properties 수정
   - [ ] .env 파일 생성 (로컬 테스트용)
   - [ ] RunPod 서비스 클래스 작성

3. **GitLab 설정**
   - [ ] CI/CD 환경변수 추가
   - [ ] .gitlab-ci.yml 파일 수정

4. **테스트**
   - [ ] 로컬 환경 테스트
   - [ ] 테스트 서버 배포
   - [ ] 프로덕션 배포

## 🔧 테스트 코드

### curl로 직접 테스트:

```bash
curl -X POST https://api.runpod.ai/v2/{YOUR_ENDPOINT_ID}/run \
  -H "Authorization: Bearer {YOUR_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "session_id": "test-001",
      "game_mode": 0,
      "user_sentence": "공주가 숲에서 마법사를 만났습니다",
      "status": 0,
      "character_cards": ["공주", "마법사"]
    }
  }'
```

### Java 테스트 코드:

```java
@Test
public void testRunPodIntegration() {
    SceneRequest request = SceneRequest.builder()
        .sessionId("test-001")
        .gameMode(0)
        .userSentence("공주가 숲에서 마법사를 만났습니다")
        .status(0)
        .characterCards(Arrays.asList("공주", "마법사"))
        .build();
    
    ImageResponse response = runPodService.generateImage(request).block();
    
    assertNotNull(response);
    assertNotNull(response.getImage());
    System.out.println("S3 URL: " + response.getS3Url());
}
```

## 📌 중요 참고사항

1. **API 키 보안**
   - 절대 코드에 직접 하드코딩하지 마세요
   - 항상 환경변수를 통해 관리

2. **엔드포인트 URL 형식**
   - 동기 호출: `/run`
   - 비동기 호출: `/runsync`
   - 상태 확인: `/status/{job_id}`

3. **타임아웃 설정**
   - RunPod 기본 타임아웃: 300초
   - WebClient 타임아웃도 동일하게 설정 권장

4. **에러 처리**
   - Cold start로 인한 초기 지연 고려
   - 재시도 로직 구현 권장

---

**작성일**: 2025.08.26  
**프로젝트**: Long Ago  
**담당**: RunPod 서버리스 연동
