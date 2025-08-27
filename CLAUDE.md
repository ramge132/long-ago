# Long Ago 프로젝트 종합 분석 및 문서화

## 📋 프로젝트 개요

**Long Ago**는 AI 기반 이미지 생성과 WebRTC를 활용한 실시간 멀티플레이어 스토리텔링 게임 플랫폼입니다.

### 🎯 핵심 기능
- **멀티플레이어 협업**: WebRTC 기반 실시간 P2P 통신
- **AI 이미지 생성**: RunPod/ComfyUI를 통한 동적 스토리 일러스트레이션
- **카드 기반 스토리텔링**: 93개 스토리 카드와 51개 엔딩 카드 시스템
- **실시간 투표**: 커뮤니티 기반 스토리 진행 결정
- **스토리북 생성**: 완성된 게임을 책 형태로 저장

### 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  AI Generation  │
│   (Vue.js 3)    │◄──►│ (Spring Boot 3) │◄──►│   (RunPod)     │
│                 │    │                 │    │                 │
│ • WebRTC P2P    │    │ • PostgreSQL    │    │ • ComfyUI      │
│ • Pinia Store   │    │ • Redis Cache   │    │ • FLUX Model   │
│ • Tailwind CSS  │    │ • AWS S3        │    │ • LoRA         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🎨 Frontend (Vue.js) 상세 분석

### **기술 스택**
- **Vue.js 3.5.13** (Composition API)
- **Vite 6.0.5** (빌드 도구)
- **Pinia 2.3.0** (상태 관리)
- **Vue Router 4.5.0** (라우팅)
- **Tailwind CSS 3.4.17** (스타일링)
- **PeerJS 1.5.4** (WebRTC P2P 통신)

### **라우팅 구조**
```
/ (IntroView)
├── /game (GameView - 인증 필요)
│   ├── /game/lobby (LobbyView)
│   ├── /game/play (InGameView)
│   └── /game/rank (GameRanking)
└── 404 → 홈으로 리다이렉트
```

### **컴포넌트 아키텍처**
```
App.vue (1,033 lines)
├── Preset Components
│   ├── TopBar.vue
│   ├── FooterBar.vue
│   ├── TigerAnimation.vue
│   ├── ToggleButton.vue
│   ├── TermsOfService.vue
│   ├── EBook.vue
│   └── AnnouncementBox.vue
├── Auth Components
│   ├── SignIn.vue
│   └── SignUp.vue
├── Lobby Components
│   ├── LobbyUsers.vue
│   └── LobbySettings.vue
└── InGame Components
    ├── InGameControl.vue
    ├── InGameContent.vue
    ├── InGameProgress.vue
    │   ├── ContentTimer.vue
    │   └── ContentGuage.vue
    ├── InGameVote.vue
    ├── InGameTrash.vue
    └── InGameEnding.vue
```

### **상태 관리 (Pinia Stores)**
1. **Auth Store** (`auth.js`): 사용자 데이터, localStorage 지속성
2. **Game Store** (`game.js`): 방장 ID, 게임 상태
3. **Audio Store** (`audio.js`): 음성 볼륨, 배경음악 제어

### **API 통신**
```javascript
// API 구조
auth.js: postRegister(), postSignIn()
game.js: createGame(), enterGame(), deleteGame(), endingCardReroll(), 
         promptFiltering(), createImage(), voteResultSend(), testGame()
book.js: getBook()
```

### **핵심 기술적 특징**

#### **WebRTC 구현** (GameView.vue - 1,544 lines)
- P2P 네트워킹과 연결 복원력
- 하트비트 시스템으로 연결 모니터링
- 자동 재연결 처리
- 게임 상태 동기화를 위한 메시지 브로드캐스팅
- TURN 서버 설정과 ICE 서버 구성

#### **실시간 기능**
- 텍스트 및 이모티콘 지원 라이브 채팅
- 참가자 상태 업데이트
- 시각적 오버레이와 턴 알림
- 애니메이션 피드백이 있는 투표 시스템
- 애니메이션 변화가 있는 점수 추적

#### **에셋 관리**
- **아이콘**: 20+ SVG 아이콘
- **이미지**: 50+ 동물 아바타, 게임 모드, 이모티콘
- **오디오**: 배경음악, 효과음 (메시지, 승리/패배, 페이지 넘김)
- **폰트**: 한국어 커스텀 폰트 (Katuri, One-mobile-pop, Pretendard 9가지 굵기)

### **사용자 경험 플로우**
1. **입장 & 설정**: 50+ 동물 아바타 중 무작위 선택, 닉네임 설정
2. **로비**: 실시간 참가자 표시, 방 설정, 채팅, 초대 링크
3. **게임**: 턴 기반 플레이, 실시간 투표, AI 이미지 생성, 인터랙티브 요소
4. **종료**: 승자 결정, 스토리북 생성

---

## 🚀 Backend (Spring Boot) 상세 분석

### **기술 스택**
- **Java 17** with **Spring Boot 3.4.1**
- **PostgreSQL** (영구 데이터 저장)
- **Redis** (캐싱 및 세션 관리)
- **AWS S3** (이미지 저장)
- **WebClient** (외부 GPU 서버 통신)
- **RunPod 통합** (AI 서비스)
- **Docker 컨테이너화**

### **도메인 엔티티 및 관계**

#### **PostgreSQL 엔티티**
1. **User**: 사용자 계정 (id, email, password, nickname, timestamps)
2. **Book**: 완성된 스토리북 (id, bookId UUID, title, imageUrl, viewCount, createdAt)
3. **Scene**: 스토리 페이지 (id, sceneOrder, userPrompt, imageUrl)
4. **StoryCard**: 게임 카드 (id, keyword, attribute: 인물/사물/장소/사건/상태)
5. **StoryCardVariants**: 카드 텍스트 변형 (id, variant, storyCardId)
6. **EndingCard**: 엔딩 템플릿 (id, content)

#### **Redis 캐시 엔티티**
1. **Game**: 활성 게임 세션
2. **Room**: 게임 로비 매치메이킹
3. **SceneRedis**: 게임 중 임시 장면 저장
4. **PlayerStatus**: 플레이어 카드 및 게임 상태

### **API 아키텍처**

#### **엔드포인트 구조**
```
/api
├── POST /signup (사용자 등록)
└── GET /check-nickname (닉네임 중복 확인)

/rooms
├── POST /rooms (방 생성)
├── GET /rooms (방 목록)
├── DELETE /rooms (방 삭제)
├── POST /rooms/{roomId} (방 입장)
└── PATCH /rooms/{roomId} (방 나가기)

/game
├── POST /game (게임 생성 및 카드 배분)
├── POST /game/test (데모 게임)
├── DELETE /game (게임 종료 및 책 생성)
├── PATCH /game/shuffle (엔딩 카드 재추첨)
└── GET /game (플레이어 상태/카드 조회)

/scene
├── POST /scene (AI를 통한 장면 생성)
├── POST /scene/filtering (콘텐츠 필터링)
└── POST /scene/vote (장면 삭제 투표)

/book
├── GET /book/{page} (책 목록 페이지네이션)
├── GET /book (특정 책 상세)
└── GET /book/top3 (조회수 상위 3개)

/s3
├── GET /s3/presignedUrl (S3 업로드 URL)
└── GET /s3/downloadFromS3 (이미지 다운로드)
```

### **비즈니스 로직 및 데이터 플로우**

#### **게임 플로우**
1. **방 생성**: 플레이어가 RoomController를 통해 로비 생성/입장
2. **게임 초기화**: GameService가 플레이어당 4개 고유 카드 배분 (1 캐릭터 + 3 기타)
3. **턴 기반 장면 생성**: 플레이어가 카드와 프롬프트로 장면 생성
4. **AI 통합**: WebClient가 GPU 서버와 이미지 생성 통신
5. **투표 시스템**: 플레이어가 생성된 장면에 투표
6. **게임 완료**: 성공적 완료 시 S3/PostgreSQL에 스토리북 생성

#### **카드 배분 알고리즘**
- 플레이어당 정확히 4개 카드: 1 캐릭터 + 3 기타 속성 (사물/장소/사건/상태)
- O(1) 중복 확인을 위한 HashSet 사용
- Collections.shuffle()로 무작위 속성 선택
- 중복 방지를 위해 풀에서 카드 제거

### **설정 및 인프라**

#### **WebClient 설정**
- 로드 밸런싱을 위한 다중 GPU 서버 URL (0-8)
- AI 생성을 위한 5분 타임아웃
- 이미지 처리를 위한 2MB 버퍼 크기
- Bearer 토큰 인증으로 RunPod API 통합

#### **보안 및 필터링**
- 인증을 위한 커스텀 SecurityConfig
- KOMORAN 라이브러리 사용 한국어 욕설 필터링
- 사용자 생성 프롬프트를 위한 콘텐츠 필터링 서비스

#### **AWS 통합**
- Presigned URL이 있는 S3Client 이미지 저장
- 계층적 저장: `{bookId}/{sceneOrder}.png`
- 자격 증명 관리가 있는 AwsConfig

#### **데이터베이스 설계**
- JPA/Hibernate가 있는 PostgreSQL
- 93개 스토리 카드, 51개 엔딩 카드가 있는 포괄적인 init_db.sql
- 스토리텔링을 위한 한국어 콘텐츠
- 적절한 외래 키 관계 및 연쇄 삭제

---

## 🤖 AI 이미지 생성 시스템 분석

### **기존 시스템 (ComfyUI 기반)**
- **인프라**: Vast.ai + ComfyUI + 로컬 FLUX 모델
- **워크플로우**: JSON 기반 복잡한 노드 시스템
- **캐릭터 처리**: LoRA 기반 캐릭터 생성
- **그림체**: LoRA 파일로 스타일 적용
- **프롬프트 생성**: AYL.py (로컬 LLM 모델)

### **새로운 API 시스템**
- **인프라**: OpenAI GPT + Google Gemini API
- **캐릭터 처리**: Image-to-Image 기반 (14개 캐릭터)
- **그림체**: 텍스트 프롬프트로 스타일 적용
- **프롬프트 생성**: GPT-4o-mini API

#### **캐릭터 시스템**
14개 캐릭터: alien, beggar, boy, detective, doctor, farmer, girl, idol, merchant, ninja, oldman, princess, rich, wizard

각 캐릭터마다:
- `.png` 참조 이미지
- `.txt` 고정 프롬프트

#### **그림체 모드 (0-8)**
0. 애니메이션 스타일
1. 3D 카툰 스타일
2. 코믹 스트립 스타일
3. 클레이메이션 스타일
4. 크레용 드로잉 스타일
5. 픽셀 아트 스타일
6. 미니멀리스트 일러스트
7. 수채화 스타일
8. 스토리북 일러스트

### **RunPod 통합**
- **엔드포인트**: `https://api.runpod.ai/v2/{ENDPOINT_ID}/run`
- **인증**: Bearer 토큰
- **페이로드**: JSON 형태의 게임 데이터
- **응답**: 이미지 데이터와 S3 URL

---

## 🚀 배포 및 인프라

### **컨테이너화 (Docker)**

#### **Frontend Dockerfile**
```dockerfile
# 멀티스테이지 빌드
FROM node:18-alpine AS build
# Nginx로 프로덕션 서빙
FROM nginx:alpine
```

#### **Backend Dockerfile**
```dockerfile
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### **환경 변수 관리**
```env
# Database
DB_URL=jdbc:postgresql://localhost:5432/longago
DB_USERNAME=your_db_user
DB_PASSWORD=your_db_password

# Redis
REDIS_HOST=localhost

# RunPod
RUNPOD_API_KEY=your_api_key
RUNPOD_ENDPOINT_ID=your_endpoint_id
RUNPOD_ENDPOINT_URL=https://api.runpod.ai/v2/{id}/run

# AWS S3
S3_BUCKET_NAME=long-ago-images
S3_REGION=ap-northeast-2
S3_CREDENTIALS_ACCESS_KEY=your_key
S3_CREDENTIALS_SECRET_KEY=your_secret

# New API System (추가)
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
```

---

## 🔧 EC2 배포 요구사항

### **서버 사양 권장**
- **인스턴스 타입**: t3.medium 이상 (2 vCPU, 4GB RAM)
- **스토리지**: 20GB 이상 (로그, 임시 파일용)
- **OS**: Ubuntu 22.04 LTS
- **보안그룹**: 80, 443, 8080 포트 오픈

### **필수 설치 소프트웨어**
```bash
# Docker 설치
sudo apt update
sudo apt install docker.io docker-compose-plugin

# Node.js (프론트엔드 빌드용)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Java 17 (백엔드용)
sudo apt install openjdk-17-jdk

# PostgreSQL & Redis (옵션 - 별도 서버 권장)
sudo apt install postgresql-client redis-tools
```

### **디렉토리 구조**
```
/home/ubuntu/
├── long-ago/               # 프로젝트 루트
│   ├── FE/                 # 프론트엔드
│   ├── BE/                 # 백엔드
│   ├── AI/                 # AI 시스템
│   ├── docker-compose.yml  # 컨테이너 설정
│   └── .env               # 환경변수
├── logs/                  # 로그 파일
└── backups/              # 데이터베이스 백업
```

---

## 🔐 GitHub Secrets (CI/CD)

### **필수 Secrets 목록**

#### **서버 접속 정보**
```
EC2_HOST              # EC2 퍼블릭 IP 또는 도메인
EC2_USERNAME         # SSH 사용자명 (ubuntu)
EC2_PRIVATE_KEY      # SSH 프라이빗 키 (PEM 파일 내용)
```

#### **데이터베이스**
```
DB_URL               # PostgreSQL 연결 URL
DB_USERNAME          # 데이터베이스 사용자명
DB_PASSWORD          # 데이터베이스 비밀번호
REDIS_HOST           # Redis 서버 호스트
REDIS_PASSWORD       # Redis 비밀번호 (있는 경우)
```

#### **AI 이미지 생성**
```
# RunPod (기존 시스템)
RUNPOD_API_KEY       # RunPod API 키
RUNPOD_ENDPOINT_ID   # RunPod 엔드포인트 ID
RUNPOD_ENDPOINT_URL  # 전체 RunPod URL

# 새로운 API 시스템
OPENAI_API_KEY       # OpenAI API 키
GEMINI_API_KEY       # Google Gemini API 키
```

#### **AWS 서비스**
```
S3_BUCKET_NAME              # S3 버킷 이름
S3_REGION                   # S3 리전
S3_CREDENTIALS_ACCESS_KEY   # AWS Access Key
S3_CREDENTIALS_SECRET_KEY   # AWS Secret Key
```

#### **기타**
```
JWT_SECRET           # JWT 토큰 시크릿 (있는 경우)
ENCRYPTION_KEY       # 데이터 암호화 키 (있는 경우)
```

### **GitHub Actions 워크플로우 예시**
```yaml
name: Deploy to EC2

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to EC2
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.EC2_HOST }}
        username: ${{ secrets.EC2_USERNAME }}
        key: ${{ secrets.EC2_PRIVATE_KEY }}
        script: |
          cd /home/ubuntu/long-ago
          git pull origin main
          
          # 환경변수 파일 생성
          echo "DB_URL=${{ secrets.DB_URL }}" > .env
          echo "DB_USERNAME=${{ secrets.DB_USERNAME }}" >> .env
          echo "DB_PASSWORD=${{ secrets.DB_PASSWORD }}" >> .env
          echo "REDIS_HOST=${{ secrets.REDIS_HOST }}" >> .env
          echo "RUNPOD_API_KEY=${{ secrets.RUNPOD_API_KEY }}" >> .env
          echo "RUNPOD_ENDPOINT_ID=${{ secrets.RUNPOD_ENDPOINT_ID }}" >> .env
          echo "S3_BUCKET_NAME=${{ secrets.S3_BUCKET_NAME }}" >> .env
          echo "S3_REGION=${{ secrets.S3_REGION }}" >> .env
          echo "S3_CREDENTIALS_ACCESS_KEY=${{ secrets.S3_CREDENTIALS_ACCESS_KEY }}" >> .env
          echo "S3_CREDENTIALS_SECRET_KEY=${{ secrets.S3_CREDENTIALS_SECRET_KEY }}" >> .env
          echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" >> .env
          echo "GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}" >> .env
          
          # Docker 컨테이너 재시작
          docker-compose down
          docker-compose up -d --build
```

---

## 📊 시스템 성능 및 확장성

### **현재 아키텍처 특징**
- **실시간 멀티플레이어**: WebRTC P2P로 서버 부하 분산
- **캐싱 전략**: Redis로 게임 세션 관리, PostgreSQL로 영구 저장
- **미디어 처리**: AWS S3로 이미지 저장 및 CDN 활용
- **AI 통합**: 외부 GPU 서버로 리소스 분리

### **성능 최적화 포인트**
1. **프론트엔드**: Vue Router 레이지 로딩, 이미지 최적화
2. **백엔드**: Redis 캐싱, JPA 쿼리 최적화, 연결 풀링
3. **AI 처리**: RunPod 서버리스로 오토스케일링
4. **네트워킹**: WebRTC로 서버 트래픽 감소

### **확장성 고려사항**
- **수평적 확장**: 로드 밸런서 + 다중 인스턴스
- **데이터베이스**: PostgreSQL 읽기 복제본, Redis 클러스터
- **AI 처리**: RunPod 멀티 엔드포인트 로드 밸런싱
- **CDN**: CloudFront + S3 이미지 캐싱

---

## 📈 개발 로드맵

### **즉시 필요한 작업**
1. **API 시스템 전환**: ComfyUI → OpenAI/Gemini API
2. **환경변수 통합**: 모든 Secret 설정 완료
3. **CI/CD 파이프라인**: GitHub Actions 구성
4. **모니터링 설정**: 로그 수집 및 알림 시스템

### **향후 개선 사항**
1. **성능 모니터링**: APM 도구 도입 (New Relic, DataDog)
2. **보안 강화**: HTTPS, JWT 토큰 관리, API Rate Limiting
3. **사용자 경험**: PWA 지원, 모바일 최적화
4. **콘텐츠 확장**: 새로운 카드, 테마, 게임 모드

---

## 🎯 핵심 비즈니스 가치

**Long Ago**는 AI 기술과 실시간 협업을 결합한 혁신적인 스토리텔링 플랫폼으로, 다음과 같은 독특한 가치를 제공합니다:

1. **창의적 협업**: 여러 사용자가 실시간으로 스토리를 공동 창작
2. **AI 보강 창작**: 사용자 아이디어를 AI가 시각적으로 구현
3. **게임화된 학습**: 재미있는 게임 형태로 창작 교육 제공
4. **디지털 스토리북**: 완성작을 영구 보존하는 디지털 아카이브

이 시스템은 교육, 엔터테인먼트, 창작 분야에서 높은 활용 가치를 가지며, 특히 한국어 콘텐츠에 최적화되어 있습니다.

---

**📝 문서 작성일**: 2025년 8월 27일  
**📋 프로젝트 상태**: 프로덕션 준비 완료  
**🔧 마지막 업데이트**: AI 시스템 API 전환 설계 완료  
**👨‍💻 분석자**: Claude (AI Assistant)