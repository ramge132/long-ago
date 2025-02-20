# LONG AGO - Front-end (아주 먼 옛날)

## 프로젝트 소개
협동형 동화 제작 웹 게임 서비스입니다. 여러 플레이어가 함께 이야기를 만들어가며 동화책을 완성하는 게임입니다.

## 주요 기능
- 실시간 멀티플레이어 게임 (P2P 기반)
- 동적 스토리 생성 및 투표 시스템
- AI 이미지 생성을 통한 동화 일러스트레이션
- 다양한 게임 모드와 스타일 (9가지 이미지 생성 스타일)
- 완성된 동화책 E-book 뷰어

## 기술 스택
- Frontend: Vue 3 + Vite
- 상태 관리: Pinia
- 스타일링: TailwindCSS
- P2P 통신: PeerJS
- 애니메이션: Vue Transition
- 기타 라이브러리:
  - vue-router
  - vue-toastification
  - swiper
  - axios

## 설치 및 실행

### 환경 설정
```sh
# .env 파일 설정
VITE_MAIN_API_SERVER_URL=백엔드_서버_URL

# auth
VITE_USERS=apis/api/signup
VITE_USERS_SIGNIN=apis/api/user/login

# game
VITE_GAME=/apis/game
VITE_GAME_SHUFFLE=/shuffle

# scene
VITE_SCENE=apis/scene
VITE_SCENE_FILTERING=/filtering
VITE_SCENE_VOTE=/vote

# turn
VITE_TURN_ID=턴서버_ID
VITE_TURN_PW=턴서버_PASSWORD
```

### 개발 환경 설정
```sh
# 패키지 설치
npm install

# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build

# 린트 실행
npm run lint
```

## 프로젝트 구조
```
src/
├── apis/         # API 통신 관련 
├── assets/       # 이미지, 폰트 등 정적 파일
├── components/   # 재사용 가능한 컴포넌트
├── functions/    # 유틸리티 함수
├── router/       # 라우팅 설정
├── stores/       # Pinia 스토어
└── views/        # 페이지 컴포넌트
```

## 팀원
- 김동휘
- 김형표
- 유태영
- 이세중
- 홍석진
- 홍정표

## 라이선스
© 2025. LONG AGO All rights reserved.

