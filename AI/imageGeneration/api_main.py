import os
import json
import asyncio
import base64
import shutil
import boto3
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import uvicorn

from api_image_generator import APIImageGenerationSystem

app = FastAPI()

# AWS S3 설정 (환경변수에서 가져오기)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# S3 클라이언트 초기화
s3_client = None
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and S3_BUCKET_NAME:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

# 출력 디렉토리 설정
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# API 이미지 생성 시스템 초기화
api_system = APIImageGenerationSystem()

# 세션 데이터 저장소
session_data: Dict[str, Dict[str, Any]] = {}

class RequestData(BaseModel):
    session_id: str
    game_mode: int
    user_sentence: str
    status: int  # 0: 진행, 1: 종료, 2: 전원 패배

@app.post("/generate")
async def generate_image_api(data: RequestData):
    """
    새로운 API 기반 이미지 생성 엔드포인트
    """
    session_id = data.session_id
    game_mode = data.game_mode
    user_sentence = data.user_sentence
    status = data.status

    print(f"🔹 [API] 요청 데이터 - session_id: {session_id}, game_mode: {game_mode}, user_sentence: {user_sentence}, status: {status}")

    # 지원하지 않는 모드 체크 (0~8만 허용)
    valid_modes = set(range(9))
    if game_mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 game_mode: {game_mode}")

    # 전원 패배(status == 2) 시: 폴더와 session_data 삭제 후 에러 반환
    if status == 2:
        folder_to_delete = os.path.join(OUTPUT_DIR, session_id)
        if os.path.exists(folder_to_delete):
            shutil.rmtree(folder_to_delete)
        if session_id in session_data:
            del session_data[session_id]
        raise HTTPException(status_code=400, detail="전원 패배")

    # 세션 데이터 초기화 또는 업데이트
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

    print("🔹 [Session Data] " + json.dumps(session_data[session_id], indent=2, ensure_ascii=False))

    # 출력 폴더 생성
    session_folder = os.path.join(OUTPUT_DIR, session_id)
    os.makedirs(session_folder, exist_ok=True)
    
    try:
        # API 기반 이미지 생성
        print("🔹 [API 이미지 생성] 시작...")
        image_bytes, updated_session_data = await api_system.generate_image(
            user_sentence, 
            game_mode, 
            session_data[session_id]
        )
        
        # 세션 데이터 업데이트
        session_data[session_id].update(updated_session_data)
        
        # 이미지를 로컬에 저장
        image_filename = f"{session_id}_{session_data[session_id]['count']}.png"
        image_path = os.path.join(session_folder, image_filename)
        
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        print(f"✅ [로컬 저장] {image_path}")
        
        # S3에 업로드 (설정되어 있는 경우)
        s3_url = None
        if s3_client:
            try:
                s3_key = f"images/{session_id}/{image_filename}"
                s3_client.put_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=s3_key,
                    Body=image_bytes,
                    ContentType='image/png'
                )
                s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
                print(f"✅ [S3 업로드] {s3_url}")
            except Exception as e:
                print(f"⚠️ [S3 업로드 실패] {e}")
        
        # 세션 데이터를 JSON 파일로 저장
        session_data_file = os.path.join(session_folder, "session_data.json")
        with open(session_data_file, 'w', encoding='utf-8') as f:
            json.dump(session_data[session_id], f, ensure_ascii=False, indent=2)
        
        print("✅ [API 이미지 생성 완료]")
        
    except Exception as e:
        print(f"❌ [API 이미지 생성 실패] {str(e)}")
        # 실패 시 폴더 정리
        if os.path.exists(session_folder):
            shutil.rmtree(session_folder)
        if session_id in session_data:
            del session_data[session_id]
        raise HTTPException(status_code=500, detail=str(e))

    # 게임 종료(status가 1 또는 2) 시: output 폴더와 session_data 삭제
    if status in (1, 2):
        if os.path.exists(session_folder):
            shutil.rmtree(session_folder)
        if session_id in session_data:
            del session_data[session_id]

    # 이미지를 응답으로 반환
    return Response(content=image_bytes, media_type="image/png")

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "message": "API Image Generation System is running",
        "characters_loaded": len(api_system.character_manager.characters),
        "available_characters": api_system.character_manager.get_all_character_names()
    }

@app.get("/characters")
async def get_characters():
    """사용 가능한 캐릭터 목록 반환"""
    characters = {}
    for name, character in api_system.character_manager.characters.items():
        characters[name] = {
            "name": character.name,
            "prompt": character.prompt,
            "image_available": os.path.exists(character.image_path)
        }
    return characters

@app.post("/test")
async def test_generation():
    """테스트용 이미지 생성 엔드포인트"""
    test_data = RequestData(
        session_id="test_session",
        game_mode=0,
        user_sentence="아름다운 숲속에 햇빛이 비치고 있다",
        status=0
    )
    
    return await generate_image_api(test_data)

if __name__ == "__main__":
    print("🚀 API 기반 이미지 생성 시스템을 시작합니다...")
    print(f"📁 출력 디렉토리: {OUTPUT_DIR}")
    print(f"🎭 로드된 캐릭터 수: {len(api_system.character_manager.characters)}")
    print(f"🎨 사용 가능한 캐릭터: {', '.join(api_system.character_manager.get_all_character_names())}")
    
    # 환경변수 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️ GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    if not s3_client:
        print("⚠️ AWS S3 설정이 완료되지 않았습니다. 이미지는 로컬에만 저장됩니다.")
    
    uvicorn.run("api_main:app", host="0.0.0.0", port=8190, reload=True)