#!/usr/bin/env python3
"""
Long Ago - 통합 이미지 생성 서비스 v3.0 (최종 안정화 버전)
- 명시적 파라미터 전달 및 안정성 강화
"""
import os
import asyncio
import base64
import logging
import random
from typing import Optional, Dict, List

import uvicorn
import httpx
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from PIL import Image
import io

# ================== 프롬프트 설정 ==================
CONTEXTUAL_PROMPT_TEMPLATE = "Understand the context from the previous story and generate an image for the current scene. Previous Story: {previous_story}, Current Scene: {current_scene}"
PROMPT_SUFFIX = "high quality, detailed illustration"
DRAWING_STYLES = ["anime style, vibrant colors", "cute 3d cartoon style", "comic strip style", "storybook illustration"]
COMPOSITION_VARIATIONS = ["medium shot", "wide shot", "dramatic close-up", "low angle shot"]

# ================== 기본 설정 ==================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
character_references = {}
game_contexts = {}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI(title="Unified Image Generation Service v3.0", version="3.0.0")

# ================== 엔티티 관리 ==================
class EntityManager:
    def __init__(self):
        self.keywords = {
            'characters': {'호랑이': 'tiger', '유령': 'ghost', '농부': 'farmer', '상인': 'merchant', '신': 'god', '외계인': 'alien', '박사': 'doctor', '아이돌': 'idol', '마법사': 'wizard', '마왕': 'demon king', '소년': 'boy', '소녀': 'girl', '부자': 'rich person', '탐정': 'detective', '노인': 'old man', '가난뱅이': 'beggar', '공주': 'princess', '닌자': 'ninja'},
            'locations': {"숲": "forest", "성": "castle", "마을": "village", "바다": "ocean"},
            'objects': {'핸드폰': 'smartphone', '마차': 'carriage', '인형': 'doll', '지도': 'map', '칼': 'sword'}
        }
        self.all_keywords_sorted = sorted([k for d in self.keywords.values() for k in d], key=len, reverse=True)

    def get_entity_type(self, keyword):
        for type, kw_dict in self.keywords.items():
            if keyword in kw_dict: return type
        return None

    def extract_entities(self, text: str, allowed_keywords: Optional[List[str]] = None) -> Dict[str, List[str]]:
        entities = {"characters": [], "locations": [], "objects": []}
        search_list = allowed_keywords if allowed_keywords is not None else self.all_keywords_sorted
        processed_text = text
        for keyword in sorted(search_list, key=len, reverse=True):
            if keyword in processed_text:
                entity_type = self.get_entity_type(keyword)
                if entity_type:
                    entities[entity_type].append(keyword)
                    processed_text = processed_text.replace(keyword, " " * len(keyword), 1)
        return entities

# ================== 프롬프트 생성기 ==================
class PromptGenerator:
    def create(self, user_prompt: str, previous_story: str, drawing_style_index: int) -> str:
        base_prompt = CONTEXTUAL_PROMPT_TEMPLATE.format(previous_story=previous_story, current_scene=user_prompt)
        style_parts = [DRAWING_STYLES[drawing_style_index], random.choice(COMPOSITION_VARIATIONS), PROMPT_SUFFIX]
        return f"{base_prompt}, {', '.join(style_parts)}"

# ================== 이미지 생성 서비스 ==================
class ImageGenerationService:
    def __init__(self):
        self.entity_manager = EntityManager()
        self.prompt_generator = PromptGenerator()

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
                if result.get('candidates') and result['candidates'][0].get('content', {}).get('parts', []):
                    image_part = result['candidates'][0]['content']['parts'][0]
                    if 'inlineData' in image_part:
                        return base64.b64decode(image_part['inlineData']['data'])
                raise Exception("Image generation failed or was blocked by safety filters.")
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}")
                raise

    async def generate_scene(self, gameId: str, userId: str, userPrompt: str, turn: int, selectedKeywords: Optional[List[str]], drawingStyle: int, isEnding: bool) -> bytes:
        logger.info(f"=== v3.0 Scene Request: game_id={gameId}, turn={turn} ===")
        
        context = game_contexts.setdefault(gameId, {"story_history": [], "last_character": None})
        
        previous_story = " ".join(context["story_history"])
        
        contextual_prompt = userPrompt
        if context["last_character"]:
            if "그는" in contextual_prompt or "그녀는" in contextual_prompt:
                contextual_prompt = contextual_prompt.replace("그는", context["last_character"]).replace("그녀는", context["last_character"])
                logger.info(f"-> Pronoun replaced: [{contextual_prompt}]")
        
        dynamic_prompt = self.prompt_generator.create(contextual_prompt, previous_story, drawingStyle)

        context["story_history"].append(contextual_prompt)
        turn_entities = self.entity_manager.extract_entities(contextual_prompt, allowed_keywords=selectedKeywords)
        if turn_entities["characters"]:
            context["last_character"] = turn_entities["characters"][-1]

        ref_image = None
        current_char_kr = turn_entities.get('characters', [context.get('last_character')])[0]
        if current_char_kr:
            char_en = self.entity_manager.keywords['characters'].get(current_char_kr)
            if char_en and char_en in character_references.get(gameId, {}):
                ref_image = character_references[gameId][char_en]
                logger.info(f"-> Using reference for '{char_en}'")

        image_data = await self._generate_with_gemini(dynamic_prompt, ref_image)

        if not ref_image and turn_entities.get("characters"):
            char_en = self.entity_manager.keywords['characters'].get(turn_entities["characters"][0])
            if char_en:
                character_references.setdefault(gameId, {})[char_en] = image_data
                logger.info(f"-> New reference saved for '{char_en}'")
        
        return image_data

# ================== API 모델 및 엔드포인트 ==================
image_service = ImageGenerationService()

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
        content = await image_service.generate_scene(
            gameId=request.gameId,
            userId=request.userId,
            userPrompt=request.userPrompt,
            turn=request.turn,
            selectedKeywords=request.selectedKeywords,
            drawingStyle=request.drawingStyle,
            isEnding=request.isEnding
        )
        return Response(content=content, media_type="image/png")
    except Exception as e:
        logger.error(f"API Error in /generate-scene: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Image generation failed.")

@app.delete("/game/{game_id}")
async def cleanup_game_endpoint(game_id: str):
    character_references.pop(game_id, None)
    game_contexts.pop(game_id, None)
    logger.info(f"🗑️ Cleaned up data for game {game_id}.")
    return {"message": f"Cleaned up data for game {game_id}."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8190)
