import os
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from llama_cpp import Llama
import folder_paths
import gc
import torch

# 환경설정
GLOBAL_Instruct_MODEL_DIR = os.path.join(folder_paths.models_dir, "LLM_instruct_models")
GLOBAL_GGUF_MODEL_DIR = os.path.join(folder_paths.models_dir, "LLM_gguf_models")

LOADED_MODELS = {}
SUMMARY_STORY = ""
PREVIOUS_PROMPT = ""
DESCRIPTION = ""

# 모델 언로드 기능 제어 플래그 (True로 설정하면, 사용 후 모델을 언로드합니다)
ENABLE_MODEL_UNLOAD = True  # 필요에 따라 주석 처리하거나 값을 변경하세요.

STORY_PROMPT = (
    "You are an AI assistant specialized in summarizing stories summarized in English and Korean stories currently entered. "
    "Your mission is to fully grasp the context of the summarized story and the Korean story currently entered, and then update the summarized English story. "
    "1. Mandatory Format: You must print only the summary story. "
    "2. Summarization of Inputs: - Continuously build a coherent summary of the story based on all user inputs up to the current point. "
    "   - Ensure that each subject appears only once in the [Subject] component, eliminating any duplicates. "
    "3. Missing or Partial Information: - If the user’s input lacks certain components (e.g., no explicit Time), use context from the summarized story to maintain a natural, cohesive narrative. "
    "4. Strict Limitations: - Do not introduce new story elements beyond what the user provides. "
    "   - Do not modify or extend the user’s narrative beyond summarization. "
    "   - Use only the content explicitly stated by the user, plus any relevant context from the summarized story to fill in missing details. "
    "# Important: - Add new information without ever deleting existing information. "
    "- Type of Input: Summarized story, current user input. "
    "- Output format: a summary of the summarized story and the current user's input."
)

DESCRIPTION_PROMPT = (    
    """
    You are an AI that synthesizes input data to produce an up-to-date, concise, and detailed 'Description' in English.
    
    Follow these structured steps:
    
    1. Main Subjects:
       - Identify all key subjects (characters, animals, objects).
       - For each subject, you MUST include the following sub-points:
         * Physical/External Features:
           - Keep the consistent external traits from older data (e.g., clothing style, color scheme, weapons/items, basic body shape).
           - Only remove or modify these if the newest user input explicitly changes them.
         * Emotional Expressions:
           - Overwrite older emotional states with the newest user input. 
           - If there's any conflict, the latest info prevails.
         * Actions/Poses:
           - Similarly, disregard older action/pose details unless they remain valid and do not contradict new info.
           - Focus on the new or current actions the subject is taking as per the latest input.
         * Auditory Cues: 
           - Mention relevant sounds if the newest input or scene context calls for it (growling, rustling, footsteps, etc.).
         * Additional Details (optional):
           - Only if relevant. E.g., symbolic items, small environment interactions (dust, debris). 
           - Do not duplicate old details that are no longer relevant.
         * Relative Positioning:
           - This is CRITICAL for multiple characters. Indicate precisely how each subject is positioned relative to others (foreground, background, left/right, distance, etc.).
           - If the newest input changes the subject’s location, update accordingly and remove outdated references.
    
    2. Environment:
       - Briefly describe location (forest, city, battlefield, etc.), time/weather, and dynamic elements (shifting shadows, falling leaves, etc.).
       - Use older environment details ONLY if still valid. Remove duplicates or contradictory info.
    
    3. Mood & Narrative:
       - Reflect the overall atmosphere and how the new user input changes or intensifies it.
       - Describe tensions, relationships, conflicts, or potential resolutions, but focus on the immediate scenario. 
       - Do NOT re-summarize the entire past storyline—only keep what is relevant for the current moment.
    
    4. Formatting & Constraints:
       - Structure your output in sections: Main Subjects (with the sub-points for each subject), Environment, Mood & Narrative.
       - Do NOT create an overall structure summary or retell the entire past events.
       - If older details conflict with the newest user input, remove or revise them. 
       - Keep the text concise, ensuring no repeated or redundant statements from previous descriptions.
       - The final goal is a coherent snapshot of the scene that prioritizes the latest user input for all dynamic aspects (emotion, action, position).
    
    IMPORTANT:
    - You will receive a 'Previous Description' plus new user input. 
    - Extract only the stable external features from older data, and override all emotional/positional/action details with the new input.
    - This ensures a fresh, updated Description without outdated or duplicate info.
    """
)


IMAGE_PROMPT = (
    """
    You are an AI that takes the newly updated 'Description' and converts it into a single ultra-detailed cinematic scene in English.
    
    Please adhere to the following:
    
    1. Input Description:
       - The Description already has each subject's current emotional state, actions/poses, relative positioning, and any relevant environment or mood details.
       - Respect these updated details strictly. If older references conflict, ignore them.
    
    2. Output Format:
       - Produce exactly ONE cohesive paragraph.
       - Begin with: "ultra-detailed cinematic scene," 
       - Then depict the scenario with strong, dynamic verbs and vivid sensory details (motion blur, lighting, sounds, environmental interactions).
    
    3. Key Instructions:
       - Preserve each subject’s external appearance from the updated Description (e.g., clothing style, color, weapons).
       - Use the newest emotional expressions, actions, poses, and relative positions as given.
       - Ensure that multiple subjects do not merge; maintain their distinct positions via consistent references (e.g., "in the foreground," "to the left," "several paces away," etc.).
       - Highlight transitional motion effects (dust trails, shockwaves, etc.) and emphasize changes signaled by the latest input.
    
    4. Constraints:
       - DO NOT repeat older or contradictory text from previous versions. 
       - Avoid bullet points or separate headings—only one cinematic paragraph.
       - If there's any mention in the updated Description about changes to a subject’s state or location, reflect that precisely. 
       - The focus is on the current moment. Avoid rehashing prior events or extended backstory.
    
    Goal:
    - Deliver a powerful, immersive snapshot that shows exactly how the scene looks and feels after the latest changes, with correct subject positions, actions, and emotions.
    """
)


class BaseAYL_Node:
    def summary_story(self, story, user_input: str):
        combined_input = f"Story_summary: {story}\nUser_Input: {user_input}"
        messages = [
            {"role": "system", "content": STORY_PROMPT},
            {"role": "user", "content": combined_input}
        ]
        return self.generate_model_output(messages)

    def generate_description(self, story, description, user_input: str) -> str:
        combined_input = f"Story summary: {story}\nDescription: {description}\nCurrent story: {user_input}"
        messages = [
            {"role": "system", "content": DESCRIPTION_PROMPT},
            {"role": "user", "content": combined_input}
        ]
        return self.generate_model_output(messages)

    def generate_image_prompt(self, story, description, pre_prompt, user_input: str):
        combined_input = (
            # f"Story summary: {story}\n"
            f"Description: {description}\n"
            # f"Previous Image Prompt: {pre_prompt}\n"
            f"Current story: {user_input}"
        )
        messages = [
            {"role": "system", "content": IMAGE_PROMPT},
            {"role": "user", "content": combined_input}
        ]
        return self.generate_model_output(messages)

    def generate_model_output(self, messages):
        raise NotImplementedError("Subclass load ERROR")

# AYL_API_Node (단순히 FastAPI에서 전달한 prev_prompt, summary, description을 넘겨주는 역할)
class AYL_API_Node:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "previous_prompt": ("STRING", {"multiline": True, "dynamicPrompt": True, "default": ""}),
                "summary_story": ("STRING", {"multiline": True, "dynamicPrompt": True, "default": ""}),
                "description": ("STRING", {"multiline": True, "dynamicPrompt": True, "default": ""}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }
    CATEGORY = "Yeonri/LLM"
    FUNCTION = "main"
    RETURN_TYPES = ("AYL_API",)
    RETURN_NAMES = ("ayl_api_node",)
    OUTPUT_NODE = True
    def main(self, previous_prompt="", summary_story="", description="", unique_id=None, extra_pnginfo=None):
        ayl_api_node = (previous_prompt, summary_story, description)
        return (ayl_api_node,)

# AYL_Node (예: Instruct 모델 사용, status 인자 포함)
class AYL_Node(BaseAYL_Node):
    @classmethod
    def INPUT_TYPES(cls):
        model_list = []
        if os.path.isdir(GLOBAL_Instruct_MODEL_DIR):
            model_dirs = [
                d for d in os.listdir(GLOBAL_Instruct_MODEL_DIR)
                if os.path.isdir(os.path.join(GLOBAL_Instruct_MODEL_DIR, d))
            ]
            model_list.extend(model_dirs)
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompt": True, "default": ""}),
                "model": (model_list,),
                "max_tokens": ("INT", {"default": 4096, "min": 10, "max": 8192}),
                "status": ("INT", {"default": 0, "min": 0, "max": 2})
            },
            "optional": {
                "ayl_api_node": ("AYL_API",),
            },
        }
    CATEGORY = "Yeonri/LLM"
    FUNCTION = "main"
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("output_prompt", "summary_story", "description")
    def main(self, text, model, max_tokens, status, ayl_api_node=None):
        global LOADED_MODELS, SUMMARY_STORY, PREVIOUS_PROMPT, DESCRIPTION
        model_path = os.path.join(GLOBAL_Instruct_MODEL_DIR, model)
        if not LOADED_MODELS:
            if os.path.isdir(model_path):
                snapshot_dir = os.path.join(model_path, "snapshots")
                if os.path.isdir(snapshot_dir):
                    subfolders = [
                        os.path.join(snapshot_dir, folder)
                        for folder in os.listdir(snapshot_dir)
                        if os.path.isdir(os.path.join(snapshot_dir, folder))
                    ]
                    if subfolders:
                        latest_snapshot = max(subfolders, key=os.path.getmtime)
                        print("Most recently received snapshot folder:", latest_snapshot)
                    else:
                        latest_snapshot = None
                        print("There are no subfolders within the snapshots folder.")
                else:
                    latest_snapshot = None
                    print("The snapshot directory does not exist:", snapshot_dir)
                if latest_snapshot is None:
                    raise ValueError("유효한 snapshot folder를 찾을 수 없습니다.")
                self.model = AutoModelForCausalLM.from_pretrained(
                    latest_snapshot,
                    torch_dtype="auto",
                    device_map="auto",
                )
                self.tokenizer = AutoTokenizer.from_pretrained(latest_snapshot)
                LOADED_MODELS[model] = (self.model, self.tokenizer)
            else:
                raise ValueError(f"Model path not found: {model_path}")
        if ayl_api_node:
            PREVIOUS_PROMPT = ayl_api_node[0]
            SUMMARY_STORY = ayl_api_node[1]
            DESCRIPTION = ayl_api_node[2]
        SUMMARY_STORY = self.summary_story(SUMMARY_STORY, text)
        DESCRIPTION = self.generate_description(DESCRIPTION, DESCRIPTION, text)
        if status == 0:
            output_prompt = self.generate_image_prompt(PREVIOUS_PROMPT, DESCRIPTION, PREVIOUS_PROMPT, text)
        elif status == 1:
            output_prompt = self.generate_cover_prompt(PREVIOUS_PROMPT, DESCRIPTION, text)
        else:
            output_prompt = self.generate_image_prompt(PREVIOUS_PROMPT, DESCRIPTION, PREVIOUS_PROMPT, text)
        return (output_prompt, SUMMARY_STORY, DESCRIPTION)
    def generate_cover_prompt(self, previous_prompt, description, user_input):
        cover_prompt = (
            "You are an AI assistant specialized in creating cover image prompts for story books. "
            "Based on the provided story summary and description, generate a cover image prompt in English. "
            "Also, provide a title for the story. "
            "Your response should first contain the title on the first line, followed by the cover prompt on the second line. "
            "Do not include any additional text."
        )
        combined_input = f"Story summary: {SUMMARY_STORY}\nDescription: {description}\nUser Input: {user_input}"
        messages = [
            {"role": "system", "content": cover_prompt},
            {"role": "user", "content": combined_input}
        ]
        return self.generate_model_output(messages)
    def generate_model_output(self, messages):
        text_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text_prompt], return_tensors="pt").to(self.model.device)
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=self.max_tokens
        )
        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response
    
# AYL_GGUF_Node (GGUF 모델 사용, session_id 추가 및 JSON 저장 부분 활성화)
class AYL_GGUF_Node(BaseAYL_Node):
    @classmethod
    def INPUT_TYPES(cls):
        model_list = []
        if os.path.isdir(GLOBAL_GGUF_MODEL_DIR):
            gguf_files = [
                file for file in os.listdir(GLOBAL_GGUF_MODEL_DIR)
                if file.endswith('.gguf')
            ]
            model_list.extend(gguf_files)
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompt": True, "default": ""}),
                "model": (model_list, ),
                "max_tokens": ("INT", {"default": 4096, "min": 10, "max": 8192}),
                "n_gpu_layers": ("INT", {"default": 10, "max": 1000}),
                "n_threads": ("INT", {"default": 50, "max": 50}),
                "status": ("INT", {"default": 0, "min": 0, "max": 2}),
                "session_id": ("STRING", {"default": ""})
            },
            "optional": {
                "ayl_api_node": ("AYL_API",),
            },
        }
    
    CATEGORY = "Yeonri/LLM"
    FUNCTION = "main"
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("output_prompt", "summary_story", "description")
    
    def main(self, text, model, max_tokens, n_gpu_layers, n_threads, status, session_id, ayl_api_node=None):
        global LOADED_MODELS, SUMMARY_STORY, PREVIOUS_PROMPT, DESCRIPTION
        model_path = os.path.join(GLOBAL_GGUF_MODEL_DIR, model)
        if model not in LOADED_MODELS:
            if model.endswith(".gguf"):
                self.model = Llama(model_path=model_path, n_ctx=max_tokens, n_gpu_layers=n_gpu_layers, n_threads=n_threads)
                self.max_tokens = max_tokens
                LOADED_MODELS[model] = self.model
            else:
                raise ValueError(f"Invalid GGUF model file: {model}")
        else:
            self.model = LOADED_MODELS[model]

        if ayl_api_node:
            PREVIOUS_PROMPT = ayl_api_node[0]
            SUMMARY_STORY = ayl_api_node[1]
            DESCRIPTION = ayl_api_node[2]
        SUMMARY_STORY = self.summary_story(SUMMARY_STORY, text)
        DESCRIPTION = self.generate_description(DESCRIPTION, DESCRIPTION, text)
        if status == 0:
            output_prompt = self.generate_image_prompt(PREVIOUS_PROMPT, DESCRIPTION, PREVIOUS_PROMPT, text)
        elif status == 1:
            output_prompt = self.generate_cover_prompt(PREVIOUS_PROMPT, DESCRIPTION, text)
        else:
            output_prompt = self.generate_image_prompt(PREVIOUS_PROMPT, DESCRIPTION, PREVIOUS_PROMPT, text)
        
        # JSON 저장 부분: AYL_GGUF_Node의 출력값을 session 폴더에 저장
        if session_id:
            session_folder = os.path.join("/workspace/ComfyUI/output", session_id)
            if not os.path.exists(session_folder):
                os.makedirs(session_folder, exist_ok=True)
            output_file = os.path.join(session_folder, "ayl_output.json")
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump({
                        "prev_prompt": output_prompt,
                        "summary": SUMMARY_STORY,
                        "description": DESCRIPTION
                    }, f, ensure_ascii=False, indent=4)
                print(f"✅ [AYL_GGUF_Node] JSON 출력 저장 완료: {output_file}")
            except Exception as e:
                print(f"❌ [AYL_GGUF_Node] JSON 출력 저장 실패: {str(e)}")
        # 모델 언로드 기능: ENABLE_MODEL_UNLOAD 플래그가 True이면, 사용 후 모델을 전역 변수에서 삭제합니다.
        if ENABLE_MODEL_UNLOAD:
            if model in LOADED_MODELS:
                del LOADED_MODELS[model]
            # 추가: 현재 노드 인스턴스의 모델 참조 해제
            self.model = None
            self.tokenizer = None  # (사용하는 경우)
            gc.collect()
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            print(f"✅ [AYL_Node] 모델 언로드 및 VRAM 정리 완료: {model}")

        return (output_prompt, SUMMARY_STORY, DESCRIPTION)
    
    def generate_cover_prompt(self, previous_prompt, description, user_input):
        cover_prompt = (
            "You are an AI assistant specialized in creating cover image prompts for story books. "
            "Based on the provided story summary and description, generate a cover image prompt in English. "
            "Also, provide a title for the story. "
            "Your response should first contain the title on the first line, followed by the cover prompt on the second line. "
            "Do not include any additional text."
        )
        combined_input = f"Story summary: {SUMMARY_STORY}\nDescription: {description}\nUser Input: {user_input}"
        messages = [
            {"role": "system", "content": cover_prompt},
            {"role": "user", "content": combined_input}
        ]
        return self.generate_model_output(messages)
    
    def generate_model_output(self, messages):
        gguf_response = self.model.create_chat_completion(messages=messages)
        return gguf_response["choices"][0]["message"]['content']

# AYL_SaveOutput_Node는 더 이상 사용하지 않습니다.
# 노드 매핑
NODE_CLASS_MAPPINGS = {
    "AYL_Node": AYL_Node,
    "AYL_GGUF_Node": AYL_GGUF_Node,
    "AYL_API_Node": AYL_API_Node,
    # "AYL_SaveOutput_Node": AYL_SaveOutput_Node,  # 제거됨
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AYL_Node": "AYL_Node",
    "AYL_GGUF_Node": "AYL_GGUF_Node",
    "AYL_API_Node": "AYL_API_Node",
    # "AYL_SaveOutput_Node": "AYL_SaveOutput_Node",  # 제거됨
}
