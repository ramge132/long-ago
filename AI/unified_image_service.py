#!/usr/bin/env python3
"""
Long Ago - 통합 이미지 생성 서비스 v2.0 (Image-to-Image 지원)
- Text-to-Image와 Image-to-Image 모두 지원
- 인물/사물/장소 레퍼런스 관리로 일관성 유지
- 게임별 세션 데이터 관리
"""

import os
import sys
import asyncio
import json
import base64
import logging
import io
import random
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

import uvicorn
import httpx
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from PIL import Image
from openai import OpenAI
import requests

# ================== 환경 설정 ==================

# 환경변수 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 캐릭터 파일 경로
CHARACTERS_DIR = Path(__file__).parent / "imageGeneration" / "characters"

# ================== 프롬프트 설정 (최상단 집중 관리) ==================

# 1. 그림체 스타일 정의 (9가지)
DRAWING_STYLES = [
    "anime style, vibrant colors, detailed illustration",           # 0: 애니메이션 스타일
    "cute 3d cartoon style, soft colors, rounded features",         # 1: 3D 카툰 스타일
    "comic strip style, bold outlines, dramatic expressions",       # 2: 만화 스타일
    "claymation style, 3D rendered, soft clay texture",            # 3: 클레이메이션
    "crayon drawing style, childlike, soft pastels",               # 4: 크레용 그림
    "pixel art style, retro gaming aesthetic, sharp pixels",       # 5: 픽셀 아트
    "minimalist illustration, clean lines, simple colors",         # 6: 미니멀리즘
    "watercolor painting style, soft blending, artistic",          # 7: 수채화
    "storybook illustration, whimsical, detailed"                  # 8: 동화책 일러스트
]

# 2. Text-to-Image 다양성 프롬프트 변형
TEXT_TO_IMAGE_VARIETY_MODIFIERS = [
    "creative and unique perspective",
    "fresh artistic interpretation", 
    "imaginative composition",
    "unexpected creative angle",
    "artistic and original viewpoint",
    "innovative visual approach",
    "distinctive artistic style",
    "novel and inventive perspective"
]

# 3. Image-to-Image 구도 다양화 옵션
IMAGE_TO_IMAGE_COMPOSITION_VARIETY = [
    "dynamic camera angle",           # 역동적인 카메라 앵글
    "interesting perspective",         # 흥미로운 관점
    "creative composition",           # 창의적인 구도
    "varied camera distance",         # 다양한 카메라 거리
    "cinematic framing",             # 영화적 프레이밍
    "dramatic viewpoint",            # 드라마틱한 시점
    "unique angle",                  # 독특한 앵글
    "fresh perspective",             # 신선한 관점
    "wide-angle view",               # 광각 뷰
    "close-up dramatic shot",        # 클로즈업 드라마틱 샷
    "bird's eye view",               # 조감도
    "low angle heroic shot",         # 로우앵글 영웅적 샷
    "tilted dutch angle",            # 틸트된 더치 앵글
    "over-the-shoulder view"         # 어깨 너머 뷰
]

# 4. 장면별 특수 프롬프트 템플릿
SCENE_TEMPLATES = {
    "ending": "Epic finale scene with dramatic atmosphere. ",
    "action": "Dynamic action scene with intense energy. ",
    "calm": "Peaceful and serene atmosphere. ",
    "emotional": "Emotionally charged scene with deep feelings. "
}

# 5. 기본 이미지 설정
IMAGE_SETTINGS = {
    "quality": 95  # JPEG 압축 품질 (1-100)
}

# FastAPI 앱 초기화
app = FastAPI(title="Unified Image Generation Service v2", version="2.0.0")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== 엔티티 관리 시스템 ==================

@dataclass
class Entity:
    name: str  # 영어 이름
    korean_name: str
    entity_type: str  # '인물', '사물', '장소'
    image_path: Optional[str] = None
    prompt: Optional[str] = None

class EntityManager:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.korean_to_english_map: Dict[str, str] = {}
        self.load_entities()

    def load_entities(self):
        """init_db.sql 기반 모든 개체 로드"""
        
        # 캐릭터 정보
        character_details = {
            "alien": {"korean": "외계인"}, "beggar": {"korean": "가난뱅이"}, "boy": {"korean": "소년"},
            "detective": {"korean": "탐정"}, "doctor": {"korean": "박사"}, "farmer": {"korean": "농부"},
            "girl": {"korean": "소녀"}, "idol": {"korean": "아이돌"}, "merchant": {"korean": "상인"},
            "ninja": {"korean": "닌자"}, "oldman": {"korean": "노인"}, "princess": {"korean": "공주"},
            "rich": {"korean": "부자"}, "wizard": {"korean": "마법사"}, "god": {"korean": "신"},
            "tiger": {"korean": "호랑이"}, "ghost": {"korean": "유령"}, "devil": {"korean": "마왕"}
        }

        for name, details in character_details.items():
            image_path = CHARACTERS_DIR / f"{name}.png"
            txt_path = CHARACTERS_DIR / f"{name}.txt"
            prompt = ""
            
            if txt_path.exists():
                with open(txt_path, 'r', encoding='utf-8') as f:
                    prompt = f.read().strip()
            
            entity = Entity(
                name=name,
                korean_name=details["korean"],
                entity_type='인물',
                image_path=str(image_path) if image_path.exists() else None,
                prompt=prompt
            )
            self.entities[name] = entity
            self.korean_to_english_map[details["korean"]] = name

        # init_db.sql 키워드
        sql_entities = {
            '핸드폰': 'phone', '마차': 'carriage', '인형': 'doll', '부적': 'talisman',
            '지도': 'map', '가면': 'mask', '칼': 'sword', '피리': 'flute',
            '지팡이': 'staff', '태양': 'sun', '날개': 'wings', '의자': 'chair',
            '시계': 'clock', '도장': 'stamp', '보석': 'gem', 'UFO': 'ufo',
            '덫': 'trap', '총': 'gun', '타임머신': 'timemachine', '감자': 'potato',
            '바다': 'sea', '다리': 'bridge', '묘지': 'cemetery', '식당': 'restaurant',
            '박물관': 'museum', '비밀통로': 'secretpassage', '사막': 'desert',
            '저택': 'mansion', '천국': 'heaven'
        }
        
        entity_types = {
            '핸드폰': '사물', '마차': '사물', '인형': '사물', '부적': '사물',
            '지도': '사물', '가면': '사물', '칼': '사물', '피리': '사물',
            '지팡이': '사물', '태양': '사물', '날개': '사물', '의자': '사물',
            '시계': '사물', '도장': '사물', '보석': '사물', 'UFO': '사물',
            '덫': '사물', '총': '사물', '타임머신': '사물', '감자': '사물',
            '바다': '장소', '다리': '장소', '묘지': '장소', '식당': '장소',
            '박물관': '장소', '비밀통로': '장소', '사막': '장소',
            '저택': '장소', '천국': '장소'
        }

        for korean, english in sql_entities.items():
            if english not in self.entities:
                self.entities[english] = Entity(
                    name=english,
                    korean_name=korean,
                    entity_type=entity_types.get(korean, '사물')
                )
            self.korean_to_english_map[korean] = english

    def get_entity(self, name: str) -> Optional[Entity]:
        return self.entities.get(name)

    def detect_entities_in_text(self, text: str) -> List[str]:
        detected = []
        for korean, english in self.korean_to_english_map.items():
            if korean in text:
                detected.append(english)
        
        return sorted(list(set(detected)), 
                     key=lambda x: text.find(self.get_entity(x).korean_name) 
                     if self.get_entity(x) else -1)

# ================== 요청/응답 모델 ==================

class SceneGenerationRequest(BaseModel):
    gameId: str
    userId: str
    userPrompt: str
    turn: int
    drawingStyle: int
    isEnding: bool
    sessionData: Optional[Dict] = None  # 세션 데이터 추가

class BookCoverGenerationRequest(BaseModel):
    storyContent: str
    gameId: str
    drawingStyle: int

# ================== 세션 관리 ==================

class SessionManager:
    """게임별 세션 데이터 관리"""
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def get_session(self, game_id: str) -> Dict:
        if game_id not in self.sessions:
            self.sessions[game_id] = {
                "prev_prompt": "",
                "summary": "",
                "description": "",
                "entity_references": {}
            }
        return self.sessions[game_id]
    
    def update_session(self, game_id: str, data: Dict):
        self.sessions[game_id] = data
    
    def clear_session(self, game_id: str):
        if game_id in self.sessions:
            del self.sessions[game_id]

# ================== 이미지 생성 서비스 ==================

class UnifiedImageServiceV2:
    def __init__(self):
        """통합 이미지 생성 서비스 v2 초기화"""
        if not all([OPENAI_API_KEY, GEMINI_API_KEY]):
            logger.error("필수 환경변수가 설정되지 않았습니다")
            sys.exit(1)
        
        self.entity_manager = EntityManager()
        self.session_manager = SessionManager()
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        logger.info("통합 이미지 생성 서비스 v2 초기화 완료 (Image-to-Image 지원)")

    async def generate_scene_image(self, request: SceneGenerationRequest) -> bytes:
        """장면 이미지 생성 - Image-to-Image 지원"""
        try:
            logger.info("=== 이미지 생성 요청 시작 (v2) ===")
            logger.info(f"게임ID: {request.gameId}, 사용자ID: {request.userId}, 턴: {request.turn}")
            logger.info(f"사용자 입력: [{request.userPrompt}]")
            
            # 세션 데이터 가져오기
            session_data = request.sessionData or self.session_manager.get_session(request.gameId)
            
            # 엔티티 탐지
            detected_entities = self.entity_manager.detect_entities_in_text(request.userPrompt)
            logger.info(f"🔹 발견된 엔티티: {detected_entities}")
            
            # 스타일 가져오기
            art_style = DRAWING_STYLES[request.drawingStyle]
            
            # 레퍼런스 관리
            entity_references = session_data.get('entity_references', {})
            
            # Image-to-Image 또는 Text-to-Image 결정
            if detected_entities:
                logger.info("🔹 Image-to-Image 모드 활성화")
                image_data = await self._generate_with_references(
                    request.userPrompt,
                    detected_entities,
                    entity_references,
                    art_style,
                    request.isEnding
                )
                
                # 첫 등장 엔티티 레퍼런스 저장
                for entity_name in detected_entities:
                    if entity_name not in entity_references:
                        entity = self.entity_manager.get_entity(entity_name)
                        if entity and entity.entity_type == '인물':
                            logger.info(f"🔹 '{entity.korean_name}' 레퍼런스 저장")
                            entity_references[entity_name] = base64.b64encode(image_data).decode('utf-8')
                
            else:
                logger.info("🔹 Text-to-Image 모드")
                image_data = await self._generate_text_to_image(
                    request.userPrompt,
                    art_style,
                    request.isEnding
                )
            
            # 세션 업데이트
            updated_session = {
                "prev_prompt": request.userPrompt,
                "summary": session_data.get("summary", "") + " " + request.userPrompt,
                "description": "",
                "entity_references": entity_references
            }
            self.session_manager.update_session(request.gameId, updated_session)
            
            logger.info(f"✅ 이미지 생성 완료: {len(image_data)} bytes")
            return image_data
            
        except Exception as e:
            logger.error(f"이미지 생성 실패: {str(e)}")
            raise HTTPException(status_code=500, detail=f"이미지 생성 실패: {str(e)}")

    async def _generate_with_references(self, prompt: str, entities: List[str], 
                                       references: Dict, style: str, is_ending: bool) -> bytes:
        """레퍼런스 이미지를 활용한 Image-to-Image 생성"""
        
        # 레퍼런스 이미지 수집 (최대 3개)
        reference_images = []
        reference_prompts = []
        
        for entity_name in entities[:3]:  # 최대 3개만
            entity = self.entity_manager.get_entity(entity_name)
            if not entity:
                continue
            
            # 레퍼런스 이미지 찾기
            if entity_name in references:
                # 저장된 레퍼런스 사용
                logger.info(f"   - '{entity.korean_name}' 레퍼런스 재사용")
                img_data = base64.b64decode(references[entity_name])
                reference_images.append(Image.open(io.BytesIO(img_data)))
            elif entity.image_path:
                # 기본 이미지 사용
                logger.info(f"   - '{entity.korean_name}' 기본 이미지 사용")
                reference_images.append(Image.open(entity.image_path))
            
            if entity.prompt:
                reference_prompts.append(entity.prompt)
        
        # Gemini Image-to-Image API 호출
        if reference_images:
            return await self._call_gemini_image_to_image(
                reference_images, prompt, reference_prompts, style
            )
        else:
            return await self._generate_text_to_image(prompt, style, is_ending)

    async def _generate_text_to_image(self, prompt: str, style: str, is_ending: bool) -> bytes:
        """Text-to-Image 생성"""
        if is_ending:
            full_prompt = f"{style} 스타일로 그린 결말 장면: {prompt}. No text, words, or writing in the image."
        else:
            full_prompt = f"{style} 스타일로 그린 {prompt} 이미지. No text, words, or writing in the image."
        
        return await self._call_gemini_text_to_image(full_prompt)

    async def _call_gemini_text_to_image(self, prompt: str) -> bytes:
        """Gemini Text-to-Image API 호출"""
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key={GEMINI_API_KEY}"
        
        # 최상단에 정의된 다양성 프롬프트 사용
        selected_modifier = random.choice(TEXT_TO_IMAGE_VARIETY_MODIFIERS)
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Create a picture of: {prompt}. {selected_modifier}"
                }]
            }]
        }
        
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if 'candidates' in result and result['candidates']:
            for part in result['candidates'][0].get('content', {}).get('parts', []):
                if 'inlineData' in part:
                    return base64.b64decode(part['inlineData']['data'])
        
        raise Exception("이미지 생성 실패")

    async def _call_gemini_image_to_image(self, ref_images: List[Image.Image], 
                                         prompt: str, ref_prompts: List[str], style: str) -> bytes:
        """Gemini Image-to-Image API 호출 - 프롬프트 기반 다양성
        
        Args:
            ref_images: 레퍼런스 이미지들
            prompt: 생성할 장면 설명
            ref_prompts: 레퍼런스 캐릭터 설명
            style: 그림 스타일
        """
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key={GEMINI_API_KEY}"
        
        # 최상단에 정의된 구도 다양화 옵션 사용
        selected_composition = random.choice(IMAGE_TO_IMAGE_COMPOSITION_VARIETY)
        
        # parts 구성 - 디자인 참조만 하도록 수정
        parts = [{
            "text": f"Using the provided reference images as design references only, create a new scene. "
                   f"Reference the character designs (clothing style, colors, general appearance) but create them in new poses and expressions appropriate for the scene. "
                   f"{' '.join(ref_prompts)} "
                   f"Scene: {prompt}. "
                   f"Style: {style}. "
                   f"Use {selected_composition} for creative variety. "
                   f"No text, words, or writing in the image."
        }]
        
        # 레퍼런스 이미지 추가
        for img in ref_images:
            buffer = io.BytesIO()
            if img.mode == 'RGBA':
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
                img = rgb_img
            img.save(buffer, format='JPEG', quality=95)
            
            parts.append({
                "inlineData": {
                    "mimeType": "image/jpeg",
                    "data": base64.b64encode(buffer.getvalue()).decode('utf-8')
                }
            })
        
        payload = {
            "contents": [{"parts": parts}]
        }
        
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if 'candidates' in result and result['candidates']:
            for part in result['candidates'][0].get('content', {}).get('parts', []):
                if 'inlineData' in part:
                    return base64.b64decode(part['inlineData']['data'])
        
        raise Exception("Image-to-Image 생성 실패")

    async def generate_book_cover(self, request: BookCoverGenerationRequest) -> tuple[str, bytes]:
        """책 표지 생성"""
        # 기존 로직 유지
        title = "멋진 이야기"  # 간단히 처리
        # 텍스트 없는 책 표지 이미지 생성
        cover_prompt = f"beautiful book cover illustration without any text or title"
        cover_image = await self._generate_text_to_image(
            cover_prompt,
            DRAWING_STYLES[request.drawingStyle],
            False
        )
        return title, cover_image

# 전역 서비스 인스턴스
image_service = UnifiedImageServiceV2()

# ================== API 엔드포인트 ==================

@app.post("/generate-scene")
async def generate_scene_image(request: SceneGenerationRequest):
    """장면 이미지 생성 API"""
    try:
        image_data = await image_service.generate_scene_image(request)
        return Response(content=image_data, media_type="image/png")
    except Exception as e:
        logger.error(f"API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-cover")
async def generate_book_cover(request: BookCoverGenerationRequest):
    """책 표지 생성 API"""
    try:
        title, image_data = await image_service.generate_book_cover(request)
        return {
            "title": title,
            "image_data": base64.b64encode(image_data).decode('utf-8'),
            "success": True
        }
    except Exception as e:
        logger.error(f"API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "features": ["text-to-image", "image-to-image"]
    }

@app.delete("/session/{game_id}")
async def clear_session(game_id: str):
    """게임 세션 정리"""
    image_service.session_manager.clear_session(game_id)
    return {"message": f"Session cleared for game {game_id}"}

if __name__ == "__main__":
    logger.info("=== Long Ago 통합 이미지 생성 서비스 v2 시작 ===")
    logger.info("✅ Image-to-Image 기능 활성화")
    logger.info(f"OpenAI API 키: {'설정됨' if OPENAI_API_KEY else '없음'}")
    logger.info(f"Gemini API 키: {'설정됨' if GEMINI_API_KEY else '없음'}")
    
    uvicorn.run(app, host="0.0.0.0", port=8190)
