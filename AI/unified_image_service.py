"""
통합 이미지 생성 서비스
현재 Java에서 처리하던 모든 이미지 생성 로직을 하나로 통합
"""

import os
import json
import base64
import asyncio
import boto3
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import uvicorn
import requests
from PIL import Image
import io

# OpenAI 및 Gemini 클라이언트
from openai import OpenAI
import google.generativeai as genai

app = FastAPI(title="Unified Image Generation Service", version="2.0.0")

# 환경변수 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION", "ap-northeast-2")

# API 클라이언트 초기화
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
genai.configure(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=S3_REGION
) if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY else None

# 스타일 정의 (Java와 동일)
DRAWING_STYLES = [
    "애니메이션 스타일", "3D 카툰 스타일", "코믹 스트립 스타일", "클레이메이션 스타일",
    "크레용 드로잉 스타일", "픽셀 아트 스타일", "미니멀리스트 일러스트", "수채화 스타일", "스토리북 일러스트"
]

# 요청/응답 모델
class SceneGenerationRequest(BaseModel):
    gameId: str
    userId: str
    userPrompt: str
    turn: int
    drawingStyle: int = 0
    isEnding: bool = False

class BookCoverGenerationRequest(BaseModel):
    storyContent: str
    drawingStyle: int = 0

class SceneGenerationResponse(BaseModel):
    success: bool
    imageUrl: Optional[str] = None
    message: str
    gptPrompt: Optional[str] = None

class BookCoverGenerationResponse(BaseModel):
    success: bool
    title: Optional[str] = None
    imageUrl: Optional[str] = None
    message: str

class UnifiedImageService:
    """통합 이미지 생성 서비스 클래스"""
    
    def __init__(self):
        self.openai_client = openai_client
        self.s3_client = s3_client
        
    async def generate_scene_image(self, request: SceneGenerationRequest) -> SceneGenerationResponse:
        """게임 장면 이미지 생성 (현재 SceneService 로직과 동일)"""
        try:
            # 1단계: GPT로 프롬프트 변환
            gpt_prompt = await self._generate_prompt_with_gpt(
                request.userPrompt, 
                request.drawingStyle, 
                request.isEnding
            )
            
            # 2단계: Gemini로 이미지 생성
            image_data = await self._generate_image_with_gemini(gpt_prompt)
            
            # 3단계: S3에 업로드
            object_key = f"{request.gameId}/{request.turn}.png"
            image_url = await self._upload_to_s3(image_data, object_key)
            
            return SceneGenerationResponse(
                success=True,
                imageUrl=image_url,
                message="이미지 생성 성공",
                gptPrompt=gpt_prompt
            )
            
        except Exception as e:
            return SceneGenerationResponse(
                success=False,
                message=f"이미지 생성 실패: {str(e)}"
            )
    
    async def generate_book_cover(self, request: BookCoverGenerationRequest) -> BookCoverGenerationResponse:
        """책 표지 생성 (현재 GameService 로직과 동일)"""
        try:
            # 1단계: GPT로 책 제목 생성
            book_title = await self._generate_book_title(request.storyContent)
            
            # 2단계: Gemini로 표지 이미지 생성
            cover_prompt = self._create_cover_prompt(book_title, request.drawingStyle)
            image_data = await self._generate_image_with_gemini(cover_prompt)
            
            # 3단계: S3에 업로드 (표지는 0.png)
            book_id = f"book_{hash(request.storyContent) % 1000000:06d}"  # 임시 책 ID
            object_key = f"{book_id}/0.png"
            image_url = await self._upload_to_s3(image_data, object_key)
            
            return BookCoverGenerationResponse(
                success=True,
                title=book_title,
                imageUrl=image_url,
                message="책 표지 생성 성공"
            )
            
        except Exception as e:
            return BookCoverGenerationResponse(
                success=False,
                message=f"책 표지 생성 실패: {str(e)}"
            )
    
    async def _generate_prompt_with_gpt(self, user_sentence: str, game_mode: int, is_ending: bool) -> str:
        """GPT로 프롬프트 변환 (Java callGPTWithRetry 로직과 동일)"""
        style = DRAWING_STYLES[game_mode] if game_mode < len(DRAWING_STYLES) else DRAWING_STYLES[0]
        
        prompt_instruction = (
            f"결말: {user_sentence}. 이 문장을 {style} 스타일의 이미지로 만들기 위한 핵심 영어 키워드를 나열해줘." 
            if is_ending else 
            f"문장: {user_sentence}. 이 문장을 {style} 스타일의 이미지로 만들기 위한 핵심 영어 키워드를 나열해줘."
        )
        
        # GPT-5 Responses API 호출 (Java와 동일한 구조)
        response = self.openai_client.chat.completions.create(
            model="gpt-5-nano",  # Java에서 사용하는 모델과 동일
            messages=[{"role": "user", "content": prompt_instruction}],
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
    
    async def _generate_book_title(self, story_content: str) -> str:
        """GPT로 책 제목 생성 (Java generateBookTitle 로직과 동일)"""
        # 길이 제한 (200자) - Java와 동일
        if len(story_content) > 200:
            story_content = story_content[:200]
        
        prompt = f"다음 스토리를 10자 이내의 창의적인 제목으로 만들어주세요. 다른 설명 없이 제목만 말해주세요. 스토리: {story_content}"
        
        response = self.openai_client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        
        return response.choices[0].message.content.strip()
    
    def _create_cover_prompt(self, book_title: str, drawing_style: int) -> str:
        """책 표지 프롬프트 생성 (Java와 동일)"""
        style = DRAWING_STYLES[drawing_style] if drawing_style < len(DRAWING_STYLES) else DRAWING_STYLES[0]
        
        return (f"Create a beautiful book cover for a story titled '{book_title}'. "
                f"Style: {style}. The cover should be artistic, captivating, and suitable for a storybook. "
                f"Include the title text elegantly integrated into the design.")
    
    async def _generate_image_with_gemini(self, prompt: str) -> bytes:
        """Gemini로 이미지 생성 (Java callGeminiWithRetryForCover 로직과 동일)"""
        full_prompt = f"Generate an image: {prompt} portrait orientation, 9:16 aspect ratio, vertical format, 720x1280 resolution"
        
        # 재시도 로직 (Java와 동일하게 최대 5회)
        for attempt in range(1, 6):
            try:
                # Gemini API 직접 호출 (Java와 동일한 방식)
                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key={GEMINI_API_KEY}"
                
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{
                        "parts": [{"text": full_prompt}]
                    }]
                }
                
                response = requests.post(api_url, headers=headers, json=payload, timeout=180)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 이미지 데이터 추출 및 변환
                    if (result.get("candidates") and 
                        len(result["candidates"]) > 0 and 
                        result["candidates"][0].get("content") and
                        result["candidates"][0]["content"].get("parts") and
                        len(result["candidates"][0]["content"]["parts"]) > 0):
                        
                        part = result["candidates"][0]["content"]["parts"][0]
                        if "inlineData" in part and "data" in part["inlineData"]:
                            image_data = base64.b64decode(part["inlineData"]["data"])
                            return image_data
                
                raise Exception(f"Gemini 응답 형식 오류: {response.text}")
                
            except Exception as e:
                if attempt == 5:  # 마지막 시도
                    raise Exception(f"Gemini 이미지 생성 실패 (5회 시도): {str(e)}")
                await asyncio.sleep(2)  # 2초 대기 후 재시도
        
        raise Exception("Gemini에서 이미지 생성 실패")
    
    async def _upload_to_s3(self, image_data: bytes, object_key: str) -> str:
        """S3에 이미지 업로드 (Java uploadImageToS3 로직과 동일)"""
        if not self.s3_client:
            raise Exception("S3 클라이언트가 초기화되지 않음")
        
        self.s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=object_key,
            Body=image_data,
            ContentType='image/png'
        )
        
        # HTTPS URL 반환 (Java baseUrl 로직과 동일)
        return f"https://longago.io/images/s3/downloadFromS3?objectKey={object_key}"

# 서비스 인스턴스 생성
image_service = UnifiedImageService()

# API 엔드포인트
@app.post("/generate-scene", response_model=SceneGenerationResponse)
async def generate_scene_endpoint(request: SceneGenerationRequest):
    """게임 장면 이미지 생성 API"""
    return await image_service.generate_scene_image(request)

@app.post("/generate-cover", response_model=BookCoverGenerationResponse)
async def generate_cover_endpoint(request: BookCoverGenerationRequest):
    """책 표지 생성 API"""
    return await image_service.generate_book_cover(request)

@app.get("/health")
async def health_check():
    """헬스체크"""
    return {"status": "healthy", "service": "unified_image_service", "version": "2.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8190)