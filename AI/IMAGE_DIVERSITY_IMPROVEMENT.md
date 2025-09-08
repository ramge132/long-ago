# 이미지 다양성 개선 가이드

## 개요
Gemini-2.5-flash-image-preview API의 Image-to-Image 기능에서 발생하는 구조적 반복 문제를 해결하기 위한 프롬프트 기반 개선 방법

## 문제점
- 기존: 캐릭터 일관성은 유지되지만 이미지 구도가 너무 비슷함
- 원인: Gemini API가 일관성 유지에 최적화되어 있어 구도 변화가 적음

## 해결 방법

### 1. 프롬프트 기반 다양성 제어

Gemini-2.5-flash-image-preview API는 이미지 생성 시 별도의 generation config 파라미터를 지원하지 않습니다. 
따라서 **프롬프트 엔지니어링**을 통해 다양성을 제어합니다.

#### Text-to-Image 다양성 프롬프트
```python
variety_modifiers = [
    "creative and unique perspective",
    "fresh artistic interpretation", 
    "imaginative composition",
    "unexpected creative angle"
]
```

#### Image-to-Image 구도 다양화
```python
composition_variety = [
    "dynamic camera angle",
    "interesting perspective", 
    "creative composition",
    "varied camera distance",
    "cinematic framing",
    "dramatic viewpoint",
    "unique angle",
    "fresh perspective"
]
```

### 2. 장면별 프롬프트 강화

액션이나 엔딩 장면에서 더 다양한 구도를 위한 프롬프트 추가:

#### 정적인 장면
```
"Maintain consistent character appearance with subtle composition variation"
```

#### 동적인 장면  
```
"Dynamic action scene with dramatic camera angle while keeping character features"
```

#### 엔딩 장면
```
"Cinematic finale with epic perspective, maintaining character consistency"
```

### 3. 랜덤 프롬프트 변형

매 생성마다 다른 구도 지시어를 랜덤으로 선택하여 추가:

```python
import random

# 랜덤으로 구도 옵션 선택
selected_composition = random.choice(composition_variety)

prompt = f"Scene: {user_prompt}. Use {selected_composition} while keeping character consistency."
```

## 구현 전략

### 프롬프트 구조
```
1. 레퍼런스 이미지 유지 요청
2. 장면 설명
3. 스타일 지정
4. 구도 변형 지시
5. 종횡비 지정
```

예시:
```
"Using the provided reference images, create a new image. 
Maintain character appearances exactly as shown in references.
Scene: [사용자 프롬프트]
Style: [그림 스타일]
Use [랜덤 구도 옵션] while keeping character consistency.
Portrait orientation, 9:16 aspect ratio"
```

## 효과

1. **캐릭터 일관성 유지**: 레퍼런스 이미지로 인물 외형 보존
2. **구도 다양화**: 프롬프트 내 구도 지시어로 다양한 앵글 생성
3. **자연스러운 변화**: 강제적이지 않은 자연스러운 구도 변화

## 주의사항

- Gemini 이미지 생성 API는 텍스트 생성과 달리 temperature, topK, topP 파라미터를 지원하지 않음
- 다양성은 전적으로 프롬프트 엔지니어링에 의존
- 너무 강한 변화 지시는 캐릭터 일관성을 해칠 수 있음

## 추가 최적화 방안

1. **프롬프트 라이브러리 확장**
   - 더 많은 구도/앵글 표현 추가
   - 장르별 특화 프롬프트 개발

2. **컨텍스트 기반 선택**
   - 이전 이미지와 다른 구도 우선 선택
   - 장면 내용에 맞는 구도 자동 매칭

3. **A/B 테스트**
   - 다양한 프롬프트 조합 테스트
   - 사용자 선호도 기반 최적화
