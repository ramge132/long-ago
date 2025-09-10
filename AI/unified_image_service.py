#!/usr/bin/env python3
"""
Long Ago - 통합 이미지 생성 서비스 v2.0
- 엔티티 기반 추출 및 관리
- 동적 프롬프트 조합 및 스타일 다양화
- 안정적인 폴백 메커니즘
"""

import os
import sys
import asyncio
import json
import base64
import logging
import io
import random
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

import uvicorn
import httpx
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from PIL import Image
import requests

# 환경변수 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 캐릭터 파일 경로
CHARACTERS_DIR = Path(__file__).parent / "imageGeneration" / "characters"

# 캐릭터 레퍼런스 저장소 (게임별로 관리)
character_references = {}

# ================== 프롬프트 설정 ==================

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

# 2. 구도 다양화 옵션
COMPOSITION_VARIATIONS = [
    "medium shot",
    "wide shot showing full scene",
    "dramatic close-up",
    "over-the-shoulder perspective",
    "bird's eye view",
    "low angle shot",
    "diagonal composition",
    "rule of thirds composition"
]

# 3. 표정 및 포즈 옵션
EXPRESSION_VARIATIONS = [
    "surprised", "happy", "sad", "angry", "thoughtful", 
    "excited", "worried", "determined", "laughing", "crying"
]

POSE_VARIATIONS = [
    "standing", "sitting", "running", "jumping", "reaching out",
    "pointing", "looking up", "looking down", "hands on hips", "arms crossed"
]

# 4. 시간대별 조명 효과
TIME_OF_DAY_LIGHTING = {
    "morning": "soft morning light, golden hour glow, long shadows",
    "afternoon": "bright daylight, clear visibility, natural colors",
    "evening": "warm sunset lighting, orange and pink sky, dramatic shadows",
    "night": "moonlight, starry sky, mysterious atmosphere"
}

# FastAPI 앱 초기화
app = FastAPI(title="Unified Image Generation Service v2", version="2.0.0")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== 엔티티 관리 시스템 ==================

class EntityManager:
    """
    엔티티(캐릭터, 객체, 장소) 추출 및 관리
    """
    def __init__(self):
        # 캐릭터 타입 매핑 (한글 -> 영문)
        self.character_keywords = {
            "공주": "princess", "왕자": "prince", "마법사": "wizard", 
            "소년": "boy", "소녀": "girl", "노인": "oldman",
            "탐정": "detective", "박사": "doctor", "농부": "farmer",
            "아이돌": "idol", "상인": "merchant", "닌자": "ninja",
            "부자": "rich", "가난뱅이": "beggar", "외계인": "alien"
        }
        
        # 장소 관련 키워드
        self.location_keywords = {
            "숲": "forest", "성": "castle", "마을": "village",
            "바다": "ocean", "산": "mountain", "동굴": "cave",
            "학교": "school", "집": "house", "정원": "garden",
            "사막": "desert", "우주": "space", "도시": "city"
        }
        
        # 객체 관련 키워드
        self.object_keywords = {
            "검": "sword", "마법지팡이": "magic wand", "책": "book",
            "보물": "treasure", "열쇠": "key", "거울": "mirror",
            "꽃": "flower", "나무": "tree", "별": "star"
        }
        
        # 감정 키워드
        self.emotion_keywords = {
            "행복": "happy", "슬픔": "sad", "분노": "angry",
            "놀람": "surprised", "두려움": "scared", "기쁨": "joyful"
        }
        
        # 기본 캐릭터 이미지 로드
        self.default_images = {}
        self._load_default_images()
    
    def _load_default_images(self):
        """기본 캐릭터 이미지 로드"""
        for korean, english in self.character_keywords.items():
            image_path = CHARACTERS_DIR / f"{english}.png"
            if image_path.exists():
                with open(image_path, 'rb') as f:
                    self.default_images[english] = f.read()
                logger.info(f"✓ 기본 이미지 로드: {english}.png")
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """텍스트에서 엔티티 추출"""
        entities = {
            "characters": [],
            "locations": [],
            "objects": [],
            "emotions": []
        }
        
        # 캐릭터 추출
        for korean, english in self.character_keywords.items():
            if korean in text:
                entities["characters"].append(english)
        
        # 장소 추출
        for korean, english in self.location_keywords.items():
            if korean in text:
                entities["locations"].append(english)
        
        # 객체 추출
        for korean, english in self.object_keywords.items():
            if korean in text:
                entities["objects"].append(english)
        
        # 감정 추출
        for korean, english in self.emotion_keywords.items():
            if korean in text:
                entities["emotions"].append(english)
        
        return entities
    
    def get_default_image(self, character_type: str) -> Optional[bytes]:
        """기본 캐릭터 이미지 반환"""
        return self.default_images.get(character_type)

# ================== 프롬프트 생성기 ==================

class PromptGenerator:
    """
    동적 프롬프트 생성 및 조합
    """
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
    
    def create_dynamic_prompt(self, 
                            user_prompt: str, 
                            drawing_style: int = 0,
                            is_ending: bool = False) -> str:
        """
        사용자 입력을 기반으로 동적 프롬프트 생성
        """
        # 엔티티 추출
        entities = self.entity_manager.extract_entities(user_prompt)
        
        # 기본 프롬프트 구성
        prompt_parts = []
        
        # 스타일 추가
        prompt_parts.append(DRAWING_STYLES[drawing_style])
        
        # 캐릭터 설명
        if entities["characters"]:
            char_desc = ", ".join(entities["characters"])
            # 표정과 포즈 랜덤 추가
            expression = random.choice(EXPRESSION_VARIATIONS)
            pose = random.choice(POSE_VARIATIONS)
            prompt_parts.append(f"{char_desc} character, {expression} expression, {pose}")
        
        # 장소 설명
        if entities["locations"]:
            location_desc = ", ".join(entities["locations"])
            # 시간대 조명 효과 랜덤 추가
            time_key = random.choice(list(TIME_OF_DAY_LIGHTING.keys()))
            lighting = TIME_OF_DAY_LIGHTING[time_key]
            prompt_parts.append(f"in {location_desc}, {lighting}")
        
        # 객체 설명
        if entities["objects"]:
            objects_desc = ", ".join(entities["objects"])
            prompt_parts.append(f"with {objects_desc}")
        
        # 구도 다양화
        composition = random.choice(COMPOSITION_VARIATIONS)
        prompt_parts.append(composition)
        
        # 엔딩 특별 효과
        if is_ending:
            prompt_parts.append("epic finale scene, dramatic lighting, emotional climax")
        
        # 품질 향상 키워드
        prompt_parts.append("high quality, detailed illustration, vibrant colors")
        
        # 안전 키워드
        prompt_parts.append("safe for work, no text, no watermark")
        
        final_prompt = ", ".join(prompt_parts)
        
        logger.info(f"Generated prompt: {final_prompt[:100]}...")
        return final_prompt

# ================== 이미지 생성 서비스 ==================

class ImageGenerationService:
    """
    통합 이미지 생성 서비스
    """
    def __init__(self):
        self.entity_manager = EntityManager()
        self.prompt_generator = PromptGenerator(self.entity_manager)
        self.gemini_api_key = GEMINI_API_KEY
        
        if not self.gemini_api_key:
            logger.error("GEMINI_API_KEY 환경변수가 설정되지 않았습니다!")
            sys.exit(1)
        
        logger.info("이미지 생성 서비스 초기화 완료")
    
    async def generate_image_with_gemini(self, prompt: str, reference_image: Optional[bytes] = None) -> bytes:
        """
        Gemini API를 사용한 이미지 생성 (Text-to-Image 또는 Image-to-Image)
        """
        import requests
        
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key={self.gemini_api_key}"
        
        parts = []
        
        # Image-to-Image 모드
        if reference_image:
            # 레퍼런스 이미지를 base64로 인코딩
            ref_base64 = base64.b64encode(reference_image).decode('utf-8')
            parts.append({
                "inlineData": {
                    "mimeType": "image/png",
                    "data": ref_base64
                }
            })
            parts.append({
                "text": f"Based on the character in this reference image, generate a new scene: {prompt}. Keep the exact same character appearance, only change the scene and pose."
            })
        else:
            # Text-to-Image 모드
            parts.append({
                "text": f"Generate an image: {prompt}"
            })
        
        payload = {
            "contents": [{
                "parts": parts
            }],
            "generationConfig": {
                "temperature": 0.8,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 8192
            }
        }
        
        try:
            response = requests.post(api_url, json=payload, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Gemini API 오류: {response.status_code}")
                logger.error(f"응답: {response.text}")
                raise Exception(f"Gemini API 오류: {response.status_code}")
            
            result = response.json()
            
            # 이미지 데이터 추출
            if 'candidates' in result and result['candidates']:
                for part in result['candidates'][0].get('content', {}).get('parts', []):
                    if 'inlineData' in part:
                        image_data = base64.b64decode(part['inlineData']['data'])
                        return image_data
            
            raise Exception("이미지 데이터를 찾을 수 없습니다")
            
        except Exception as e:
            logger.error(f"Gemini 이미지 생성 실패: {str(e)}")
            raise
    
    async def generate_scene_image(self, 
                                 user_prompt: str,
                                 drawing_style: int = 0,
                                 is_ending: bool = False,
                                 game_id: str = None,
                                 turn: int = 0) -> bytes:
        """
        장면 이미지 생성 (Image-to-Image 지원)
        """
        try:
            logger.info(f"=== 이미지 생성 요청 시작 (v2) ===")
            logger.info(f"게임ID: {game_id}, 사용자ID: {user_prompt[:50]}, 턴: {turn}")
            logger.info(f"사용자 입력: [{user_prompt}]")
            
            # 엔티티 추출
            entities = self.entity_manager.extract_entities(user_prompt)
            detected_characters = entities["characters"]
            logger.info(f"🔹 발견된 엔티티: {detected_characters}")
            
            # 동적 프롬프트 생성
            dynamic_prompt = self.prompt_generator.create_dynamic_prompt(
                user_prompt, drawing_style, is_ending
            )
            
            # 게임별 캐릭터 레퍼런스 확인
            reference_image = None
            if game_id and detected_characters:
                game_refs = character_references.get(game_id, {})
                
                # 첫 번째 발견된 캐릭터의 레퍼런스 사용
                for char in detected_characters:
                    if char in game_refs:
                        reference_image = game_refs[char]
                        logger.info(f"🔹 '{char}' 캐릭터 레퍼런스 사용 (Image-to-Image)")
                        break
            
            if reference_image:
                logger.info(f"🔹 Image-to-Image 모드")
            else:
                logger.info(f"🔹 Text-to-Image 모드")
            
            # Gemini로 이미지 생성
            image_data = await self.generate_image_with_gemini(dynamic_prompt, reference_image)
            
            # 새로운 캐릭터라면 레퍼런스로 저장
            if game_id and detected_characters and not reference_image:
                if game_id not in character_references:
                    character_references[game_id] = {}
                
                for char in detected_characters:
                    if char not in character_references[game_id]:
                        character_references[game_id][char] = image_data
                        logger.info(f"✅ '{char}' 캐릭터 레퍼런스 저장 (턴 {turn})")
            
            logger.info(f"✅ 이미지 생성 완료: {len(image_data)} bytes")
            return image_data
            
        except Exception as e:
            logger.error(f"이미지 생성 실패: {str(e)}")
            
            # 2차 시도: 기본 캐릭터 이미지 반환
            entities = self.entity_manager.extract_entities(user_prompt)
            if entities["characters"]:
                char_type = entities["characters"][0]
                default_image = self.entity_manager.get_default_image(char_type)
                if default_image:
                    logger.info(f"✓ 기본 이미지 사용: {char_type}")
                    return default_image
            
            # 3차: 빈 이미지 반환
            logger.warning("기본 이미지도 없음, 빈 이미지 반환")
            return self._create_empty_image()
    
    def _create_empty_image(self) -> bytes:
        """빈 이미지 생성"""
        img = Image.new('RGB', (512, 512), color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    async def generate_book_cover(self, story_content: str, drawing_style: int = 0) -> tuple[str, bytes]:
        """
        책 표지 생성 (GPT-5-nano로 제목 생성)
        """
        try:
            # 1. GPT-5-nano로 제목 생성
            title = await self._generate_title_with_gpt5(story_content)
            logger.info(f"📚 GPT-5로 생성된 책 제목: [{title}]")
            
            # 2. 표지 프롬프트 생성
            cover_prompt = f"book cover illustration, title '{title}', {DRAWING_STYLES[drawing_style]}, epic, centered composition"
            
            # 3. Gemini로 표지 이미지 생성
            image_data = await self.generate_image_with_gemini(cover_prompt)
            logger.info(f"🎨 표지 이미지 생성 완료: {len(image_data)} bytes")
            
            return title, image_data
            
        except Exception as e:
            logger.error(f"표지 생성 실패: {str(e)}")
            # 폴백: 간단한 제목 생성
            title = self._generate_simple_title(story_content)
            return title, self._create_empty_image()
    
    async def _generate_title_with_gpt5(self, story: str) -> str:
        """
        GPT-5-nano를 사용한 책 제목 생성
        """
        if not OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY가 설정되지 않음. 기본 제목 생성으로 폴백")
            return self._generate_simple_title(story)
        
        try:
            # 스토리 요약 (너무 길면 잘라냄)
            story_summary = story[:500] if len(story) > 500 else story
            
            # GPT-5-nano API 호출
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-5-nano",
                "input": f"다음 이야기의 창의적이고 흥미로운 한국어 제목을 10자 이내로 만들어주세요. 제목만 답하세요: {story_summary}",
                "text": {"verbosity": "low"},
                "reasoning": {"effort": "minimal"}
            }
            
            response = requests.post(
                "https://api.openai.com/v1/responses",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # GPT-5 응답에서 제목 추출
                if "output_text" in result:
                    title = result["output_text"].strip()
                elif "output" in result and isinstance(result["output"], list):
                    for output in result["output"]:
                        if "text" in output:
                            title = output["text"].strip()
                            break
                        elif output.get("type") == "message" and "content" in output:
                            for content in output["content"]:
                                if content.get("type") == "output_text" and "text" in content:
                                    title = content["text"].strip()
                                    break
                else:
                    logger.warning("GPT-5 응답에서 제목을 찾을 수 없음")
                    return self._generate_simple_title(story)
                
                # 제목이 너무 길면 잘라냄
                if len(title) > 15:
                    title = title[:15]
                
                return title
            else:
                logger.error(f"GPT-5 API 오류: {response.status_code}")
                return self._generate_simple_title(story)
                
        except Exception as e:
            logger.error(f"GPT-5 제목 생성 실패: {str(e)}")
            return self._generate_simple_title(story)
    
    def _generate_simple_title(self, story: str) -> str:
        """간단한 제목 생성"""
        # 스토리에서 주요 캐릭터 찾기
        entities = self.entity_manager.extract_entities(story)
        
        if entities["characters"]:
            # 첫 번째 캐릭터 기반 제목
            char_map = {
                "princess": "공주의 모험",
                "prince": "왕자의 여정",
                "wizard": "마법사의 비밀",
                "boy": "소년의 이야기",
                "girl": "소녀의 꿈",
                "oldman": "노인의 지혜",
                "detective": "탐정의 추리",
                "doctor": "박사의 발견",
                "farmer": "농부의 하루",
                "idol": "아이돌의 무대",
                "merchant": "상인의 거래",
                "ninja": "닌자의 임무",
                "rich": "부자의 비밀",
                "beggar": "가난뱅이의 행운",
                "alien": "외계인의 방문"
            }
            first_char = entities["characters"][0]
            if first_char in char_map:
                return char_map[first_char]
        
        # 장소 기반 제목
        if entities["locations"]:
            location_map = {
                "forest": "숲속의 이야기",
                "castle": "성의 전설",
                "village": "마을의 비밀",
                "ocean": "바다의 노래",
                "mountain": "산의 전설",
                "cave": "동굴의 신비",
                "school": "학교 이야기",
                "house": "집으로 가는 길",
                "garden": "정원의 기적",
                "desert": "사막의 별",
                "space": "우주 모험",
                "city": "도시의 빛"
            }
            first_loc = entities["locations"][0]
            if first_loc in location_map:
                return location_map[first_loc]
        
        # 기본값
        return "아주 먼 옛날 이야기"

# 전역 서비스 인스턴스
image_service = ImageGenerationService()

# ================== API 엔드포인트 ==================

class SceneGenerationRequest(BaseModel):
    gameId: str
    userId: str
    userPrompt: str
    turn: int
    drawingStyle: int = 0
    isEnding: bool = False

class BookCoverGenerationRequest(BaseModel):
    storyContent: str
    gameId: str
    drawingStyle: int = 0

@app.post("/generate-scene")
async def generate_scene_endpoint(request: SceneGenerationRequest):
    """장면 이미지 생성 API"""
    try:
        logger.info(f"Scene generation request: {request.userPrompt[:50]}...")
        
        image_data = await image_service.generate_scene_image(
            user_prompt=request.userPrompt,
            drawing_style=request.drawingStyle,
            is_ending=request.isEnding,
            game_id=request.gameId,
            turn=request.turn
        )
        
        return Response(
            content=image_data,
            media_type="image/png"
        )
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-cover")
async def generate_cover_endpoint(request: BookCoverGenerationRequest):
    """책 표지 생성 API"""
    try:
        logger.info(f"Cover generation request for game: {request.gameId}")
        
        title, image_data = await image_service.generate_book_cover(
            story_content=request.storyContent,
            drawing_style=request.drawingStyle
        )
        
        return {
            "title": title,
            "image_data": base64.b64encode(image_data).decode('utf-8'),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "features": [
            "entity-extraction",
            "dynamic-prompts",
            "style-variation",
            "fallback-mechanism"
        ]
    }

@app.get("/entities/extract")
async def extract_entities_endpoint(text: str):
    """엔티티 추출 테스트 API"""
    entities = image_service.entity_manager.extract_entities(text)
    return {
        "input": text,
        "entities": entities
    }

@app.delete("/game/{game_id}")
async def cleanup_game_endpoint(game_id: str):
    """게임 종료 시 레퍼런스 정리"""
    if game_id in character_references:
        char_count = len(character_references[game_id])
        del character_references[game_id]
        logger.info(f"🗑️ 게임 {game_id}의 캐릭터 레퍼런스 {char_count}개 정리 완료")
        return {"message": f"Game {game_id} references cleaned ({char_count} characters)"}
    return {"message": f"No references found for game {game_id}"}

# ================== 메인 실행 ==================

if __name__ == "__main__":
    logger.info("="*50)
    logger.info("Long Ago 이미지 생성 서비스 v2.0 시작")
    logger.info("포트: 8190")
    logger.info("="*50)
    
    uvicorn.run(app, host="0.0.0.0", port=8190)
