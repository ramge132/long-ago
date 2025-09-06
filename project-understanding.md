# 🎮 Long Ago (아주 먼 옛날) - 프로젝트 완전 이해 가이드

## 📌 프로젝트 핵심 요약

**Long Ago**는 여러 사용자가 실시간으로 협력하여 하나의 동화책을 만드는 웹 게임입니다. 각 플레이어가 입력한 문장은 AI를 통해 즉시 삽화로 변환되어 시각적인 스토리북을 완성합니다.

### 🎯 핵심 동작 원리
```
사용자 문장 입력 → GPT-5-nano (프롬프트 최적화) → Gemini 2.5 Flash (이미지 생성) → 실시간 P2P 동기화
```

## 🏗️ 기술 스택 및 시스템 구조

### Frontend (Vue.js 3)
- **프레임워크**: Vue 3 (Composition API)
- **빌드 도구**: Vite 5.x
- **상태 관리**: Pinia
- **P2P 통신**: PeerJS (WebRTC wrapper)
- **스타일링**: Tailwind CSS
- **HTTP 통신**: Axios

### Backend (Spring Boot)
- **프레임워크**: Spring Boot 3.x
- **언어**: Java 17+
- **데이터베이스**: 
  - MySQL 8.0 (영구 데이터: 책, 장면, 사용자)
  - Redis 7.x (임시 데이터: 게임 세션, 카드)
- **외부 서비스**:
  - OpenAI API (GPT-5-nano)
  - Google Gemini API (2.5 Flash Image Preview)
  - AWS S3 (이미지 저장)

### AI Service (Python FastAPI)
- **프레임워크**: FastAPI
- **포트**: 8190
- **주요 라이브러리**: httpx, uvicorn
- **역할**: 
  - GPT와 Gemini API 통합 관리
  - 이미지 생성 재시도 로직
  - 바이너리 이미지 데이터 직접 반환

## 🎮 게임 플로우 상세

### 1. 게임 준비 단계

#### 프로필 설정
- 42종 동물 프로필 중 선택
- 자동 생성 닉네임 (변경 가능)

#### 로비 시스템
```javascript
// 방장이 방 생성
const peer = new Peer(config);
const roomId = compressUUID(peerId);
const inviteLink = `${baseUrl}?roomID=${roomId}`;

// 게스트 참가
connectToRoom(decompressUUID(roomId));
```

### 2. 게임 설정
- **제한 시간**: 30-40초 (2초 단위)
- **카드 개수**: 스토리 카드 4개
- **그림 스타일**: 9가지 (애니메이션, 3D, 코믹북 등)
- **최대 인원**: 6명

### 3. 게임 진행

#### 턴 순서 결정 (무작위)
```javascript
// GameView.vue
const inGameOrder = shuffleArray([0, 1, 2, 3, 4, 5].slice(0, participants.length));

// 각 플레이어의 실제 턴 순서 계산
participants.forEach((p, i) => {
  if (p.id === peerId) {
    const turnIndex = inGameOrder.indexOf(i);
    myTurn = turnIndex; // 무작위 턴 순서
  }
});
```

#### 이야기 제출 프로세스
1. **문장 작성**: 카드 키워드 포함 필수
2. **필터링 검사**: 부적절한 내용 체크
3. **이미지 생성**: Python 서비스 호출
4. **투표 진행**: 10초간 찬성/반대
5. **결과 처리**: 과반수 승인 시 통과

#### 투표 시스템
```javascript
// 투표 집계 및 결과 처리
const upCount = votings.filter(v => v.selected === 'up').length;
const downCount = votings.filter(v => v.selected === 'down').length;
const accepted = upCount >= downCount; // 동수 시 찬성

if (accepted) {
  currentPlayer.score += 2;  // 일반 카드
  // 또는
  currentPlayer.score += 5;  // 결말 카드
} else {
  currentPlayer.score -= 1;
  bookContents.pop();  // 이미지 제거
}
```

### 4. 결말 조건

#### 정상 종료
- 긴장감 35% 이상 시 결말카드 사용 가능
- 결말카드 투표 통과 시 게임 종료

#### 강제 종료
- 긴장감 100% 초과
- 모든 플레이어 퇴장

## 💡 핵심 기능별 코드 위치

### P2P 통신 (WebRTC)
**파일**: `FE/src/views/GameView.vue`

주요 메시지 타입:
- `gameStart`: 게임 시작 신호
- `sendPrompt`: 문장 전송
- `sendImage`: 이미지 전송
- `voteResult`: 투표 결과
- `nextTurn`: 다음 턴 진행
- `stopVotingAndShowWarning`: 부적절 콘텐츠 경고
- `showResultsWithCover`: 게임 종료 및 결과

### 이미지 생성 파이프라인
**Backend**: `BE/src/main/java/com/example/b101/service/SceneService.java`
**Python**: `AI/unified_image_service.py`

```python
# Python 서비스 플로우
async def generate_scene_image(request):
    # 1. 직접 Gemini로 이미지 생성 (GPT 단계 제거로 속도 향상)
    style = DRAWING_STYLES[request.drawingStyle]
    enhanced_prompt = f"{style} 스타일로 그린 {request.userPrompt} 이미지"
    
    # 2. Gemini API 호출 (재시도 로직 포함)
    image_data = await _generate_image_with_gemini(enhanced_prompt)
    
    # 3. 바이너리 이미지 데이터 반환
    return image_data  # S3 업로드는 Java에서 처리
```

### 부적절 콘텐츠 처리
**503 에러 = 부적절한 콘텐츠**

```javascript
// GameView.vue - stopVotingAndShowWarning 함수
const stopVotingAndShowWarning = async (data) => {
  // 1. 투표 즉시 중단
  prompt.value = "";
  isElected.value = false;
  votings.value = [];
  
  // 2. 점수 차감
  affectedPlayer.score -= 1;
  
  // 3. 책 내용 제거
  bookContents.value.pop();
  
  // 4. 경고 모달 표시
  showInappropriateWarningModal(data.warningData);
  
  // 5. 3초 후 다음 턴
  setTimeout(async () => {
    await showOverlay('whoTurn');
    inProgress.value = true;
  }, 3000);
};
```

## 🐛 최근 해결된 주요 버그

### Bug #1: 부적절한 콘텐츠 후 투표 불가
**원인**: `stopVotingAndShowWarning`에서 `isVoted = true` 설정
**해결**: `isVoted = false`로 유지하여 다음 투표 가능

### Bug #2: 책 페이지 넘김 비동기화
**원인**: 게스트의 `isElected` 상태 미동기화
**해결**: 
```javascript
// voteResult 케이스에 else 블록 추가
if (currTurn === myTurn) {
  isElected = voteAccepted;
} else {
  // 게스트도 동일하게 처리
  isElected = voteAccepted;
}
```

### Bug #3: 턴 순서 표시 불일치
**원인**: `myTurn`이 참가 순서를 저장
**해결**: `inGameOrder`에서의 위치를 저장
```javascript
const turnIndex = inGameOrder.indexOf(i);
myTurn = turnIndex; // 무작위 턴 순서
```

## 🚀 배포 구조

### Docker 컨테이너
- Backend (Spring Boot): 8080 포트
- Frontend (Vue.js): 80 포트  
- AI Server (Python): 8190 포트
- MySQL: 3306 포트
- Redis: 6379 포트

### AWS 인프라
- EC2: 애플리케이션 서버
- RDS: MySQL 데이터베이스
- ElastiCache: Redis 캐시
- S3: 이미지 저장소
- CloudFront: CDN

## 📊 성능 최적화

### Frontend 최적화 (완료)
- **번들 분할**: vendor 라이브러리 별도 청크
- **레이지 로딩**: 라우트별 코드 분할
- **로딩 화면**: 즉시 표시되는 인라인 CSS
- **결과**: 초기 로드 3-5초 → 1-2초

### 이미지 생성 최적화
- **직접 생성**: GPT 단계 제거로 속도 향상
- **재시도 로직**: 최대 2회 시도 (일반), 8회 시도 (표지)
- **타임아웃 설정**: 일반 12초, 표지 20초

## 🔧 환경 설정

### 필수 환경 변수
```properties
# Backend (application.properties)
OPENAI_API_KEY=${OPENAI_API_KEY}
GEMINI_API_KEY=${GEMINI_API_KEY}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

# Python Service
OPENAI_API_KEY=...
GEMINI_API_KEY=...
```

### API 엔드포인트
- **게임 생성**: POST /game
- **이미지 생성**: POST /scene
- **투표 처리**: POST /scene/vote
- **게임 종료**: DELETE /game
- **Python 이미지**: POST /generate-scene

## 📝 개발 시 주의사항

### 1. P2P 동기화
- 모든 상태 변경은 브로드캐스트 필요
- 타이머는 개별 관리 (동기화 X)
- 연결 끊김 시 자동 재연결

### 2. 이미지 생성
- 503 에러는 부적절한 콘텐츠
- 이미지는 바이너리로 직접 전달
- S3 업로드는 Java에서 처리

### 3. 투표 시스템  
- 10초 타이머 (자동 찬성)
- 동수 시 찬성 처리
- 부적절 콘텐츠는 투표 중단

### 4. 턴 관리
- `inGameOrder`: 무작위 순서 배열
- `currTurn`: 현재 턴 인덱스
- `myTurn`: 나의 턴 순서

## 🎯 앞으로의 작업 방향

### 단기 과제
1. 이미지 최적화 (WebP 변환)
2. PWA 구현
3. 폰트 최적화
4. CDN 통합

### 중장기 과제
1. 모바일 앱 개발
2. 실시간 음성 채팅
3. 토너먼트 모드
4. NFT 통합

## 💬 문제 해결 가이드

### WebRTC 연결 실패
→ TURN 서버 설정 확인

### 이미지 생성 실패
→ API 키 확인, 할당량 체크

### 투표 동기화 문제
→ `isVoted`, `isElected` 상태 확인

### 턴 순서 오류
→ `inGameOrder` 배열 확인

---

**마지막 업데이트**: 2025-09-07
**작성자**: AI Assistant (Claude)
**버전**: 3.0.0

> 이 문서는 Long Ago 프로젝트의 완전한 이해를 위한 가이드입니다. 매 작업 시 이 문서를 참조하여 프로젝트 컨텍스트를 유지하세요.
