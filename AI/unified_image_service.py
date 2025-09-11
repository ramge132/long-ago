#!/usr/bin/env python3
"""
Long Ago - 통합 이미지 생성 서비스 v4.0 (Image-to-Image 강화 버전)
- 캐릭터 일관성을 위한 Image-to-Image 방식 적용
- GPT-5-nano를 통한 동적 캐릭터 인식
- 캐릭터별 레퍼런스 이미지 관리 강화
"""
import os
import asyncio
import base64
import logging
import json
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field

import uvicorn
import httpx
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from PIL import Image
import io

# ================== 프롬프트 설정 ==================
# 컨텍스트 기반 프롬프트 템플릿
CONTEXTUAL_PROMPT_TEMPLATE = "Please review the entire previous story to understand the context and generate an image for the current scene. Previous Story: {previous_story}, Current Scene: {current_scene}"

# 기본 프롬프트 설정
PROMPT_SUFFIX = "high quality, detailed illustration, consistent character appearance"

# 그림 스타일 (9가지 모드)
DRAWING_STYLES = [
    "anime style, vibrant colors",           # 0: 기본
    "3D rendered style, volumetric lighting", # 1: 3D
    "comic strip style, speech bubbles",      # 2: 코믹북
    "clay animation style, stop motion",      # 3: 클레이
    "crayon drawing, childlike art",          # 4: 유치원
    "pixel art, 8-bit retro game",           # 5: 픽셀
    "PS1 polygon style, low poly 3D",        # 6: PS1
    "watercolor storybook illustration",      # 7: 동화책
    "modern digital art illustration"         # 8: 일러스트
]

# 카메라 앵글 변화 (제거 - 일관성을 위해)
# COMPOSITION_VARIATIONS = ["medium shot", "wide shot", "dramatic close-up", "low angle shot"]

# ================== 기본 설정 ==================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # GPT-5-nano용

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="Unified Image Generation Service v4.0", 
    version="4.0.0",
    description="Image-to-Image 방식을 활용한 캐릭터 일관성 강화 버전"
)

# ================== 데이터 클래스 ==================
@dataclass
class CharacterInfo:
    """캐릭터 정보 저장용 클래스"""
    name: str
    first_appearance_turn: int
    reference_image: bytes
    description: str = ""
    appearance_count: int = 1

@dataclass
class GameContext:
    """게임별 컨텍스트 관리 클래스"""
    story_history: List[str] = field(default_factory=list)
    characters: Dict[str, CharacterInfo] = field(default_factory=dict)
    last_mentioned_character: Optional[str] = None
    last_mentioned_object: Optional[str] = None  # 사물 대명사 처리용
    total_turns: int = 0

# 전역 게임 컨텍스트 저장소
game_contexts: Dict[str, GameContext] = {}

# ================== 엔티티 추출기 (하드코딩) ==================
class EntityExtractor:
    """init_db.sql 기반 하드코딩된 엔티티 추출"""
    
    def __init__(self):
        # init_db.sql에서 추출한 인물 카드 (17개)
        self.characters = {
            '호랑이', '유령', '농부', '상인', '신', '외계인', '박사', 
            '아이돌', '마법사', '마왕', '소년', '소녀', '부자', '탐정', 
            '노인', '가난뱅이', '공주', '닌자'
        }
        
        # init_db.sql에서 추출한 사물 카드 (20개)
        self.objects = {
            '핸드폰', '마차', '인형', '부적', '지도', '가면', '칼', 
            '피리', '지팡이', '태양', '날개', '의자', '시계', '도장', 
            '보석', 'UFO', '덫', '총', '타임머신', '감자'
        }
        
    def extract_entities(self, text: str, selected_keywords: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """
        텍스트에서 캐릭터와 사물 추출
        Returns: {"characters": [...], "objects": [...]}
        """
        found_entities = {
            "characters": [],
            "objects": []
        }
        
        # selectedKeywords에서 먼저 확인
        if selected_keywords:
            for keyword in selected_keywords:
                if keyword in self.characters:
                    found_entities["characters"].append(keyword)
                elif keyword in self.objects:
                    found_entities["objects"].append(keyword)
        
        # userPrompt에서도 확인 (추가로)
        for character in self.characters:
            if character in text and character not in found_entities["characters"]:
                found_entities["characters"].append(character)
                
        for obj in self.objects:
            if obj in text and obj not in found_entities["objects"]:
                found_entities["objects"].append(obj)
        
        return found_entities

# ================== 이미지 생성 서비스 ==================
class ImageGenerationService:
    def __init__(self):
        self.entity_extractor = EntityExtractor()
        
    async def _call_gemini_api(
        self, 
        prompt: str, 
        reference_image: Optional[bytes] = None,
        retry_count: int = 3
    ) -> bytes:
        """
        Gemini API 호출 (Text-to-Image 또는 Image-to-Image)
        
        Args:
            prompt: 생성할 이미지의 텍스트 프롬프트
            reference_image: 참조 이미지 (Image-to-Image용)
            retry_count: 재시도 횟수
        """
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key={GEMINI_API_KEY}"
        
        # parts 구성 (Image-to-Image인 경우 이미지를 먼저 추가)
        parts = []
        
        if reference_image:
            # Image-to-Image: 레퍼런스 이미지를 먼저 추가 (Gemini 문서 권장사항)
            logger.info("Using Image-to-Image mode with reference image")
            parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": base64.b64encode(reference_image).decode()
                }
            })
            # 프롬프트 수정: 캐릭터 일관성을 위한 강화된 지시
            enhanced_prompt = (
                f"Using the provided image of the character, create a new scene where {prompt}. "
                f"Keep the character's face, hair, clothing style, and all physical features exactly the same as shown in the reference image. "
                f"The character should be recognizable as the same person from the reference."
            )
            parts.append({"text": enhanced_prompt})
        else:
            # Text-to-Image: 프롬프트만 추가
            logger.info("Using Text-to-Image mode")
            parts.append({"text": prompt})
        
        # API 요청
        async with httpx.AsyncClient() as client:
            for attempt in range(retry_count):
                try:
                    response = await client.post(
                        api_url,
                        json={
                            "contents": [{
                                "parts": parts
                            }],
                            "safetySettings": [
                                {
                                    "category": "HARM_CATEGORY_HATE_SPEECH",
                                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                                },
                                {
                                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                                },
                                {
                                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                                },
                                {
                                    "category": "HARM_CATEGORY_HARASSMENT",
                                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                                }
                            ]
                        },
                        timeout=40.0
                    )
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    # 응답 검증
                    if 'candidates' not in result or not result['candidates']:
                        raise Exception("No candidates in response")
                    
                    candidate = result['candidates'][0]
                    if 'content' not in candidate or 'parts' not in candidate['content']:
                        raise Exception("Invalid response structure")
                    
                    response_parts = candidate['content']['parts']
                    # inline_data 또는 inlineData 둘 다 처리 (API 응답 형식 변화 대응)
                    image_part = None
                    for part in response_parts:
                        if 'inline_data' in part:
                            image_part = part['inline_data']
                            break
                        elif 'inlineData' in part:
                            image_part = part['inlineData']
                            break
                    
                    if not image_part:
                        raise Exception("No image data in response")
                    
                    # Base64 디코딩
                    image_data = base64.b64decode(image_part['data'])
                    logger.info(f"Successfully generated image (size: {len(image_data)} bytes)")
                    return image_data
                    
                except httpx.HTTPStatusError as e:
                    logger.error(f"Gemini API HTTP error (attempt {attempt + 1}/{retry_count}): {e}")
                    if attempt == retry_count - 1:
                        raise HTTPException(status_code=503, detail="Image generation failed due to content policy")
                        
                except Exception as e:
                    logger.error(f"Gemini API error (attempt {attempt + 1}/{retry_count}): {e}")
                    if attempt == retry_count - 1:
                        raise
                    
                # 재시도 전 대기
                await asyncio.sleep(2 ** attempt)
        
        raise HTTPException(status_code=500, detail="Failed to generate image after all retries")
    
    def _resolve_references(
        self, 
        text: str, 
        context: GameContext
    ) -> str:
        """
        대명사나 지시어를 실제 엔티티 이름으로 변환
        예: "그녀는" -> "공주는", "그것은" -> "칼은"
        """
        resolved_text = text
        
        # 캐릭터 대명사 처리
        if context.last_mentioned_character:
            character_pronouns = {
                "그는": context.last_mentioned_character + "는",
                "그가": context.last_mentioned_character + "가",
                "그를": context.last_mentioned_character + "를",
                "그의": context.last_mentioned_character + "의",
                "그녀는": context.last_mentioned_character + "는",
                "그녀가": context.last_mentioned_character + "가",
                "그녀를": context.last_mentioned_character + "를",
                "그녀의": context.last_mentioned_character + "의",
                "그들은": context.last_mentioned_character + "들은",
                "그들이": context.last_mentioned_character + "들이",
                "그들을": context.last_mentioned_character + "들을",
                "그들의": context.last_mentioned_character + "들의",
            }
            
            for pronoun, replacement in character_pronouns.items():
                if pronoun in text:
                    resolved_text = resolved_text.replace(pronoun, replacement)
                    logger.info(f"Character pronoun resolved: '{pronoun}' -> '{replacement}'")
        
        # 사물 대명사 처리
        if context.last_mentioned_object:
            object_pronouns = {
                # 단수
                "그것은": context.last_mentioned_object + "은",
                "그것이": context.last_mentioned_object + "이",
                "그것을": context.last_mentioned_object + "을",
                "그것의": context.last_mentioned_object + "의",
                "이것은": context.last_mentioned_object + "은",
                "이것이": context.last_mentioned_object + "이",
                "이것을": context.last_mentioned_object + "을",
                "이것의": context.last_mentioned_object + "의",
                "저것은": context.last_mentioned_object + "은",
                "저것이": context.last_mentioned_object + "이",
                "저것을": context.last_mentioned_object + "을",
                "저것의": context.last_mentioned_object + "의",
                "이건": context.last_mentioned_object + "은",
                "이게": context.last_mentioned_object + "가",
                "그건": context.last_mentioned_object + "은",
                "그게": context.last_mentioned_object + "가",
                "저건": context.last_mentioned_object + "은",
                "저게": context.last_mentioned_object + "가",
                # 복수
                "그것들은": context.last_mentioned_object + "들은",
                "그것들이": context.last_mentioned_object + "들이",
                "그것들을": context.last_mentioned_object + "들을",
                "그것들의": context.last_mentioned_object + "들의",
                "이것들은": context.last_mentioned_object + "들은",
                "이것들이": context.last_mentioned_object + "들이",
                "이것들을": context.last_mentioned_object + "들을",
                "이것들의": context.last_mentioned_object + "들의",
                "저것들은": context.last_mentioned_object + "들은",
                "저것들이": context.last_mentioned_object + "들이",
                "저것들을": context.last_mentioned_object + "들을",
                "저것들의": context.last_mentioned_object + "들의",
            }
            
            for pronoun, replacement in object_pronouns.items():
                if pronoun in text:
                    resolved_text = resolved_text.replace(pronoun, replacement)
                    logger.info(f"Object pronoun resolved: '{pronoun}' -> '{replacement}'")
                
        return resolved_text
    
    async def generate_scene(
        self,
        gameId: str,
        userId: str,
        userPrompt: str,
        turn: int,
        selectedKeywords: Optional[List[str]],
        drawingStyle: int,
        isEnding: bool
    ) -> bytes:
        """
        장면 이미지 생성 메인 메소드
        """
        logger.info(f"=== Scene Generation Request ===")
        logger.info(f"Game: {gameId}, Turn: {turn}, Ending: {isEnding}")
        logger.info(f"Prompt: {userPrompt}")
        logger.info(f"Style: {drawingStyle}, Keywords: {selectedKeywords}")
        
        # 게임 컨텍스트 가져오기 또는 생성
        if gameId not in game_contexts:
            game_contexts[gameId] = GameContext()
        context = game_contexts[gameId]
        context.total_turns = turn
        
        # 이전 스토리 컨텍스트 (전체 스토리 사용)
        previous_story = " ".join(context.story_history) if context.story_history else ""
        logger.info(f"Previous story length: {len(context.story_history)} sentences")
        
        # 대명사 해결
        resolved_prompt = self._resolve_references(userPrompt, context)
        
        # 엔티티 추출 (캐릭터 & 사물)
        entities = self.entity_extractor.extract_entities(resolved_prompt, selectedKeywords)
        characters = entities.get("characters", [])
        objects = entities.get("objects", [])
        
        logger.info(f"Extracted characters: {characters}")
        logger.info(f"Extracted objects: {objects}")
        
        # 마지막 언급된 사물 업데이트
        if objects:
            context.last_mentioned_object = objects[0]
        
        # 스토리 히스토리에 추가
        context.story_history.append(resolved_prompt)
        
        # 프롬프트 생성
        if isEnding:
            # 엔딩인 경우 모든 주요 캐릭터를 포함
            main_characters = list(context.characters.keys())[:3]  # 최대 3명
            if main_characters:
                character_desc = ", ".join(main_characters)
                base_prompt = f"Final scene with {character_desc}. {resolved_prompt}"
            else:
                base_prompt = f"Final scene: {resolved_prompt}"
        else:
            base_prompt = CONTEXTUAL_PROMPT_TEMPLATE.format(
                previous_story=previous_story,
                current_scene=resolved_prompt
            )
        
        # 스타일 추가
        style = DRAWING_STYLES[drawingStyle] if 0 <= drawingStyle < len(DRAWING_STYLES) else DRAWING_STYLES[0]
        full_prompt = f"{base_prompt}, {style}, {PROMPT_SUFFIX}"
        
        # 레퍼런스 이미지 선택
        reference_image = None
        current_character = None
        
        if characters:
            # 첫 번째 캐릭터를 메인으로 사용
            current_character = characters[0]
            context.last_mentioned_character = current_character
            
            # 기존 캐릭터인지 확인
            if current_character in context.characters:
                # 기존 캐릭터: 레퍼런스 이미지 사용 (Image-to-Image)
                char_info = context.characters[current_character]
                reference_image = char_info.reference_image
                char_info.appearance_count += 1
                logger.info(f"Using reference for existing character: {current_character} (appearance #{char_info.appearance_count})")
            else:
                # 새 캐릭터: 첫 등장
                logger.info(f"New character detected: {current_character}")
        
        # 최종 프롬프트 로그 출력
        logger.info(f"=== Final Prompt to Gemini ===")
        logger.info(f"Prompt: {full_prompt[:500]}..." if len(full_prompt) > 500 else f"Prompt: {full_prompt}")
        logger.info(f"Using reference image: {reference_image is not None}")
        
        # 이미지 생성
        image_data = await self._call_gemini_api(full_prompt, reference_image)
        
        # 새 캐릭터인 경우 레퍼런스로 저장
        if current_character and current_character not in context.characters:
            context.characters[current_character] = CharacterInfo(
                name=current_character,
                first_appearance_turn=turn,
                reference_image=image_data,
                description=resolved_prompt
            )
            logger.info(f"Saved reference image for new character: {current_character}")
        
        return image_data
    
    async def _generate_cover_prompt_with_gpt(self, title: str, summary: str, characters: List[str]) -> str:
        """
        GPT-5-nano를 사용하여 표지 이미지 프롬프트 생성
        """
        if not OPENAI_API_KEY:
            # GPT API 키가 없으면 기본 프롬프트 사용
            logger.warning("OpenAI API key not found, using default cover prompt")
            if characters:
                return f"Book cover illustration for '{title}'. Featuring {', '.join(characters)}. {summary}. Epic composition, professional book cover design"
            return f"Book cover illustration for '{title}'. {summary}. Epic composition, professional book cover design"
        
        try:
            prompt = f"""
            Create a detailed image generation prompt for a book cover with:
            Title: {title}
            Summary: {summary}
            Main characters: {', '.join(characters) if characters else 'No specific characters'}
            
            Generate an artistic and compelling prompt for the book cover illustration.
            Focus on visual composition, mood, and style suitable for a storybook.
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-5-nano",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 200
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                gpt_prompt = result['choices'][0]['message']['content']
                logger.info(f"GPT-5-nano generated cover prompt: {gpt_prompt[:100]}...")
                return gpt_prompt
                
        except Exception as e:
            logger.error(f"GPT-5-nano cover prompt generation failed: {e}")
            # 폴백: 기본 프롬프트 사용
            if characters:
                return f"Book cover illustration for '{title}'. Featuring {', '.join(characters)}. {summary}. Epic composition, professional book cover design"
            return f"Book cover illustration for '{title}'. {summary}. Epic composition, professional book cover design"
    
    async def generate_book_cover(
        self,
        gameId: str,
        title: str,
        summary: str
    ) -> bytes:
        """
        책 표지 생성 (GPT-5-nano로 프롬프트 생성 + 주요 캐릭터 포함)
        """
        logger.info(f"=== Book Cover Generation ===")
        logger.info(f"Title: {title}")
        
        context = game_contexts.get(gameId)
        
        # 주요 캐릭터 정보 수집 (최대 3명)
        character_names = []
        reference_image = None
        
        if context and context.characters:
            main_characters = sorted(
                context.characters.values(),
                key=lambda x: x.appearance_count,
                reverse=True
            )[:3]
            
            character_names = [char.name for char in main_characters]
            # 가장 많이 등장한 캐릭터의 레퍼런스 사용
            reference_image = main_characters[0].reference_image if main_characters else None
        
        # GPT-5-nano로 프롬프트 생성
        prompt = await self._generate_cover_prompt_with_gpt(title, summary, character_names)
        
        # 표지 생성 (더 많은 재시도)
        return await self._call_gemini_api(prompt, reference_image, retry_count=5)

# ================== API 모델 ==================
class SceneGenerationRequest(BaseModel):
    gameId: str
    userId: str
    userPrompt: str
    turn: int
    selectedKeywords: Optional[List[str]] = None
    drawingStyle: int = 0
    isEnding: bool = False

class BookCoverRequest(BaseModel):
    gameId: str
    title: str
    summary: str

# ================== 서비스 인스턴스 ==================
image_service = ImageGenerationService()

# ================== API 엔드포인트 ==================
@app.post("/generate-scene")
async def generate_scene_endpoint(request: SceneGenerationRequest):
    """장면 이미지 생성 API"""
    try:
        logger.info(f"Received scene generation request for game {request.gameId}")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in scene generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-cover")
async def generate_cover_endpoint(request: BookCoverRequest):
    """책 표지 생성 API"""
    try:
        logger.info(f"Received cover generation request for game {request.gameId}")
        
        content = await image_service.generate_book_cover(
            gameId=request.gameId,
            title=request.title,
            summary=request.summary
        )
        
        return Response(content=content, media_type="image/png")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in cover generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/game/{game_id}")
async def cleanup_game_endpoint(game_id: str):
    """게임 종료 시 데이터 정리"""
    if game_id in game_contexts:
        context = game_contexts[game_id]
        character_count = len(context.characters)
        turn_count = context.total_turns
        
        del game_contexts[game_id]
        
        logger.info(f"🗑️ Cleaned up game {game_id} (characters: {character_count}, turns: {turn_count})")
        return {
            "message": f"Cleaned up data for game {game_id}",
            "stats": {
                "characters": character_count,
                "turns": turn_count
            }
        }
    else:
        return {"message": f"No data found for game {game_id}"}

@app.get("/game/{game_id}/context")
async def get_game_context(game_id: str):
    """게임 컨텍스트 조회 (디버깅용)"""
    if game_id not in game_contexts:
        raise HTTPException(status_code=404, detail="Game not found")
    
    context = game_contexts[game_id]
    return {
        "game_id": game_id,
        "total_turns": context.total_turns,
        "story_length": len(context.story_history),
        "characters": list(context.characters.keys()),
        "last_mentioned_character": context.last_mentioned_character
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "version": "4.0.0",
        "active_games": len(game_contexts),
        "gemini_api_configured": bool(GEMINI_API_KEY),
        "openai_api_configured": bool(OPENAI_API_KEY)
    }

# ================== 메인 실행 ==================
if __name__ == "__main__":
    # API 키 확인
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in environment variables!")
    else:
        logger.info("✅ Gemini API key configured")
    
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not found - will use fallback character detection")
    else:
        logger.info("✅ OpenAI API key configured")
    
    # 서버 시작
    logger.info("🚀 Starting Image Generation Service v4.0...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8190,
        log_level="info"
    )
