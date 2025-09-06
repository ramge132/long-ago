# 🎮 Long Ago 프로젝트 기술 정리본

## 📌 프로젝트 핵심 정보

### 프로젝트 개요
- **이름**: Long Ago (아주 먼 옛날)
- **유형**: 실시간 웹 기반 협동 스토리텔링 게임
- **핵심 메커니즘**: 
  - 사용자들이 순서대로 한 문장씩 이야기를 이어가며 하나의 완성된 책 제작
  - AI가 실시간으로 각 문장에 대한 삽화 생성
  - P2P 통신으로 실시간 멀티플레이어 게임 진행

## 🏗️ 기술 아키텍처

### 1. Backend (Spring Boot)
```
- Framework: Spring Boot 3.x
- Language: Java 17+
- Database: 
  - MySQL (영구 데이터: 완성된 책, 사용자 정보)
  - Redis (임시 데이터: 게임 세션, 장면 데이터)
- Storage: AWS S3 (이미지 파일 영구 저장)
- API Clients:
  - OpenAI WebClient (GPT-5-nano API)
  - Gemini WebClient (Gemini 2.5 Flash Image Preview)
  - Python Service WebClient (통합 이미지 서비스)
```

#### 핵심 서비스
- **GameService**: 게임 생성/종료, 책 표지 생성
- **SceneService**: 장면 생성, 이미지 생성 요청
- **BookService**: 책 조회, 자동 삭제 (7일)
- **S3Service**: AWS S3 이미지 업로드
- **FilteringService**: 프롬프트 필터링

### 2. Frontend (Vue.js)
```
- Framework: Vue.js 3 (Composition API)
- Build Tool: Vite
- Styling: Tailwind CSS
- State Management: Pinia
- P2P Communication: PeerJS (WebRTC)
- Router: Vue Router
```

#### 핵심 컴포넌트
- **GameView.vue**: 메인 게임 로직, P2P 통신 관리
- **InGameContent.vue**: 게임 플레이 UI
- **LobbyView.vue**: 게임 대기실
- **ResultView.vue**: 게임 결과 화면

### 3. AI/이미지 생성 시스템 (Python)
```
- Framework: FastAPI
- Port: 8190
- LLM: OpenAI GPT-5-nano
- Image Gen: Google Gemini 2.5 Flash Image Preview
- 특징:
  - 재시도 로직 (장면: 1회, 표지: 7회)
  - 바이너리 이미지 데이터 직접 반환
  - 비동기 처리 (asyncio)
```

## 🎲 게임 시스템

### 카드 시스템
```
플레이어당 카드:
- 이야기 카드 4장 (인물, 사물, 장소, 사건/상태)
- 결말 카드 1장

카드 분배 로직:
- 인물 카드는 반드시 1장
- 나머지 3장은 중복 없이 랜덤 속성
```

### 점수 시스템
```
- 이야기 카드 통과: +2점
- 결말 카드 통과: +5점
- 투표 탈락: -1점
- 타임아웃: -1점
- 부적절한 콘텐츠: -1점
- 초기 점수: 10점
```

### 투표 시스템
```
- 투표 시간: 10초
- 통과 조건: 찬성 >= 반대
- 투표 미참여 시: 현재 선택값(기본: 찬성)으로 자동 투표
```

### 긴장감 시스템
```
- 계산식: (현재 장면 수 / (플레이어 수 × 3)) × 100
- 35% 이상: 결말 카드 사용 가능
- 100% 도달: 게임 강제 종료 (전체 실패)
```

## 📡 P2P 통신 프로토콜

### 메시지 타입 (30여종)
```javascript
주요 메시지:
- newParticipant: 새 참가자 입장
- currentParticipants: 현재 참가자 목록
- gameStart: 게임 시작
- sendPrompt: 문장 제출
- sendImage: 이미지 전송 (ArrayBuffer)
- voteResult: 투표 결과
- nextTurn: 다음 턴
- stopVotingAndShowWarning: 부적절한 콘텐츠 경고
- gameEnd: 게임 종료
- showResultsWithCover: 결과창 표시
- bookCoverUpdate: 표지 업데이트
```

### 연결 관리
```
- STUN/TURN 서버 사용
- 하트비트: 5초 간격
- 재연결: 3초 후 자동 시도
- 최대 참가자: 6명
```

## 🔄 데이터 플로우

### 이미지 생성 플로우
```
1. 사용자 입력 (Vue.js)
   ↓
2. API 요청 (Spring Boot)
   ↓
3. Python 서비스 호출 (FastAPI)
   ↓
4. Gemini API 호출 (직접 이미지 생성)
   ↓
5. 바이너리 이미지 반환
   ↓
6. Redis 임시 저장
   ↓
7. WebRTC로 모든 플레이어에게 전송
   ↓
8. 게임 종료 시 S3 업로드
```

### 책 표지 생성 플로우
```
1. 게임 종료 트리거
   ↓
2. Python 서비스에 스토리 전송
   ↓
3. GPT-5-nano로 제목 생성 (최대 8회 시도)
   ↓
4. Gemini로 표지 이미지 생성 (최대 8회 시도)
   ↓
5. 제목과 이미지 반환
   ↓
6. S3 업로드 및 MySQL 저장
   ↓
7. 모든 플레이어에게 결과 전송
```

## 🐛 최근 해결된 이슈 (v2.0.0)

### P2P 동기화 버그
```
문제: 부적절한 콘텐츠 발생 후 투표 결과 표시 불일치
원인: voteTimer와 warningTimer 충돌

해결책:
1. sendPrompt 케이스에서 타이머 완전 정리
   - voteTimer, warningTimer 모두 clear
   - votings 배열 완전 초기화
   - isElected 상태 초기화

2. voteResult 케이스에서 중복 체크
   - votings 배열 추가 전 중복 검사
   - 동기화된 투표 결과 계산

3. stopVotingAndShowWarning 함수 개선
   - 모든 타이머 즉시 정리
   - 3초 후 다음 턴 진행
```

### 게임 종료 플로우 최적화
```
기존: 표지 생성 완료까지 대기 (5-10초)
개선: 비동기 처리로 1초 내 결과창 표시

구현:
1. 투표 통과 즉시 백그라운드 표지 생성 시작
2. 1초 후 기본값으로 결과창 표시
3. 표지 완성 시 자동 업데이트 (bookCoverUpdate 메시지)
```

## 🔧 환경 설정

### 필수 API 키
```bash
# Backend (.env 또는 application.properties)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=longago-images

# Python Service (.env)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
```

### 서비스 포트
```
- Backend: 8080
- Frontend: 5173 (dev) / 80 (prod)
- Python AI Service: 8190
- MySQL: 3306
- Redis: 6379
```

## 📊 성능 최적화

### 이미지 생성 최적화
- GPT 프롬프트 단계 생략 (직접 Gemini 호출)
- 재시도 로직으로 안정성 향상
- 타임아웃 설정 (장면: 12초, 표지: 20초)

### P2P 통신 최적화
- ArrayBuffer 변환으로 이미지 전송
- 하트비트로 연결 상태 모니터링
- 중복 메시지 필터링

### 프론트엔드 최적화
- 컴포넌트 lazy loading
- 이미지 blob URL 관리
- 메모리 누수 방지 (타이머 정리)

## 🚨 알려진 제한사항

### API 관련
- Gemini API 일일 할당량: 제한적
- GPT-5-nano 응답 구조 변동 가능
- 콘텐츠 필터링으로 인한 생성 거부

### 시스템 관련
- 최대 동시 접속자: 6명
- 책 자동 삭제: 7일
- 이미지 크기: 최대 10MB

### 브라우저 호환성
- Chrome/Edge: 완벽 지원
- Firefox: WebRTC 일부 제한
- Safari: TURN 서버 필수

## 📈 모니터링 포인트

### 백엔드 로그
```java
// GameService.java
log.info("🎮🎮🎮 === finishGame 시작 ===");
log.info("🎮🎮🎮 gameId: {}", gameId);

// SceneService.java  
log.info("=== 이미지 생성 요청 시작 ===");
log.info("게임ID: {}, 사용자ID: {}, 턴: {}", ...);
```

### Python 서비스 로그
```python
logger.info("=== Gemini API 호출 시작 ===")
logger.info(f"🔄 시도 {attempt}/{max_retries}")
logger.info("✅ 이미지 생성 성공")
```

### 프론트엔드 디버깅
```javascript
console.log("P2P 메시지 수신:", data.type);
console.log("투표 결과:", votings.value);
console.log("게임 종료 처리 시작");
```

## 🔮 향후 개선 방향

### 단기 계획
- [ ] Gemini API 할당량 모니터링 시스템
- [ ] 이미지 캐싱 메커니즘
- [ ] 투표 UI 개선

### 장기 계획
- [ ] 다중 언어 지원
- [ ] AI 캐릭터 일관성 향상
- [ ] 모바일 앱 개발
- [ ] 소셜 기능 추가

---

**최종 업데이트**: 2025-01-27  
**버전**: 2.0.0  
**작성자**: AI Assistant
