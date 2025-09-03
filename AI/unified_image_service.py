#!/usr/bin/env python3
"""
Long Ago - 통합 이미지 생성 서비스 (Python)
기존 Java SceneService.java와 GameService.java의 로직을 정확히 복제

- OpenAI GPT-5 Responses API를 사용한 프롬프트 생성
- Google Gemini 2.5 Flash Image Preview API를 사용한 이미지 생성  
- 바이너리 이미지 데이터 반환 (S3 업로드는 Java에서 처리)
- 재시도 로직 포함
- 결말카드/일반카드 구분 처리
"""

import os
import sys
import asyncio
import json
import base64
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

import uvicorn
import httpx
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 환경변수 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 그림체 스타일 정의 (Java와 동일)
DRAWING_STYLES = [
    "애니메이션 스타일", "3D 카툰 스타일", "코믹 스트립 스타일", "클레이메이션 스타일",
    "크레용 드로잉 스타일", "픽셀 아트 스타일", "미니멀리스트 일러스트", "수채화 스타일", "스토리북 일러스트"
]

# =============================================================================
# 이미지 생성용 프롬프트 템플릿 상수
# =============================================================================

# GPT 프롬프트 생성 템플릿
GPT_SCENE_PROMPT_TEMPLATE = "문장: {user_sentence}. 이 문장을 {style} 스타일의 이미지로 만들기 위한 핵심 영어 키워드를 나열해줘."
GPT_ENDING_PROMPT_TEMPLATE = "결말: {user_sentence}. 이 문장을 {style} 스타일의 이미지로 만들기 위한 핵심 영어 키워드를 나열해줘."

# GPT 책 제목 생성 프롬프트
GPT_BOOK_TITLE_PROMPT_TEMPLATE = "다음 스토리를 10자 이내의 창의적인 제목으로 만들어주세요. 다른 설명 없이 제목만 말해주세요. 스토리: {story_content}"

# Gemini 이미지 생성 프롬프트 템플릿
GEMINI_IMAGE_PROMPT_TEMPLATE = "Generate an image: {prompt}"

# 책 표지 이미지 프롬프트 템플릿  
BOOK_COVER_PROMPT_TEMPLATE = "Create a beautiful book cover for a story titled '{book_title}'. Style: {style}. The cover should be artistic, captivating, and suitable for a storybook."

# FastAPI 앱 초기화
app = FastAPI(title="Unified Image Generation Service", version="2.0.0")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 요청/응답 모델
class SceneGenerationRequest(BaseModel):
    gameId: str
    userId: str
    userPrompt: str
    turn: int
    drawingStyle: int
    isEnding: bool

# SceneGenerationResponse는 바이너리 이미지 데이터 직접 반환으로 대체

class BookCoverGenerationRequest(BaseModel):
    storyContent: str
    gameId: str
    drawingStyle: int

class BookCoverGenerationResponse(BaseModel):
    success: bool
    title: Optional[str] = None
    message: str

class UnifiedImageService:
    def __init__(self):
        """통합 이미지 생성 서비스 초기화"""
        if not all([OPENAI_API_KEY, GEMINI_API_KEY]):
            logger.error("필수 환경변수가 설정되지 않았습니다")
            sys.exit(1)
        
        logger.info("통합 이미지 생성 서비스 초기화 완료")

    async def generate_scene_image(self, request: SceneGenerationRequest) -> bytes:
        """장면 이미지 생성 (Java SceneService.createScene 로직 복제) - 바이너리 이미지 데이터 반환"""
        try:
            logger.info("=== 이미지 생성 요청 시작 ===")
            logger.info(f"게임ID: {request.gameId}, 사용자ID: {request.userId}, 턴: {request.turn}")
            logger.info(f"사용자 입력: [{request.userPrompt}] (길이: {len(request.userPrompt)}자)")
            logger.info(f"그림체 모드: {request.drawingStyle}")
            
            # 프론트엔드에서 전달받은 isEnding 값 사용 (실제 게임 로직에 기반)
            is_ending_card = request.isEnding
            
            logger.info("=== 결말카드 판정 결과 ===")
            logger.info(f"프론트엔드에서 전달받은 isEnding: {request.isEnding}")
            logger.info(f"최종 판정: {'결말' if is_ending_card else '일반'} 카드")
            
            # 1단계: GPT로 프롬프트 생성
            if is_ending_card:
                logger.info("=== 결말카드 GPT 프롬프트 생성 시작 ===")
                enhanced_prompt = await self._generate_ending_prompt_with_gpt(request.userPrompt, request.drawingStyle)
                logger.info(f"결말카드용 GPT 프롬프트 생성 완료: [{enhanced_prompt}]")
            else:
                logger.info("=== 일반카드 GPT 프롬프트 생성 시작 ===")
                enhanced_prompt = await self._generate_prompt_with_gpt(request.userPrompt, request.drawingStyle)
                logger.info(f"일반카드용 GPT 프롬프트 생성 완료: [{enhanced_prompt}]")
            
            # 2단계: Gemini로 이미지 생성
            logger.info("=== Gemini 이미지 생성 시작 ===")
            image_data = await self._generate_image_with_gemini(enhanced_prompt)
            logger.info("=== Gemini 이미지 생성 성공 ===")
            logger.info(f"생성된 이미지 크기: {len(image_data)} bytes")
            
            # 바이너리 이미지 데이터 반환 (S3 업로드는 Java에서 처리)
            logger.info(f"새로운 API에서 생성된 이미지 크기 : {len(image_data)}")
            logger.info("=== Python 서비스에서 바이너리 이미지 데이터 반환 ===")
            
            return image_data
            
        except Exception as e:
            logger.error(f"이미지 생성 실패: {str(e)}")
            logger.error(f"에러 상세:", exc_info=True)
            raise HTTPException(status_code=500, detail=f"이미지 생성 실패: {str(e)}")

    async def generate_book_cover(self, request: BookCoverGenerationRequest) -> tuple[str, bytes]:
        """책 표지 생성 (Java GameService.finishGame 로직 복제) - 제목과 바이너리 이미지 데이터 반환"""
        try:
            logger.info("=== 책 표지 생성 시작 ===")
            
            # 1단계: 스토리 요약 및 제목 생성
            logger.info("=== 1단계: 스토리 요약 및 제목 생성 시작 ===")
            book_title = await self._generate_book_title(request.storyContent)
            logger.info(f"GPT로 생성된 책 제목: [{book_title}]")
            
            if not book_title or not book_title.strip():
                raise RuntimeError("제목 생성 실패 - 빈 제목")
            
            # 2단계: 표지 이미지 생성
            logger.info("=== 2단계: 표지 이미지 생성 시작 ===")
            cover_image_data = await self._generate_cover_image(book_title, request.drawingStyle)
            logger.info(f"Gemini로 생성된 표지 이미지 크기: {len(cover_image_data)} bytes")
            
            if not cover_image_data or len(cover_image_data) == 0:
                raise RuntimeError("이미지 생성 실패 - 빈 이미지")
            
            # 제목과 바이너리 이미지 데이터 반환 (S3 업로드는 Java에서 처리)
            logger.info("=== Python 서비스에서 제목과 바이너리 이미지 데이터 반환 ===")
            
            return book_title, cover_image_data
            
        except Exception as e:
            logger.error(f"책 표지 생성 실패: {str(e)}")
            logger.error(f"에러 상세:", exc_info=True)
            raise HTTPException(status_code=500, detail=f"책 표지 생성 실패: {str(e)}")

    async def _generate_prompt_with_gpt(self, user_sentence: str, game_mode: int, max_retries: int = 1) -> str:
        """OpenAI GPT-5 Responses API를 사용하여 프롬프트 생성 (Java callGPTWithRetry 로직 정확히 복제)"""
        return await self._call_gpt_with_retry(user_sentence, game_mode, max_retries, is_ending_card=False)
    
    async def _generate_ending_prompt_with_gpt(self, ending_card_content: str, game_mode: int, max_retries: int = 1) -> str:
        """결말카드 전용 OpenAI GPT 프롬프트 생성 (Java generateEndingPromptWithGPT 로직 복제)"""
        return await self._call_gpt_with_retry(ending_card_content, game_mode, max_retries, is_ending_card=True)
    
    async def _call_gpt_with_retry(self, user_sentence: str, game_mode: int, max_retries: int, is_ending_card: bool) -> str:
        """재시도 로직이 포함된 GPT API 호출 (Java callGPTWithRetry 로직 정확히 복제)"""
        
        card_type = "결말카드" if is_ending_card else "일반카드"
        logger.info(f"=== {card_type} GPT API 호출 시작 (최대 {max_retries + 1}회 시도) ===")
        logger.info(f"입력 문장: [{user_sentence}], 게임모드: {game_mode}")
        
        # 그림체 스타일 정의 (Java와 동일)
        style = DRAWING_STYLES[game_mode] if game_mode < len(DRAWING_STYLES) else DRAWING_STYLES[0]
        logger.info(f"선택된 스타일: {style}")
        
        # 재시도 로직 (Java와 동일)
        for attempt in range(1, max_retries + 2):  # 1부터 시작
            try:
                logger.info(f"🔄 {card_type} GPT API 시도 {attempt}/{max_retries + 1}")
                
                # GPT-5 Responses API 요청 구조 (Java와 정확히 동일)
                prompt_instruction = (
                    GPT_ENDING_PROMPT_TEMPLATE.format(user_sentence=user_sentence, style=style)
                    if is_ending_card else 
                    GPT_SCENE_PROMPT_TEMPLATE.format(user_sentence=user_sentence, style=style)
                )
                
                request_body = {
                    "model": "gpt-5-nano",
                    "input": prompt_instruction,
                    "reasoning": {"effort": "low"},
                    "text": {"verbosity": "low"}
                }
                
                logger.info(f"GPT-5 Responses API 요청 전송 중... (시도 {attempt})")
                
                # OpenAI Responses API 호출 (Java와 동일한 엔드포인트)
                headers = {
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://api.openai.com/v1/responses",
                        json=request_body,
                        headers=headers
                    )
                    
                    if response.status_code >= 400:
                        error_body = response.text
                        logger.error(f"🚨 OpenAI API 에러 응답 본문: {error_body}")
                        raise RuntimeError(f"OpenAI API 에러: {error_body}")
                    
                    response_json = response.json()
                
                logger.info("OpenAI API 응답 수신: 응답 있음")
                logger.info(f"응답 JSON 구조: {response_json}")
                
                # 응답 파싱 (Java와 정확히 동일한 로직)
                generated_prompt = None
                
                # 1. output_text 직접 확인
                if "output_text" in response_json:
                    generated_prompt = response_json["output_text"].strip()
                    logger.info(f"✅ output_text에서 프롬프트 발견: [{generated_prompt}]")
                    
                # 2. output 배열 확인
                elif "output" in response_json and isinstance(response_json["output"], list):
                    output_array = response_json["output"]
                    logger.info(f"output 배열 크기: {len(output_array)}")
                    
                    for i, output_node in enumerate(output_array):
                        logger.info(f"output[{i}] 타입: {output_node.get('type', '')}")
                        
                        # 메시지 타입인 경우
                        if output_node.get("type") == "message" and "content" in output_node:
                            content_array = output_node["content"]
                            if isinstance(content_array, list):
                                for j, content in enumerate(content_array):
                                    logger.info(f"content[{j}] 타입: {content.get('type', '')}")
                                    
                                    if content.get("type") == "output_text" and "text" in content:
                                        generated_prompt = content["text"].strip()
                                        logger.info(f"✅ content에서 프롬프트 발견: [{generated_prompt}]")
                                        break
                        # 직접 텍스트가 있는 경우
                        elif "text" in output_node:
                            generated_prompt = output_node["text"].strip()
                            logger.info(f"✅ output 노드에서 프롬프트 발견: [{generated_prompt}]")
                        
                        if generated_prompt:
                            break
                            
                # 3. choices 배열 확인 (Chat Completions 스타일)
                elif "choices" in response_json and isinstance(response_json["choices"], list):
                    choices = response_json["choices"]
                    if len(choices) > 0:
                        first_choice = choices[0]
                        if "message" in first_choice and "content" in first_choice["message"]:
                            generated_prompt = first_choice["message"]["content"].strip()
                            logger.info(f"✅ choices에서 프롬프트 발견: [{generated_prompt}]")
                
                if generated_prompt and generated_prompt.strip():
                    logger.info(f"✅ {card_type} GPT API 성공 (시도 {attempt}): [{generated_prompt}]")
                    return generated_prompt
                
                logger.warning(f"⚠️ GPT 응답에서 텍스트 필드 없음 (시도 {attempt})")
                if attempt < max_retries + 1:
                    await asyncio.sleep(0.5 * attempt)  # 대기 시간
                    
            except Exception as e:
                logger.error(f"❌ {card_type} GPT API 시도 {attempt} 실패: {str(e)}")
                
                if attempt == max_retries + 1:
                    logger.error(f"🚨 {card_type} GPT API 최종 실패 - 원본 문장 사용")
                    return user_sentence  # 최종 실패시 원본 문장 반환
                
                # 대기 후 재시도
                await asyncio.sleep(0.5 * attempt)
        
        return user_sentence  # fallback
    
    async def _generate_book_title(self, story_content: str, max_retries: int = 4) -> str:
        """OpenAI GPT를 사용하여 스토리를 요약하고 책 제목 생성 (Java generateBookTitle 로직 정확히 복제)"""
        logger.info("=== 책 제목 생성 시작 ===")
        
        # 길이 제한 (200자) - Java와 동일
        if len(story_content) > 200:
            story_content = story_content[:200]
        
        logger.info(f"스토리 내용 길이: {len(story_content)} 글자")
        logger.info(f"스토리 내용 미리보기: {story_content[:min(100, len(story_content))]}...")
        
        # 재시도 로직 (최대 5번 시도 - 제목 생성은 필수)
        for attempt in range(1, max_retries + 2):  # 1~5
            try:
                logger.info(f"🔄 책 제목 생성 시도 {attempt}/{max_retries + 1}")
                
                # GPT-5 Responses API 요청 구조 (Java와 정확히 동일)
                request_body = {
                    "model": "gpt-5-nano",
                    "input": GPT_BOOK_TITLE_PROMPT_TEMPLATE.format(story_content=story_content),
                    "text": {"verbosity": "low"},
                    "reasoning": {"effort": "minimal"}
                }
                
                logger.info(f"GPT-5 Responses API 요청 전송 중... (시도 {attempt})")
                
                headers = {
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://api.openai.com/v1/responses",
                        json=request_body,
                        headers=headers
                    )
                    
                    if response.status_code >= 400:
                        error_body = response.text
                        logger.error(f"🚨 OpenAI API 에러 응답 본문: {error_body}")
                        raise RuntimeError(f"OpenAI API 에러: {error_body}")
                    
                    response_json = response.json()
                
                logger.info("GPT API 응답 수신: 응답 있음")
                
                if not response_json:
                    raise RuntimeError("GPT API null 응답")
                
                # JSON 키들을 수집 (Java와 동일)
                field_names = list(response_json.keys())
                logger.info(f"응답 JSON 키들: {', '.join(field_names) if field_names else '없음'}")
                logger.info(f"전체 응답: {response_json}")
                
                generated_title = None
                
                # 1. output_text 직접 확인
                if "output_text" in response_json:
                    generated_title = response_json["output_text"].strip()
                    logger.info(f"✅ output_text에서 제목 발견: [{generated_title}]")
                    
                # 2. output 배열 확인
                elif "output" in response_json and isinstance(response_json["output"], list):
                    output_array = response_json["output"]
                    logger.info(f"output 배열 크기: {len(output_array)}")
                    
                    for i, output_node in enumerate(output_array):
                        logger.info(f"output[{i}] 타입: {output_node.get('type', '')}")
                        
                        # 메시지 타입인 경우
                        if output_node.get("type") == "message" and "content" in output_node:
                            content_array = output_node["content"]
                            if isinstance(content_array, list):
                                for j, content in enumerate(content_array):
                                    logger.info(f"content[{j}] 타입: {content.get('type', '')}")
                                    
                                    if content.get("type") == "output_text" and "text" in content:
                                        generated_title = content["text"].strip()
                                        logger.info(f"✅ content에서 제목 발견: [{generated_title}]")
                                        break
                        # 직접 텍스트가 있는 경우
                        elif "text" in output_node:
                            generated_title = output_node["text"].strip()
                            logger.info(f"✅ output 노드에서 제목 발견: [{generated_title}]")
                        
                        if generated_title:
                            break
                            
                # 3. choices 배열 확인 (Chat Completions 스타일)
                elif "choices" in response_json and isinstance(response_json["choices"], list):
                    choices = response_json["choices"]
                    if len(choices) > 0:
                        first_choice = choices[0]
                        if "message" in first_choice and "content" in first_choice["message"]:
                            generated_title = first_choice["message"]["content"].strip()
                            logger.info(f"✅ choices에서 제목 발견: [{generated_title}]")
                
                if generated_title and generated_title.strip():
                    logger.info(f"✅ 책 제목 생성 성공 (시도 {attempt}): [{generated_title}]")
                    return generated_title
                
                logger.warning(f"⚠️ GPT 응답에서 choices 필드 없음 (시도 {attempt})")
                if attempt < max_retries + 1:
                    await asyncio.sleep(1.0)  # 1초 대기 후 재시도
                    
            except Exception as e:
                logger.error(f"❌ 책 제목 생성 시도 {attempt} 실패: {str(e)}")
                if attempt == max_retries + 1:
                    logger.error("🚨 책 제목 생성 최종 실패 - RuntimeException 던짐")
                    raise RuntimeError(f"GPT 제목 생성 필수 - {max_retries + 1}회 시도 모두 실패: {str(e)}")
                else:
                    try:
                        await asyncio.sleep(1.0)  # 1초 대기 후 재시도
                    except Exception:
                        raise RuntimeError("제목 생성 중 인터럽트 발생")
        
        # 이 지점에 도달하면 안 됨 (모든 재시도 실패)
        logger.error("🚨 CRITICAL: 책 제목 생성 로직 오류 - 이 지점에 도달하면 안 됨")
        raise RuntimeError("책 제목 생성 로직 오류")

    async def _generate_image_with_gemini(self, prompt: str, max_retries: int = 1) -> bytes:
        """Gemini 2.5 Flash Image Preview를 사용하여 이미지 생성 (Java callGeminiWithRetry 로직 정확히 복제)"""
        return await self._call_gemini_with_retry(prompt, max_retries)
    
    async def _generate_cover_image(self, book_title: str, drawing_style: int) -> bytes:
        """표지 이미지 생성 (Java generateCoverImage 로직 정확히 복제)"""
        # 그림체 모드에 따른 스타일 정의 (Java와 동일)
        style = DRAWING_STYLES[drawing_style] if drawing_style < len(DRAWING_STYLES) else DRAWING_STYLES[0]
        
        # 표지 이미지 프롬프트 생성 (Java와 동일)
        cover_prompt = BOOK_COVER_PROMPT_TEMPLATE.format(book_title=book_title, style=style)
        
        # 책표지 생성을 위해 재시도 횟수 증가 (Java와 동일)
        return await self._call_gemini_with_retry_for_cover(cover_prompt, 4)  # 4회 재시도 (총 5번)
    
    async def _call_gemini_with_retry(self, prompt: str, max_retries: int) -> bytes:
        """재시도 로직이 포함된 Gemini API 호출 (Java callGeminiWithRetry 로직 정확히 복제)"""
        logger.info(f"=== Gemini 2.5 Flash Image Preview API 호출 시작 (최대 {max_retries + 1}회 시도) ===")
        logger.info(f"입력 프롬프트: [{prompt}] (길이: {len(prompt)}자)")
        
        for attempt in range(1, max_retries + 2):  # 1부터 시작
            try:
                logger.info(f"🔄 Gemini API 시도 {attempt}/{max_retries + 1}")
                
                # Gemini 2.5 Flash Image Preview API 요청 구조 (Java와 동일)
                full_prompt = GEMINI_IMAGE_PROMPT_TEMPLATE.format(prompt=prompt)
                
                request_body = {
                    "contents": [{
                        "parts": [{
                            "text": full_prompt
                        }]
                    }]
                }
                
                logger.info(f"Gemini API 전송 프롬프트: [{full_prompt}] (길이: {len(full_prompt)}자)")
                
                # Gemini 2.5 Flash Image Preview API 호출
                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key={GEMINI_API_KEY}"
                
                logger.info(f"Gemini API URL: {api_url[:api_url.rfind('key=') + 4]}***")
                logger.info("Gemini API 요청 전송 중...")
                
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(api_url, json=request_body)
                    
                    if response.status_code >= 400:
                        error_text = response.text
                        logger.error(f"Gemini API 에러: {error_text}")
                        raise RuntimeError(f"Gemini API 에러: {error_text}")
                        
                    response_json = response.json()
                
                logger.info("=== Gemini API 응답 수신 ===")
                logger.info("응답 상태: 응답 있음")
                
                # 디버깅: 실제 응답 내용 로깅
                logger.info(f"🔍 Gemini API 실제 응답 내용: {response_json}")
                
                if not response_json:
                    logger.error("Gemini API에서 null 응답 수신")
                    raise RuntimeError("Gemini API null 응답")
                
                # 응답 파싱 (Java와 정확히 동일)
                logger.info("=== Gemini API 응답 JSON 분석 ===")
                
                # candidates 확인
                if "candidates" not in response_json:
                    logger.error(f"❌ Gemini API 응답에 'candidates' 필드 없음! (시도 {attempt})")
                    
                    # 에러 정보 상세 분석 (Java와 동일)
                    if "error" in response_json:
                        error = response_json["error"]
                        error_message = error.get("message", "No message")
                        logger.error(f"🚨 Gemini API 에러: {error_message}")
                        
                        # 필터링 관련 에러 감지 (Java와 동일)
                        if any(keyword in error_message.lower() for keyword in ["blocked", "filter", "safety"]):
                            logger.error("🔒 콘텐츠 필터링으로 인한 생성 거부 감지!")
                            raise RuntimeError(f"콘텐츠 필터링으로 인한 이미지 생성 거부: {error_message}")
                    
                    raise RuntimeError("Gemini API candidates 필드 누락")
                
                candidates = response_json["candidates"]
                if len(candidates) == 0:
                    logger.error(f"❌ candidates 배열이 비어있음! (시도 {attempt})")
                    
                    # promptFeedback 확인 (필터링 정보)
                    if "promptFeedback" in response_json:
                        prompt_feedback = response_json["promptFeedback"]
                        logger.error(f"  - promptFeedback: {prompt_feedback}")
                        
                        if "blockReason" in prompt_feedback:
                            block_reason = prompt_feedback["blockReason"]
                            logger.error(f"🔒 프롬프트가 안전 필터에 의해 차단됨: {block_reason}")
                            raise RuntimeError(f"프롬프트 안전 필터 차단: {block_reason}")
                    
                    raise RuntimeError("Gemini API candidates 배열 비어있음")
                
                logger.info(f"candidates 개수: {len(candidates)}")
                candidate = candidates[0]
                
                # candidate의 필터링 상태 확인 (Java와 동일)
                if "finishReason" in candidate:
                    finish_reason = candidate["finishReason"]
                    logger.info(f"finishReason: {finish_reason}")
                    
                    # 필터링으로 인한 중단 감지
                    if finish_reason == "SAFETY":
                        logger.error("🔒 콘텐츠가 안전 필터에 의해 차단됨!")
                        raise RuntimeError(f"SAFETY 필터 차단 - 유해 콘텐츠 감지: {finish_reason}")
                
                # content 및 parts 확인 (Java와 동일)
                if "content" not in candidate:
                    logger.error("❌ candidate에 'content' 필드 없음!")
                    raise RuntimeError("Gemini API candidate content 누락")
                
                candidate_content = candidate["content"]
                if "parts" not in candidate_content:
                    logger.error("❌ content에 'parts' 필드 없음!")
                    raise RuntimeError("Gemini API content parts 누락")
                
                parts = candidate_content["parts"]
                logger.info(f"parts 개수: {len(parts)}")
                
                # 각 part 검사 (Java와 동일)
                for i, current_part in enumerate(parts):
                    logger.info(f"=== Part {i} 분석 ===")
                    
                    # inlineData 방식 확인
                    if "inlineData" in current_part:
                        inline_data = current_part["inlineData"]
                        
                        if "data" in inline_data:
                            base64_data = inline_data["data"]
                            logger.info("✅ SUCCESS: Base64 이미지 데이터 발견!")
                            logger.info(f"Base64 데이터 길이: {len(base64_data)} 글자")
                            
                            image_bytes = base64.b64decode(base64_data)
                            logger.info(f"✅ Gemini API 성공 (시도 {attempt}) ===")
                            logger.info(f"최종 이미지 크기: {len(image_bytes)} bytes")
                            return image_bytes
                
                logger.error(f"❌ 모든 parts를 검사했지만 이미지 데이터를 찾을 수 없음! (시도 {attempt})")
                raise RuntimeError("Gemini에서 이미지 데이터를 찾을 수 없음")
                
            except Exception as e:
                logger.error(f"❌ Gemini API 시도 {attempt} 실패: {str(e)}")
                
                if attempt == max_retries + 1:
                    logger.error("🚨 Gemini API 최종 실패 - RuntimeException 던짐")
                    raise RuntimeError(f"이미지 생성 최종 실패: {str(e)}")
                
                # 짧은 대기 (500ms * attempt)
                wait_time = 0.5 * attempt
                logger.info(f"⏰ {wait_time}s 대기 후 재시도...")
                
                try:
                    await asyncio.sleep(wait_time)
                except Exception:
                    logger.error("대기 중 인터럽트 발생")
                    raise RuntimeError(f"이미지 생성 인터럽트: {str(e)}")
        
        raise RuntimeError("Gemini API 재시도 로직 오류")  # fallback
    
    async def _call_gemini_with_retry_for_cover(self, prompt: str, max_retries: int) -> bytes:
        """재시도 로직이 포함된 Gemini API 호출 (책 표지용) - Java callGeminiWithRetryForCover 로직 정확히 복제"""
        logger.info(f"=== Gemini 2.5 Flash Image Preview API 호출 시작 (최대 {max_retries + 1}회 시도) - 책 표지 ===")
        logger.info(f"입력 프롬프트: [{prompt}] (길이: {len(prompt)}자)")
        
        for attempt in range(1, max_retries + 2):  # 1부터 시작
            try:
                logger.info(f"🔄 Gemini API 시도 {attempt}/{max_retries + 1} - 책 표지")
                
                # Gemini 2.5 Flash Image Preview API 요청 구조 (Java와 동일)
                full_prompt = GEMINI_IMAGE_PROMPT_TEMPLATE.format(prompt=prompt)
                
                request_body = {
                    "contents": [{
                        "parts": [{
                            "text": full_prompt
                        }]
                    }]
                }
                
                logger.info(f"Gemini API 전송 프롬프트: [{full_prompt}] (길이: {len(full_prompt)}자)")
                
                # Gemini 2.5 Flash Image Preview API 호출
                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key={GEMINI_API_KEY}"
                
                logger.info(f"Gemini API URL: {api_url[:api_url.rfind('key=') + 4]}***")
                logger.info("Gemini API 요청 전송 중...")
                
                async with httpx.AsyncClient(timeout=180.0) as client:  # 책 표지는 더 긴 타임아웃
                    response = await client.post(api_url, json=request_body)
                    
                    if response.status_code >= 400:
                        error_text = response.text
                        logger.error(f"Gemini API 에러: {error_text}")
                        raise RuntimeError(f"Gemini API 에러: {error_text}")
                        
                    response_json = response.json()
                
                logger.info("=== Gemini API 응답 수신 ===")
                logger.info("응답 상태: 응답 있음")
                
                # 디버깅: 실제 응답 내용 로깅 (표지용)
                logger.info(f"🔍 Gemini API 실제 응답 내용 (표지): {response_json}")
                
                if not response_json:
                    logger.error("Gemini API에서 null 응답 수신")
                    raise RuntimeError("Gemini API null 응답")
                
                # 응답 파싱은 _call_gemini_with_retry와 동일한 로직 사용
                logger.info("=== Gemini API 응답 JSON 분석 ===")
                
                # candidates 확인
                if "candidates" not in response_json:
                    logger.error(f"❌ Gemini API 응답에 'candidates' 필드 없음! (시도 {attempt})")
                    
                    # 에러 정보 상세 분석
                    if "error" in response_json:
                        error = response_json["error"]
                        error_message = error.get("message", "No message")
                        logger.error(f"🚨 Gemini API 에러: {error_message}")
                        
                        # 필터링 관련 에러 감지
                        if any(keyword in error_message.lower() for keyword in ["blocked", "filter", "safety"]):
                            logger.error("🔒 콘텐츠 필터링으로 인한 생성 거부 감지!")
                            raise RuntimeError(f"콘텐츠 필터링으로 인한 이미지 생성 거부: {error_message}")
                    
                    raise RuntimeError("Gemini API candidates 필드 누락")
                
                candidates = response_json["candidates"]
                if len(candidates) == 0:
                    logger.error(f"❌ candidates 배열이 비어있음! (시도 {attempt})")
                    
                    # promptFeedback 확인 (필터링 정보)
                    if "promptFeedback" in response_json:
                        prompt_feedback = response_json["promptFeedback"]
                        logger.error(f"  - promptFeedback: {prompt_feedback}")
                        
                        if "blockReason" in prompt_feedback:
                            block_reason = prompt_feedback["blockReason"]
                            logger.error(f"🔒 프롬프트가 안전 필터에 의해 차단됨: {block_reason}")
                            raise RuntimeError(f"프롬프트 안전 필터 차단: {block_reason}")
                    
                    raise RuntimeError("Gemini API candidates 배열 비어있음")
                
                logger.info(f"candidates 개수: {len(candidates)}")
                candidate = candidates[0]
                
                # candidate의 필터링 상태 확인
                if "finishReason" in candidate:
                    finish_reason = candidate["finishReason"]
                    logger.info(f"finishReason: {finish_reason}")
                    
                    # 필터링으로 인한 중단 감지
                    if finish_reason == "SAFETY":
                        logger.error("🔒 콘텐츠가 안전 필터에 의해 차단됨!")
                        raise RuntimeError(f"SAFETY 필터 차단 - 유해 콘텐츠 감지: {finish_reason}")
                
                # content 및 parts 확인
                if "content" not in candidate:
                    logger.error("❌ candidate에 'content' 필드 없음!")
                    raise RuntimeError("Gemini API candidate content 누락")
                
                candidate_content = candidate["content"]
                if "parts" not in candidate_content:
                    logger.error("❌ content에 'parts' 필드 없음!")
                    raise RuntimeError("Gemini API content parts 누락")
                
                parts = candidate_content["parts"]
                logger.info(f"parts 개수: {len(parts)}")
                
                # 각 part 검사
                for i, current_part in enumerate(parts):
                    logger.info(f"=== Part {i} 분석 ===")
                    
                    # inlineData 방식 확인
                    if "inlineData" in current_part:
                        inline_data = current_part["inlineData"]
                        
                        if "data" in inline_data:
                            base64_data = inline_data["data"]
                            logger.info("✅ SUCCESS: Base64 이미지 데이터 발견!")
                            logger.info(f"Base64 데이터 길이: {len(base64_data)} 글자")
                            
                            image_bytes = base64.b64decode(base64_data)
                            logger.info(f"✅ Gemini API 성공 (시도 {attempt}) - 책 표지 ===")
                            logger.info(f"최종 이미지 크기: {len(image_bytes)} bytes")
                            return image_bytes
                
                logger.error(f"❌ 모든 parts를 검사했지만 이미지 데이터를 찾을 수 없음! (시도 {attempt})")
                raise RuntimeError("Gemini에서 이미지 데이터를 찾을 수 없음")
                
            except Exception as e:
                logger.error(f"❌ Gemini API 시도 {attempt} 실패 - 책 표지: {str(e)}")
                
                if attempt == max_retries + 1:
                    logger.error("🚨 Gemini API 최종 실패 - 책 표지 - RuntimeException 던짐")
                    raise RuntimeError(f"표지 이미지 생성 최종 실패: {str(e)}")
                
                # 짧은 대기 (500ms * attempt)
                wait_time = 0.5 * attempt
                logger.info(f"⏰ {wait_time}s 대기 후 재시도...")
                
                try:
                    await asyncio.sleep(wait_time)
                except Exception:
                    logger.error("대기 중 인터럽트 발생")
                    raise RuntimeError(f"표지 이미지 생성 인터럽트: {str(e)}")
        
        raise RuntimeError("Gemini API 재시도 로직 오류 - 책 표지")  # fallback


# 전역 서비스 인스턴스
image_service = UnifiedImageService()

@app.post("/generate-scene")
async def generate_scene_image(request: SceneGenerationRequest):
    """장면 이미지 생성 API - 바이너리 이미지 데이터 반환"""
    try:
        image_data = await image_service.generate_scene_image(request)
        return Response(content=image_data, media_type="image/png")
    except Exception as e:
        logger.error(f"장면 이미지 생성 API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@app.post("/generate-cover")
async def generate_book_cover(request: BookCoverGenerationRequest):
    """책 표지 생성 API - 제목과 바이너리 이미지 데이터 반환"""
    try:
        title, image_data = await image_service.generate_book_cover(request)
        return {
            "title": title,
            "image_data": base64.b64encode(image_data).decode('utf-8'),
            "success": True,
            "message": "책 표지 생성 성공"
        }
    except Exception as e:
        logger.error(f"책 표지 생성 API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Unified Image Generation Service",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    logger.info("=== Long Ago 통합 이미지 생성 서비스 시작 ===")
    logger.info(f"OpenAI API 키 설정됨: {bool(OPENAI_API_KEY)}")
    logger.info(f"Gemini API 키 설정됨: {bool(GEMINI_API_KEY)}")
    logger.info("바이너리 이미지 데이터 반환 모드 - S3 업로드는 Java에서 처리")
    
    uvicorn.run(app, host="0.0.0.0", port=8190)