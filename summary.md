# 아주 먼 옛날 프로젝트 요약 (v1.0)

## 1. 프로젝트 개요
- **서비스명:** 아주 먼 옛날 (A Long Time Ago)
- **핵심 기능:** 여러 사용자가 한 문장씩 이어가며 실시간으로 이야기를 만들고, 각 문장에 맞춰 AI가 삽화를 생성해주는 웹 기반 협업 스토리텔링 게임
- **목표:** LLM과 이미지 생성 AI를 활용한 독창적이고 창의적인 게임 경험 제공

## 2. 주요 기술 스택
- **Frontend (FE):** Vue.js, Vite, Tailwind CSS
- **Backend (BE):** Spring Boot, Java, Spring Security, JPA
- **AI:**
    - **언어 모델(LLM):** OpenAI GPT-5-Nano
    - **이미지 생성:** Google Gemini 2.5 Flash Image Preview
- **인프라:** Docker, Nginx, AWS (EC2, S3), Redis
- **데이터베이스:** PostgreSQL (JPA 연동), Redis (캐싱 및 실시간 데이터)

## 3. 핵심 아키텍처 및 플로우

### 3.1. 게임 로직 (BE)
1. **게임 생성:** 사용자들이 로비에 모여 게임을 시작하면, `GameService`가 고유한 `gameId`와 함께 게임 세션을 생성합니다.
2. **카드 분배:** `CardService`를 통해 각 플레이어에게 이야기 카드(4장)와 결말 카드(1장)를 무작위로 분배합니다.
3. **게임 데이터 관리:** 게임 상태, 플레이어 정보, 카드 등은 빠른 접근을 위해 **Redis**에 저장 및 관리됩니다.
4. **이야기 제출 및 투표:**
    - 플레이어는 자신의 턴에 카드를 사용해 문장을 제출합니다.
    - `FilteringService`가 제출된 문장의 카드 키워드 포함 여부 및 부적절한 단어를 검증합니다.
    - 다른 플레이어들은 제출된 문장의 개연성을 투표하고, 과반수 찬성 시 이야기가 공식적으로 채택됩니다.
5. **게임 종료:**
    - 결말 카드가 사용되거나 특정 조건이 충족되면 게임이 종료됩니다.
    - `GameService`는 Redis에 저장된 장면(scene)들을 취합하여 S3에 최종 이미지들을 업로드하고, 책(Book) 정보를 DB에 저장합니다.

### 3.2. AI 이미지 생성 파이프라인
- **통합 API (`AI/imageGeneration/api_image_generator.py`):**
    - 백엔드로부터 사용자 문장, 게임 모드(그림체), 세션 데이터를 받습니다.
    - **GPT-5-Nano**를 사용하여 다음 3단계 프롬프트를 생성합니다.
        1. **스토리 요약 (Story Summary):** 이전 내용과 현재 문장을 합쳐 전체 줄거리를 요약합니다.
        2. **장면 묘사 (Description):** 요약된 스토리와 캐릭터 정보를 바탕으로 현재 장면에 대한 구체적인 묘사를 생성합니다.
        3. **이미지 프롬프트 (Image Prompt):** 장면 묘사를 기반으로 이미지 생성을 위한 최종 프롬프트를 만듭니다.
    - **Gemini 2.5 Flash Image Preview**를 사용하여 최종 프롬프트와 참조 이미지(캐릭터가 있을 경우)를 기반으로 **720x1280 (9:16)** 크기의 삽화를 생성합니다.

### 3.3. 프론트엔드 (FE)
- **상태 관리:** Pinia (`stores/game.js`, `stores/auth.js`)
- **라우팅:** Vue Router (`router/index.js`)
- **핵심 컴포넌트:**
    - `App.vue`: 최상위 컴포넌트로, 라우팅 및 전역 UI(로딩, 팝업 등)를 관리합니다.
    - `InGameContent.vue`: 게임의 핵심인 동화책 UI를 담당합니다.
        - **책 UI:** CSS `transform`과 `perspective`를 이용해 3D 책 넘김 효과를 구현합니다.
        - **페이지 크기:** 각 페이지는 **300x400 (3:4)** 크기로 고정되어 있습니다.
        - **이미지 마스킹:** 생성된 삽화(`story-image`)는 `object-fit: cover`로 페이지를 꽉 채우고, `ink_mask.png`를 이용해 **잉크 테두리 효과**가 적용됩니다.

## 4. 주요 변경 및 결정 사항 (v1.0)
- **이미지 로딩 방식:** 과거 CDN 방식에서 벗어나, 현재는 백엔드가 S3에 저장된 이미지를 직접 스트리밍하는 방식으로 변경되었습니다.
- **이미지 생성 서버:** Vast.ai/Runpod 기반의 자체 서버 운영에서, **OpenAI와 Gemini API를 직접 호출**하는 방식으로 전환하여 안정성과 확장성을 확보했습니다.
- **이미지-마스크 크기 문제 해결:**
    - AI가 생성하는 9:16 이미지가 웹의 3:4 페이지에 표시될 때 발생하는 비율 불일치 문제를 해결했습니다.
    - 이미지에 `object-fit: cover`를 적용해 페이지를 꽉 채우고, 마스크 크기(`mask-size: 100% 100%`)를 조정하여 **이미지와 마스크가 완벽히 정렬**되도록 수정했습니다.
    - 기존의 복잡했던 잉크 효과 애니메이션은 제거하고, `ink_mask.png`를 이용한 단순하고 명확한 마스킹 방식으로 변경했습니다.

## 5. 프로젝트 구조 (주요 파일)
- **`AI/imageGeneration/api_image_generator.py`**: 이미지 생성의 모든 로직(LLM 프롬프트 생성, Gemini API 호출)을 담당하는 핵심 AI 파일.
- **`BE/src/main/java/com/example/b101/service/GameService.java`**: 게임의 생성, 진행, 종료 등 핵심 비즈니스 로직을 처리.
- **`FE/src/components/InGame/InGameContent.vue`**: 사용자가 보는 동화책의 시각적 요소와 인터랙션을 모두 구현한 컴포넌트.
- **`summary.md`**: 프로젝트의 현재 상태와 아키텍처를 요약한 문서 (바로 이 파일).

## 6. 서버 접속 정보
- **EC2 메인 서버 접속:** `ssh -i ".\long-ago-main-key.pem" ubuntu@16.176.206.134`
- **서버 환경:** AWS EC2 (Ubuntu)
- **배포된 서비스:** 백엔드 Spring Boot 애플리케이션 (포트 8080)

## 7. CI/CD 및 환경변수 관리
- **자동 배포:** GitHub Actions를 통한 자동 CI/CD 파이프라인
- **환경변수:** GitHub Secrets를 통해 자동 할당

### GitHub Secrets 목록
- **서버 관련**
  - `MAIN_SERVER_KEY`: EC2 SSH 프라이빗 키
  - `MAIN_SERVER_URI`: EC2 서버 주소
  - `CLOUDFRONT_DISTRIBUTION_ID`: CloudFront 배포 ID

- **데이터베이스**
  - `DB_DRIVER`: 데이터베이스 드라이버
  - `DB_PASSWORD_MAIN`: PostgreSQL 비밀번호
  - `DB_URL_MAIN`: PostgreSQL 연결 URL
  - `DB_USERNAME_MAIN`: PostgreSQL 사용자명
  - `REDIS_HOST`: Redis 서버 호스트

- **AI API**
  - `GEMINI_API_KEY`: Google Gemini API 키 (이미지 생성)
  - `TTS_API_KEY`: Google TTS API 키 (음성 합성 - 별도 키 필요)
  - `OPENAI_API_KEY`: OpenAI API 키
  - `RUNPOD_API_KEY`: RunPod API 키
  - `RUNPOD_ENDPOINT_ID`: RunPod 엔드포인트 ID

**⚠️ 중요: 새로운 API 키 추가 시 주의사항**
- GitHub Secrets에 새 API 키를 추가할 때는 반드시 `.github/workflows/deploy.yml` 파일의 배포 스크립트도 함께 수정해야 합니다.
- 예: `TTS_API_KEY` 추가 시 → `echo "TTS_API_KEY=${{ secrets.TTS_API_KEY }}" >> .env` 라인을 배포 스크립트에 추가

## 8. 배포 아키텍처 및 Docker 관리

### 8.1. Docker Compose 파일 관리 방식
이 프로젝트는 **서버 중심 Docker 관리 방식**을 사용합니다:

- **로컬 저장소**: docker-compose.yml 파일이 존재하지 않음
- **EC2 서버**: `/home/ubuntu/docker-compose.yml` 파일을 직접 관리
- **배포 방식**: GitHub Actions에서 환경변수만 `.env` 파일에 설정하고, 기존 docker-compose.yml 사용

### 8.2. 환경변수 주입 방식
```yaml
# 서버의 docker-compose.yml 구조
app:
  image: ${BE_IMAGE_NAME}:latest
  environment:
    - DB_URL=${DB_URL_MAIN}
    - GEMINI_API_KEY=${GEMINI_API_KEY}
    - TTS_API_KEY=${TTS_API_KEY}  # 수동으로 추가 필요
    # ... 기타 환경변수들
```

### 8.3. 새로운 환경변수 추가 절차
1. **GitHub Secrets 추가**: 저장소 Settings → Secrets → Actions에서 새 변수 추가
2. **배포 스크립트 수정**: `.github/workflows/deploy.yml`에서 `.env` 파일 생성 부분에 추가
3. **⚠️ 서버 Docker Compose 수정**: SSH로 서버 접속하여 `docker-compose.yml`의 `environment` 섹션에 수동 추가
4. **컨테이너 재시작**: `docker-compose up -d app` 실행

### 8.4. 일반적인 배포 문제 해결

#### 문제 1: Spring Boot 컨테이너 시작 실패
**증상**: `docker ps`에서 백엔드 컨테이너가 `Exited (1)` 상태
**원인**: 환경변수 누락으로 인한 Spring Boot 시작 실패
```bash
# 해결 방법
ssh -i ".\long-ago-main-key.pem" ubuntu@16.176.206.134 "docker logs ubuntu-app-1 --tail=20"
# 로그에서 "Could not resolve placeholder" 에러 확인
# docker-compose.yml에 누락된 환경변수 추가 후 재시작
```

#### 문제 2: API 엔드포인트 404 오류
**증상**: 백엔드는 실행되지만 `https://longago.io/rooms` 등이 404 반환
**원인**: Nginx 설정에서 API 경로 라우팅 누락
```nginx
# nginx/default.conf에 추가 필요한 설정들
location /rooms {
    proxy_pass http://app:8080/rooms;
    proxy_set_header Host $host;
    # ... 기타 헤더들
}
```

#### 문제 3: 환경변수 불일치
**현상**: 로컬에서는 작동하지만 서버에서만 실패
**해결**: 서버의 `.env` 파일과 `docker-compose.yml`의 `environment` 섹션 동기화 확인

- **AWS 서비스**
  - `S3_BUCKET_NAME`: S3 버킷 이름
  - `S3_CREDENTIALS_ACCESS_KEY`: AWS Access Key
  - `S3_CREDENTIALS_SECRET_KEY`: AWS Secret Key
  - `S3_REGION`: S3 리전

- **Docker Hub**
  - `DOCKERHUB_PASSWORD_MAIN`: Docker Hub 비밀번호
  - `DOCKERHUB_USERNAME_MAIN`: Docker Hub 사용자명
  - `IMAGE_BE_MAIN`: 백엔드 이미지명
  - `IMAGE_FE_MAIN`: 프론트엔드 이미지명

- **프론트엔드 환경변수**
  - `VITE_ASSETS_PATH`: 에셋 경로
  - `VITE_CDN_URL`: CDN URL
  - `VITE_GAME`: 게임 API 엔드포인트
  - `VITE_GAME_SHUFFLE`: 게임 셔플 API 엔드포인트
  - `VITE_GOOGLE_CLIENT_ID`: Google OAuth 클라이언트 ID
  - `VITE_MAIN_API_SERVER_URL_MAIN`: 메인 API 서버 URL
  - `VITE_SCENE`: 장면 API 엔드포인트
  - `VITE_SCENE_FILTERING`: 장면 필터링 API 엔드포인트
  - `VITE_SCENE_VOTE`: 장면 투표 API 엔드포인트
  - `VITE_TURN_ID`: TURN 서버 ID
  - `VITE_TURN_PW`: TURN 서버 비밀번호
  - `VITE_TURN_SERVER_URL`: TURN 서버 URL
  - `VITE_USERS`: 사용자 API 엔드포인트
  - `VITE_USERS_SIGNIN`: 로그인 API 엔드포인트

- **기타**
  - `WEBCLIENT_BASE_URL`: WebClient 기본 URL
