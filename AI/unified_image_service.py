#!/usr/bin/env python3
"""
Long Ago - 통합 이미지 생성 서비스 v2.4
- 사용자 의도 기반 엔티티 추출 및 문맥 보강 로직
"""
import os
import sys
import asyncio
import base64
import logging
import io
import random
from typing import Optional, Dict, List

import uvicorn
import httpx
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

# 환경변수 설정 및 기본 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DRAWING_STYLES = [
    "anime style, vibrant colors, detailed illustration",
    "cute 3d cartoon style", "comic strip style", "claymation style", 
    "crayon drawing style", "pixel art style", "minimalist illustration",
    "watercolor painting style", "storybook illustration"
]

# 게임별 상태 저장소
character_references = {}
game_contexts = {}

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(title="Unified Image Generation Service v2.4", version="2.4.0")

# ================== 엔티티 관리 시스템 ==================
class EntityManager:
    def __init__(self):
        self.keywords = {
            'characters': {'호랑이': 'tiger', '유령': 'ghost', '농부': 'farmer', '상인': 'merchant', '신': 'god', '외계인': 'alien', '박사': 'doctor', '아이돌': 'idol', '마법사': 'wizard', '마왕': 'demon king', '소년': 'boy', '소녀': 'girl', '부자': 'rich person', '탐정': 'detective', '노인': 'old man', '가난뱅이': 'beggar', '공주': 'princess', '닌자': 'ninja'},
            'locations': {"숲": "forest", "성": "castle", "마을": "village", "바다": "ocean", "산": "mountain", "동굴": "cave"},
            'objects': {'핸드폰': 'smartphone', '마차': 'carriage', '인형': 'doll', '부적': 'talisman', '지도': 'map', '가면': 'mask', '칼': 'sword', '피리': 'flute', '지팡이': 'staff', '태양': 'sun', '날개': 'wings', '의자': 'chair', '시계': 'clock', '도장': 'seal', '보석': 'jewel', 'UFO': 'UFO', '덫': 'trap', '총': 'gun', '타임머신': 'time machine', '감자': 'potato'}
        }
        self.all_keywords_sorted = sorted(self.keywords['characters'].keys() | self.keywords['locations'].keys() | self.keywords['objects'].keys(), key=len, reverse=True)

    def get_entity_type(self, keyword):
        for type, kw_dict in self.keywords.items():
            if keyword in kw_dict:
                return type
        return None

    def extract_entities(self, text: str, allowed_keywords: Optional[List[str]] = None) -> Dict[str, List[str]]:
        entities = {"characters": [], "locations": [], "objects": []}
        search_list = allowed_keywords if allowed_keywords is not None else self.all_keywords_sorted
        search_list.sort(key=len, reverse=True)

        processed_text = text
        for keyword in search_list:
            if keyword in processed_text:
                entity_type = self.get_entity_type(keyword)
                if entity_type:
                    entities[entity_type].append(keyword)
                    processed_text = processed_text.replace(keyword, " " * len(keyword))
        return entities

# ================== 프롬프트 생성기 ==================
class PromptGenerator:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    def create(self, user_prompt: str, entities: Dict[str, List[str]], drawing_style: int, is_ending: bool) -> str:
        prompt_parts = [f"A scene from a story: {user_prompt}", DRAWING_STYLES[drawing_style]]
        
        def append_prompt_part(entity_type, prefix):
            if entities.get(entity_type): # .get()으로 안전하게 접근
                kw_dict = self.entity_manager.keywords.get(entity_type, {})
                english_list = [kw_dict.get(k, k) for k in entities[entity_type] if k in kw_dict]
                if english_list:
                    prompt_parts.append(f"{prefix}: {', '.join(english_list)}")

        append_prompt_part("characters", "Featuring")
        append_prompt_part("locations", "Setting")
        append_prompt_part("objects", "With important object")
        
        if is_ending: prompt_parts.append("epic finale scene")
        prompt_parts.extend(["high quality, detailed illustration", "no text, no watermark"])
        
        final_prompt = ", ".join(prompt_parts)
        logger.info(f"-> Generated Prompt: {final_prompt[:120]}...")
        return final_prompt

# ================== 이미지 생성 서비스 ==================
class ImageGenerationService:
    def __init__(self):
        self.entity_manager = EntityManager()
        self.prompt_generator = PromptGenerator(self.entity_manager)
    
    async def _generate_with_gemini(self, prompt: str, ref_image: Optional[bytes] = None) -> bytes:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key={GEMINI_API_KEY}"
        parts = [{"text": prompt}]
        if ref_image:
            parts.insert(0, {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(ref_image).decode()}})
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(api_url, json={"contents": [{"parts": parts}]}, timeout=40)
                response.raise_for_status()
                result = response.json()
                if result.get('candidates'):
                    return base64.b64decode(result['candidates'][0]['content']['parts'][0]['inlineData']['data'])
                raise Exception("No image data in Gemini response")
            except (httpx.HTTPStatusError, Exception) as e:
                logger.error(f"Gemini API call failed: {e}")
                raise

    async def generate_scene(self, user_prompt: str, selected_keywords: Optional[List[str]], drawing_style: int, is_ending: bool, game_id: str, turn: int) -> bytes:
        logger.info(f"=== v2.4 Scene Request: game_id={game_id}, turn={turn}, selected_keywords={selected_keywords}")
        logger.info(f"Original User Prompt: [{user_prompt}]")

        context = game_contexts.setdefault(game_id, {"last_character": None, "turn": 0})
        
        # 1. 사용자 의도 파악
        turn_entities = self.entity_manager.extract_entities(user_prompt, allowed_keywords=selected_keywords)
        logger.info(f"-> Entities from user intent: {turn_entities}")

        # 2. AI 프롬프트용 최종 엔티티 구성
        prompt_entities = {k: v[:] for k, v in turn_entities.items()}
        if context["last_character"] and not prompt_entities["characters"]:
            logger.info(f"-> Context Injection: Adding '{context['last_character']}' to prompt entities.")
            prompt_entities["characters"].append(context["last_character"])

        # 3. 동적 프롬프트 생성
        dynamic_prompt = self.prompt_generator.create(user_prompt, prompt_entities, drawing_style, is_ending)

        # 4. 문맥 업데이트
        context["turn"] += 1
        if turn_entities["characters"]:
            context["last_character"] = turn_entities["characters"][-1]

        # 5. 레퍼런스 이미지 찾기 및 생성
        ref_image = None
        if prompt_entities["characters"]:
            char_en = self.entity_manager.keywords['characters'].get(prompt_entities["characters"][0])
            if char_en and char_en in character_references.get(game_id, {}):
                ref_image = character_references[game_id][char_en]
                logger.info(f"-> Using reference image for '{char_en}'")

        image_data = await self._generate_with_gemini(dynamic_prompt, ref_image)

        # 6. 새 레퍼런스 저장
        if turn_entities["characters"]:
            char_en = self.entity_manager.keywords['characters'].get(turn_entities["characters"][0])
            if char_en and char_en not in character_references.get(game_id, {}):
                character_references.setdefault(game_id, {})[char_en] = image_data
                logger.info(f"-> New reference saved for '{char_en}'")
        
        logger.info("-> Scene generation complete.")
        return image_data

# ================== API 모델 및 엔드포인트 ==================
image_service = ImageGenerationService()  # 서비스 객체 생성

class SceneGenerationRequest(BaseModel):
    gameId: str
    userPrompt: str
    turn: int
    selectedKeywords: Optional[List[str]] = None
    drawingStyle: int = 0
    isEnding: bool = False

@app.post("/generate-scene")
async def generate_scene_endpoint(request: SceneGenerationRequest):
    try:
        return Response(await image_service.generate_scene(
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
    cleaned_count = 0
    if game_id in character_references:
        cleaned_count += len(character_references.pop(game_id))
    if game_id in game_contexts:
        cleaned_count += 1
        game_contexts.pop(game_id)
    
    if cleaned_count > 0:
        message = f"Cleaned up data for game {game_id}."
        logger.info(f"🗑️ {message}")
        return {"message": message}
    return {"message": f"No data to clean for game {game_id}."}

if __name__ == "__main__":
    logger.info("Starting Long Ago Image Service v2.4")
    uvicorn.run(app, host="0.0.0.0", port=8190)
