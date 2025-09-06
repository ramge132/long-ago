# 🎨 Long Ago - 실시간 협동 스토리텔링 게임

## 📖 프로젝트 개요

**Long Ago (아주 먼 옛날)**는 최신 AI 기술을 활용한 실시간 멀티플레이어 협동 스토리텔링 웹게임입니다. 플레이어들이 순서대로 한 문장씩 이야기를 이어가며, AI가 각 문장을 실시간으로 삽화로 변환하여 하나의 완성된 동화책을 만들어가는 혁신적인 게임입니다.

### 🌟 핵심 특징
1. **실시간 AI 이미지 생성**: 사용자 입력을 즉시 삽화로 변환
2. **P2P 멀티플레이어**: WebRTC 기반 실시간 통신으로 최대 6명 동시 플레이
3. **민주적 스토리텔링**: 투표 시스템을 통한 이야기 품질 관리
4. **다양한 그림 스타일**: 9가지 독특한 아트 스타일 지원
5. **영구 보존**: 완성된 이야기는 갤러리에 영구 보관

### 🎯 게임의 목표
- 플레이어들이 협력하여 흥미롭고 일관성 있는 이야기 창작
- 카드 키워드를 활용한 창의적인 문장 작성
- 적절한 긴장감 구축 후 만족스러운 결말 도출
- 최고 점수를 획득하여 우승자 등극

## 🏗️ 시스템 아키텍처

### 🔧 기술 스택 상세

#### Backend (Spring Boot)
```
Spring Boot 3.x
├── Core
│   ├── Java 17+
│   ├── Spring Web MVC
│   ├── Spring Data JPA
│   └── Spring WebFlux (WebClient)
├── Database
│   ├── MySQL 8.0 (영구 데이터)
│   │   ├── Book 테이블
│   │   ├── Scene 테이블
│   │   └── User 테이블
│   └── Redis 7.x (임시 게임 데이터)
│       ├── 게임 세션 정보
│       ├── 플레이어 상태
│       └── 카드 정보
├── External Services
│   ├── OpenAI API (GPT-5-nano)
│   ├── Google Gemini API (2.5 Flash)
│   └── AWS S3 (이미지 저장소)
└── Security
    ├── API Key 관리
    └── CORS 설정
```

#### Frontend (Vue.js 3)
```
Vue.js 3 (Composition API)
├── Build & Dev
│   ├── Vite 5.x
│   ├── ESLint
│   └── PostCSS
├── UI/UX
│   ├── Tailwind CSS 3.x
│   ├── Custom Animations
│   └── Responsive Design
├── State Management
│   ├── Pinia Store
│   │   ├── auth.js (사용자 인증)
│   │   ├── game.js (게임 상태)
│   │   └── audio.js (사운드 관리)
│   └── Reactive Refs
├── Communication
│   ├── PeerJS (WebRTC wrapper)
│   ├── Axios (HTTP client)
│   └── WebSocket (실시간 통신)
└── Media
    ├── Web Audio API (TTS)
    └── Canvas API (이미지 처리)
```

#### AI/Image Generation System
```
Python FastAPI
├── API Server
│   ├── FastAPI 0.100+
│   ├── Uvicorn ASGI
│   └── Port 8190
├── AI Integration
│   ├── OpenAI Python SDK
│   ├── Google Generative AI SDK
│   └── Prompt Engineering
├── Image Processing
│   ├── PIL/Pillow
│   ├── Base64 encoding
│   └── S3 Upload (boto3)
└── Character System
    ├── 14 Character Presets
    ├── Style Templates
    └── Context Management
```

## 📂 상세 프로젝트 구조

```
long-ago/
├── BE/ (Backend - Spring Boot)
│   ├── src/main/java/com/example/b101/
│   │   ├── controller/
│   │   │   ├── AuthController.java         # 사용자 인증 API
│   │   │   ├── GameController.java         # 게임 관리 API
│   │   │   │   ├── POST /game              # 게임 생성
│   │   │   │   ├── DELETE /game            # 게임 종료
│   │   │   │   └── PATCH /game/shuffle     # 카드 리롤
│   │   │   ├── SceneController.java        # 장면 생성 API
│   │   │   │   ├── POST /scene             # 이미지 생성
│   │   │   │   ├── POST /scene/filtering   # 프롬프트 검증
│   │   │   │   └── POST /scene/vote        # 투표 처리
│   │   │   └── BookController.java         # 책 조회 API
│   │   │       ├── GET /book/{page}        # 페이지네이션
│   │   │       └── GET /book/top3          # 인기 책
│   │   ├── service/
│   │   │   ├── GameService.java            # 핵심 게임 로직
│   │   │   │   ├── saveGame()              # Redis 저장
│   │   │   │   ├── finishGame()            # 게임 종료 처리
│   │   │   │   ├── generateBookTitle()     # GPT 제목 생성
│   │   │   │   └── generateCoverImage()    # 표지 생성
│   │   │   ├── SceneService.java           # 장면 생성 로직
│   │   │   │   ├── createScene()           # 메인 프로세스
│   │   │   │   ├── callGPTWithRetry()      # GPT 호출
│   │   │   │   └── callGeminiWithRetry()   # Gemini 호출
│   │   │   ├── FilteringService.java       # 콘텐츠 필터링
│   │   │   │   ├── validatePrompt()        # 프롬프트 검증
│   │   │   │   └── detectInappropriate()   # 부적절 감지
│   │   │   └── S3service.java              # AWS S3 관리
│   │   │       ├── uploadImage()           # 이미지 업로드
│   │   │       └── generatePresignedUrl()  # URL 생성
│   │   ├── domain/                         # JPA 엔티티
│   │   ├── dto/                            # 데이터 전송 객체
│   │   └── config/                         # 설정 클래스
│   └── resources/
│       └── application.properties          # 환경 설정
│
├── FE/ (Frontend - Vue.js)
│   ├── src/
│   │   ├── views/
│   │   │   ├── IntroView.vue              # 시작 화면
│   │   │   ├── GameView.vue               # 게임 메인 (P2P 통신 핵심)
│   │   │   ├── ResultView.vue             # 결과 화면
│   │   │   ├── GalleryView.vue            # 갤러리
│   │   │   └── Game/
│   │   │       ├── LobbyView.vue          # 게임 로비
│   │   │       └── InGameView.vue         # 게임 진행
│   │   ├── components/
│   │   │   ├── InGame/
│   │   │   │   ├── InGameContent.vue      # 게임 콘텐츠 (책 페이지)
│   │   │   │   ├── InGameEnding.vue       # 결말 카드 UI
│   │   │   │   ├── ContentTimer.vue       # 타이머 컴포넌트
│   │   │   │   └── ContentChatting.vue    # 채팅 컴포넌트
│   │   │   ├── Lobby/
│   │   │   │   ├── LobbyUsers.vue         # 참가자 목록
│   │   │   │   ├── LobbySettings.vue      # 게임 설정
│   │   │   │   └── LobbyChatting.vue      # 로비 채팅
│   │   │   └── Presets/
│   │   │       ├── FooterBar.vue          # 하단 바
│   │   │       └── ProfileSelect.vue      # 프로필 선택
│   │   ├── stores/                        # Pinia 스토어
│   │   ├── apis/                          # API 함수
│   │   ├── router/                        # 라우팅
│   │   └── assets/                        # 정적 자원
│
└── AI/ (AI/Image Generation)
    └── imageGeneration/
        ├── api_main.py                     # FastAPI 메인
        ├── api_image_generator.py          # 이미지 생성 로직
        ├── characters/                     # 14종 캐릭터
        │   ├── boy.png + boy.txt
        │   ├── girl.png + girl.txt
        │   ├── wizard.png + wizard.txt
        │   └── ... (총 14종)
        └── workflows/                      # 스타일 템플릿
```

## 🎮 상세 게임 플로우

### 1️⃣ 게임 준비 단계

#### 프로필 설정
```javascript
// 42종 동물 프로필 중 선택
const profiles = [
  'bear', 'cat', 'dog', 'rabbit', 'fox', 'wolf', 
  'tiger', 'lion', 'elephant', 'giraffe', ...
];

// 닉네임 자동 생성 (변경 가능)
const defaultNickname = `이야기꾼_${Math.random().toString(36).substr(2, 5)}`;
```

#### 로비 시스템
1. **방 생성 (방장)**
   - PeerJS 초기화 및 peer ID 생성
   - 압축된 방 ID를 초대 링크로 변환
   - WebRTC 연결 대기

2. **방 참가 (게스트)**
   - 초대 링크의 방 ID 파싱
   - 방장과 P2P 연결 수립
   - 기존 참가자들과 메시 연결

### 2️⃣ 게임 설정 단계

#### 설정 가능 옵션
```javascript
const gameSettings = {
  turnTime: 30,        // 30-40초 (2초 단위)
  cardCount: 4,        // 스토리 카드 수
  gameMode: 0,         // 0-8 (9가지 스타일)
  maxPlayers: 6        // 최대 인원
};
```

#### 9가지 그림 스타일
| 모드 | 스타일명 | 프롬프트 특징 |
|------|----------|---------------|
| 0 | 기본 | 일반적인 동화책 스타일 |
| 1 | 3D | 3D 렌더링, 입체적 표현 |
| 2 | 코믹북 | 만화책, 말풍선 포함 |
| 3 | 클레이 | 클레이 애니메이션 스타일 |
| 4 | 유치원 | 크레용, 아동 그림체 |
| 5 | 픽셀 | 8비트 레트로 게임 |
| 6 | PS1 | 초기 3D 폴리곤 |
| 7 | 동화책 | 수채화 동화 일러스트 |
| 8 | 일러스트 | 현대적 디지털 아트 |

### 3️⃣ 게임 진행 단계

#### 턴 순서 결정 (무작위)
```javascript
// 참가자 배열 인덱스를 무작위로 섞어 턴 순서 결정
const inGameOrder = shuffleArray([0, 1, 2, 3, 4, 5].slice(0, participants.length));

// 각 플레이어의 턴 순서 계산
participants.forEach((p, i) => {
  if (p.id === peerId) {
    const turnIndex = inGameOrder.indexOf(i);
    myTurn = turnIndex; // 실제 턴 순서 (0부터 시작)
  }
});
```

#### 카드 시스템
```javascript
// 플레이어당 카드 배분
const playerCards = {
  storyCards: [
    { id: 1, keyword: "마법의 숲" },
    { id: 2, keyword: "신비한 동굴" },
    { id: 3, keyword: "황금 열쇠" },
    { id: 4, keyword: "비밀의 문" }
  ],
  endingCard: {
    content: "그리고 모두 행복하게 살았답니다"
  }
};
```

#### 이야기 제출 프로세스
1. **문장 작성**: 카드 키워드를 포함한 문장 작성
2. **프롬프트 필터링**: 부적절한 내용 검사
3. **이미지 생성 요청**: GPT → Gemini 파이프라인
4. **투표 시작**: 10초간 찬성/반대 투표
5. **결과 처리**: 과반수 이상 찬성 시 통과

#### 투표 시스템 상세
```javascript
// 투표 로직
const voteEnd = async (data) => {
  // 투표 집계
  const upCount = votings.filter(v => v.selected === 'up').length;
  const downCount = votings.filter(v => v.selected === 'down').length;
  
  // 과반수 판정 (동수일 경우 찬성)
  const accepted = upCount >= downCount;
  
  if (accepted) {
    // 통과: 점수 +2, 카드 제거, 다음 턴
    currentPlayer.score += 2;
    removeUsedCard();
    nextTurn();
  } else {
    // 탈락: 점수 -1, 이미지 삭제, 다음 턴
    currentPlayer.score -= 1;
    removeLastBookPage();
    nextTurn();
  }
};
```

### 4️⃣ 결말 단계

#### 결말 카드 사용 조건
- 긴장감 35% 이상 도달 시 사용 가능
- 긴장감 계산: `(현재 페이지 수 / (플레이어 수 × 3)) × 100`

#### 게임 종료 조건
1. **정상 종료**: 결말 카드 투표 통과
2. **강제 종료**: 긴장감 100% 초과
3. **비정상 종료**: 모든 플레이어 퇴장

### 5️⃣ 결과 단계

#### 점수 계산 시스템
| 행동 | 점수 변화 | 설명 |
|------|-----------|------|
| 스토리 카드 통과 | +2점 | 일반 문장 승인 |
| 스토리 카드 탈락 | -1점 | 투표 부결 |
| 결말 카드 성공 | +5점 | 게임 성공적 종료 |
| 타임아웃 | -1점 | 시간 초과 |
| 부적절한 콘텐츠 | -1점 | 필터링 감지 |

#### 책 생성 프로세스
```javascript
// 1. 책 제목 생성 (GPT-5-nano)
const generateBookTitle = async (scenes) => {
  const prompt = `다음 이야기의 제목을 지어주세요: ${scenes.join(' ')}`;
  return await callGPT(prompt);
};

// 2. 표지 이미지 생성 (Gemini)
const generateCoverImage = async (title, summary) => {
  const prompt = `동화책 표지, 제목: ${title}, 내용: ${summary}`;
  return await callGemini(prompt);
};

// 3. 데이터베이스 저장
const saveBook = async (bookData) => {
  await bookRepository.save(bookData);
  await s3Service.uploadImages(bookData.scenes);
};
```

## 🔌 P2P 통신 메커니즘 상세

### WebRTC/PeerJS 구조

#### 연결 수립 과정
```javascript
// 1. Peer 초기화
const peer = new Peer({
  config: {
    iceServers: [{
      urls: TURN_SERVER_URL,
      username: TURN_ID,
      credential: TURN_PW
    }]
  }
});

// 2. 연결 설정
const setupConnection = (conn) => {
  // ICE 연결 상태 모니터링
  conn.peerConnection.oniceconnectionstatechange = () => {
    if (state === 'failed' || state === 'disconnected') {
      handleReconnection(conn.peer);
    }
  };
  
  // 하트비트 유지 (5초마다)
  setInterval(() => {
    if (conn.open) {
      sendMessage("heartbeat", { timestamp: Date.now() }, conn);
    }
  }, 5000);
};

// 3. 메시지 처리
conn.on("data", (data) => {
  switch(data.type) {
    case "gameStart": handleGameStart(data); break;
    case "sendPrompt": handlePromptReceived(data); break;
    case "voteResult": handleVoteResult(data); break;
    case "nextTurn": handleNextTurn(data); break;
    // ... 기타 메시지 타입
  }
});
```

#### 주요 P2P 메시지 타입

| 메시지 타입 | 발신자 | 수신자 | 용도 |
|------------|--------|--------|------|
| newParticipant | 신규 참가자 | 방장 | 참가 알림 |
| currentParticipants | 방장 | 신규 참가자 | 현재 상태 동기화 |
| gameStart | 방장 | 전체 | 게임 시작 신호 |
| sendPrompt | 현재 턴 | 전체 | 문장 전송 |
| sendImage | 현재 턴 | 전체 | 이미지 전송 |
| voteResult | 각 플레이어 | 전체 | 투표 결과 |
| nextTurn | 현재 턴 | 전체 | 다음 턴 진행 |
| stopVotingAndShowWarning | 현재 턴 | 전체 | 부적절 콘텐츠 알림 |
| showResultsWithCover | 방장 | 전체 | 게임 종료 및 결과 |
| bookCoverUpdate | 방장 | 전체 | 표지 업데이트 |

### 상태 동기화 메커니즘

#### 게임 상태 관리
```javascript
// 공유 상태 (모든 플레이어 동기화)
const sharedState = {
  participants: [],      // 참가자 목록
  inGameOrder: [],      // 턴 순서
  currTurn: 0,          // 현재 턴 인덱스
  bookContents: [],     // 책 내용
  votings: [],          // 투표 현황
  isElected: false      // 선출 여부
};

// 개인 상태 (각자 관리)
const localState = {
  myTurn: null,         // 내 턴 순서
  storyCards: [],       // 내 카드
  isVoted: false,       // 투표 여부
  peerId: ""           // 내 peer ID
};
```

#### 타이머 동기화
```javascript
// 투표 타이머 (10초)
let voteTimer = setTimeout(async () => {
  if (!isVoted) {
    // 자동으로 찬성 투표
    await voteEnd({ selected: "up" });
  }
}, 10000);

// 경고 타이머 (3초)
let warningTimer = setTimeout(async () => {
  await showOverlay('whoTurn');
  inProgress = true;
}, 3000);
```

## 🐛 최근 해결된 주요 버그 상세 분석

### Bug #1: 부적절한 콘텐츠 생성 후 투표 참여 불가

#### 증상
- 부적절한 이미지 생성으로 경고 발생 후 다음 턴에서 투표 불가
- 투표 UI는 표시되지만 실제 투표가 전송되지 않음

#### 원인 분석
```javascript
// 문제 코드
const stopVotingAndShowWarning = async (data) => {
  isVoted.value = true;  // ❌ 버그: 투표 완료로 잘못 설정
  // ... 경고 처리
};
```

#### 해결 방법
```javascript
// 수정된 코드
const stopVotingAndShowWarning = async (data) => {
  // isVoted를 true로 설정하지 않음
  prompt.value = "";     // 투표 UI 숨김
  isElected.value = false;
  
  // 타이머 정리 후 상태 초기화
  if (voteTimer) {
    clearTimeout(voteTimer);
    voteTimer = null;
  }
  
  // 3초 후 정상 진행
  warningTimer = setTimeout(async () => {
    isVoted.value = false;  // ✅ 다음 투표 가능하도록 리셋
    await showOverlay('whoTurn');
    inProgress.value = true;
  }, 3000);
};
```

### Bug #2: 책 페이지 넘김 비동기화

#### 증상
- 부적절한 이미지 생성 후 홀수/짝수 패턴으로 페이지 넘김 실패
- 일부 플레이어만 페이지가 넘어가는 현상

#### 원인 분석
```javascript
// 문제: voteResult 케이스에서 게스트의 isElected 동기화 누락
case "voteResult":
  if (currTurn.value === myTurn.value) {
    isElected.value = true;  // 방장만 설정
    // 게스트는 설정 안 됨 ❌
  }
  break;
```

#### 해결 방법
```javascript
// 수정: 모든 플레이어가 동일한 투표 결과 처리
case "voteResult":
  const voteAccepted = upCount >= downCount;
  
  if (currTurn.value === myTurn.value) {
    if (voteAccepted) {
      isElected.value = true;  // 방장 설정
    }
  } else {
    // ✅ 게스트도 동일하게 처리
    if (voteAccepted) {
      isElected.value = true;  // 게스트도 설정
    }
  }
  break;
```

### Bug #3: 턴 순서 표시 불일치

#### 증상
- "당신의 차례는 n번입니다" 메시지가 참가 순서를 표시
- 실제 게임은 무작위 순서로 진행되어 혼란 발생
- myTurn.svg와 프로필 표시기는 올바른 무작위 순서 표시

#### 원인 분석
```javascript
// 문제: myTurn이 participants 배열 인덱스를 저장
participants.value.forEach((p, i) => {
  if (p.id === peerId.value) {
    myTurn.value = i;  // ❌ 참가 순서 저장
  }
});

// 실제 필요한 것: inGameOrder에서의 위치
// inGameOrder = [2, 0, 3, 1] 이면
// 참가자 0번의 실제 턴은 2번째 (인덱스 1)
```

#### 해결 방법
```javascript
// 수정: inGameOrder에서의 위치를 찾아 저장
participants.value.forEach((p, i) => {
  if (p.id === peerId.value) {
    // i는 participants 배열에서의 인덱스
    const turnIndex = inGameOrder.value.indexOf(i);
    myTurn.value = turnIndex;  // ✅ 무작위 턴 순서에서의 위치
  }
});

// 결과:
// - "당신의 차례는 2번입니다" (올바른 무작위 순서)
// - 실제로 2번째 턴에 플레이
// - UI 표시기도 2번째 턴에 활성화
```

## 🔒 보안 및 안정성

### API 키 관리
```properties
# application.properties
OPENAI_API_KEY=${OPENAI_API_KEY}
GEMINI_API_KEY=${GEMINI_API_KEY}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
```

### 에러 처리 및 재시도 로직
```java
// GameService.java
@Retryable(value = {Exception.class}, maxAttempts = 5, backoff = @Backoff(delay = 2000))
public String generateBookTitle(List<String> scenes) {
    try {
        return callGPTAPI(buildPrompt(scenes));
    } catch (Exception e) {
        log.error("GPT API 호출 실패: {}", e.getMessage());
        return "아주 먼 옛날";  // 기본값 반환
    }
}
```

### 부적절한 콘텐츠 필터링
```javascript
// 503 에러 = 부적절한 콘텐츠 감지
if (error?.response?.status === 503) {
  // 1. 점수 차감
  currentPlayer.score -= 1;
  
  // 2. 콘텐츠 제거
  bookContents.pop();
  
  // 3. 경고 표시
  showInappropriateWarningModal({
    message: "부적절한 이미지가 생성되었습니다"
  });
  
  // 4. 다음 턴 진행
  nextTurn();
}
```

## 📊 성능 최적화 전략

### 이미지 생성 최적화
1. **병렬 처리**: GPT와 Gemini API 동시 호출
2. **캐싱**: Redis에 프롬프트-이미지 매핑 저장
3. **압축**: WebP 포맷으로 이미지 크기 30% 감소
4. **CDN**: CloudFront를 통한 이미지 전송 속도 개선
5. **프리로딩**: 다음 턴 이미지 미리 로드

### 프론트엔드 최적화
```javascript
// 컴포넌트 레이지 로딩
const GameView = () => import('./views/GameView.vue');
const GalleryView = () => import('./views/GalleryView.vue');

// 이미지 프리로딩
const preloadImage = (url) => {
  const img = new Image();
  img.src = url;
  return img;
};

// 디바운싱 처리
const debouncedSearch = debounce((query) => {
  searchBooks(query);
}, 300);
```

### 백엔드 최적화
```java
// 비동기 처리
@Async
public CompletableFuture<String> generateImageAsync(String prompt) {
    return CompletableFuture.supplyAsync(() -> {
        return callGeminiAPI(prompt);
    });
}

// 캐싱 전략
@Cacheable(value = "books", key = "#bookId")
public BookDto getBookById(String bookId) {
    return bookRepository.findById(bookId);
}

// 데이터베이스 인덱싱
@Table(name = "books", indexes = {
    @Index(name = "idx_created_at", columnList = "created_at"),
    @Index(name = "idx_view_count", columnList = "view_count")
})
```

## 🚀 배포 및 인프라

### Docker 컨테이너화
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./BE
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
    depends_on:
      - mysql
      - redis
  
  frontend:
    build: ./FE
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
  
  ai-server:
    build: ./AI
    ports:
      - "8190:8190"
    environment:
      - PYTHONUNBUFFERED=1
  
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: longago
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### AWS 인프라 구성
```
EC2 인스턴스
├── Application Load Balancer
│   ├── Target Group 1: Backend (8080)
│   ├── Target Group 2: Frontend (80)
│   └── Target Group 3: AI Server (8190)
├── RDS (MySQL)
│   ├── Multi-AZ 구성
│   └── 자동 백업 활성화
├── ElastiCache (Redis)
│   └── 클러스터 모드
├── S3 Bucket
│   ├── /images (게임 이미지)
│   ├── /covers (책 표지)
│   └── /characters (캐릭터 프리셋)
└── CloudFront CDN
    └── S3 오리진
```

### CI/CD 파이프라인
```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Backend
        run: |
          cd BE
          ./gradlew build
          docker build -t longago-backend .
      
      - name: Build Frontend
        run: |
          cd FE
          npm install
          npm run build
          docker build -t longago-frontend .
      
      - name: Deploy to ECR
        run: |
          aws ecr get-login-password | docker login
          docker push $ECR_REGISTRY/longago-backend
          docker push $ECR_REGISTRY/longago-frontend
      
      - name: Update ECS Service
        run: |
          aws ecs update-service --cluster longago --service backend
          aws ecs update-service --cluster longago --service frontend
```

## 📝 API 문서 상세

### Game API Endpoints

#### POST /game - 게임 생성
```json
Request:
{
  "bossId": "uuid-string",
  "players": ["player1-id", "player2-id"],
  "drawingStyle": 0,
  "turnTime": 30
}

Response:
{
  "success": true,
  "data": {
    "gameId": "game-uuid",
    "status": {
      "storyCards": [
        {"id": 1, "keyword": "마법의 숲"},
        {"id": 2, "keyword": "신비한 동굴"}
      ],
      "endingCard": {
        "content": "그리고 모두 행복하게..."
      }
    }
  }
}
```

#### DELETE /game - 게임 종료
```json
Request:
{
  "gameId": "game-uuid",
  "isForceStopped": false
}

Response:
{
  "success": true,
  "data": {
    "bookId": "book-uuid",
    "title": "용감한 모험가의 이야기",
    "bookCover": "https://s3.amazonaws.com/covers/book-uuid.png"
  }
}
```

### Scene API Endpoints

#### POST /scene - 이미지 생성
```json
Request:
{
  "gameId": "game-uuid",
  "userId": "user-uuid",
  "userPrompt": "마법의 숲에서 용을 만났다",
  "turn": 1,
  "isEnding": false
}

Response:
{
  "success": true,
  "data": {
    "imageUrl": "https://s3.amazonaws.com/images/scene-uuid.png",
    "processTime": 3500
  }
}
```

## 🔍 트러블슈팅 가이드

### 일반적인 문제 해결

#### 1. WebRTC 연결 실패
```javascript
// 문제: NAT/방화벽으로 인한 P2P 연결 실패
// 해결: TURN 서버 설정
const peer = new Peer({
  config: {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' },
      {
        urls: 'turn:your-turn-server.com:3478',
        username: 'username',
        credential: 'password'
      }
    ]
  }
});
```

#### 2. 이미지 생성 타임아웃
```java
// 문제: Gemini API 응답 시간 초과
// 해결: 타임아웃 시간 증가 및 재시도
@Bean
public WebClient webClient() {
    return WebClient.builder()
        .clientConnector(new ReactorClientHttpConnector(
            HttpClient.create()
                .responseTimeout(Duration.ofSeconds(30))
        ))
        .build();
}
```

#### 3. Redis 세션 만료
```properties
# 문제: 게임 중 세션 만료
# 해결: TTL 시간 연장
spring.redis.timeout=7200
spring.session.redis.flush-mode=on_save
spring.session.redis.namespace=spring:session
```

## 📈 모니터링 및 로깅

### 로깅 전략
```java
// Logback 설정
@Slf4j
public class GameService {
    public void startGame(String gameId) {
        log.info("게임 시작: gameId={}", gameId);
        MDC.put("gameId", gameId);
        
        try {
            // 게임 로직
        } catch (Exception e) {
            log.error("게임 시작 실패: gameId={}, error={}", 
                gameId, e.getMessage(), e);
        } finally {
            MDC.clear();
        }
    }
}
```

### 메트릭 수집
```javascript
// 프론트엔드 성능 메트릭
const measurePerformance = () => {
  const perfData = performance.getEntriesByType('navigation')[0];
  
  const metrics = {
    loadTime: perfData.loadEventEnd - perfData.fetchStart,
    domReady: perfData.domContentLoadedEventEnd - perfData.fetchStart,
    resourceLoad: perfData.responseEnd - perfData.fetchStart
  };
  
  // 백엔드로 메트릭 전송
  sendMetrics(metrics);
};
```

## 🎯 향후 개발 계획

### 단기 목표 (1-3개월)
1. **모바일 앱 개발**: React Native 기반 iOS/Android 앱
2. **AI 모델 개선**: GPT-4 Vision 통합으로 이미지 일관성 향상
3. **실시간 음성 채팅**: WebRTC 음성 채널 추가
4. **토너먼트 모드**: 경쟁 게임 모드 추가

### 중기 목표 (3-6개월)
1. **글로벌 확장**: 다국어 지원 (영어, 일본어, 중국어)
2. **NFT 통합**: 완성된 책을 NFT로 발행
3. **AI 캐릭터**: NPC 플레이어 추가
4. **스트리밍 기능**: Twitch/YouTube 연동

### 장기 목표 (6-12개월)
1. **메타버스 통합**: 3D 가상 공간에서 게임 진행
2. **출판 서비스**: 실제 책 출판 연계
3. **교육 플랫폼**: 학교/교육기관용 버전
4. **AI 스토리 코치**: 이야기 작성 도우미

## 🤝 기여 가이드

### 개발 환경 설정
```bash
# 저장소 클론
git clone https://github.com/yourusername/long-ago.git
cd long-ago

# Backend 설정
cd BE
cp .env.example .env
# .env 파일에 API 키 설정
./gradlew build
./gradlew bootRun

# Frontend 설정
cd ../FE
npm install
npm run dev

# AI Server 설정
cd ../AI
pip install -r requirements.txt
python api_main.py
```

### 코드 스타일 가이드
- **Java**: Google Java Style Guide
- **JavaScript**: Airbnb JavaScript Style Guide
- **Python**: PEP 8
- **커밋 메시지**: Conventional Commits

### 테스트 작성
```java
// JUnit 5 테스트 예시
@Test
void testGameCreation() {
    // Given
    GameCreateRequest request = new GameCreateRequest();
    request.setBossId("test-boss");
    request.setPlayers(Arrays.asList("player1", "player2"));
    
    // When
    GameResponse response = gameService.createGame(request);
    
    // Then
    assertNotNull(response.getGameId());
    assertEquals(2, response.getPlayerCount());
}
```

## 📄 라이선스 및 저작권

### 오픈소스 라이브러리
- Vue.js: MIT License
- Spring Boot: Apache License 2.0
- PeerJS: MIT License
- FastAPI: MIT License

### 자체 개발 코드
- 저작권: Long Ago Team
- 라이선스: Proprietary (비공개)

### 이미지 및 아트워크
- 캐릭터 디자인: 자체 제작
- AI 생성 이미지: 사용자 소유권

## 📞 연락처 및 지원

### 기술 지원
- Email: support@longago.game
- Discord: https://discord.gg/longago
- Documentation: https://docs.longago.game

### 버그 리포트
- GitHub Issues: https://github.com/longago/issues
- Bug Tracker: https://bugs.longago.game

### 커뮤니티
- Reddit: r/LongAgoGame
- Twitter: @LongAgoGame
- YouTube: Long Ago Official

---

**Last Updated**: 2025-09-07  
**Version**: 2.1.0  
**Contributors**: 15+ developers

> "모든 위대한 이야기는 '아주 먼 옛날'로 시작됩니다..."
