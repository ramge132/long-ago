#!/usr/bin/env python3
"""
Long Ago - 통합 이미지 생성 서비스 v2.3
- 엔티티 기반 추출 및 관리
- 동적 프롬프트 조합 및 스타일 다양화
- 안정적인 폴백 메커니즘
- 사용자 의도 기반 및 문맥 보강 로직 분리
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

# 게임별 상태 저장소
character_references = {}
game_contexts = {}

def _add_korean_particle(noun: str, particle_pair: tuple[str, str]) -> str:
    if not isinstance(noun, str) or not noun: return ""
    last_char = noun[-1]
    if '가' <= last_char <= '힣':
        has_batchim = (ord(last_char) - 0xAC00) % 28 > 0
        return noun + particle_pair[0] if has_batchim else noun + particle_pair[1]
    return noun + particle_pair[1]

# ================== 프롬프트 설정 ==================
DRAWING_STYLES = [
    "anime style, vibrant colors, detailed illustration",
    "cute 3d cartoon style, soft colors, rounded features",
    "comic strip style, bold outlines, dramatic expressions",
    "claymation style, 3D rendered, soft clay texture",
    "crayon drawing style, childlike, soft pastels",
    "pixel art style, retro gaming aesthetic, sharp pixels",
    "minimalist illustration, clean lines, simple colors",
    "watercolor painting style, soft blending, artistic",
    "storybook illustration, whimsical, detailed"
]
COMPOSITION_VARIATIONS = ["medium shot", "wide shot", "dramatic close-up", "over-the-shoulder perspective"]
EXPRESSION_VARIATIONS = ["surprised", "happy", "sad", "angry", "thoughtful", "excited"]
POSE_VARIATIONS = ["standing", "sitting", "running", "jumping", "looking up"]
TIME_OF_DAY_LIGHTING = { "morning": "soft morning light", "afternoon": "bright daylight", "evening": "warm sunset lighting", "night": "moonlight" }

# ================== FastAPI 앱 및 로깅 ==================
app = FastAPI(title="Unified Image Generation Service v2.3", version="2.3.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== 엔티티 관리 시스템 ==================
class EntityManager:
    def __init__(self):
        self.character_keywords = { '호랑이': 'tiger', '유령': 'ghost', '농부': 'farmer', '상인': 'merchant', '신': 'god', '외계인': 'alien', '박사': 'doctor', '아이돌': 'idol', '마법사': 'wizard', '마왕': 'demon king', '소년': 'boy', '소녀': 'girl', '부자': 'rich person', '탐정': 'detective', '노인': 'old man', '가난뱅이': 'beggar', '공주': 'princess', '닌자': 'ninja' }
        self.location_keywords = { "숲": "forest", "성": "castle", "마을": "village", "바다": "ocean", "산": "mountain", "동굴": "cave", "학교": "school", "집": "house", "정원": "garden", "사막": "desert", "우주": "space", "도시": "city", "다리": "bridge", "묘지": "cemetery", "식당": "restaurant", "박물관": "museum", "비밀통로": "secret passage", "저택": "mansion", "천국": "heaven" }
        self.object_keywords = { '핸드폰': 'smartphone', '마차': 'carriage', '인형': 'doll', '부적': 'talisman', '지도': 'map', '가면': 'mask', '칼': 'sword', '피리': 'flute', '지팡이': 'staff', '태양': 'sun', '날개': 'wings', '의자': 'chair', '시계': 'clock', '도장': 'seal', '보석': 'jewel', 'UFO': 'UFO', '덫': 'trap', '총': 'gun', '타임머신': 'time machine', '감자': 'potato', "검": "sword", "마법지팡이": "magic wand", "책": "book", "보물": "treasure", "열쇠": "key", "거울": "mirror", "꽃": "flower", "나무": "tree", "별": "star" }
        self.emotion_keywords = { "행복": "happy", "슬픔": "sad", "분노": "angry", "놀람": "surprised", "두려움": "scared", "기쁨": "joyful" }
        
        self.all_keywords = []
        for cat_dict in [self.character_keywords, self.location_keywords, self.object_keywords, self.emotion_keywords]:
            for kor, eng in cat_dict.items():
                self.all_keywords.append(kor)
        self.all_keywords.sort(key=len, reverse=True)

    def get_entity_type(self, keyword):
        if keyword in self.character_keywords: return "characters"
        if keyword in self.location_keywords: return "locations"
        if keyword in self.object_keywords: return "objects"
        if keyword in self.emotion_keywords: return "emotions"
        return None

    def extract_entities(self, text: str, allowed_keywords: Optional[List[str]] = None) -> Dict[str, List[str]]:
        entities = {"characters": [], "locations": [], "objects": [], "emotions": []}
        search_list = allowed_keywords if allowed_keywords is not None else self.all_keywords
        
        # 선택된 키워드도 긴 단어 우선으로 정렬
        search_list.sort(key=len, reverse=True)

        processed_text = text
        for keyword in search_list:
            if keyword in processed_text:
                entity_type = self.get_entity_type(keyword)
                if entity_type and keyword not in entities[entity_type]:
                    entities[entity_type].append(keyword)
                processed_text = processed_text.replace(keyword, " " * len(keyword))
        return entities

# ================== 프롬프트 생성기 ==================
class PromptGenerator:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    def create_dynamic_prompt(self, user_prompt: str, entities: Dict[str, List[str]], drawing_style: int, is_ending: bool) -> str:
        prompt_parts = [f"A scene from a story: {user_prompt}", DRAWING_STYLES[drawing_style]]
        
        if entities["characters"]:
            english_chars = [self.entity_manager.character_keywords.get(k, k) for k in entities["characters"]]
            prompt_parts.append(f"Featuring: {', '.join(english_chars)}, {random.choice(EXPRESSION_VARIATIONS)}, {random.choice(POSE_VARIATIONS)}")
        
        if entities["locations"]:
            english_locs = [self.entity_manager.location_keywords.get(k, k) for k in entities["locations"]]
            prompt_parts.append(f"Setting: {', '.join(english_locs)}, {random.choice(list(TIME_OF_DAY_LIGHTING.values()))}")

        if entities["objects"]:
            english_objs = [self.entity_manager.object_keywords.get(k, k) for k in entities["objects"]]
            prompt_parts.append(f"With important object: {', '.join(english_objs)}")
        
        prompt_parts.append(random.choice(COMPOSITION_VARIATIONS))
        if is_ending:
            prompt_parts.append("epic finale scene, dramatic lighting, emotional climax")
        prompt_parts.extend(["high quality, detailed illustration, vibrant colors", "safe for work, no text, no watermark"])
        
        final_prompt = ", ".join(prompt_parts)
        logger.info(f"Generated prompt: {final_prompt[:120]}...")
        return final_prompt

# ================== 이미지 생성 서비스 ==================
class ImageGenerationService:
    def __init__(self):
        self.entity_manager = EntityManager()
        self.prompt_generator = PromptGenerator(self.entity_manager)
    
    async def generate_image_with_gemini(self, prompt: str, reference_image: Optional[bytes] = None) -> bytes:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key={GEMINI_API_KEY}"
        parts = []
        if reference_image:
            ref_base64 = base64.b64encode(reference_image).decode('utf-8')
            parts.append({"inlineData": {"mimeType": "image/png", "data": ref_base64}})
            parts.append({"text": f"Based on the character in this reference image, generate a new scene: {prompt}. Focus on the scene described by the text. Keep the exact same character appearance, only change the scene, pose, and expression."})
        else:
            parts.append({"text": f"{prompt}"})
        
        payload = {"contents": [{"parts": parts}]}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload, timeout=40)
            if response.status_code != 200:
                logger.error(f"Gemini API Error: {response.status_code} {response.text}")
                raise Exception(f"Gemini API Error: {response.status_code}")
            
            result = response.json()
            if 'candidates' in result and result['candidates'][0].get('content', {}).get('parts', []):
                image_data = base64.b64decode(result['candidates'][0]['content']['parts'][0]['inlineData']['data'])
                return image_data
            raise Exception("No image data in Gemini response")

    async def generate_scene_image(self, user_prompt: str, selected_keywords: Optional[List[str]], drawing_style: int, is_ending: bool, game_id: str, turn: int) -> bytes:
        logger.info(f"=== v2.3 Scene Request: game_id={game_id}, turn={turn}, selected_keywords={selected_keywords}")
        logger.info(f"Original User Prompt: [{user_prompt}]")

        context = game_contexts.setdefault(game_id, {"mentioned_characters": [], "last_character": None, "turn": 0})
        
        # 1. 사용자 의도 파악: 원본 문장에서 허용된(선택된) 키워드만으로 엔티티 추출
        current_turn_entities = self.entity_manager.extract_entities(user_prompt, allowed_keywords=selected_keywords)
        logger.info(f"-> ENTITIES FROM USER INTENT: {current_turn_entities}")

        # 2. 대명사 치환
        contextual_prompt = user_prompt
        if context["turn"] > 0 and context["last_character"]:
            temp_prompt = contextual_prompt.replace("그는", context["last_character"]).replace("그녀는", context["last_character"])
            if temp_prompt != contextual_prompt:
                logger.info(f"-> PRONOUNS REPLACED: [{temp_prompt}]")
                contextual_prompt = temp_prompt

        # 3. AI 프롬프트용 최종 엔티티 목록 구성
        prompt_entities = {k: v[:] for k, v in current_turn_entities.items()}
        if context["turn"] > 0 and context["last_character"] and not prompt_entities["characters"]:
            logger.info(f"-> CONTEXT INJECTION: Adding '{context['last_character']}' to prompt entities.")
            prompt_entities["characters"].append(context["last_character"])

        # 4. 동적 프롬프트 생성
        dynamic_prompt = self.prompt_generator.create_dynamic_prompt(contextual_prompt, prompt_entities, drawing_style, is_ending)

        # 5. 문맥 업데이트 (사용자 의도 기준)
        context["turn"] += 1
        if current_turn_entities["characters"]:
            last_char = current_turn_entities["characters"][-1]
            context["last_character"] = last_char
            if last_char not in context["mentioned_characters"]:
                 context["mentioned_characters"].append(last_char)

        # 6. 레퍼런스 이미지 찾기
        reference_image = None
        if prompt_entities["characters"]:
            char_en = self.entity_manager.character_keywords.get(prompt_entities["characters"][0])
            if char_en and char_en in character_references.get(game_id, {}):
                reference_image = character_references[game_id][char_en]
                logger.info(f"-> Using reference image for '{char_en}'")

        # 7. 이미지 생성
        image_data = await self.generate_image_with_gemini(dynamic_prompt, reference_image)

        # 8. 새 레퍼런스 저장
        if current_turn_entities["characters"]:
            char_kr = current_turn_entities["characters"][0]
            char_en = self.entity_manager.character_keywords.get(char_kr)
            if char_en and char_en not in character_references.get(game_id, {}):
                character_references.setdefault(game_id, {})[char_en] = image_data
                logger.info(f"-> New reference saved for '{char_en}'")
        
        logger.info("-> Scene generation complete.")
        return image_data

# ================== API 모델 및 엔드포인트 ==================
class SceneGenerationRequest(BaseModel):
    gameId: str
    userId: str
    userPrompt: str
    turn: int
    selectedKeywords: Optional[List[str]] = None
    drawingStyle: int = 0
    isEnding: bool = False

@app.post("/generate-scene")
async def generate_scene_endpoint(request: SceneGenerationRequest):
    try:
        return Response(await image_service.generate_scene_image(
            user_prompt=request.userPrompt,
            selected_keywords=request.selectedKeywords,
            drawing_style=request.drawingStyle,
            is_ending=request.isEnding,
            game_id=request.gameId,
            turn=request.turn
        ), media_type="image/png")
    except Exception as e:
        logger.error(f"API Error in /generate-scene: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/game/{game_id}")
async def cleanup_game_endpoint(game_id: str):
    cleaned_messages = []
    if game_id in character_references:
        cleaned_messages.append(f"Cleaned {len(character_references.pop(game_id))} char references.")
    if game_id in game_contexts:
        cleaned_messages.append("Cleaned game context.")
    
    if cleaned_messages:
        message = f"Game {game_id} cleanup: {' '.join(cleaned_messages)}"
        logger.info(f"🗑️ {message}")
        return {"message": message}
    return {"message": f"No data for game {game_id}."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8190)
