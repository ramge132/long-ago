#!/usr/bin/env python3
"""
Long Ago - 통합 이미지 생성 서비스 v3.0 (향상된 Image-to-Image)
- 인물 일관성을 위한 개선된 레퍼런스 관리
- 첫 등장 인물 자동 저장 및 재사용
- Gemini 2.5 Flash Image-to-Image API 최적화
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
from dataclasses import dataclass, field
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

# 3. 캐릭터 일관성 프롬프트
CHARACTER_CONSISTENCY_PROMPT = """
Maintain exact character appearance from reference:
- Same facial features and structure
- Same hair color and style
- Same clothing colors and design
- Same body proportions
Only change: pose, expression, and position in scene
"""

# FastAPI 앱 초기화
app = FastAPI(title="Unified Image Generation Service v3", version="3.0.0")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== 데이터 모델 ==================

@dataclass
class CharacterReference:
    """캐릭터 레퍼런스 정보"""
    name: str
    korean_name: str
    first_appearance_turn: int
    image_data: str  # base64 encoded
    description: str  # GPT가 생성한 캐릭터 설명
    
@dataclass
class GameSession:
    """게임 세션 정보"""
    game_id: str
    drawing_style: int
    character_refs: Dict[str, CharacterReference] = field(default_factory=dict)
    story_context: str = ""
    turn_count: int = 0

# ================== 엔티티 관리 시스템 ==================

class EntityManager:
    def __init__(self):
        self.character_keywords = {
            "공주": "princess", "왕자": "prince", "마법사": "wizard", 
            "소년": "boy", "소녀": "girl", "노인": "oldman",
            "탐정": "detective", "박사": "doctor", "농부": "farmer",
            "아이돌": "idol", "상인": "merchant", "닌자": "ninja",
            "부자": "rich", "가난뱅이": "beggar", "외계인": "alien",
            "신": "god", "호랑이": "tiger", "유령": "ghost", "마왕": "devil",
            "왕": "king", "여왕": "queen", "기사": "knight",
            "요정": "fairy", "천사": "angel", "악마": "demon",
            "해적": "pirate", "도둑": "thief", "전사": "warrior"
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
                    self.default_images[english] = base64.b64encode(f.read()).decode('utf-8')
    
    def detect_characters(self, text: str) -> List[Tuple[str, str]]:
        """텍스트에서 캐릭터 감지 (한글명, 영문명) 튜플 리스트 반환"""
        detected = []
        for korean, english in self.character_keywords.items():
            if korean in text:
                detected.append((korean, english))
        return detected
    
    def get_default_image(self, character_type: str) -> Optional[str]:
        """기본 캐릭터 이미지 반환 (base64)"""
        return self.default_images.get(character_type)

# ================== 세션 관리 ==================

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, GameSession] = {}
        self.entity_manager = EntityManager()
    
    def get_or_create_session(self, game_id: str, drawing_style: int = 0) -> GameSession:
        """세션 가져오기 또는 생성"""
        if game_id not in self.sessions:
            self.sessions[game_id] = GameSession(
                game_id=game_id,
                drawing_style=drawing_style
            )
        return self.sessions[game_id]
    
    def add_character_reference(self, game_id: str, char_name: str, 
                               korean_name: str, image_data: str, 
                               turn: int, description: str):
        """캐릭터 레퍼런스 추가"""
        session = self.get_or_create_session(game_id)
        if char_name not in session.character_refs:
            session.character_refs[char_name] = CharacterReference(
                name=char_name,
                korean_name=korean_name,
                first_appearance_turn=turn,
                image_data=image_data,
                description=description
            )
            logger.info(f"✅ '{korean_name}' 캐릭터 레퍼런스 저장 (턴 {turn})")
    
    def get_character_reference(self, game_id: str, char_name: str) -> Optional[CharacterReference]:
        """캐릭터 레퍼런스 가져오기"""
        session = self.sessions.get(game_id)
        if session:
            return session.character_refs.get(char_name)
        return None
    
    def clear_session(self, game_id: str):
        """세션 정리"""
        if game_id in self.sessions:
            del self.sessions[game_id]
            logger.info(f"🗑️ 게임 {game_id} 세션 정리 완료")

# ================== 요청/응답 모델 ==================

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

# ================== 이미지 생성 서비스 ==================

class ImageGenerationService:
    def __init__(self):
        if not all([OPENAI_API_KEY, GEMINI_API_KEY]):
            logger.error("❌ 필수 API 키가 설정되지 않았습니다")
            sys.exit(1)
        
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.session_manager = SessionManager()
        self.entity_manager = EntityManager()
        
        logger.info("✅ 이미지 생성 서비스 v3.0 초기화 완료")
    
    async def generate_scene_image(self, request: SceneGenerationRequest) -> bytes:
        """장면 이미지 생성 - 향상된 Image-to-Image"""
        try:
            logger.info("="*50)
            logger.info(f"📸 이미지 생성 요청")
            logger.info(f"   게임: {request.gameId}, 턴: {request.turn}")
            logger.info(f"   입력: {request.userPrompt}")
            
            # 세션 가져오기
            session = self.session_manager.get_or_create_session(
                request.gameId, request.drawingStyle
            )
            session.turn_count = request.turn
            
            # 캐릭터 감지
            detected_chars = self.entity_manager.detect_characters(request.userPrompt)
            logger.info(f"   감지된 캐릭터: {[k for k, v in detected_chars]}")
            
            # GPT로 이미지 프롬프트 생성
            image_prompt = await self._create_image_prompt(
                request.userPrompt,
                detected_chars,
                session,
                request.isEnding
            )
            
            # 이미지 생성 (레퍼런스 있으면 Image-to-Image, 없으면 Text-to-Image)
            reference_chars = []
            for korean_name, english_name in detected_chars:
                ref = session.character_refs.get(english_name)
                if ref:
                    reference_chars.append(ref)
                    logger.info(f"   ♻️ '{korean_name}' 레퍼런스 재사용")
            
            if reference_chars:
                # Image-to-Image 생성
                logger.info(f"   🎨 Image-to-Image 모드 (레퍼런스 {len(reference_chars)}개)")
                image_data = await self._generate_with_references(
                    image_prompt,
                    reference_chars,
                    DRAWING_STYLES[request.drawingStyle]
                )
            else:
                # Text-to-Image 생성
                logger.info(f"   🎨 Text-to-Image 모드")
                image_data = await self._generate_text_to_image(
                    image_prompt,
                    DRAWING_STYLES[request.drawingStyle]
                )
            
            # 새로 등장한 캐릭터 레퍼런스 저장
            for korean_name, english_name in detected_chars:
                if english_name not in session.character_refs:
                    # 캐릭터 설명 생성
                    char_description = await self._create_character_description(
                        korean_name, request.userPrompt
                    )
                    
                    # 레퍼런스 저장
                    self.session_manager.add_character_reference(
                        request.gameId,
                        english_name,
                        korean_name,
                        base64.b64encode(image_data).decode('utf-8'),
                        request.turn,
                        char_description
                    )
            
            # 스토리 컨텍스트 업데이트
            session.story_context += f" {request.userPrompt}"
            
            logger.info(f"   ✅ 이미지 생성 완료 ({len(image_data)} bytes)")
            return image_data
            
        except Exception as e:
            logger.error(f"❌ 이미지 생성 실패: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _create_image_prompt(self, user_prompt: str, detected_chars: List[Tuple[str, str]], 
                                  session: GameSession, is_ending: bool) -> str:
        """GPT를 사용한 이미지 프롬프트 생성"""
        try:
            # 캐릭터 설명 준비
            char_descriptions = []
            for korean_name, english_name in detected_chars:
                ref = session.character_refs.get(english_name)
                if ref:
                    char_descriptions.append(f"{korean_name}: {ref.description}")
            
            # GPT 프롬프트
            system_prompt = """You are an expert at converting Korean story text into detailed English image generation prompts.
            Create vivid, descriptive prompts that capture the scene, emotions, and atmosphere.
            Include character descriptions if provided."""
            
            user_message = f"""Convert this Korean text to an English image prompt:
            Text: {user_prompt}
            
            {"Known characters: " + ", ".join(char_descriptions) if char_descriptions else ""}
            {"This is an ending scene - make it epic and conclusive." if is_ending else ""}
            
            Create a detailed visual description in English."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"GPT 프롬프트 생성 실패, 기본 변환 사용: {e}")
            return user_prompt
    
    async def _create_character_description(self, korean_name: str, context: str) -> str:
        """캐릭터 외형 설명 생성"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Create a brief visual description of a character based on their role and context."},
                    {"role": "user", "content": f"Character: {korean_name}\nContext: {context}\n\nDescribe their appearance briefly:"}
                ],
                max_tokens=100,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except:
            return f"A {korean_name} character"
    
    async def _generate_with_references(self, prompt: str, references: List[CharacterReference], 
                                       style: str) -> bytes:
        """레퍼런스를 사용한 Image-to-Image 생성"""
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-image-exp:generateContent?key={GEMINI_API_KEY}"
        
        # 구도 다양화
        composition = random.choice(COMPOSITION_VARIATIONS)
        
        # Parts 구성
        parts = []
        
        # 텍스트 프롬프트
        parts.append({
            "text": f"""{CHARACTER_CONSISTENCY_PROMPT}

Scene description: {prompt}
Art style: {style}
Composition: {composition}

IMPORTANT: Keep the exact appearance of characters from reference images.
Only change their pose and expression to fit the new scene.
No text or writing in the image."""
        })
        
        # 레퍼런스 이미지 추가 (최대 3개)
        for i, ref in enumerate(references[:3]):
            try:
                # base64 디코딩
                image_bytes = base64.b64decode(ref.image_data)
                
                # PIL로 열어서 JPEG로 변환
                img = Image.open(io.BytesIO(image_bytes))
                
                # RGBA를 RGB로 변환
                if img.mode == 'RGBA':
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])
                    img = rgb_img
                
                # JPEG로 인코딩
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=95)
                jpeg_data = buffer.getvalue()
                
                parts.append({
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": base64.b64encode(jpeg_data).decode('utf-8')
                    }
                })
                
                # 캐릭터 설명 추가
                parts.append({
                    "text": f"Reference character {i+1}: {ref.korean_name} - {ref.description}"
                })
                
            except Exception as e:
                logger.warning(f"레퍼런스 이미지 처리 실패: {e}")
                continue
        
        # API 호출
        payload = {
            "contents": [{
                "parts": parts
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 8192
            }
        }
        
        response = requests.post(api_url, json=payload, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Gemini API 오류: {response.status_code} - {response.text}")
            # Fallback to text-to-image
            return await self._generate_text_to_image(prompt, style)
        
        result = response.json()
        
        # 이미지 추출
        if 'candidates' in result and result['candidates']:
            for part in result['candidates'][0].get('content', {}).get('parts', []):
                if 'inlineData' in part:
                    return base64.b64decode(part['inlineData']['data'])
        
        raise Exception("Image-to-Image 생성 실패")
    
    async def _generate_text_to_image(self, prompt: str, style: str) -> bytes:
        """Text-to-Image 생성"""
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-image-exp:generateContent?key={GEMINI_API_KEY}"
        
        # 구도 다양화
        composition = random.choice(COMPOSITION_VARIATIONS)
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"""Create an image:
{prompt}

Art style: {style}
Composition: {composition}
High quality, detailed illustration.
No text, words, or writing in the image."""
                }]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 8192
            }
        }
        
        response = requests.post(api_url, json=payload, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Gemini API 오류: {response.status_code}")
            raise HTTPException(status_code=500, detail="이미지 생성 실패")
        
        result = response.json()
        
        # 이미지 추출
        if 'candidates' in result and result['candidates']:
            for part in result['candidates'][0].get('content', {}).get('parts', []):
                if 'inlineData' in part:
                    return base64.b64decode(part['inlineData']['data'])
        
        raise Exception("Text-to-Image 생성 실패")
    
    async def generate_book_cover(self, request: BookCoverGenerationRequest) -> tuple[str, bytes]:
        """책 표지 생성"""
        try:
            # GPT로 제목 생성
            title = await self._generate_book_title(request.storyContent)
            
            # 표지 이미지 생성
            cover_prompt = f"Epic book cover illustration for '{title}', {DRAWING_STYLES[request.drawingStyle]}"
            cover_image = await self._generate_text_to_image(
                cover_prompt,
                DRAWING_STYLES[request.drawingStyle]
            )
            
            return title, cover_image
            
        except Exception as e:
            logger.error(f"표지 생성 실패: {e}")
            # 기본값 반환
            return "멋진 이야기", b""
    
    async def _generate_book_title(self, story: str) -> str:
        """GPT를 사용한 책 제목 생성"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a creative writer who creates engaging book titles in Korean."},
                    {"role": "user", "content": f"Create a short, catchy Korean title for this story:\n{story[:500]}"}
                ],
                max_tokens=50,
                temperature=0.8
            )
            return response.choices[0].message.content.strip()
        except:
            return "아주 먼 옛날"

# ================== 전역 서비스 인스턴스 ==================

image_service = ImageGenerationService()

# ================== API 엔드포인트 ==================

@app.post("/generate-scene")
async def generate_scene_endpoint(request: SceneGenerationRequest):
    """장면 이미지 생성 API"""
    try:
        image_data = await image_service.generate_scene_image(request)
        return Response(
            content=image_data,
            media_type="image/png",
            headers={
                "X-Character-Count": str(len(image_service.session_manager.sessions.get(request.gameId, GameSession(request.gameId, 0)).character_refs))
            }
        )
    except Exception as e:
        logger.error(f"API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-cover")
async def generate_cover_endpoint(request: BookCoverGenerationRequest):
    """책 표지 생성 API"""
    try:
        title, image_data = await image_service.generate_book_cover(request)
        return {
            "title": title,
            "image_data": base64.b64encode(image_data).decode('utf-8') if image_data else "",
            "success": True
        }
    except Exception as e:
        logger.error(f"API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{game_id}")
async def get_session_info(game_id: str):
    """세션 정보 조회"""
    session = image_service.session_manager.sessions.get(game_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "game_id": session.game_id,
        "turn_count": session.turn_count,
        "character_count": len(session.character_refs),
        "characters": [
            {
                "name": ref.korean_name,
                "first_turn": ref.first_appearance_turn
            }
            for ref in session.character_refs.values()
        ]
    }

@app.delete("/session/{game_id}")
async def clear_session_endpoint(game_id: str):
    """게임 세션 정리"""
    image_service.session_manager.clear_session(game_id)
    return {"message": f"Session cleared for game {game_id}"}

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "features": [
            "text-to-image",
            "image-to-image",
            "character-consistency",
            "gpt-prompt-enhancement"
        ],
        "active_sessions": len(image_service.session_manager.sessions)
    }

# ================== 메인 실행 ==================

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("🚀 Long Ago 이미지 생성 서비스 v3.0 시작")
    logger.info("✨ 주요 기능:")
    logger.info("   - 향상된 Image-to-Image 캐릭터 일관성")
    logger.info("   - GPT 기반 프롬프트 최적화")
    logger.info("   - 게임별 세션 관리")
    logger.info("   - Gemini 2.5 Flash 최적화")
    logger.info("="*60)
    
    if not OPENAI_API_KEY:
        logger.error("❌ OPENAI_API_KEY 환경변수를 설정하세요")
        sys.exit(1)
    
    if not GEMINI_API_KEY:
        logger.error("❌ GEMINI_API_KEY 환경변수를 설정하세요")
        sys.exit(1)
    
    uvicorn.run(app, host="0.0.0.0", port=8190)
