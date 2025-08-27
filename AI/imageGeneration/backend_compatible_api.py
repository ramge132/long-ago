"""
기존 백엔드와 100% 호환되는 API 엔드포인트
"""
import os
import json
import asyncio
import base64
import shutil
import boto3
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import uvicorn

from api_image_generator import APIImageGenerationSystem

app = FastAPI()

# 기존 백엔드와 동일한 요청 형식
class BackendCompatibleRequest(BaseModel):
    """기존 백엔드 SceneService가 보내는 형식과 동일"""
    input: Dict[str, Any]

# 새로운 API 시스템 초기화
api_system = APIImageGenerationSystem()
session_data: Dict[str, Dict[str, Any]] = {}

@app.post("/")
async def generate_image_backend_compatible(data: BackendCompatibleRequest):
    """
    기존 백엔드와 100% 호환되는 엔드포인트
    RunPod 형식 그대로 받아서 처리
    """
    try:
        # 기존 RunPod 형식에서 데이터 추출
        input_data = data.input
        session_id = input_data.get("session_id")
        game_mode = input_data.get("game_mode")
        user_sentence = input_data.get("user_sentence")
        status = input_data.get("status", 0)
        character_cards = input_data.get("character_cards", [])
        
        print(f"🔹 [호환 API] 요청 - session_id: {session_id}, game_mode: {game_mode}")
        print(f"🔹 [호환 API] user_sentence: {user_sentence}, status: {status}")
        
        # 전원 패배 처리
        if status == 2:
            if session_id in session_data:
                del session_data[session_id]
            raise HTTPException(status_code=400, detail="전원 패배")
        
        # 세션 데이터 관리
        if session_id not in session_data:
            session_data[session_id] = {
                "count": 1,
                "prev_prompt": "",
                "summary": "",
                "description": "",
                "game_mode": game_mode,
                "user_sentence": user_sentence
            }
        else:
            session_data[session_id]["count"] += 1
            session_data[session_id]["user_sentence"] = user_sentence
        
        # 새로운 API 시스템으로 이미지 생성
        image_bytes, updated_session_data = await api_system.generate_image(
            user_sentence, 
            game_mode, 
            session_data[session_id]
        )
        
        # 세션 데이터 업데이트
        session_data[session_id].update(updated_session_data)
        
        # 게임 종료 시 세션 정리
        if status in (1, 2):
            if session_id in session_data:
                del session_data[session_id]
        
        # 기존 백엔드가 기대하는 형식으로 응답
        if status == 1:
            # 책 표지 생성인 경우 - RunPod 형식 JSON 응답
            response_data = {
                "id": f"job-{session_id}",
                "status": "COMPLETED",
                "output": {
                    "filename": f"{session_id}_cover.png",
                    "s3_url": f"https://example.s3.amazonaws.com/{session_id}_cover.png",
                    "image": base64.b64encode(image_bytes).decode('utf-8'),
                    "media_type": "image/png",
                    "character_cards": character_cards,
                    "session_info": {
                        "count": session_data[session_id]["count"] if session_id in session_data else 1,
                        "summary": updated_session_data.get("summary", "")
                    }
                }
            }
            return response_data
        else:
            # 일반 이미지 생성인 경우 - 바이트 배열 직접 반환 (기존 방식)
            return Response(content=image_bytes, media_type="image/png")
            
    except Exception as e:
        print(f"❌ [호환 API 오류] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{job_id}")
async def check_job_status(job_id: str):
    """
    RunPod 상태 확인 API 호환성을 위한 엔드포인트
    """
    return {
        "id": job_id,
        "status": "COMPLETED",
        "output": {
            "message": "Job completed successfully"
        }
    }

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "message": "Backend Compatible API System is running",
        "characters_loaded": len(api_system.character_manager.characters)
    }

if __name__ == "__main__":
    print("🚀 백엔드 호환 API 시스템 시작...")
    print("📡 기존 RunPod 엔드포인트와 100% 호환")
    
    # 기존 RunPod URL과 동일한 포트 사용
    uvicorn.run("backend_compatible_api:app", host="0.0.0.0", port=8188, reload=True)