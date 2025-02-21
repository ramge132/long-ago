import copy
import json
import asyncio
import os
import glob
import random
import shutil  # 폴더 삭제용
from urllib import request as urlrequest
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# --- 환경 설정 ---
COMFYUI_IP = "127.0.0.1:18188"
WORKFLOW_PATH = "/workspace/ComfyUI/workflow/taeyeong_v11.json"
OUTPUT_DIR = "/workspace/ComfyUI/output"
RANDOM_SEED = True         # True이면 seed를 랜덤으로 생성, False이면 고정 seed 사용
FIXED_SEED = 553653017491233

def load_workflow():
    try:
        with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
            workflow = json.load(f)
        print("✅ 워크플로우 파일 로드 완료!")
        return workflow
    except Exception as e:
        print(f"❌ 워크플로우 로드 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="워크플로우 로드 실패")

workflow_template = load_workflow()

# --- 세션 데이터 관리 ---
# session_data: 키는 session_id, 값은 { count, prev_prompt, summary, description, game_mode, user_sentence }
session_data = {}

class RequestData(BaseModel):
    session_id: str
    game_mode: int
    user_sentence: str
    status: int  # 0: 진행, 1: 종료, 2: 전원 패배

@app.post("/generate")
async def generate(data: RequestData):
    session_id = data.session_id
    game_mode = data.game_mode
    user_sentence = data.user_sentence
    status = data.status

    print(f"🔹 [FastAPI] 요청 데이터 - session_id: {session_id}, game_mode: {game_mode}, user_sentence: {user_sentence}, status: {status}")

    # 지원하지 않는 모드 체크 (0~8만 허용)
    valid_modes = set(range(9))
    if game_mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 game_mode: {game_mode}")

    # --- 세션 데이터 업데이트 ---
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

    print("🔹 [Session Data] " + json.dumps(session_data, indent=4, ensure_ascii=False))

    # 전원 패배(status == 2) 시: 폴더와 session_data 삭제 후 에러 반환
    if status == 2:
        folder_to_delete = os.path.join(OUTPUT_DIR, session_id)
        if os.path.exists(folder_to_delete):
            shutil.rmtree(folder_to_delete)
        if session_id in session_data:
            del session_data[session_id]
        raise HTTPException(status_code=400, detail="전원 패배")
    
    # --- 출력 폴더 생성 ---
    session_folder = os.path.join(OUTPUT_DIR, session_id)
    if not os.path.exists(session_folder):
        os.makedirs(session_folder, exist_ok=True)
    prefix = os.path.join(session_folder, f"{session_id}_{session_data[session_id]['count']}")

    # --- 워크플로우 구성 ---
    workflow = copy.deepcopy(workflow_template)
    
    # Seed 설정: RANDOM_SEED가 True이면 랜덤 seed, 아니면 고정 seed 사용
    if RANDOM_SEED:
        seed_value = random.randint(0, 10**15)
    else:
        seed_value = FIXED_SEED
    if "34" in workflow and "seed" in workflow["34"]["inputs"]:
        workflow["34"]["inputs"]["seed"] = seed_value

    # === game_mode에 따른 수정 사항 적용 ===
    # 1. 노드26 (LoraLoader) 설정
    lora_config = {
        0: {"lora_name": "0_MJanime_Flux_LoRa_v3_Final.safetensors", "strength_model": 1},
        1: {"lora_name": "1_Cute_3d_Cartoon_Flux.safetensors",   "strength_model": 0.6},
        2: {"lora_name": "2_comic_strip_style_v2.safetensors",    "strength_model": 1},
        3: {"lora_name": "3_claymation-000012.safetensors",         "strength_model": 0.9},
        4: {"lora_name": "4_5yocrayon1_cap_d6a3e12-00031.safetensors","strength_model": 0.95},
        5: {"lora_name": "5_Pixel_Art_Flux.safetensors",            "strength_model": 0.7},
        6: {"lora_name": "6_ningraphix-00031.safetensors",          "strength_model": 1},
        7: {"lora_name": "7_macha1_cap_d6a3e12.safetensors",         "strength_model": 0.6},
        8: {"lora_name": "8_pp-storybook_rank2_bf16.safetensors",     "strength_model": 1},
    }
    workflow["26"]["inputs"]["lora_name"] = lora_config[game_mode]["lora_name"]
    workflow["26"]["inputs"]["strength_model"] = lora_config[game_mode]["strength_model"]

    # 2. 노드40 (AYL_API_Node) 입력값 설정
    workflow["40"]["inputs"]["previous_prompt"] = session_data[session_id]["prev_prompt"]
    workflow["40"]["inputs"]["summary_story"]   = session_data[session_id]["summary"]
    workflow["40"]["inputs"]["description"]     = session_data[session_id]["description"]

    # 3. 노드53, 54, 55 (ShowText 노드) 설정: 출력 텍스트 확인용
    if "53" in workflow:
        workflow["53"]["inputs"]["text"] = session_data[session_id]["prev_prompt"]
    if "54" in workflow:
        workflow["54"]["inputs"]["text"] = session_data[session_id]["summary"]
    if "55" in workflow:
        workflow["55"]["inputs"]["text"] = session_data[session_id]["description"]

    # 4. 노드39 (AYL_GGUF_Node)의 입력값 설정
    workflow["39"]["inputs"]["session_id"] = session_id
    workflow["39"]["inputs"]["game_mode"] = game_mode
    workflow["39"]["inputs"]["text"] = user_sentence  # 원본 문장 전달
    workflow["39"]["inputs"]["status"] = status

    # 5. 노드56 (Text Concatenate) 설정: game_mode에 따라 특정 텍스트 필드만 활성화
    # 활성화할 텍스트 필드와 해당 노드 번호 매핑 (0~8)
    text_node_mapping = {
        0: ("text_a", ["63", 0]),
        1: ("text_b", ["64", 0]),
        2: ("text_c", ["65", 0]),
        3: ("text_d", ["66", 0]),
        4: ("text_e", ["67", 0]),
        5: ("text_f", ["68", 0]),
        6: ("text_g", ["69", 0]),
        7: ("text_h", ["70", 0]),
        8: ("text_i", ["71", 0]),
    }
    # 모든 텍스트 필드를 비활성화(빈 문자열) 처리
    for key in ["text_a", "text_b", "text_c", "text_d", "text_e", "text_f", "text_g", "text_h", "text_i"]:
        workflow["56"]["inputs"][key] = ""
    # game_mode에 해당하는 텍스트 필드만 활성화
    field, node_ref = text_node_mapping[game_mode]
    workflow["56"]["inputs"][field] = node_ref
    # text_n는 항상 활성화 (AYL_GGUF_Node의 출력)
    workflow["56"]["inputs"]["text_n"] = ["39", 0]

    # 6. KSampler (노드34) steps 설정
    ksampler_steps = {
        0: 25,
        1: 30,
        2: 25,
        3: 30,
        4: 20,
        5: 25,
        6: 25,
        7: 20,
        8: 25,
    }
    if "34" in workflow and "inputs" in workflow["34"]:
        workflow["34"]["inputs"]["steps"] = ksampler_steps[game_mode]

    # 7. 노드32 (CLIPTextEncodeFlux) 설정: Text Concatenate 노드 56의 출력을 입력으로 사용
    workflow["32"]["inputs"]["clip_l"] = ("56", 0)
    workflow["32"]["inputs"]["t5xxl"] = ("56", 0)
    print(f"🔹 [Prompt 설정] clip_l: {workflow['32']['inputs']['clip_l']}")
    print(f"🔹 [Prompt 설정] t5xxl: {workflow['32']['inputs']['t5xxl']}")

    # 8. 노드9 (SaveImage) 설정
    workflow["9"]["inputs"]["filename_prefix"] = prefix

    # --- ComfyUI 서버에 워크플로우 전송 (이미지 생성 트리거) ---
    try:
        payload = {"prompt": workflow}
        payload_data = json.dumps(payload).encode("utf-8")
        print(f"🔹 [API 요청] ComfyUI 서버로 워크플로우 전송:\n{json.dumps(payload, indent=4, ensure_ascii=False)}")
        req = urlrequest.Request(f"http://{COMFYUI_IP}/prompt", data=payload_data, headers={"Content-Type": "application/json"})
        res = urlrequest.urlopen(req)
        print(f"✅ [API 응답] 상태 코드: {res.getcode()}")
    except Exception as e:
        print(f"❌ [API 오류] {str(e)}")
        if os.path.exists(session_folder):
            shutil.rmtree(session_folder)
        if session_id in session_data:
            del session_data[session_id]
        raise HTTPException(status_code=500, detail=str(e))
    
    # --- 이미지 생성 완료 대기 (최대 60초) ---
    image_bytes = None
    for _ in range(100):
        generated_images = glob.glob(prefix + "*.png")
        if generated_images:
            latest_image = sorted(generated_images)[-1]
            print(f"✅ [이미지 생성 완료] {latest_image}")
            with open(latest_image, "rb") as img_file:
                image_bytes = img_file.read()
            break
        await asyncio.sleep(2)
    
    if image_bytes is None:
        if os.path.exists(session_folder):
            shutil.rmtree(session_folder)
        if session_id in session_data:
            del session_data[session_id]
        print("❌ 이미지 생성 실패: 시간 초과")
        raise HTTPException(status_code=500, detail="Image generation failed: Timeout")
    
    # --- JSON 파일 읽어 session_data 업데이트 ---
    # AYL_GGUF_Node 내부에서 JSON 파일을 저장하도록 처리되었으므로,
    # 생성 후 일정 시간 대기하고 JSON 파일이 있으면 내용을 읽어서 session_data를 업데이트합니다.
    ayl_output_file = os.path.join(session_folder, "ayl_output.json")
    wait_time = 10  # 최대 10초 대기
    while wait_time > 0 and not os.path.exists(ayl_output_file):
        await asyncio.sleep(1)
        wait_time -= 1
    if os.path.exists(ayl_output_file):
        try:
            with open(ayl_output_file, "r", encoding="utf-8") as f:
                ayl_data = json.load(f)
            session_data[session_id]["prev_prompt"] = ayl_data.get("prev_prompt", "")
            session_data[session_id]["summary"] = ayl_data.get("summary", "")
            session_data[session_id]["description"] = ayl_data.get("description", "")
            print("🔹 [Session Data Updated]")
            print(json.dumps(session_data[session_id], indent=4, ensure_ascii=False))
        except Exception as e:
            print(f"❌ [Session Data Update Error] {str(e)}")
    else:
        print("❌ [Session Data Update] ayl_output.json 파일이 존재하지 않습니다.")
    
    # 게임 종료(status가 1 또는 2) 시: output 폴더와 session_data 삭제
    if status in (1, 2):
        if os.path.exists(session_folder):
            shutil.rmtree(session_folder)
        if session_id in session_data:
            del session_data[session_id]

    return Response(content=image_bytes, media_type="image/png")

if __name__ == "__main__":
    uvicorn.run("just_image:app", host="0.0.0.0", port=8189, reload=True)
