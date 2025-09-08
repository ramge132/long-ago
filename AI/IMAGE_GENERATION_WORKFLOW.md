# Long Ago 이미지 생성 시스템 상세 동작 방식

## 📋 시스템 개요

`unified_image_service.py`는 Long Ago 게임의 모든 이미지 생성을 담당하는 통합 서비스입니다.

### 핵심 기능
1. **Text-to-Image**: 텍스트만으로 이미지 생성
2. **Image-to-Image**: 레퍼런스 이미지를 활용한 일관성 있는 이미지 생성
3. **엔티티 관리**: 캐릭터/사물/장소의 레퍼런스 관리
4. **세션 관리**: 게임별 컨텍스트 유지

## 🔄 전체 동작 플로우

```
사용자 입력 (한국어 문장)
    ↓
Java Backend (BE/SceneService.java)
    ↓
Python API 호출 (port 8190)
    ↓
unified_image_service.py
    ├─→ 엔티티 탐지 (EntityManager)
    ├─→ 세션 데이터 확인 (SessionManager)
    ├─→ 모드 결정 (Text-to-Image vs Image-to-Image)
    ├─→ Gemini API 호출
    ├─→ 이미지 생성
    └─→ 레퍼런스 저장 & 반환
```

## 📊 상세 동작 프로세스

### 1. 요청 수신 및 초기화

```python
POST /generate-scene
{
    "gameId": "game_123",
    "userId": "user_456",
    "userPrompt": "공주가 성에서 나왔습니다",
    "turn": 5,
    "drawingStyle": 0,  # 0-8 중 선택 (애니메이션, 3D카툰 등)
    "isEnding": false,
    "sessionData": {...}  # 선택사항
}
```

#### 처리 과정:
1. **요청 검증**: SceneGenerationRequest 모델로 파싱
2. **로깅**: 게임ID, 사용자ID, 턴 정보 기록
3. **세션 로드**: 게임별 저장된 컨텍스트 불러오기

### 2. 엔티티 탐지 시스템

#### EntityManager 동작:
```python
# 입력: "공주가 성에서 나왔습니다"
# 과정:
1. korean_to_english_map 순회
   - "공주" 발견 → "princess" 매핑
   - "성" 발견 → 매핑 없음 (엔티티 아님)

2. 발견된 엔티티: ["princess"]

3. 엔티티 정보 조회:
   - name: "princess"
   - korean_name: "공주"
   - entity_type: "인물"
   - image_path: "characters/princess.png"
   - prompt: "beautiful princess with crown"
```

#### 지원 엔티티 (총 48개):
- **인물 (18개)**: 공주, 마법사, 소년, 소녀, 닌자, 탐정 등
- **사물 (20개)**: 칼, 지도, 가면, 시계, 보석 등
- **장소 (10개)**: 바다, 사막, 저택, 천국, 묘지 등

### 3. 이미지 생성 모드 결정

```python
if detected_entities:  # 엔티티가 발견된 경우
    → Image-to-Image 모드
else:  # 엔티티가 없는 경우
    → Text-to-Image 모드
```

### 4-A. Text-to-Image 모드 (엔티티 없음)

#### 프롬프트 구성:
```python
# 1. 스타일 선택 (9가지 중 1개)
style = DRAWING_STYLES[request.drawingStyle]
# 예: "anime style, vibrant colors, detailed illustration"

# 2. 다양성 프롬프트 (랜덤 선택)
modifier = random.choice(TEXT_TO_IMAGE_VARIETY_MODIFIERS)
# 예: "creative and unique perspective"

# 3. 최종 프롬프트 조합
final_prompt = f"""
Create a picture of: {style} 스타일로 그린 {userPrompt} 이미지.
{modifier}.
Make it portrait orientation, 9:16 aspect ratio
"""
```

#### Gemini API 호출:
```python
# API 엔드포인트
POST https://generativelanguage.googleapis.com/v1beta/models/
     gemini-2.5-flash-image-preview:generateContent

# 페이로드
{
    "contents": [{
        "parts": [{
            "text": final_prompt
        }]
    }]
}

# 응답 처리
→ base64 인코딩된 이미지 데이터 수신
→ 디코딩 후 바이너리 이미지로 변환
```

### 4-B. Image-to-Image 모드 (엔티티 존재)

#### 레퍼런스 이미지 수집:
```python
for entity in detected_entities[:3]:  # 최대 3개
    if entity in saved_references:
        # 세션에 저장된 레퍼런스 사용
        → 이전에 생성된 이미지 재사용
    elif entity.image_path exists:
        # 기본 레퍼런스 이미지 사용
        → characters/princess.png 등
```

#### 프롬프트 구성:
```python
# 1. 구도 다양화 (14가지 옵션 중 랜덤)
composition = random.choice(IMAGE_TO_IMAGE_COMPOSITION_VARIETY)
# 예: "dynamic camera angle"

# 2. 최종 프롬프트
prompt = f"""
Using the provided reference images, create a new image.
Maintain character appearances exactly as shown in references.
{character_descriptions}
Scene: {userPrompt}.
Style: {style}.
Use {composition} while keeping character consistency.
Portrait orientation, 9:16 aspect ratio
"""
```

#### Gemini API 호출 (멀티모달):
```python
# 페이로드 구성
{
    "contents": [{
        "parts": [
            {"text": prompt},  # 텍스트 프롬프트
            {"inlineData": {   # 레퍼런스 이미지 1
                "mimeType": "image/jpeg",
                "data": base64_image_1
            }},
            {"inlineData": {   # 레퍼런스 이미지 2
                "mimeType": "image/jpeg",
                "data": base64_image_2
            }}
        ]
    }]
}
```

### 5. 레퍼런스 관리 시스템

#### 첫 등장 시:
```python
if entity_name not in entity_references:
    if entity.type == '인물':  # 인물만 저장
        # 생성된 이미지를 레퍼런스로 저장
        entity_references[entity_name] = base64.encode(generated_image)
        logger.info(f"'{entity.korean_name}' 레퍼런스 저장")
```

#### 재등장 시:
```python
if entity_name in entity_references:
    # 저장된 레퍼런스 사용
    reference_image = base64.decode(entity_references[entity_name])
    → Image-to-Image로 일관성 유지
```

### 6. 세션 데이터 관리

#### 세션 구조:
```python
session_data = {
    "prev_prompt": "이전 사용자 입력",
    "summary": "누적된 스토리 요약",
    "description": "",
    "entity_references": {
        "princess": "base64_encoded_image_data",
        "wizard": "base64_encoded_image_data",
        # ... 게임 중 등장한 모든 인물 레퍼런스
    }
}
```

#### 업데이트:
```python
# 매 요청 후 세션 업데이트
updated_session = {
    "prev_prompt": current_prompt,
    "summary": previous_summary + " " + current_prompt,
    "entity_references": updated_references
}
SessionManager.update_session(game_id, updated_session)
```

## 🎨 프롬프트 다양성 전략

### Text-to-Image 다양성 (8가지 변형)
- "creative and unique perspective"
- "fresh artistic interpretation"
- "imaginative composition"
- "unexpected creative angle"
- "artistic and original viewpoint"
- "innovative visual approach"
- "distinctive artistic style"
- "novel and inventive perspective"

### Image-to-Image 구도 다양화 (14가지)
- **기본 앵글**: dynamic, interesting, creative, unique
- **거리 변화**: varied distance, wide-angle, close-up
- **영화적 기법**: cinematic framing, dramatic viewpoint
- **특수 앵글**: bird's eye view, low angle heroic, tilted dutch angle
- **시점 변화**: over-the-shoulder, fresh perspective

## 📊 성능 및 제약사항

### API 제한
- **Gemini API**: 
  - 최대 3개 레퍼런스 이미지 동시 사용
  - 이미지 크기: 제한 없음 (자동 리사이징)
  - 응답 시간: 평균 2-5초

### 메모리 관리
- **세션 데이터**: 메모리 내 저장 (서버 재시작 시 초기화)
- **이미지 캐싱**: base64 인코딩으로 세션에 저장
- **가비지 컬렉션**: `/session/{game_id}` DELETE로 수동 정리

### 이미지 사양
- **종횡비**: 9:16 (세로형, 모바일 최적화)
- **품질**: JPEG 95%
- **크기**: 평균 200-500KB

## 🔧 에러 처리

### 일반적인 에러 상황:
1. **API 키 누락**: 환경변수 확인
2. **엔티티 파일 없음**: 기본 이미지 스킵
3. **Gemini API 실패**: HTTPException 500 반환
4. **이미지 디코딩 실패**: 예외 로깅 후 재시도

### 복구 전략:
```python
try:
    image = generate_image()
except Exception as e:
    logger.error(f"이미지 생성 실패: {e}")
    # Text-to-Image로 폴백
    image = generate_fallback_image()
```

## 📈 최적화 포인트

1. **레퍼런스 재사용**: 동일 캐릭터 반복 시 일관성 보장
2. **프롬프트 캐싱**: 자주 사용되는 조합 사전 정의
3. **비동기 처리**: async/await로 동시 요청 처리
4. **로깅 최적화**: 디버그/프로덕션 레벨 분리

## 🚀 실행 방법

```bash
# 환경변수 설정
export OPENAI_API_KEY="your-key"
export GEMINI_API_KEY="your-key"

# 서비스 실행
python unified_image_service.py

# API 확인
curl http://localhost:8190/health
```

## 📝 요약

1. **통합 관리**: 모든 이미지 생성을 하나의 서비스에서 처리
2. **지능적 모드 선택**: 엔티티 유무에 따라 최적 방식 선택
3. **일관성 보장**: Image-to-Image로 캐릭터 외형 유지
4. **다양성 확보**: 랜덤 프롬프트로 구도 변화
5. **세션 기반**: 게임별 독립적 컨텍스트 관리
