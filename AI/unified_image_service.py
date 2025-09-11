#!/usr/bin/env python3
"""
Long Ago - 통합 이미지 생성 서비스 v2.9 (프롬프트 구성 개선)
- 사용자 의도 기반 엔티티 추출, 안정적인 상태 관리 및 오류 처리
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

# ================== 프롬프트 설정 (상단으로 이동) ==================
CONTEXTUAL_PROMPT_TEMPLATE = "Understand the context from the previous story and generate an image for the current scene. Previous Story: {previous_story}, Current Scene: {current_scene}"
PROMPT_SUFFIX = "high quality, detailed illustration"
DRAWING_STYLES = [
    "anime style, vibrant colors, detailed illustration", "cute 3d cartoon style", 
    "comic strip style", "claymation style", "crayon drawing style", "pixel art style", 
    "minimalist illustration", "watercolor painting style", "storybook illustration"
]
COMPOSITION_VARIATIONS = [
    "medium shot", "wide shot", "dramatic close-up", "over-the-shoulder perspective", 
    "bird's eye view", "low angle shot", "diagonal composition"
]
TIME_OF_DAY_LIGHTING = {
    "morning": "soft morning light", "afternoon": "bright daylight", 
    "evening": "warm sunset lighting", "night": "mysterious moonlight"
}

# ================== 기본 설정 ==================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- 상태 저장소 ---
character_references = {}
game_contexts = {}

# --- 로깅 ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Unified Image Generation Service v2.9", version="2.9.0")

# --- 엔티티 관리 ---
class EntityManager:
    def __init__(self):
        self.keywords = {
            'characters': {'호랑이': 'tiger', '유령': 'ghost', '농부': 'farmer', '상인': 'merchant', '신': 'god', '외계인': 'alien', '박사': 'doctor', '아이돌': 'idol', '마법사': 'wizard', '마왕': 'demon king', '소년': 'boy', '소녀': 'girl', '부자': 'rich person', '탐정': 'detective', '노인': 'old man', '가난뱅이': 'beggar', '공주': 'princess', '닌자': 'ninja'},
            'locations': {"숲": "forest", "성": "castle", "마을": "village", "바다": "ocean", "산": "mountain", "동굴": "cave"},
            'objects': {'핸드폰': 'smartphone', '마차': 'carriage', '인형': 'doll', '부적': 'talisman', '지도': 'map', '가면': 'mask', '칼': 'sword', '피리': 'flute', '지팡이': 'staff', '태양': 'sun', '날개': 'wings', '의자': 'chair', '시계': 'clock', '도장': 'seal', '보석': 'jewel', 'UFO': 'UFO', '덫': 'trap', '총': 'gun', '타임머신': 'time machine', '감자': 'potato'}
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
                    processed_text = processed_text.replace(keyword, " " * len(keyword))
        return entities

# --- 프롬프트 생성기 ---
class PromptGenerator:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    def create(self, user_prompt: str, previous_story: str, drawing_style_index: int, is_ending: bool) -> str:
        
        # 새로운 템플릿 적용
        final_prompt = CONTEXTUAL_PROMPT_TEMPLATE.format(
            previous_story=previous_story,
            current_scene=user_prompt
        )
        
        # 추가적인 스타일링 키워드들
        style_parts = [
            DRAWING_STYLES[drawing_style_index],
            random.choice(COMPOSITION_VARIATIONS),
            PROMPT_SUFFIX
        ]
        if is_ending:
            style_parts.append("epic finale scene")

        final_prompt_with_style = f"{final_prompt}, {', '.join(style_parts)}"
        
        logger.info(f"-> Generated Prompt: {final_prompt_with_style[:200]}...")
        return final_prompt_with_style

# --- 이미지 생성 서비스 ---
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
                if result.get('candidates') and result['candidates'][0].get('content', {}).get('parts', []):
                    image_part = result['candidates'][0]['content']['parts'][0]
                    if 'inlineData' in image_part:
                        return base64.b64decode(image_part['inlineData']['data'])
                raise Exception("Image generation failed, possibly due to safety filters.")
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}")
                raise

    async def generate_scene(self, user_prompt: str, selected_keywords: Optional[List[str]], drawing_style: int, is_ending: bool, game_id: str, turn: int) -> bytes:
        logger.info(f"=== v2.10 Scene Request: game_id={game_id}, turn={turn}, selected_keywords={selected_keywords}")
        logger.info(f"Original User Prompt: [{user_prompt}]")
        
        context = game_contexts.setdefault(game_id, {"story_history": [], "last_character": None})
        
        # 1. 이전 스토리 구성
        previous_story = " ".join(context["story_history"])
        
        # 2. 대명사 치환
        contextual_prompt = user_prompt
        if context["last_character"]:
            lc = context["last_character"]
            if "그는" in contextual_prompt or "그녀는" in contextual_prompt:
                contextual_prompt = contextual_prompt.replace("그는", lc).replace("그녀는", lc)
                logger.info(f"-> Pronoun replaced: [{contextual_prompt}]")

        # 3. 동적 프롬프트 생성 (새로운 방식)
        dynamic_prompt = self.prompt_generator.create(contextual_prompt, previous_story, drawing_style, is_ending)
        
        # 4. 문맥 업데이트
        context["story_history"].append(contextual_prompt)
        turn_entities = self.entity_manager.extract_entities(contextual_prompt, allowed_keywords=selected_keywords)
        if turn_entities["characters"]:
            context["last_character"] = turn_entities["characters"][-1]

        # 5. 레퍼런스 이미지 관리
        ref_image = None
        # 현재 씬과 이전 스토리를 모두 포함하여 캐릭터를 찾음
        all_relevant_entities = self.entity_manager.extract_entities(f"{previous_story} {contextual_prompt}")
        if all_relevant_entities["characters"]:
            char_kr = all_relevant_entities["characters"][0] # 가장 먼저 언급된 캐릭터 기준
            char_en = self.entity_manager.keywords['characters'].get(char_kr)
            if char_en:
                game_refs = character_references.get(game_id)
                if game_refs and char_en in game_refs:
                    ref_image = game_refs[char_en]
                    logger.info(f"-> Using reference image for '{char_en}'")
        
        image_data = await self._generate_with_gemini(dynamic_prompt, ref_image)
        
        # 6. 새로운 캐릭터 레퍼런스 저장 (이번 턴에 처음 등장한 경우)
        if not ref_image and turn_entities["characters"]:
            char_kr = prompt_entities["characters"][0]
            char_en = self.entity_manager.keywords['characters'].get(char_kr)
            if char_en:
                game_refs = character_references.get(game_id)
                if game_refs and char_en in game_refs:
                    ref_image = game_refs[char_en]
                    logger.info(f"-> Using reference image for '{char_en}'")
        
        image_data = await self._generate_with_gemini(dynamic_prompt, ref_image)

        if not ref_image and turn_entities["characters"]:
            char_kr = turn_entities["characters"][0]
            char_en = self.entity_manager.keywords['characters'].get(char_kr)
            if char_en:
                character_references.setdefault(game_id, {})[char_en] = image_data
                logger.info(f"-> New reference saved for '{char_en}'")
        
        logger.info("-> Scene generation complete.")
        return image_data

    async def generate_book_cover(self, story_content: str, drawing_style: int) -> tuple[str, bytes]:
        """
        책 표지 생성 (GPT-5-nano로 제목 생성)
        """
        try:
            title = await self._generate_title_with_gpt5(story_content)
            logger.info(f"📚 GPT-5로 생성된 책 제목: [{title}]")
            
            cover_prompt = f"book cover illustration, title '{title}', {DRAWING_STYLES[drawing_style]}, epic, centered composition"
            
            image_data = await self._generate_with_gemini(cover_prompt)
            logger.info(f"🎨 표지 이미지 생성 완료: {len(image_data)} bytes")
            
            return title, image_data
            
        except Exception as e:
            logger.error(f"표지 생성 실패: {e}")
            title = self._generate_simple_title(story_content)
            img = io.BytesIO()
            Image.new('RGB', (512, 512), 'white').save(img, 'PNG')
            return title, img.getvalue()

    async def _generate_title_with_gpt5(self, story: str) -> str:
        """
        GPT-5-nano를 사용한 책 제목 생성
        """
        if not OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY가 설정되지 않음. 기본 제목 생성으로 폴백")
            return self._generate_simple_title(story)
        
        try:
            story_summary = story[:500] if len(story) > 500 else story
            
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-5-nano",
                "input": f"다음 이야기의 창의적이고 흥미로운 한국어 제목을 10자 이내로 만들어주세요. 제목만 답하세요: {story_summary}",
                "text": {"verbosity": "low"}, "reasoning": {"effort": "minimal"}
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post("https://api.openai.com/v1/responses", headers=headers, json=payload, timeout=15)
                response.raise_for_status()
                result = response.json()
                
                title = result.get("output_text", "").strip() or result.get("output", [{}])[0].get("text", "").strip()
                if title:
                    return title[:15]
            
            logger.warning("GPT-5 응답에서 제목을 찾을 수 없음")
            return self._generate_simple_title(story)
                
        except Exception as e:
            logger.error(f"GPT-5 제목 생성 실패: {e}")
            return self._generate_simple_title(story)

    def _generate_simple_title(self, story: str) -> str:
        """간단한 제목 생성"""
        entities = self.entity_manager.extract_entities(story)
        
        if entities["characters"]:
            first_char_kr = entities["characters"][0]
            if "공주" in first_char_kr: return "공주의 모험"
            if "왕자" in first_char_kr: return "왕자의 여정"
            return f"{first_char_kr}의 이야기"
            
        if entities["locations"]:
            return f"{entities['locations'][0]}에서 생긴 일"
            
        return "아주 먼 옛날 이야기"


# ================== API 모델 및 엔드포인트 ==================
image_service = ImageGenerationService()

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
        content = await image_service.generate_scene(**request.model_dump())
        return Response(content=content, media_type="image/png")
    except Exception as e:
        logger.error(f"API Error in /generate-scene: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Image generation failed.")

class BookCoverGenerationRequest(BaseModel):
    storyContent: str
    gameId: str
    drawingStyle: int = 0

@app.post("/generate-cover")
async def generate_cover_endpoint(request: BookCoverGenerationRequest):
    """책 표지 생성 API"""
    try:
        title, image_data = await image_service.generate_book_cover(
            story_content=request.storyContent,
            drawing_style=request.drawingStyle
        )
        return {
            "title": title,
            "image_data": base64.b64encode(image_data).decode('utf-8')
        }
    except Exception as e:
        logger.error(f"API Error in /generate-cover: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Cover generation failed.")

@app.delete("/game/{game_id}")
async def cleanup_game_endpoint(game_id: str):
    cleaned = character_references.pop(game_id, None) or game_contexts.pop(game_id, None)
    message = f"Cleaned up data for game {game_id}." if cleaned else "No data to clean."
    logger.info(f"🗑️ {message}")
    return {"message": message}

if __name__ == "__main__":
    logger.info("Starting Long Ago Image Service v2.9")
    uvicorn.run(app, host="0.0.0.0", port=8190)
