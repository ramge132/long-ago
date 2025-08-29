# API 기반 이미지 생성 시스템

이 시스템은 기존의 ComfyUI와 로컬 모델 기반 이미지 생성을 대체하여, OpenAI GPT API와 Google Gemini API를 사용한 완전한 API 기반 이미지 생성 시스템입니다.

## 주요 기능

### 🎭 캐릭터 기반 이미지 생성
- 14개의 캐릭터 카드 지원 (alien, beggar, boy, detective, doctor, farmer, girl, idol, merchant, ninja, oldman, princess, rich, wizard)
- 캐릭터가 언급되면 자동으로 image-to-image 모드로 전환
- 각 캐릭터별 고정 프롬프트와 참조 이미지 활용

### 🎨 다양한 그림체 지원
- 9가지 그림체 모드 (0-8)
  - 0: 애니메이션 스타일
  - 1: 3D 카툰 스타일  
  - 2: 코믹 스트립 스타일
  - 3: 클레이메이션 스타일
  - 4: 크레용 드로잉 스타일
  - 5: 픽셀 아트 스타일
  - 6: 미니멀리스트 일러스트
  - 7: 수채화 스타일
  - 8: 스토리북 일러스트

### 🚀 API 기반 처리
- **GPT API**: 사용자 입력을 이미지 생성용 프롬프트로 변환
- **Gemini API**: 텍스트/이미지에서 이미지 생성
- AWS S3 연동으로 이미지 저장

## 시스템 아키텍처

```
사용자 입력 → GPT API (프롬프트 생성) → Gemini API (이미지 생성) → S3 저장 → 웹 응답
              ↓                          ↓
        스토리 요약/설명              캐릭터 감지 시
                                   image-to-image 모드
```

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
`.env.example` 파일을 참고하여 `.env` 파일을 생성하고 다음 값들을 설정하세요:

```env
# 필수: API 키
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# 선택적: AWS S3 설정 (없으면 로컬 저장만)
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=your_s3_bucket_name
```

### 3. API 키 발급 방법

#### OpenAI API Key
1. [OpenAI Platform](https://platform.openai.com)에 가입
2. API Keys 섹션에서 새 키 생성
3. 현재는 `gpt-5-nano` 모델을 사용

#### Gemini API Key
1. [Google AI Studio](https://makersuite.google.com/app/apikey)에 접속
2. 새 API 키 생성
3. `gemini-2.5-flash-image-preview` 모델 권한 확인

## 사용 방법

### 1. 서버 시작
```bash
cd AI
python imageGeneration/api_main.py
```

서버는 `http://localhost:8190`에서 실행됩니다.

### 2. API 엔드포인트

#### 이미지 생성 (POST /generate)
```json
{
    "session_id": "unique_session_id",
    "game_mode": 0,
    "user_sentence": "닌자가 숲속에서 수행을 하고 있다",
    "status": 0
}
```

#### 서버 상태 확인 (GET /health)
```bash
curl http://localhost:8190/health
```

#### 사용 가능한 캐릭터 목록 (GET /characters)
```bash
curl http://localhost:8190/characters
```

#### 테스트 생성 (POST /test)
```bash
curl -X POST http://localhost:8190/test
```

## 캐릭터 시스템

### 캐릭터 감지
시스템은 사용자 입력에서 다음과 같은 방식으로 캐릭터를 자동 감지합니다:

- 한국어: "닌자", "공주", "의사" 등
- 영어: "ninja", "princess", "doctor" 등

### Image-to-Image 모드
캐릭터가 감지되면:
1. 해당 캐릭터의 참조 이미지 로드
2. 캐릭터별 고정 프롬프트 적용
3. 생성된 프롬프트와 함께 Gemini API로 전달
4. 일관된 캐릭터 특성을 유지한 이미지 생성

## 예시

### 예시 1: 캐릭터 없는 경우
```
입력: "아름다운 숲속에 햇빛이 비치고 있다"
→ Text-to-Image 모드
→ 그림체만 적용되어 이미지 생성
```

### 예시 2: 단일 캐릭터
```
입력: "닌자가 숲속에서 수행을 하고 있다"
→ Image-to-Image 모드
→ ninja.png + ninja.txt + 생성된 프롬프트
```

### 예시 3: 다중 캐릭터
```
입력: "닌자와 공주가 만났다"
→ Image-to-Image 모드
→ ninja.png + princess.png + 각각의 프롬프트 결합
```

## 파일 구조

```
AI/
├── imageGeneration/
│   ├── characters/          # 캐릭터 이미지 및 프롬프트
│   │   ├── ninja.png
│   │   ├── ninja.txt
│   │   └── ...
│   ├── api_image_generator.py  # 핵심 생성 로직
│   ├── api_main.py            # FastAPI 서버
│   └── output/                # 생성된 이미지 저장
├── requirements.txt
├── .env.example
└── README.md
```

## 기존 시스템과의 차이점

| 구분 | 기존 시스템 | 새로운 API 시스템 |
|------|-------------|-------------------|
| 인프라 | Vast.ai + ComfyUI + 로컬 모델 | OpenAI + Gemini API |
| 캐릭터 | LoRA 기반 | Image-to-Image 기반 |
| 그림체 | LoRA 파일 | 텍스트 프롬프트 |
| 유지보수 | 복잡한 인프라 관리 | 간단한 API 호출 |
| 확장성 | 하드웨어 제한 | 클라우드 기반 확장 |

## 문제 해결

### 일반적인 오류

1. **API 키 오류**: `.env` 파일의 API 키가 올바른지 확인
2. **모듈 없음**: `pip install -r requirements.txt` 실행
3. **캐릭터 이미지 없음**: `characters/` 폴더의 파일들 확인
4. **S3 업로드 실패**: AWS 권한 및 버킷 설정 확인

### 로그 확인
서버 실행 시 콘솔에 자세한 로그가 출력됩니다:
- `🔹 [GPT]`: GPT API 호출 상태
- `🔹 [캐릭터 감지]`: 감지된 캐릭터 정보
- `🔹 [Gemini]`: 이미지 생성 모드
- `✅`: 성공 메시지
- `❌`: 오류 메시지

## 성능 최적화

1. **세션 데이터 관리**: 메모리에서 세션 상태 유지
2. **이미지 캐싱**: 동일한 입력에 대한 결과 재사용 고려
3. **비동기 처리**: asyncio를 활용한 동시 요청 처리
4. **에러 핸들링**: API 호출 실패 시 재시도 로직

## 향후 개선 사항

1. **GPT-5-nano 지원**: 출시 시 모델 업그레이드
2. **캐릭터 추가**: 새로운 캐릭터 동적 로드
3. **데이터베이스 연동**: 세션 데이터 영구 저장
4. **모니터링**: API 사용량 및 성능 모니터링
5. **배치 처리**: 여러 이미지 동시 생성
