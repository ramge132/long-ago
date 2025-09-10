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
# 게임별 문맥 저장소 (등장인물, 사물 등)
game_contexts = {}

def _add_korean_particle(noun: str, particle_pair: tuple[str, str]) -> str:
    """
    한글 명사에 올바른 조사를 붙여줍니다. (은/는, 이/가, 을/를)
    particle_pair: ('은', '는'), ('이', '가'), ('을', '를')
    """
    if not isinstance(noun, str) or not noun:
        return ""
        
    last_char = noun[-1]
    if '가' <= last_char <= '힣':
        has_batchim = (ord(last_char) - 0xAC00) % 28 > 0
        return noun + particle_pair[0] if has_batchim else noun + particle_pair[1]
    return noun + particle_pair[1]

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
        # 캐릭터 타입 매핑 (한글 -> 영문) - init_db.sql 기반
        self.character_keywords = {
            '호랑이': 'tiger', '유령': 'ghost', '농부': 'farmer', '상인': 'merchant',
            '신': 'god', '외계인': 'alien', '박사': 'doctor', '아이돌': 'idol',
            '마법사': 'wizard', '마왕': 'demon king', '소년': 'boy', '소녀': 'girl',
            '부자': 'rich person', '탐정': 'detective', '노인': 'old man',
            '가난뱅이': 'beggar', '공주': 'princess', '닌자': 'ninja'
        }

        # 장소 관련 키워드
        self.location_keywords = {
            "숲": "forest", "성": "castle", "마을": "village",
            "바다": "ocean", "산": "mountain", "동굴": "cave",
            "학교": "school", "집": "house", "정원": "garden",
            "사막": "desert", "우주": "space", "도시": "city",
            "다리": "bridge", "묘지": "cemetery", "식당": "restaurant",
            "박물관": "museum", "비밀통로": "secret passage", "저택": "mansion", "천국": "heaven"
        }

        # 객체 관련 키워드 - init_db.sql 기반 + 기존
        self.object_keywords = {
            '핸드폰': 'smartphone', '마차': 'carriage', '인형': 'doll', '부적': 'talisman',
            '지도': 'map', '가면': 'mask', '칼': 'sword', '피리': 'flute', '지팡이': 'staff',
            '태양': 'sun', '날개': 'wings', '의자': 'chair', '시계': 'clock', '도장': 'seal',
            '보석': 'jewel', 'UFO': 'UFO', '덫': 'trap', '총': 'gun', '타임머신': 'time machine',
            '감자': 'potato',
            # 기존 유용 키워드
            "검": "sword", "마법지팡이": "magic wand", "책": "book", "보물": "treasure",
            "열쇠": "key", "거울": "mirror", "꽃": "flower", "나무": "tree", "별": "star"
        }
        
        # 감정 키워드
        self.emotion_keywords = {
            "행복": "happy", "슬픔": "sad", "분노": "angry",
            "놀람": "surprised", "두려움": "scared", "기쁨": "joyful"
        }

        # 통합 키워드 목록 생성 (긴 단어 우선)
        self.all_keywords = []
        for korean in self.character_keywords:
            self.all_keywords.append((korean, "characters"))
        for korean in self.location_keywords:
            self.all_keywords.append((korean, "locations"))
        for korean in self.object_keywords:
            self.all_keywords.append((korean, "objects"))
        for korean in self.emotion_keywords:
            self.all_keywords.append((korean, "emotions"))
        
        # 키워드 길이 기준으로 내림차순 정렬
        self.all_keywords.sort(key=lambda x: len(x[0]), reverse=True)
        
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
        """텍스트에서 엔티티(한글) 추출 (긴 단어 우선)"""
        entities = { "characters": [], "locations": [], "objects": [], "emotions": [] }
        processed_text = text
        
        for keyword, entity_type in self.all_keywords:
            if keyword in processed_text:
                if keyword not in entities[entity_type]:
                    entities[entity_type].append(keyword)
                # 다른 짧은 키워드와의 충돌을 피하기 위해 처리된 키워드를 대체
                processed_text = processed_text.replace(keyword, " " * len(keyword))
        
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
        # 엔티티 추출 (한글 이름으로 넘어옴)
        entities = self.entity_manager.extract_entities(user_prompt)
        
        # 기본 프롬프트 구성
        prompt_parts = [
            f"A scene from a story: {user_prompt}"
        ]
        
        # 스타일 추가
        prompt_parts.append(DRAWING_STYLES[drawing_style])
        
        # 캐릭터 설명 (영문으로 변환)
        if entities["characters"]:
            english_chars = [self.entity_manager.character_keywords.get(k, k) for k in entities["characters"]]
            char_desc = ", ".join(english_chars)
            expression = random.choice(EXPRESSION_VARIATIONS)
            pose = random.choice(POSE_VARIATIONS)
            prompt_parts.append(f"Featuring: {char_desc}, {expression} expression, {pose}")
        
        # 장소 설명 (영문으로 변환)
        if entities["locations"]:
            english_locs = [self.entity_manager.location_keywords.get(k, k) for k in entities["locations"]]
            location_desc = ", ".join(english_locs)
            time_key = random.choice(list(TIME_OF_DAY_LIGHTING.keys()))
            lighting = TIME_OF_DAY_LIGHTING[time_key]
            prompt_parts.append(f"Setting: {location_desc}, {lighting}")

        # 객체 설명 (영문으로 변환)
        if entities["objects"]:
            english_objs = [self.entity_manager.object_keywords.get(k, k) for k in entities["objects"]]
            objects_desc = ", ".join(english_objs)
            prompt_parts.append(f"With important object: {objects_desc}")
        
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
                "text": f"Based on the character in this reference image, generate a new scene: {prompt}. Focus on the scene described by the text. Keep the exact same character appearance, only change the scene, pose, and expression. No text, watermark, or distorted features."
            })
        else:
            # Text-to-Image 모드
            parts.append({
                "text": f"{prompt}. High quality, detailed, artistic, no text, no watermark, no distorted features."
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
        장면 이미지 생성 (문맥 관리 및 Image-to-Image 지원)
        """
        try:
            logger.info(f"=== 이미지 생성 요청 시작 (v2.2) ===")
            logger.info(f"게임ID: {game_id}, 턴: {turn}")
            logger.info(f"사용자 입력 (원본): [{user_prompt}]")

            modified_prompt = user_prompt
            context = None

            # 1. 문맥 관리 및 대명사/문맥 치환
            if game_id:
                if game_id not in game_contexts:
                    game_contexts[game_id] = {
                        "mentioned_characters": [], "last_character": None,
                        "mentioned_objects": [], "last_object": None,
                        "mentioned_locations": [], "last_location": None,
                        "turn": 0
                    }
                context = game_contexts[game_id]
                
                if context["turn"] > 0:
                    temp_prompt = modified_prompt
                    
                    # 1-1. 단일 엔티티 치환
                    if context["last_character"]:
                        lc = context["last_character"]
                        temp_prompt = temp_prompt.replace("그는", _add_korean_particle(lc, ("은", "는")))
                        temp_prompt = temp_prompt.replace("그녀는", _add_korean_particle(lc, ("은", "는")))
                        temp_prompt = temp_prompt.replace("그가", _add_korean_particle(lc, ("이", "가")))
                        temp_prompt = temp_prompt.replace("그녀가", _add_korean_particle(lc, ("이", "가")))
                        temp_prompt = temp_prompt.replace("그를", _add_korean_particle(lc, ("을", "를")))
                        temp_prompt = temp_prompt.replace("그녀를", _add_korean_particle(lc, ("을", "를")))
                        temp_prompt = temp_prompt.replace("그의", lc + "의")
                        temp_prompt = temp_prompt.replace("그녀의", lc + "의")
                    if context["last_object"]:
                        lo = context["last_object"]
                        for p in ["그것", "이것"]:
                            temp_prompt = temp_prompt.replace(f"{p}은", _add_korean_particle(lo, ("은", "는")))
                            temp_prompt = temp_prompt.replace(f"{p}이", _add_korean_particle(lo, ("이", "가")))
                            temp_prompt = temp_prompt.replace(f"{p}을", _add_korean_particle(lo, ("을", "를")))
                            temp_prompt = temp_prompt.replace(f"{p}의", lo + "의")
                    if context["last_location"]:
                        ll = context["last_location"]
                        temp_prompt = temp_prompt.replace("그곳", ll)
                    
                    # 1-2. 복수 엔티티 치환
                    if context["mentioned_characters"]:
                        chars_text = ", ".join(context["mentioned_characters"])
                        temp_prompt = temp_prompt.replace("그들은", chars_text)
                        temp_prompt = temp_prompt.replace("그들이", chars_text)
                    if context["mentioned_objects"]:
                        objs_text = ", ".join(context["mentioned_objects"])
                        temp_prompt = temp_prompt.replace("그것들은", objs_text)
                    
                    if temp_prompt != modified_prompt:
                        logger.info(f"🔹 대명사 치환 적용: [{temp_prompt}]")
                        modified_prompt = temp_prompt

                    # 1-3. 능동적 문맥 주입 (주어 없을 시)
                    current_entities = self.entity_manager.extract_entities(modified_prompt)
                    if not current_entities["characters"] and context["last_character"]:
                        # 주어가 없는 문장으로 보이면 마지막 캐릭터를 주어로 추가
                        modified_prompt = f"{_add_korean_particle(context['last_character'], ('이', '가'))} {modified_prompt}"
                        logger.info(f"🔹 캐릭터 문맥 주입: [{modified_prompt}]")

            # 2. 엔티티 추출 및 문맥 업데이트
            entities = self.entity_manager.extract_entities(modified_prompt) # entities are Korean
            logger.info(f"🔹 발견된 엔티티 (한글): {entities}")

            if context:
                context["turn"] += 1
                if entities["characters"]:
                    new_chars = [c for c in entities["characters"] if c not in context["mentioned_characters"]]
                    if new_chars: context["mentioned_characters"].extend(new_chars)
                    context["last_character"] = entities["characters"][-1]
                if entities["objects"]:
                    new_objs = [o for o in entities["objects"] if o not in context["mentioned_objects"]]
                    if new_objs: context["mentioned_objects"].extend(new_objs)
                    context["last_object"] = entities["objects"][-1]
                if entities["locations"]:
                    new_locs = [l for l in entities["locations"] if l not in context["mentioned_locations"]]
                    if new_locs: context["mentioned_locations"].extend(new_locs)
                    context["last_location"] = entities["locations"][-1]

            # 3. 동적 프롬프트 생성
            dynamic_prompt = self.prompt_generator.create_dynamic_prompt(
                modified_prompt, drawing_style, is_ending
            )

            # 4. 캐릭터 레퍼런스 확인 (Image-to-Image)
            reference_image = None
            detected_english_chars = [self.entity_manager.character_keywords.get(k) for k in entities["characters"]]
            
            if game_id and detected_english_chars:
                game_refs = character_references.get(game_id, {})
                for char_en in detected_english_chars:
                    if char_en in game_refs:
                        reference_image = game_refs[char_en]
                        logger.info(f"🔹 '{char_en}' 레퍼런스 이미지 사용 (Image-to-Image)")
                        break

            # 5. Gemini로 이미지 생성
            image_data = await self.generate_image_with_gemini(dynamic_prompt, reference_image)

            # 6. 새로운 캐릭터 레퍼런스 저장
            if game_id and detected_english_chars:
                if game_id not in character_references:
                    character_references[game_id] = {}
                for char_en in detected_english_chars:
                    if char_en and char_en not in character_references[game_id]:
                        character_references[game_id][char_en] = image_data
                        logger.info(f"✅ '{char_en}' 캐릭터 레퍼런스 저장됨 (턴 {turn})")
                        break # 첫 등장 캐릭터 하나만 저장

            logger.info(f"✅ 이미지 생성 완료: {len(image_data)} bytes")
            return image_data

        except Exception as e:
            logger.error(f"이미지 생성 실패: {str(e)}")
            
            # 2차 시도: 기본 캐릭터 이미지 반환
            fallback_entities = self.entity_manager.extract_entities(user_prompt) # Korean
            if fallback_entities["characters"]:
                char_kr = fallback_entities["characters"][0]
                char_en = self.entity_manager.character_keywords.get(char_kr)
                if char_en:
                    default_image = self.entity_manager.get_default_image(char_en)
                    if default_image:
                        logger.info(f"✓ 기본 이미지 사용: {char_en}")
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
        # 스토리에서 주요 캐릭터 찾기 (Korean)
        entities = self.entity_manager.extract_entities(story)
        
        # 영어 키로 된 맵
        char_map = {
            "princess": "공주의 모험", "prince": "왕자의 여정", "wizard": "마법사의 비밀",
            "boy": "소년의 이야기", "girl": "소녀의 꿈", "old man": "노인의 지혜",
            "detective": "탐정의 추리", "doctor": "박사의 발견", "farmer": "농부의 하루",
            "idol": "아이돌의 무대", "merchant": "상인의 거래", "ninja": "닌자의 임무",
            "rich person": "부자의 비밀", "beggar": "가난뱅이의 행운", "alien": "외계인의 방문",
            "tiger": "호랑이의 전설", "ghost": "유령의 속삭임", "god": "신의 변덕", "demon king": "마왕의 부활"
        }
        location_map = {
            "forest": "숲속의 이야기", "castle": "성의 전설", "village": "마을의 비밀",
            "ocean": "바다의 노래", "mountain": "산의 정령", "cave": "동굴의 신비",
            "school": "학교 유령", "house": "집으로 가는 길", "garden": "정원의 기적",
            "desert": "사막의 별", "space": "우주 모험", "city": "도시의 빛",
            "bridge":"다리 위의 약속", "cemetery":"묘지에서의 하룻밤", "restaurant":"수상한 식당",
            "museum":"박물관은 살아있다", "secret passage":"비밀통로의 끝", "mansion":"저택의 비밀", "heaven":"천국으로 가는 계단"
        }

        if entities["characters"]:
            first_char_kr = entities["characters"][0]
            first_char_en = self.entity_manager.character_keywords.get(first_char_kr)
            if first_char_en in char_map:
                return char_map[first_char_en]

        if entities["locations"]:
            first_loc_kr = entities["locations"][0]
            first_loc_en = self.entity_manager.location_keywords.get(first_loc_kr)
            if first_loc_en in location_map:
                return location_map[first_loc_en]
        
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
    """게임 종료 시 레퍼런스 및 문맥 정리"""
    cleaned_messages = []
    
    if game_id in character_references:
        char_count = len(character_references[game_id])
        del character_references[game_id]
        cleaned_messages.append(f"Cleaned {char_count} character references.")
        
    if game_id in game_contexts:
        del game_contexts[game_id]
        cleaned_messages.append("Cleaned game context.")

    if cleaned_messages:
        full_message = f"Game {game_id} cleanup: {' '.join(cleaned_messages)}"
        logger.info(f"🗑️ {full_message}")
        return {"message": full_message}
    
    return {"message": f"No data found for game {game_id} to clean."}

# ================== 메인 실행 ==================

if __name__ == "__main__":
    logger.info("="*50)
    logger.info("Long Ago 이미지 생성 서비스 v2.0 시작")
    logger.info("포트: 8190")
    logger.info("="*50)
    
    uvicorn.run(app, host="0.0.0.0", port=8190)
