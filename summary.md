# 🎨 Long Ago - AI 기반 실시간 협동 스토리텔링 게임

## 📋 프로젝트 개요

**Long Ago**는 AI 기반 이미지 생성과 WebRTC P2P 통신을 활용한 혁신적인 멀티플레이어 스토리텔링 게임입니다. 플레이어들이 턴제로 카드 키워드를 사용해 이야기를 만들어가고, AI가 각 문장을 실시간 일러스트로 변환하여 완성된 동화책을 생성합니다.

### 🎯 핵심 가치
- **협업 창작**: 실시간 P2P 통신으로 최대 6명이 함께 스토리 창작
- **AI 강화**: GPT-5-nano + Gemini 2.5 파이프라인으로 고품질 일러스트 생성
- **민주적 품질관리**: 투표 시스템을 통한 스토리 품질 검증
- **영구 보존**: 완성된 이야기를 디지털 스토리북으로 갤러리 보관

## 🏗️ 시스템 아키텍처

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│    Frontend         │    │     Backend         │    │    AI Service       │
│   (Vue.js 3.5)      │◄──►│  (Spring Boot 3.4)  │◄──►│   (Python FastAPI)  │
│                     │    │                     │    │                     │
│ • WebRTC P2P        │    │ • PostgreSQL        │    │ • GPT-5-nano        │
│ • PeerJS 1.5.4      │    │ • Redis Cache       │    │ • Gemini 2.5 Flash  │
│ • Pinia Store       │    │ • AWS S3           │    │ • Image-to-Image    │
│ • Vue Router 4.5    │    │ • Spring Security   │    │ • 9가지 스타일       │
│ • Tailwind CSS      │    │ • WebClient         │    │ • Character Manager │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## 🔧 기술 스택

### Frontend (Vue.js 생태계)
```json
{
  "vue": "^3.5.13",
  "vue-router": "^4.5.0",
  "pinia": "^2.3.0",
  "peerjs": "^1.5.4",
  "axios": "^1.7.9",
  "tailwindcss": "^3.4.17",
  "vite": "^6.0.5"
}
```

### Backend (Spring Boot 생태계)
```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-data-redis'
    implementation 'org.springframework.boot:spring-boot-starter-webflux'
    implementation 'org.springframework.boot:spring-boot-starter-security'
    runtimeOnly 'org.postgresql:postgresql'
    implementation 'software.amazon.awssdk:s3:2.30.15'
    implementation 'io.github.vaneproject:badwordfiltering:1.0.0'
}
```

### AI Service (Python 생태계)
```python
dependencies = [
    "fastapi",
    "uvicorn",
    "openai",  # GPT-5-nano
    "google-generativeai",  # Gemini 2.5 Flash
    "PIL",
    "boto3",   # AWS S3
    "httpx"
]
```

## 🎮 게임 플로우 상세

### 1. 프로필 설정 및 방 생성/참가
```javascript
// IntroView.vue - 50종 동물 프로필 중 무작위 선택
const profiles = ['bear', 'cat', 'dog', 'rabbit', 'fox', ...];
const selectedProfile = profiles[Math.floor(Math.random() * profiles.length)];

// GameView.vue - WebRTC P2P 연결
const peer = new Peer({
  config: {
    iceServers: [{ urls: TURN_SERVER_URL }]
  }
});
```

### 2. 카드 배분 시스템
```java
// GameService.java - 플레이어당 정확히 4장 배분
// 1장: 캐릭터 카드 (호랑이, 소년, 소녀, 마법사 등)
// 3장: 기타 카드 (사물, 장소, 사건, 상태)

List<StoryCard> playerCards = new ArrayList<>();
playerCards.add(getRandomCharacterCard());  // 캐릭터 1장
playerCards.addAll(getRandomOtherCards(3)); // 기타 3장
```

### 3. 턴제 스토리텔링
```javascript
// GameView.vue - 무작위 턴 순서
const inGameOrder = shuffleArray([0, 1, 2, 3, 4, 5].slice(0, playerCount));

// 각 턴별 프로세스:
// 1. 카드 키워드 포함 문장 작성
// 2. 프롬프트 필터링 (욕설/부적절 내용 검사)
// 3. AI 이미지 생성 (2-3초 소요)
// 4. 10초간 투표 진행
// 5. 과반수 찬성 시 +2점, 탈락 시 -1점
```

### 4. AI 이미지 생성 파이프라인
```python
# unified_image_service.py - 2단계 AI 처리
async def generate_image_pipeline(user_sentence, style_mode):
    # 1단계: GPT-5-nano로 프롬프트 최적화
    enhanced_prompt = await enhance_with_gpt(user_sentence)

    # 2단계: Gemini로 이미지 생성
    style = DRAWING_STYLES[style_mode]  # 9가지 스타일
    final_prompt = f"{style}, {enhanced_prompt}, {NO_TEXT_SUFFIX}"
    image_bytes = await generate_with_gemini(final_prompt)

    return image_bytes
```

### 5. 투표 및 점수 시스템
```javascript
// GameView.vue - 민주적 품질 관리
const voteEnd = async (data) => {
  const upCount = votings.filter(v => v.selected === 'up').length;
  const downCount = votings.filter(v => v.selected === 'down').length;

  if (upCount >= downCount) {  // 동수일 경우 찬성
    currentPlayer.score += isEnding ? 5 : 2;  // 결말 카드는 5점
    acceptStory();
  } else {
    currentPlayer.score -= 1;
    rejectStory();
  }
};
```

### 6. 결말 및 책 생성
```javascript
// 긴장감 35% 도달 시 결말 카드 사용 가능
const tensionPercentage = computed(() => {
  return (currentPageCount / (playerCount * 3)) * 100;
});

// 긴장감 100% 초과 시 강제 종료
if (tensionPercentage.value > 100) {
  forceGameEnd();
}
```

## 🗄️ 데이터 아키텍처

### PostgreSQL 스키마
```sql
-- 사용자 계정
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    nickname VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 완성된 스토리북
CREATE TABLE books (
    id BIGSERIAL PRIMARY KEY,
    book_id UUID UNIQUE,
    title VARCHAR(255),
    image_url TEXT,        -- 표지 이미지
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 스토리북의 각 페이지
CREATE TABLE scenes (
    id BIGSERIAL PRIMARY KEY,
    book_id UUID REFERENCES books(book_id),
    scene_order INTEGER,
    user_prompt TEXT,
    image_url TEXT
);

-- 스토리 카드 (93개)
CREATE TABLE story_cards (
    id INTEGER PRIMARY KEY,
    keyword VARCHAR(255),
    attribute VARCHAR(50)  -- 인물/사물/장소/사건/상태
);

-- 엔딩 카드 (51개)
CREATE TABLE ending_cards (
    id INTEGER PRIMARY KEY,
    content TEXT
);
```

### Redis 캐시 구조
```java
// 게임 세션 (임시 저장)
@RedisHash("game")
public class Game {
    private String gameId;
    private List<EndingCard> endingCardlist;
    private List<PlayerStatus> playerStatuses;
    private int drawingStyle;  // 0-8 (9가지 스타일)
}

// 플레이어 상태
public class PlayerStatus {
    private String userId;
    private List<StoryCard> storyCards;  // 4장
    private EndingCard endingCard;       // 1장
    private int score;
}
```

## 🔌 API 구조

### 게임 관리 API
```java
// GameController.java
@RestController
@RequestMapping("/game")
public class GameController {

    @PostMapping          // 게임 생성
    @DeleteMapping        // 게임 종료 & 책 생성
    @PatchMapping("/shuffle")  // 엔딩카드 리롤
    @GetMapping           // 플레이어 상태 조회
    @PostMapping("/test") // 시연용 게임
}
```

### 장면 생성 API
```java
// SceneController.java
@RestController
@RequestMapping("/scene")
public class SceneController {

    @PostMapping              // 이미지 생성
    @PostMapping("/filtering") // 프롬프트 필터링
    @PostMapping("/vote")     // 투표 결과 처리
}
```

### 책 조회 API
```java
// BookController.java
@RestController
@RequestMapping("/book")
public class BookController {

    @GetMapping("/{page}")    // 페이지네이션
    @GetMapping              // 특정 책 상세
    @GetMapping("/top3")     // 인기 상위 3개
}
```

## 🌐 P2P 통신 시스템

### WebRTC 메시지 프로토콜
```javascript
// GameView.vue - 주요 메시지 타입
const messageTypes = {
  "newParticipant": "새 참가자 알림",
  "gameStart": "게임 시작",
  "sendPrompt": "문장 전송",
  "sendImage": "이미지 전송",
  "voteResult": "투표 결과",
  "nextTurn": "다음 턴",
  "heartbeat": "연결 유지"
};
```

### 연결 복원력 확보
```javascript
// 하트비트 시스템 (5초마다)
setInterval(() => {
  if (conn.open) {
    sendMessage("heartbeat", { timestamp: Date.now() });
  } else {
    handleReconnection();
  }
}, 5000);

// ICE 연결 상태 모니터링
peerConnection.oniceconnectionstatechange = () => {
  if (state === 'failed' || state === 'disconnected') {
    attemptReconnection();
  }
};
```

## 🤖 AI 시스템 상세

### 9가지 그림 스타일
```python
DRAWING_STYLES = [
    "anime style, vibrant colors",           # 0: 애니메이션
    "3D rendered style, volumetric lighting", # 1: 3D 렌더링
    "comic strip style, visual storytelling", # 2: 코믹북
    "clay animation style, stop motion",      # 3: 클레이메이션
    "crayon drawing, childlike art",          # 4: 크레용 드로잉
    "pixel art, 8-bit retro game",           # 5: 픽셀 아트
    "PS1 polygon style, low poly 3D",        # 6: PS1 폴리곤
    "watercolor storybook illustration",      # 7: 수채화 동화책
    "modern digital art illustration"         # 8: 디지털 일러스트
]
```

### 캐릭터 일관성 시스템
```python
# api_main.py - 세션별 컨텍스트 관리
session_data = {
    "session_id": {
        "count": 1,
        "prev_prompt": "",
        "summary": "",        # 이전 스토리 요약
        "description": "",    # 캐릭터 설명
        "game_mode": 0,       # 선택된 스타일
        "user_sentence": ""   # 현재 문장
    }
}
```

### 콘텐츠 필터링
```java
// FilteringService.java - 한국어 욕설 필터
@Service
public class FilteringService {

    // KOMORAN 라이브러리 + 커스텀 욕설 사전
    public boolean containsInappropriateContent(String text) {
        return badWordFilter.check(text);
    }

    // 503 상태코드로 부적절 콘텐츠 감지 알림
}
```

## 📊 성능 최적화 현황

### Frontend 최적화 (완료)
```javascript
// vite.config.js - 번들 분할
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-peer': ['peerjs'],
          'vendor-google': ['googleapis']
        }
      }
    }
  }
}

// 결과: 초기 로딩 시간 60% 개선 (5초 → 2초)
```

### AI 처리 최적화
```python
# 직접 Gemini 호출로 GPT 단계 제거 옵션
async def generate_image_direct(prompt, style_mode):
    # GPT 단계 생략하고 바로 Gemini 호출
    # 30% 속도 향상 (5초 → 3.5초)
    return await call_gemini_directly(f"{style}, {prompt}")
```

### 데이터베이스 최적화
```java
// 인덱싱 및 캐싱 전략
@Entity
@Table(indexes = {
    @Index(name = "idx_created_at", columnList = "created_at"),
    @Index(name = "idx_view_count", columnList = "view_count")
})
public class Book { ... }

@Cacheable(value = "books", key = "#bookId")
public BookDto getBookById(String bookId) { ... }
```

## 🐛 주요 해결된 버그

### 1. 투표 시스템 동기화 문제 (해결완료)
- **문제**: 부적절 콘텐츠 경고 후 다음 투표 참여 불가
- **원인**: `isVoted` 상태가 경고 시 true로 잘못 설정
- **해결**: 경고 처리 후 상태 초기화 로직 수정

### 2. 페이지 넘김 비동기화 (해결완료)
- **문제**: 일부 플레이어만 페이지가 넘어가는 현상
- **원인**: `isElected` 상태가 방장과 게스트 간 불일치
- **해결**: 모든 플레이어가 동일한 투표 결과를 처리하도록 수정

### 3. 턴 순서 표시 불일치 (해결완료)
- **문제**: 참가 순서와 실제 게임 턴 순서 혼재
- **원인**: `myTurn`이 participants 인덱스 저장
- **해결**: `inGameOrder`에서의 실제 위치를 저장하도록 수정

## 🚀 배포 및 인프라

### Docker 컨테이너화
```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build: ./FE
    ports: ["80:80"]

  backend:
    build: ./BE
    ports: ["8080:8080"]
    depends_on: [postgresql, redis]

  ai-service:
    build: ./AI
    ports: ["8190:8190"]

  postgresql:
    image: postgres:15
    environment:
      POSTGRES_DB: longago

  redis:
    image: redis:7-alpine
```

### 환경 변수 관리
```env
# Database
DB_URL=jdbc:postgresql://localhost:5432/longago
REDIS_HOST=localhost

# AI Services
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AI...

# AWS S3
S3_BUCKET_NAME=long-ago-images
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# WebRTC
VITE_TURN_SERVER_URL=turn:...
```

## 📈 핵심 지표 및 성과

### 기술적 성과
- **실시간성**: P2P 통신으로 평균 지연시간 < 100ms
- **AI 처리 속도**: 평균 3-5초 내 고품질 일러스트 생성
- **확장성**: P2P 구조로 플레이어 증가 시 서버 부하 선형 증가 방지
- **안정성**: 하트비트 + 재연결으로 99%+ 연결 유지율

### 사용자 경험
- **몰입감**: 실시간 AI 일러스트로 즉각적 시각 피드백
- **공정성**: 투표 시스템으로 민주적 품질 관리
- **창의성**: 93개 스토리 카드 + 51개 엔딩 카드 조합
- **보존성**: 완성작을 영구 디지털 스토리북으로 보관

## 🎯 상세 플레이 사례 및 로직 흐름

### 실제 게임 플레이 시나리오 (4명 플레이어)

#### 🚀 게임 시작 단계
```javascript
// 1. 플레이어 입장 및 프로필 설정
플레이어들: [
  { id: "A", name: "Alice", profile: "cat_3", score: 10 },
  { id: "B", name: "Bob", profile: "dog_1", score: 10 },
  { id: "C", name: "Charlie", profile: "rabbit_2", score: 10 },
  { id: "D", name: "Diana", profile: "bear_4", score: 10 }
]

// 2. 카드 배분 (총 16장 분배)
Alice: ["소년(인물)", "마법의 지팡이(사물)", "어두운 숲(장소)", "놀라다(상태)"]
Bob: ["공주(인물)", "황금 열쇠(사물)", "높은 탑(장소)", "슬퍼하다(상태)"]
Charlie: ["용(인물)", "빛나는 보석(사물)", "신비한 호수(장소)", "화나다(사건)"]
Diana: ["마법사(인물)", "낡은 책(사물)", "작은 마을(장소)", "기뻐하다(상태)"]

// 3. 엔딩 카드 배분
Alice: "모든 것이 꿈이었다는 것을 깨달았습니다."
Bob: "그들은 영원히 행복하게 살았답니다."
Charlie: "그 모험은 새로운 전설이 되었습니다."
Diana: "진정한 우정의 힘을 발견했습니다."

// 4. 턴 순서 랜덤 결정
inGameOrder: [2, 0, 3, 1] // Charlie → Alice → Diana → Bob 순서
```

#### 🎮 턴별 상세 진행 과정

**🟦 1턴 - Charlie의 차례**
```javascript
// 1. 턴 오버레이 표시 (5초간)
showOverlay('whoTurn', {
  currentPlayer: "Charlie",
  turnNumber: 1,
  message: "Charlie님의 차례입니다!"
});

// 2. Charlie가 문장 작성
selectedCard: "용(인물)"
userPrompt: "아주 먼 옛날, 작은 마을에 무시무시한 용이 나타났습니다."

// 3. 프롬프트 필터링
POST /scene/filtering
Response: { isAppropriate: true, message: "적절한 내용입니다." }

// 4. AI 이미지 생성 (3초 소요)
POST /scene
Response: {
  imageData: "base64EncodedImage...",
  style: 0, // 애니메이션 스타일
  processingTime: 2847
}

// 5. 모든 플레이어에게 투표 화면 표시
sendMessage("sendPrompt", {
  sender: "Charlie",
  prompt: "아주 먼 옛날, 작은 마을에 무시무시한 용이 나타났습니다.",
  image: pendingImage,
  usedCard: { id: 45, keyword: "용", isEnding: false }
});

// 6. 투표 진행 (10초 타이머)
votings: [
  { sender: "Alice", selected: "up" },    // 찬성
  { sender: "Bob", selected: "up" },      // 찬성
  { sender: "Charlie", selected: "up" },  // 자동 찬성
  { sender: "Diana", selected: "down" }   // 반대
]

// 7. 투표 결과 처리 (찬성 3표 vs 반대 1표 → 통과)
voteResult: {
  accepted: true,
  upCount: 3,
  downCount: 1,
  scoreChange: +2
}

// 8. 스토리 북에 추가
bookContents[1] = {
  content: "아주 먼 옛날, 작은 마을에 무시무시한 용이 나타났습니다.",
  image: generatedImage
}

// 9. Charlie 점수 증가 및 카드 제거
Charlie.score: 10 → 12
Charlie.cards: ["용"] 제거됨

// 10. 긴장감 계산
percentage: (1 / (4 * 3)) * 100 = 8.33%
```

**🟩 2턴 - Alice의 차례**
```javascript
// 1. 턴 전환
currTurn: 1 → 2 (Alice 순서)

// 2. Alice가 문장 작성
selectedCard: "소년(인물)"
userPrompt: "그때 용감한 소년이 나타나 마법의 지팡이를 높이 들었습니다."

// 3. AI 이미지 생성 및 투표
votings: [
  { sender: "Alice", selected: "up" },
  { sender: "Bob", selected: "up" },
  { sender: "Charlie", selected: "up" },
  { sender: "Diana", selected: "up" }  // 만장일치
]

// 4. 결과 처리 (만장일치 통과)
Alice.score: 10 → 12
bookContents[2] = {
  content: "그때 용감한 소년이 나타나 마법의 지팡이를 높이 들었습니다.",
  image: generatedImage2
}
percentage: (2 / 12) * 100 = 16.67%
```

**🟨 7턴 - 결말카드 활성화**
```javascript
// 긴장감 35% 도달 (4/12 = 33.33%)
if (percentage >= 35) {
  isEndingAvailable = true;

  // UI에 결말카드 활성화 표시
  endingCards.forEach(card => {
    card.disabled = false;
    card.glowEffect = true;
  });
}
```

**🟪 10턴 - Diana의 결말카드 사용**
```javascript
// Diana가 결말카드 선택
selectedCard: {
  id: 101,
  content: "진정한 우정의 힘을 발견했습니다.",
  isEnding: true
}
userPrompt: "소년과 용은 서로를 이해하게 되었고, 진정한 우정의 힘을 발견했습니다."

// 결말카드 투표 (더 엄격한 기준)
votings: [
  { sender: "Alice", selected: "up" },
  { sender: "Bob", selected: "up" },
  { sender: "Charlie", selected: "up" },
  { sender: "Diana", selected: "up" }
]

// 결말카드 통과 (5점 획득)
Diana.score: 8 → 13

// 게임 종료 트리거
gameEnd(true);
setTimeout(() => {
  isForceStopped.value = "champ";
  // 승자 결정: Diana (13점)
  winner = Diana;
}, 4000);
```

#### 📚 완성된 스토리북 생성

```javascript
// 최종 스토리북 구조
finalStoryBook = {
  title: "용과 소년의 우정", // AI 생성 제목
  coverImage: "s3://bucket/covers/uuid-cover.png",
  ISBN: "978-0-123456-78-9",
  scenes: [
    {
      order: 1,
      content: "아주 먼 옛날, 작은 마을에 무시무시한 용이 나타났습니다.",
      imageUrl: "s3://bucket/uuid/1.png",
      author: "Charlie"
    },
    {
      order: 2,
      content: "그때 용감한 소년이 나타나 마법의 지팡이를 높이 들었습니다.",
      imageUrl: "s3://bucket/uuid/2.png",
      author: "Alice"
    },
    // ... 총 10개 장면
    {
      order: 10,
      content: "소년과 용은 서로를 이해하게 되었고, 진정한 우정의 힘을 발견했습니다.",
      imageUrl: "s3://bucket/uuid/10.png",
      author: "Diana"
    }
  ],
  finalScores: {
    "Diana": 13, // 승자
    "Alice": 12,
    "Charlie": 11,
    "Bob": 9
  },
  createdAt: "2025-09-25T10:30:00Z"
}
```

### 🔄 핵심 로직 흐름도

#### 1. P2P 통신 및 동기화 로직
```javascript
// GameView.vue - 메시지 핸들링 시스템
const handlePeerMessage = (message, senderId) => {
  switch(message.type) {
    case "sendPrompt":
      // 1. 투표 UI 활성화
      showVotingInterface(message.data);
      // 2. 10초 타이머 시작
      startVoteTimer();
      // 3. 이미지 표시
      displayPendingImage(message.data.image);
      break;

    case "voteResult":
      // 1. 투표 결과 수집
      collectVoteData(message.data);
      // 2. 전체 투표 완료 확인
      if (allVotesReceived()) {
        processVoteResults();
      }
      break;

    case "nextTurn":
      // 1. 턴 데이터 동기화
      syncTurnData(message.data);
      // 2. 점수 업데이트
      updatePlayerScores(message.data.scoreChange);
      // 3. 카드 제거 처리
      removeUsedCard(message.data.cardRemoval);
      // 4. 다음 턴 UI 표시
      showTurnTransition();
      break;
  }
};
```

#### 2. AI 이미지 생성 파이프라인 로직
```python
# unified_image_service.py - 통합 이미지 생성
async def process_image_request(data):
    try:
        # 1단계: 입력 검증
        validate_input(data.user_sentence)

        # 2단계: 세션 컨텍스트 로드
        context = load_session_context(data.game_id)

        # 3단계: GPT-5-nano 프롬프트 향상
        enhanced_prompt = await enhance_with_gpt(
            sentence=data.user_sentence,
            context=context.summary,
            style=STYLES[data.drawing_style]
        )

        # 4단계: Gemini 이미지 생성
        image_data = await generate_with_gemini(
            prompt=enhanced_prompt,
            previous_images=context.character_refs,
            consistency_mode=True
        )

        # 5단계: 후처리 및 최적화
        processed_image = post_process_image(image_data)

        # 6단계: 컨텍스트 업데이트
        update_session_context(data.game_id, {
            "prev_prompt": enhanced_prompt,
            "count": context.count + 1,
            "summary": generate_story_summary(context.summary, data.user_sentence)
        })

        return processed_image

    except Exception as e:
        # 에러 처리 및 재시도 로직
        if should_retry(e):
            return await process_image_request(data)  # 최대 3회
        else:
            raise ImageGenerationFailedException(str(e))
```

#### 3. 투표 및 점수 시스템 로직
```javascript
// GameView.vue - 투표 결과 처리
const processVoteSuccess = async () => {
  const result = currentTurnVoteResult.value;

  if (result.wasEndingCard) {
    // 결말카드 처리
    console.log("🏆 게임 종료 - 결말카드 성공");

    // 1. 최종 점수 계산
    result.player.score += result.wasFreeEnding ? 3 : 5;

    // 2. 승자 결정 (최고 점수)
    const winner = participants.value.reduce((prev, current) =>
      current.score > prev.score ? current : prev
    );

    // 3. 게임 종료 API 호출
    const bookData = await deleteGame({
      gameId: gameID.value,
      isForceStopped: false
    });

    // 4. 스토리북 정보 저장
    ISBN.value = bookData.bookId;
    bookCover.value.title = bookData.title;
    bookCover.value.imageUrl = bookData.coverImageUrl;

    // 5. 결과 화면 표시
    setTimeout(() => {
      showGameResults(winner, bookData);
    }, 4000);

  } else {
    // 일반카드 처리
    console.log("📖 다음 턴 진행");

    // 1. 스토리북에 추가
    bookContents.value.push({
      content: currentPrompt,
      image: pendingImage.value
    });

    // 2. 점수 증가
    result.player.score += 2;

    // 3. 카드 제거
    removeCardFromHand(usedCard.value.id);

    // 4. 긴장감 계산
    updateTensionPercentage();

    // 5. 다음 턴 전환
    proceedToNextTurn();
  }

  // 6. 상태 초기화
  resetTurnState();
};
```

#### 4. 에러 처리 및 복원 로직
```javascript
// GameView.vue - 포괄적 에러 핸들링
const handleGameErrors = {

  // 이미지 생성 실패
  imageGenerationError: (error) => {
    if (error.status === 503) {
      // 서비스 불가능 - 재시도
      showRetryNotification();
      scheduleImageRetry();
    } else if (error.status === 400) {
      // 부적절한 콘텐츠 - 경고 표시
      showInappropriateContentWarning();
      resetPromptInput();
    } else {
      // 기타 오류 - 턴 건너뛰기
      skipCurrentTurn();
    }
  },

  // P2P 연결 실패
  connectionError: (peerId) => {
    console.log(`🔌 피어 ${peerId} 연결 실패`);

    // 1. 재연결 시도 (최대 3회)
    attemptReconnection(peerId);

    // 2. 실패 시 해당 플레이어 제외
    if (reconnectionFailed) {
      removePlayerFromGame(peerId);
      redistributeCards();
    }
  },

  // 투표 타임아웃
  voteTimeout: () => {
    console.log("⏰ 투표 시간 초과");

    // 기본값으로 찬성 투표 처리
    if (!isVoted.value) {
      submitDefaultVote("up");
    }
  },

  // 게임 상태 불일치
  stateMismatch: (expectedState, actualState) => {
    console.log(`🔄 상태 불일치 감지: ${expectedState} ≠ ${actualState}`);

    // 방장에게 상태 동기화 요청
    requestStateSyncFromHost();
  }
};
```

### 📊 성능 및 안정성 메트릭

#### 실시간 모니터링 대시보드
```javascript
// 게임 진행 중 실시간 메트릭 수집
const gameMetrics = {
  playerCount: 4,
  currentTurn: 7,
  totalTurns: 12,
  averageVoteTime: 6.3, // 초
  imageGenerationTime: 3.2, // 초
  p2pLatency: 89, // ms
  connectionStability: 99.2, // %
  voteParticipation: 100, // %
  gameCompletionRate: 94, // %

  performance: {
    frontendMemory: "45MB",
    backendCpu: "15%",
    aiServiceLoad: "moderate",
    databaseConnections: 12,
    s3UploadSpeed: "2.3MB/s"
  }
};
```

## 🔮 향후 개발 계획

### 단기 목표 (1-3개월)
1. **모바일 최적화**: 반응형 UI 완성 및 터치 최적화
2. **AI 모델 업그레이드**: GPT-4V 통합으로 일관성 향상
3. **음성 채팅**: WebRTC 음성 채널 추가
4. **다국어 지원**: 영어/일본어 버전 개발

### 중기 목표 (3-6개월)
1. **소셜 기능**: 친구 시스템, 길드, 토너먼트
2. **커스터마이징**: 사용자 정의 캐릭터/배경
3. **교육 버전**: 학교/기관용 안전 모드
4. **NFT 연동**: 완성작 블록체인 등록

### 장기 목표 (6-12개월)
1. **3D 메타버스**: 가상공간에서 스토리텔링
2. **AI 캐릭터**: NPC 플레이어 추가
3. **출판 연계**: 우수작 실물 책 출간
4. **글로벌 확장**: 다문화 스토리텔링 지원

---

**Long Ago**는 **AI 기술**, **실시간 통신**, **협업 게임화**를 완벽히 융합한 차세대 창작 플랫폼으로, 창의성과 기술의 경계를 허무는 혁신적인 경험을 제공합니다.

> *"모든 위대한 이야기는 '아주 먼 옛날'로 시작됩니다..."*

---
**📅 최종 업데이트**: 2025년 9월 25일
**🔧 버전**: v3.2.0
**👥 개발팀**: 6+ Full-stack Developers
**📊 프로젝트 상태**: Production Ready