# 🎨 Long Ago - 실시간 협동 스토리텔링 게임

## 📖 프로젝트 개요

**Long Ago**는 LLM(GPT-5-nano)과 이미지 생성 AI(Gemini 2.5 Flash Image Preview)를 활용한 실시간 협동 스토리텔링 웹게임입니다. 사용자들이 순서대로 한 문장씩 이야기를 이어가며 하나의 완성된 이야기책을 만들어가는 게임입니다.

### 핵심 기능
- 사용자가 입력한 문장을 GPT-5-nano를 통해 이미지 생성용 프롬프트로 변환
- Gemini 2.5 Flash Image Preview API로 실시간 삽화 생성
- WebRTC P2P 통신을 통한 실시간 멀티플레이어 지원
- 9가지 다양한 그림 스타일 모드 지원
- 완성된 이야기는 책으로 저장되어 갤러리에서 열람 가능

## 🏗️ 시스템 아키텍처

### 기술 스택

#### Backend (Spring Boot)
- **Framework**: Spring Boot 3.x
- **Language**: Java 17+
- **Database**: MySQL (영구 저장) + Redis (임시 게임 데이터)
- **Storage**: AWS S3 (이미지 저장)
- **API Client**: WebClient (OpenAI, Google Gemini API 호출)

#### Frontend (Vue.js)
- **Framework**: Vue.js 3 (Composition API)
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Pinia
- **P2P Communication**: PeerJS (WebRTC)
- **Routing**: Vue Router

#### AI/Image Generation
- **LLM**: OpenAI GPT-5-nano (프롬프트 생성 및 책 제목 생성)
- **Image Generation**: Google Gemini 2.5 Flash Image Preview
- **Python FastAPI**: API 서버 (포트 8190)
- **Character System**: 14종의 캐릭터 프리셋

## 📂 프로젝트 구조

```
long-ago/
├── BE/                         # Spring Boot Backend
│   ├── src/main/java/com/example/b101/
│   │   ├── controller/         # REST API 컨트롤러
│   │   │   ├── GameController.java      # 게임 관리 API
│   │   │   ├── SceneController.java     # 장면 생성 API
│   │   │   └── BookController.java      # 책 조회 API
│   │   ├── service/           # 비즈니스 로직
│   │   │   ├── GameService.java         # 게임 로직
│   │   │   ├── SceneService.java        # 장면 생성 로직
│   │   │   ├── BookService.java         # 책 관리 로직
│   │   │   ├── S3service.java           # AWS S3 업로드
│   │   │   └── FilteringService.java    # 프롬프트 필터링
│   │   ├── domain/            # JPA 엔티티
│   │   │   ├── Book.java                # 책 엔티티
│   │   │   └── Scene.java               # 장면 엔티티
│   │   ├── dto/               # 데이터 전송 객체
│   │   └── config/            # 설정 클래스
│   │       └── WebClientConfig.java     # WebClient 설정
│   └── resources/
│       └── application.properties       # 애플리케이션 설정
│
├── FE/                         # Vue.js Frontend
│   ├── src/
│   │   ├── views/             # 페이지 컴포넌트
│   │   │   ├── IntroView.vue           # 시작 화면
│   │   │   ├── GameView.vue            # 메인 게임 화면
│   │   │   ├── ResultView.vue          # 결과 화면
│   │   │   └── Game/
│   │   │       └── LobbyView.vue       # 게임 로비
│   │   ├── components/        # 재사용 컴포넌트
│   │   │   ├── InGame/                 # 게임 내 컴포넌트
│   │   │   │   ├── InGameContent.vue   # 게임 콘텐츠
│   │   │   │   └── InGameEnding.vue    # 엔딩 카드
│   │   │   └── Lobby/                  # 로비 컴포넌트
│   │   │       ├── LobbyUsers.vue      # 참가자 목록
│   │   │       └── LobbySettings.vue   # 게임 설정
│   │   ├── stores/            # Pinia 스토어
│   │   │   ├── auth.js                 # 사용자 정보
│   │   │   ├── game.js                 # 게임 상태
│   │   │   └── audio.js                # 오디오 관리
│   │   ├── apis/              # API 호출 함수
│   │   └── router/            # 라우터 설정
│
└── AI/                         # AI/이미지 생성 시스템
    └── imageGeneration/
        ├── api_main.py                  # FastAPI 서버
        ├── api_image_generator.py       # 이미지 생성 로직
        └── characters/                  # 캐릭터 프리셋
            ├── boy.png/.txt
            ├── girl.png/.txt
            └── ... (14종 캐릭터)
```

## 🎮 게임 플로우

### 1. 게임 준비
1. **프로필 선택**: 42종의 동물 프로필 중 선택
2. **닉네임 입력**: 기본값 "이야기꾼_XXXXX"
3. **로비 입장**: 방장이 방을 생성하거나 기존 방에 참여

### 2. 게임 설정
- **턴당 시간**: 30-40초 (2초 단위)
- **게임 모드**: 9가지 그림 스타일
  - 기본 모드
  - 3D 모드
  - 코믹북 모드
  - 클레이 모드
  - 유치원 모드
  - 픽셀 모드
  - PS1 모드
  - 동화책 모드
  - 일러스트 모드

### 3. 게임 진행
1. **카드 배분**: 이야기 카드 4장, 결말 카드 1장
2. **이야기 전개**: 
   - 차례대로 이야기 카드 제출
   - LLM이 문장을 이미지 프롬프트로 변환
   - AI가 삽화 생성
   - 다른 플레이어들이 찬성/반대 투표
3. **결말 맺기**: 
   - 긴장감이 충분히 쌓이면 결말 카드 사용
   - 결말 투표 통과 시 게임 종료
4. **결과**: 
   - 점수 집계 및 우승자 발표
   - 완성된 이야기책 표지 생성
   - 갤러리에 저장

### 4. 점수 시스템
- 이야기 카드 통과: +10점
- 이야기 카드 실패: -5점
- 결말 카드 성공: +30점
- 결말 카드 실패: -15점

## 🔧 주요 기능 구현

### Backend 주요 기능

#### GameService.java
- `saveGame()`: 게임 생성 및 Redis 저장
- `finishGame()`: 게임 종료 처리 및 책 생성
- `generateBookTitle()`: GPT-5-nano로 책 제목 생성 (5회 재시도)
- `generateCoverImage()`: Gemini API로 표지 생성 (1회 재시도)
- `shuffleEndingCard()`: 결말 카드 리롤

#### SceneService.java
- `createScene()`: 장면 생성 메인 로직
- `callGPTWithRetry()`: GPT API 호출 (1회 재시도)
- `callGeminiWithRetry()`: Gemini API 호출 (1회 재시도)
- `parseGeminiResponse()`: Gemini 응답 파싱 및 에러 처리
- `uploadImageToS3()`: S3 이미지 업로드

#### BookService.java
- `getBooksByPageSort()`: 조회수/최신순 정렬 페이지네이션
- `getBookById()`: 특정 책 조회 및 조회수 증가
- `findBook1to3()`: 상위 3개 책 조회
- `autoDeleteBook()`: 7일 지난 책 자동 삭제 (매일 정오)

### Frontend 주요 기능

#### GameView.vue
- **WebRTC P2P 통신**: PeerJS를 통한 실시간 통신
- **게임 상태 관리**: 턴 관리, 투표 처리, 카드 관리
- **타이머 관리**: 턴별 제한 시간 카운트다운
- **메시지 처리**: 
  - `cardSubmit`: 카드 제출
  - `voteResult`: 투표 결과
  - `gameEnd`: 게임 종료
  - `bookCover`: 표지 데이터 전송

#### InGameContent.vue
- **카드 선택/제출**: 드래그 앤 드롭 인터페이스
- **실시간 삽화 표시**: 생성된 이미지 즉시 렌더링
- **투표 UI**: 찬성/반대 버튼 및 결과 표시
- **TTS 지원**: 제출된 문장 음성 재생

#### LobbyView.vue
- **방 생성/참여**: 방장/참가자 구분
- **실시간 참가자 목록**: WebRTC 연결 상태 표시
- **게임 설정**: 모드, 시간 설정
- **초대 링크**: 클립보드 복사 기능

### AI/이미지 생성 시스템

#### api_main.py (FastAPI)
- `/generate`: 이미지 생성 엔드포인트
- 세션별 컨텍스트 유지
- S3 업로드 통합
- 캐릭터 시스템 관리

#### api_image_generator.py
- **프롬프트 생성**: GPT-5-nano 활용
- **이미지 생성**: Gemini 2.5 Flash 호출
- **스타일 적용**: 9가지 모드별 프롬프트 조정
- **캐릭터 일관성**: 14종 캐릭터 프리셋 활용

## 🔐 환경 설정

### Backend (.env)
```properties
# Database
spring.datasource.url=jdbc:mysql://localhost:3306/longago
spring.datasource.username=
spring.datasource.password=

# Redis
spring.redis.host=localhost
spring.redis.port=6379

# API Keys
OPENAI_API_KEY=
GEMINI_API_KEY=

# AWS S3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
```

### AI Server (.env)
```bash
OPENAI_API_KEY=
GEMINI_API_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
```

## 🚀 실행 방법

### Backend
```bash
cd BE
./gradlew build
java -jar build/libs/b101-0.0.1-SNAPSHOT.jar
```

### Frontend
```bash
cd FE
npm install
npm run dev  # 개발 모드
npm run build  # 프로덕션 빌드
```

### AI Server
```bash
cd AI/imageGeneration
pip install -r requirements.txt
python api_main.py  # 포트 8190
```

## 📊 데이터베이스 스키마

### Book 테이블
- `id`: INT (PK, AUTO_INCREMENT)
- `book_id`: VARCHAR (UNIQUE, NOT NULL)
- `book_title`: VARCHAR (NOT NULL)
- `image_url`: VARCHAR (표지 이미지 URL)
- `view_count`: INT (조회수)
- `created_at`: DATETIME

### Scene 테이블
- `id`: INT (PK, AUTO_INCREMENT)
- `book_id`: INT (FK → Book)
- `scene_order`: INT (장면 순서)
- `prompt`: TEXT (사용자 입력 문장)
- `image_url`: VARCHAR (장면 이미지 URL)

## 🎯 주요 API 엔드포인트

### Game API
- `POST /game`: 게임 생성
- `DELETE /game`: 게임 종료 및 책 생성
- `PATCH /game/shuffle`: 결말 카드 리롤
- `GET /game`: 플레이어 상태 조회

### Scene API
- `POST /scene`: 장면 생성 (이미지 생성)
- `POST /scene/filtering`: 프롬프트 필터링
- `POST /scene/vote`: 투표 결과 처리

### Book API
- `GET /book/{page}`: 책 목록 조회 (페이지네이션)
- `GET /book?id={id}`: 특정 책 조회
- `GET /book/top3`: 상위 3개 책 조회

### AI Image Generation API
- `POST /generate`: 이미지 생성
- `GET /health`: 서버 상태 확인
- `GET /characters`: 캐릭터 목록 조회

## 🔍 알려진 이슈 및 해결 방법

### 1. 책 표지 로딩 문제
- **문제**: 책 표지만 404 에러 발생 (일반 장면은 정상)
- **원인**: 게임 종료 시점과 표지 생성 타이밍 불일치
- **해결**: 
  - GameService에 retry 로직 추가
  - 10초 대기 후 결과 화면 전환
  - WebRTC로 표지 데이터 브로드캐스트

### 2. API 키 설정
- **문제**: GPT/Gemini API 키 미설정
- **해결**: 환경변수 또는 application.properties에 설정

### 3. CORS 설정
- **문제**: 프론트엔드-백엔드 통신 차단
- **해결**: WebConfig에서 CORS 허용 설정

## 📈 성능 최적화

### 이미지 생성 최적화
- 재시도 로직으로 안정성 향상
- 세션별 컨텍스트 유지로 일관성 개선
- S3 업로드로 서버 부하 감소

### 프론트엔드 최적화
- 이미지 프리로딩
- 컴포넌트 lazy loading
- WebRTC 연결 풀 관리

### 백엔드 최적화
- Redis 캐싱으로 응답 속도 개선
- 비동기 처리 (@Async)
- 데이터베이스 인덱싱

## 🔄 업데이트 이력

### Version 2.0.0 (2025-01-27) - P2P 동기화 개선 및 게임 플로우 최적화

#### 🚀 주요 개선사항
1. **P2P 메시지 타이밍 최적화**
   - 게스트 플레이어의 결과창 지연 표시 문제 해결
   - 방장과 게스트의 동기화된 게임 종료 플로우 구현
   - 중복 결과창 표시 문제 완전 해결

2. **비동기 책 표지 생성 구현**
   - 표지 생성 응답 대기 → 요청 후 즉시 진행으로 변경
   - 게임 종료 후 1초 내에 모든 플레이어가 결과창 확인 가능
   - 백그라운드 표지 생성 완료 시 자동 업데이트

#### 🔧 기술적 개선사항

**Frontend (GameView.vue)**
- `voteEnd()` 함수 리팩토링: 동기화된 게임 종료 처리
- `gameEnd()` 함수 최적화: 비동기 표지 생성 구현
- 새로운 P2P 메시지 타입 추가:
  - `gameEndPrepare`: 게임 종료 준비 알림
  - `showResultsWithCover`: 표지 정보와 함께 결과창 표시
  - `bookCoverUpdate`: 실제 표지 생성 완료 후 업데이트

**Backend (GameService.java)**
- GPT-5 Responses API 구조 개선
- 중복 `input` 필드 제거로 API 호출 오류 해결
- 응답 파싱 로직 강화 및 fallback 처리 개선
- 에러 복원력 향상으로 게임 블로킹 방지

#### 🎮 게임 플로우 개선
1. **투표 통과 즉시**: 백그라운드 표지 생성 요청 시작
2. **1초 후**: 모든 플레이어에게 기본값으로 결과창 표시
3. **표지 완성 시**: 실제 표지로 자동 업데이트

#### 🐛 해결된 주요 버그
- ❌ 게스트 플레이어 결과창 지연 표시
- ❌ 방장 중복 결과창 표시  
- ❌ 표지 생성 대기로 인한 긴 로딩 시간
- ❌ P2P 메시지 타이밍 불일치
- ❌ GPT-5 API 요청 구조 오류

### Version 1.0.0 (2025-09-02) - 기본 기능 구현
- GPT-3.5-turbo → GPT-5-nano 마이그레이션
- CDN 제거, 정적 이미지 로딩으로 변경
- Vast.ai/Runpod → API 방식으로 전환
- 책 표지 생성 retry 로직 추가

## 📝 라이선스

이 프로젝트는 비공개 프로젝트입니다.

---

**Last Updated**: 2025-01-27  
**Version**: 2.0.0
