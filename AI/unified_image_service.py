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
import random
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

# 기본 프롬프트 설정 (텍스트 제외 명시)
PROMPT_SUFFIX = "high quality, detailed illustration, consistent character appearance, NO TEXT, no letters, no words, no writing, no speech bubbles, no captions, no titles, no labels, textless image only"

# 그림 스타일 (9가지 모드) - 텍스트 관련 요소 제거
DRAWING_STYLES = [
    "anime style, vibrant colors",           # 0: 기본
    "3D rendered style, volumetric lighting", # 1: 3D
    "comic strip style, visual storytelling only",  # 2: 코믹북 (speech bubbles 제거)
    "clay animation style, stop motion",      # 3: 클레이
    "crayon drawing, childlike art",          # 4: 유치원
    "pixel art, 8-bit retro game",           # 5: 픽셀
    "PS1 polygon style, low poly 3D",        # 6: PS1
    "watercolor storybook illustration",      # 7: 동화책
    "modern digital art illustration"         # 8: 일러스트
]

# 삭제 - 자연스러운 맥락 기반 프롬프팅으로 변경

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
    visual_description: str = ""  # 캐릭터의 시각적 특징 저장

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
        self.character_prompts = self._load_character_prompts()
    
    def _load_character_prompts(self) -> Dict[str, str]:
        """
        캐릭터별 프롬프트 파일 로드
        AI/imageGeneration/characters/ 디렉토리에서 .txt 파일 읽기
        """
        # 한글 캐릭터명을 영어 파일명으로 매핑
        character_file_mapping = {
            '호랑이': 'tiger',  # tiger.txt 파일이 없을 경우 기본값 사용
            '유령': 'ghost',
            '농부': 'farmer',
            '상인': 'merchant',
            '신': 'god',
            '외계인': 'alien',
            '박사': 'doctor',
            '아이돌': 'idol',
            '마법사': 'wizard',
            '마왕': 'demon',
            '소년': 'boy',
            '소녀': 'girl',
            '부자': 'rich',
            '탐정': 'detective',
            '노인': 'oldman',
            '가난뱅이': 'beggar',
            '공주': 'princess',
            '닌자': 'ninja'
        }
        
        prompts = {}
        base_path = "AI/imageGeneration/characters"
        
        for korean_name, english_file in character_file_mapping.items():
            file_path = f"{base_path}/{english_file}.txt"
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    prompt = f.read().strip()
                    prompts[korean_name] = prompt
                    logger.info(f"Loaded prompt for {korean_name} from {file_path}")
            except FileNotFoundError:
                # 파일이 없는 경우 기본값 사용
                default_prompts = {
                    '호랑이': 'orange striped tiger with fierce eyes',
                    '유령': 'translucent white ghost with flowing form',
                    '마왕': 'demon lord with dark armor and horns',
                    '신': 'divine being with golden aura and majestic appearance'
                }
                prompts[korean_name] = default_prompts.get(korean_name, f"{korean_name} character")
                logger.warning(f"File not found: {file_path}, using default prompt")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                prompts[korean_name] = f"{korean_name} character"
        
        return prompts
    
    def _generate_visual_description(self, character_name: str, context: str) -> str:
        """
        캐릭터별 프롬프트 파일에서 시각적 설명 가져오기
        """
        return self.character_prompts.get(character_name, f"{character_name} character")
        
    async def _call_gemini_api(
        self, 
        prompt: str, 
        reference_images: Optional[Dict[str, bytes]] = None,
        retry_count: int = 3
    ) -> bytes:
        """
        Gemini API 호출 (Text-to-Image 또는 Multi-Image-to-Image)
        
        Args:
            prompt: 생성할 이미지의 텍스트 프롬프트
            reference_images: 캐릭터별 참조 이미지 딕셔너리 {캐릭터명: 이미지}
            retry_count: 재시도 횟수
        """
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key={GEMINI_API_KEY}"
        
        # parts 구성
        parts = []
        
        if reference_images:
            # Multi-Image-to-Image: 모든 레퍼런스 이미지를 추가
            logger.info(f"Using Multi-Image-to-Image mode with {len(reference_images)} reference images")
            
            # 각 캐릭터의 레퍼런스 이미지 추가
            character_descriptions = []
            for idx, (char_name, ref_image) in enumerate(reference_images.items()):
                parts.append({
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": base64.b64encode(ref_image).decode()
                    }
                })
                character_descriptions.append(f"Image {idx+1} shows {char_name}")
                logger.info(f"Added reference image {idx+1}: {char_name}")
            
            # 프롬프트 수정: 자연스러운 맥락 기반 행동 + 캐릭터 일관성 + 구성 다양성 + 텍스트 제외
            enhanced_prompt = (
                f"Using the provided reference images of characters ({', '.join(character_descriptions)}), "
                f"create a new scene where {prompt}. "
                f"Show the characters naturally acting and responding to the scene context. "
                f"IMPORTANT: Keep each character's face, hair, and clothing style EXACTLY the same as in reference images, "
                f"but show them in natural poses and actions that fit the story context. "
                f"MUST USE DIFFERENT POSES AND CAMERA ANGLES: Use completely different body poses, hand gestures, "
                f"facial expressions, and camera viewpoints (close-up, wide shot, side view, over-the-shoulder, "
                f"bird's eye view, etc.) to create visual variety and avoid repetitive compositions. "
                f"The characters should be clearly recognizable as the same people from the reference images. "
                f"CRITICAL: Generate image WITHOUT ANY TEXT, no letters, no words, no writing, no speech bubbles."
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
                # 3인칭 대명사 (기존)
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

                # 1인칭 대명사 (캐릭터 관점에서 자신을 지칭)
                "나는": context.last_mentioned_character + "는",
                "나가": context.last_mentioned_character + "가",
                "내가": context.last_mentioned_character + "가",
                "나를": context.last_mentioned_character + "를",
                "나의": context.last_mentioned_character + "의",
                "내": context.last_mentioned_character + "의",
                "제가": context.last_mentioned_character + "가",
                "저는": context.last_mentioned_character + "는",
                "저를": context.last_mentioned_character + "를",
                "저의": context.last_mentioned_character + "의",

                # 1인칭 복수 (캐릭터가 포함된 그룹)
                "우리는": context.last_mentioned_character + "들은",
                "우리가": context.last_mentioned_character + "들이",
                "우리를": context.last_mentioned_character + "들을",
                "우리의": context.last_mentioned_character + "들의",
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

        # 주의: 투표 통과 후에만 실제 저장하도록 변경
        # 현재는 임시로 컨텍스트에 추가하여 이미지 생성에만 사용
        logger.info("임시 컨텍스트로 이미지 생성 진행 (투표 후 확정)")
        
        # 프롬프트 생성 (현재 문장을 포함한 임시 컨텍스트 사용)
        # 투표 통과 전이므로 임시로만 사용
        temp_previous_story = previous_story + (" " + resolved_prompt if previous_story else resolved_prompt)

        if isEnding:
            # 엔딩인 경우 자연스러운 결말 장면 생성
            base_prompt = f"Final scene: {resolved_prompt}"
        else:
            base_prompt = CONTEXTUAL_PROMPT_TEMPLATE.format(
                previous_story=previous_story,  # 확정된 스토리만 사용
                current_scene=resolved_prompt
            )
        
        # 스타일 추가
        style = DRAWING_STYLES[drawingStyle] if 0 <= drawingStyle < len(DRAWING_STYLES) else DRAWING_STYLES[0]
        full_prompt = f"{base_prompt}, {style}, {PROMPT_SUFFIX}"
        
        # 캐릭터 처리 및 레퍼런스 이미지 수집
        reference_images = {}  # 모든 기존 캐릭터의 레퍼런스 이미지 수집
        existing_characters = []
        new_characters = []
        
        # 모든 캐릭터 확인
        for character in characters:
            if character in context.characters:
                existing_characters.append(character)
                context.characters[character].appearance_count += 1
                # 기존 캐릭터의 레퍼런스 이미지 수집
                reference_images[character] = context.characters[character].reference_image
                logger.info(f"Existing character detected: {character} (appearance #{context.characters[character].appearance_count})")
            else:
                new_characters.append(character)
                logger.info(f"New character detected: {character}")
        
        # 프롬프트에 등장하지 않았지만 스토리에 있는 중요 캐릭터도 포함 (선택적)
        # 엔딩 장면이나 중요한 장면에서 유용
        if isEnding and context.characters:
            # 엔딩에서는 주요 캐릭터들도 포함
            for char_name, char_info in context.characters.items():
                if char_name not in reference_images and char_info.appearance_count > 1:
                    reference_images[char_name] = char_info.reference_image
                    logger.info(f"Added major character for ending: {char_name}")
        
        # 마지막 언급된 캐릭터 업데이트
        if characters:
            context.last_mentioned_character = characters[0]
        
        # 최종 프롬프트 로그 출력
        logger.info(f"=== Final Prompt to Gemini ===")
        logger.info(f"Prompt: {full_prompt[:500]}..." if len(full_prompt) > 500 else f"Prompt: {full_prompt}")
        logger.info(f"Using reference images: {list(reference_images.keys()) if reference_images else 'None'}")
        
        # 이미지 생성 (모든 기존 캐릭터의 레퍼런스 이미지 전달)
        image_data = await self._call_gemini_api(
            full_prompt, 
            reference_images if reference_images else None
        )
        
        # 새 캐릭터들의 레퍼런스 저장
        for new_char in new_characters:
            # 처음 등장한 새 캐릭터만 저장 (한 장면에 여러 새 캐릭터가 동시에 등장할 수 있음)
            if new_char not in context.characters:
                # 기본 시각적 설명 생성 (캐릭터 타입에 따라)
                visual_desc = self._generate_visual_description(new_char, resolved_prompt)
                
                context.characters[new_char] = CharacterInfo(
                    name=new_char,
                    first_appearance_turn=turn,
                    reference_image=image_data,
                    description=resolved_prompt,
                    visual_description=visual_desc
                )
                logger.info(f"Saved reference image for new character: {new_char}")
        
        return image_data
    
    async def _generate_cover_prompt_with_gpt(self, title: str, summary: str, characters: List[str]) -> str:
        """
        표지 이미지 프롬프트 생성 (자연스러운 맥락 + 텍스트 없음)
        """
        # 텍스트 제외를 명시적으로 지시
        text_exclusion = "WITHOUT ANY TEXT, no title, no letters, no words, no writing, textless cover art only"
        
        if characters:
            # 캐릭터가 있는 경우 - 자연스러운 맥락 기반 프롬프트
            character_list = ", ".join(characters[:3])
            prompt = (
                f"Epic storybook cover illustration showing {character_list} "
                f"as the main characters of this story: {summary[:100]}. "
                f"The characters are naturally interacting and expressing emotions that fit the story. "
                f"Magical and enchanting atmosphere with vibrant colors. "
                f"Fantasy art style, detailed illustration. "
                f"{text_exclusion}"
            )
        else:
            # 캐릭터가 없는 경우 분위기 중심 프롬프트
            prompt = (
                f"Beautiful storybook cover illustration. "
                f"Story theme: {summary[:100]}. "
                f"Whimsical and imaginative scene with rich details. "
                f"Fantasy art style, vibrant colors. "
                f"{text_exclusion}"
            )
        
        logger.info(f"Generated cover prompt (context-based): {prompt[:100]}...")
        return prompt
    
    async def _generate_title_from_story(self, story_content: str) -> str:
        """
        GPT-5-nano를 사용하여 스토리 내용으로부터 제목 생성 (기존 Java 로직과 동일)
        """
        try:
            # 스토리 내용 길이 제한 (200자) - Java 코드와 동일
            if len(story_content) > 200:
                story_content = story_content[:200]

            logger.info(f"제목 생성을 위한 스토리 내용 길이: {len(story_content)} 글자")

            # 기존 Java 코드와 동일한 GPT-5-nano 프롬프트
            creative_prompt = f"""이 흥미진진한 모험 이야기를 위한 멋진 동화책 제목을 지어주세요!

📚 스토리: {story_content}

💡 제목 요구사항:
- 8-15자 길이의 한국어 제목
- 호기심과 모험심을 자극하는 제목
- 주요 캐릭터나 사물을 활용한 창의적 표현
- 독자가 꼭 읽어보고 싶어지는 매력적인 제목

🎯 예시 스타일: '마법사와 황금 열쇠', '신비한 숲의 비밀', '용감한 소녀의 대모험'

제목만 답변해주세요:"""

            # GPT-5-nano Responses API 요청 (Java 코드와 동일한 설정)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/responses",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-5-nano",
                        "input": creative_prompt,
                        "text": {"verbosity": "low"},  # 간결한 응답
                        "reasoning": {"effort": "minimal"}  # 최소 추론으로 빠른 응답
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"GPT-5-nano API 응답: {result}")

                    # GPT-5 Responses API는 output 배열 안에 메시지가 있음
                    if "output" in result and isinstance(result["output"], list):
                        for output_item in result["output"]:
                            if output_item.get("type") == "message" and "content" in output_item:
                                content_list = output_item["content"]
                                if isinstance(content_list, list):
                                    for content_item in content_list:
                                        if content_item.get("type") == "output_text" and "text" in content_item:
                                            generated_title = content_item["text"].strip()
                                            # 불필요한 따옴표나 문장부호 제거
                                            title = generated_title.strip("\"'").strip()
                                            logger.info(f"✅ GPT-5-nano로 생성된 제목: [{title}]")
                                            return title

                        logger.warning(f"GPT-5-nano 응답에서 output_text를 찾을 수 없음: {result}")
                    else:
                        logger.warning(f"GPT-5-nano 응답에 'output' 배열이 없음: {result}")

                else:
                    logger.warning(f"GPT-5-nano 제목 생성 실패: {response.status_code}")
                    try:
                        error_body = response.json()
                        logger.warning(f"에러 응답: {error_body}")
                    except:
                        logger.warning(f"에러 응답 텍스트: {response.text}")

        except Exception as e:
            logger.error(f"제목 생성 중 오류: {e}")

        # 실패시 기본 제목 반환 (Java 코드와 동일)
        logger.info("GPT-5-nano 제목 생성 실패, 기본 제목 사용: '아주 먼 옛날'")
        return "아주 먼 옛날"
    
    async def generate_book_cover_with_style(
        self,
        gameId: str,
        title: str,
        summary: str,
        drawingStyle: int
    ) -> bytes:
        """
        특정 스타일로 책 표지 생성 (모든 주요 캐릭터의 레퍼런스 활용)
        """
        logger.info(f"=== Book Cover Generation with Style ===")
        logger.info(f"Title: {title}")
        logger.info(f"Drawing Style: {drawingStyle}")
        
        context = game_contexts.get(gameId)
        
        # 주요 캐릭터 정보 수집 및 레퍼런스 이미지 수집
        character_names = []
        reference_images = {}  # 모든 주요 캐릭터의 레퍼런스 이미지
        
        if context and context.characters:
            # 등장 횟수 기준으로 정렬하여 주요 캐릭터 선택 (최대 3명)
            main_characters = sorted(
                context.characters.values(),
                key=lambda x: x.appearance_count,
                reverse=True
            )[:3]
            
            # 각 주요 캐릭터의 이름과 레퍼런스 이미지 수집
            for char_info in main_characters:
                character_names.append(char_info.name)
                reference_images[char_info.name] = char_info.reference_image
                
            logger.info(f"Main characters for cover: {character_names}")
            logger.info(f"Using {len(reference_images)} reference images for cover")
        
        # GPT-5-nano로 프롬프트 생성
        base_prompt = await self._generate_cover_prompt_with_gpt(title, summary, character_names)
        
        # 스타일 추가 (텍스트 제외, 비율 관련 내용 제거)
        style = DRAWING_STYLES[drawingStyle] if 0 <= drawingStyle < len(DRAWING_STYLES) else DRAWING_STYLES[0]
        full_prompt = f"{base_prompt}, {style}, professional book cover design, NO TEXT on image"
        
        logger.info(f"Final cover prompt: {full_prompt[:200]}...")
        
        # 표지 생성 (모든 주요 캐릭터의 레퍼런스 이미지 활용, 더 많은 재시도)
        return await self._call_gemini_api(
            full_prompt, 
            reference_images if reference_images else None, 
            retry_count=5
        )
    
    async def generate_book_cover(
        self,
        gameId: str,
        title: str,
        summary: str
    ) -> bytes:
        """
        책 표지 생성 (기본 스타일, 하위 호환성 유지)
        """
        return await self.generate_book_cover_with_style(gameId, title, summary, 0)

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

class BookCoverRequestFromJava(BaseModel):
    """Java 서비스에서 보내는 표지 생성 요청"""
    storyContent: str
    gameId: str
    drawingStyle: int

class VoteResultRequest(BaseModel):
    """투표 결과 전달 요청"""
    gameId: str
    userId: str
    userPrompt: str
    turn: int
    accepted: bool
    selectedKeywords: Optional[List[str]] = None

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
async def generate_cover_endpoint(request: BookCoverRequestFromJava):
    """책 표지 생성 API (Java 서비스 호환)"""
    try:
        logger.info(f"=== Java 서비스에서 표지 생성 요청 ===")
        logger.info(f"gameId: {request.gameId}")
        logger.info(f"drawingStyle: {request.drawingStyle}")
        logger.info(f"storyContent 길이: {len(request.storyContent)} 글자")
        
        # 스토리 컨텐츠를 요약으로 사용
        summary = request.storyContent[:500] if len(request.storyContent) > 500 else request.storyContent
        
        # GPT-5-nano로 제목 생성
        title = await image_service._generate_title_from_story(request.storyContent)
        
        # 표지 이미지 생성
        image_data = await image_service.generate_book_cover_with_style(
            gameId=request.gameId,
            title=title,
            summary=summary,
            drawingStyle=request.drawingStyle
        )
        
        # Java가 기대하는 응답 형식으로 반환 (Java 705줄에서 image_data로 읽음)
        response_data = {
            "title": title,
            "image_data": base64.b64encode(image_data).decode()  # Java에서 image_data로 읽음
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in cover generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vote-result")
async def handle_vote_result(request: VoteResultRequest):
    """투표 결과 처리 - 찬성 시 컨텍스트에 추가, 반대 시 무시"""
    try:
        logger.info(f"=== 투표 결과 처리 ===")
        logger.info(f"게임: {request.gameId}, 턴: {request.turn}, 승인: {request.accepted}")
        logger.info(f"문장: {request.userPrompt}")

        if request.gameId not in game_contexts:
            logger.warning(f"게임 컨텍스트를 찾을 수 없음: {request.gameId}")
            return {"message": "Game context not found", "success": False}

        context = game_contexts[request.gameId]

        if request.accepted:
            # 투표 찬성 시: 컨텍스트에 정식 추가
            resolved_prompt = image_service._resolve_references(request.userPrompt, context)
            context.story_history.append(resolved_prompt)

            # 엔티티 추출 및 마지막 언급 정보 업데이트
            entities = image_service.entity_extractor.extract_entities(resolved_prompt, request.selectedKeywords)
            characters = entities.get("characters", [])
            objects = entities.get("objects", [])

            if characters:
                context.last_mentioned_character = characters[0]
            if objects:
                context.last_mentioned_object = objects[0]

            logger.info(f"✅ 스토리 컨텍스트에 추가됨: [{resolved_prompt}]")
            logger.info(f"현재 스토리 길이: {len(context.story_history)} 문장")
        else:
            # 투표 반대 시: 아무것도 하지 않음 (이미 컨텍스트에 추가되지 않은 상태)
            logger.info(f"❌ 투표 반대로 컨텍스트에 추가하지 않음")

        return {
            "message": "Vote result processed successfully",
            "success": True,
            "context_updated": request.accepted,
            "current_story_length": len(context.story_history)
        }

    except Exception as e:
        logger.error(f"투표 결과 처리 중 오류: {e}", exc_info=True)
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
