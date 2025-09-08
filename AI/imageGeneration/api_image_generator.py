import os
import json
import base64
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from PIL import Image
import io
import requests
from openai import OpenAI
import google.generativeai as genai

# 환경변수에서 API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 캐릭터 파일 경로
CHARACTERS_DIR = os.path.join(os.path.dirname(__file__), "characters")

@dataclass
class Entity:
    name: str  # 영어 이름 (고유 식별자)
    korean_name: str
    entity_type: str  # '인물', '사물', '장소'
    image_path: Optional[str] = None  # 캐릭터만 가짐
    prompt: Optional[str] = None      # 캐릭터만 가짐

class EntityManager:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.korean_to_english_map: Dict[str, str] = {}
        self.load_entities()

    def load_entities(self):
        """init_db.sql과 기존 캐릭터 정보를 기반으로 모든 개체 로드"""
        
        # 1. 기존 캐릭터 정보 로드 (character 폴더 기반)
        character_details = {
            "alien": {"korean": "외계인"}, "beggar": {"korean": "가난뱅이"}, "boy": {"korean": "소년"},
            "detective": {"korean": "탐정"}, "doctor": {"korean": "박사"}, "farmer": {"korean": "농부"},
            "girl": {"korean": "소녀"}, "idol": {"korean": "아이돌"}, "merchant": {"korean": "상인"},
            "ninja": {"korean": "닌자"}, "oldman": {"korean": "노인"}, "princess": {"korean": "공주"},
            "rich": {"korean": "부자"}, "wizard": {"korean": "마법사"}, "god": {"korean": "신"},
            "tiger": {"korean": "호랑이"}, "ghost": {"korean": "유령"}, "devil": {"korean": "마왕"}
        }

        for name, details in character_details.items():
            image_path = os.path.join(CHARACTERS_DIR, f"{name}.png")
            txt_path = os.path.join(CHARACTERS_DIR, f"{name}.txt")
            prompt = ""
            if os.path.exists(txt_path):
                with open(txt_path, 'r', encoding='utf-8') as f:
                    prompt = f.read().strip()
            
            if os.path.exists(image_path) or name in ["god", "tiger", "ghost", "devil"]:
                entity = Entity(
                    name=name,
                    korean_name=details["korean"],
                    entity_type='인물',
                    image_path=image_path if os.path.exists(image_path) else None,
                    prompt=prompt
                )
                self.entities[name] = entity
                self.korean_to_english_map[details["korean"]] = name

        # 2. init_db.sql의 키워드 정보 로드
        sql_entities = {
            '호랑이': 'tiger', '유령': 'ghost', '농부': 'farmer', '상인': 'merchant', '신': 'god', 
            '외계인': 'alien', '박사': 'doctor', '아이돌': 'idol', '마법사': 'wizard', '마왕': 'devil',
            '소년': 'boy', '소녀': 'girl', '부자': 'rich', '탐정': 'detective', '노인': 'oldman', 
            '가난뱅이': 'beggar', '공주': 'princess', '닌자': 'ninja',
            '핸드폰': 'phone', '마차': 'carriage', '인형': 'doll', '부적': 'talisman', '지도': 'map',
            '가면': 'mask', '칼': 'sword', '피리': 'flute', '지팡이': 'staff', '태양': 'sun',
            '날개': 'wings', '의자': 'chair', '시계': 'clock', '도장': 'stamp', '보석': 'gem',
            'UFO': 'ufo', '덫': 'trap', '총': 'gun', '타임머신': 'timemachine', '감자': 'potato',
            '바다': 'sea', '다리': 'bridge', '묘지': 'cemetery', '식당': 'restaurant', '박물관': 'museum',
            '비밀통로': 'secretpassage', '사막': 'desert', '저택': 'mansion', '천국': 'heaven'
        }
        
        entity_types = {
            '호랑이': '인물', '유령': '인물', '농부': '인물', '상인': '인물', '신': '인물', '외계인': '인물',
            '박사': '인물', '아이돌': '인물', '마법사': '인물', '마왕': '인물', '소년': '인물', '소녀': '인물',
            '부자': '인물', '탐정': '인물', '노인': '인물', '가난뱅이': '인물', '공주': '인물', '닌자': '인물',
            '핸드폰': '사물', '마차': '사물', '인형': '사물', '부적': '사물', '지도': '사물', '가면': '사물',
            '칼': '사물', '피리': '사물', '지팡이': '사물', '태양': '사물', '날개': '사물', '의자': '사물',
            '시계': '사물', '도장': '사물', '보석': '사물', 'UFO': '사물', '덫': '사물', '총': '사물',
            '타임머신': '사물', '감자': '사물',
            '바다': '장소', '다리': '장소', '묘지': '장소', '식당': '장소', '박물관': '장소',
            '비밀통로': '장소', '사막': '장소', '저택': '장소', '천국': '장소'
        }

        for korean, english in sql_entities.items():
            if english not in self.entities:
                self.entities[english] = Entity(
                    name=english,
                    korean_name=korean,
                    entity_type=entity_types.get(korean, '사물')
                )
            self.korean_to_english_map[korean] = english
            if korean == '소년': self.korean_to_english_map['소녀'] = 'girl'
            if korean == 'UFO': self.korean_to_english_map['ufo'] = 'ufo'

    def get_entity(self, name: str) -> Optional[Entity]:
        return self.entities.get(name)

    def detect_entities_in_text(self, text: str) -> List[str]:
        detected = []
        for korean, english in self.korean_to_english_map.items():
            if korean in text:
                detected.append(english)
        # 영어 이름으로도 탐지
        for english_name in self.entities.keys():
            if english_name in text.lower():
                detected.append(english_name)

        # '소년'과 '소녀'는 'boy'와 'girl'로 각각 처리
        if '소년' in text and 'boy' not in detected: detected.append('boy')
        if '소녀' in text and 'girl' not in detected: detected.append('girl')

        return sorted(list(set(detected)), key=lambda x: text.find(self.get_entity(x).korean_name) if self.get_entity(x) else -1)

class GPTPromptGenerator:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
        # 기존 AYL.py의 프롬프트 시스템을 그대로 활용
        self.story_prompt = """
You are an AI assistant specialized in summarizing stories in English and Korean stories currently entered. 
Your mission is to fully grasp the context of the summarized story and the Korean story currently entered, and then update the summarized English story. 
1. Mandatory Format: You must print only the summary story. 
2. Summarization of Inputs: - Continuously build a coherent summary of the story based on all user inputs up to the current point. 
   - Ensure that each subject appears only once in the [Subject] component, eliminating any duplicates. 
3. Missing or Partial Information: - If the user's input lacks certain components (e.g., no explicit Time), use context from the summarized story to maintain a natural, cohesive narrative. 
4. Strict Limitations: - Do not introduce new story elements beyond what the user provides. 
   - Do not modify or extend the user's narrative beyond summarization. 
   - Use only the content explicitly stated by the user, plus any relevant context from the summarized story to fill in missing details. 
# Important: - Add new information without ever deleting existing information. 
- Type of Input: Summarized story, current user input. 
- Output format: a summary of the summarized story and the current user's input.
"""
        
        self.description_prompt = """
You are a master storyteller AI. Your task is to interpret a new line in a story and create a vivid, context-aware 'Description' in English for an image generation AI. You must ensure narrative and character continuity.

**Core Inputs:**
- **Previous Description:** The description of the last scene.
- **Story Summary:** A summary of the entire story so far.
- **Current User Input:** The new sentence to add to the story.

**Reasoning Steps & Rules:**

1.  **Identify the Actor:**
    - **Rule:** If the `Current User Input` lacks a clear subject (e.g., "He went to the restaurant" or "Went to the restaurant"), you MUST infer the actor from the `Previous Description` or `Story Summary`. The most recently active character is the default actor.
    - **Action:** Explicitly state who is performing the action. Example: "The farmer, from the previous scene, goes to the restaurant."

2.  **Maintain Scene Cohesion:**
    - **Rule:** Assume the scene continues in the same location unless the `Current User Input` explicitly states a change of location.
    - **Action:** If the location is the same, integrate the new action into the existing environment from the `Previous Description`. If the location changes, describe the new environment.

3.  **Update Subject States, Don't Replace:**
    - **Rule:** For each subject (character, object), compare their state in the `Previous Description` with the `Current User Input` and describe the *change*.
    - **Sub-points for Each Subject:**
        *   **Physical/External Features:** Maintain consistency. Do not change unless explicitly stated.
        *   **Emotional Expressions & Actions/Poses:** Describe the transition. Instead of "The farmer is sad," write "The farmer, who was previously happy, now looks sad."
        *   **Relative Positioning:** Update the positions of all subjects relative to each other and the environment.

4.  **Synthesize the Final Description:**
    - **Format:** Structure your output into sections: `Main Subjects` (with sub-points for each), `Environment`, and `Mood & Narrative`.
    - **Clarity:** The description must be a clear and unambiguous instruction for the image generator.
    - **Conciseness:** Remove any redundant information from the `Previous Description` that is no longer relevant. The goal is a snapshot of the *current* moment, informed by the past.

**Example Scenario:**
-   **Previous Description:** "A happy farmer is standing in his field."
-   **Story Summary:** "A farmer was happy in his field."
-   **Current User Input:** "He felt hungry and went to the restaurant."

**Your Output should be structured like this:**

**Main Subjects:**
-   **Farmer:**
    -   Physical/External Features: (Consistent traits from before)
    -   Emotional Expressions: His expression changes from happy to hungry and determined.
    -   Actions/Poses: He is now walking towards or entering a restaurant, leaving his field behind.
**Environment:**
-   The scene transitions from a field to a restaurant. Describe the look of the restaurant.
**Mood & Narrative:**
-   The mood shifts from peaceful to one of purpose and need.
"""
        
        self.image_prompt = """
You are a cinematic artist AI. You will receive a 'Description' that details a scene, including subjects, environment, and mood. Your job is to convert this description into a single, ultra-detailed paragraph for an image generation model.

**Crucial Rule:** All subjects mentioned in the 'Main Subjects' section of the Description MUST appear together in the final image, interacting as described.

**Instructions:**

1.  **Synthesize, Don't List:** Read the entire `Description` to understand the complete context. Do not just translate points one-by-one.
2.  **Combine All Elements:** Weave together all subjects, their actions, their emotions, and their environment into one cohesive and vivid scene. If the description says "A farmer is in a restaurant," both the farmer and the restaurant must be clearly depicted in the same frame.
3.  **Dynamic Scene:** Use strong, cinematic language. Start the paragraph with "ultra-detailed cinematic scene,". Describe the lighting, camera angle, textures, and atmosphere to create a rich and immersive image.
4.  **Respect the Details:** Strictly adhere to the physical features, emotional states, actions, and relative positioning provided in the `Description`.

**Example:**
- **Input Description:**
    -   Main Subjects:
        -   Farmer: Sad, holding a golden staff.
        -   Restaurant: Dimly lit.
- **Your Output:** "ultra-detailed cinematic scene, inside a dimly lit restaurant, a sad farmer is sitting at a wooden table, holding a glowing golden staff in his hands. The soft light from the staff illuminates his melancholic face."
"""
    
    def generate_story_summary(self, previous_summary: str, user_input: str) -> str:
        """스토리 요약 생성"""
        combined_input = f"Story_summary: {previous_summary}\nUser_Input: {user_input}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": self.story_prompt},
                    {"role": "user", "content": combined_input}
                ],
                max_tokens=4096,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in story summary generation: {e}")
            return previous_summary
    
    def generate_description(self, previous_description: str, story_summary: str, user_input: str) -> str:
        """장면 설명 생성"""
        combined_input = f"Story summary: {story_summary}\nDescription: {previous_description}\nCurrent story: {user_input}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": self.description_prompt},
                    {"role": "user", "content": combined_input}
                ],
                max_tokens=4096,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in description generation: {e}")
            return previous_description
    
    def generate_image_prompt(self, description: str, user_input: str) -> str:
        """이미지 생성용 프롬프트 생성"""
        combined_input = f"Description: {description}\nCurrent story: {user_input}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": self.image_prompt},
                    {"role": "user", "content": combined_input}
                ],
                max_tokens=4096,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in image prompt generation: {e}")
            return description

class GeminiImageGenerator:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash-image-preview")
    
    def generate_text_to_image(self, prompt: str, art_style: str = "") -> bytes:
        """텍스트에서 이미지 생성 (캐릭터 없는 경우)"""
        # 9:16 비율 명시 (세로형, 720x1280 해상도)
        full_prompt = f"{prompt} {art_style} portrait orientation, 9:16 aspect ratio, vertical format, 720x1280 resolution".strip()
        
        try:
            response = self.model.generate_content([
                f"Generate an image: {full_prompt}"
            ])
            
            # 응답에서 이미지 데이터 추출
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data'):
                        return base64.b64decode(part.inline_data.data)
            
            raise Exception("No image data in response")
            
        except Exception as e:
            print(f"Error in text-to-image generation: {e}")
            raise
    
    def generate_image_to_image(self, character_images: List[Image.Image], prompt: str, character_prompts: List[str], art_style: str = "") -> bytes:
        """이미지에서 이미지 생성 (캐릭터 있는 경우)"""
        try:
            # 캐릭터 프롬프트들을 결합
            combined_character_prompt = " ".join(character_prompts)
            
            # 전체 프롬프트 구성 (9:16 비율 명시)
            full_prompt = f"Generate an image based on these reference images. {combined_character_prompt} {prompt} {art_style} portrait orientation, 9:16 aspect ratio, vertical format, 720x1280 resolution".strip()
            
            # 이미지와 텍스트를 함께 전달
            content = [full_prompt] + character_images
            
            response = self.model.generate_content(content)
            
            # 응답에서 이미지 데이터 추출
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data'):
                        return base64.b64decode(part.inline_data.data)
            
            raise Exception("No image data in response")
            
        except Exception as e:
            print(f"Error in image-to-image generation: {e}")
            raise

class APIImageGenerationSystem:
    def __init__(self):
        self.entity_manager = EntityManager()
        self.gpt_generator = GPTPromptGenerator()
        self.gemini_generator = GeminiImageGenerator()
        
        # 그림체별 스타일 프롬프트 (기존 LoRA 대체)
        self.art_styles = {
            0: "anime style, vibrant colors, detailed illustration",
            1: "cute 3d cartoon style, soft colors, rounded features",
            2: "comic strip style, bold outlines, dramatic expressions",
            3: "claymation style, 3D rendered, soft clay texture",
            4: "crayon drawing style, childlike, soft pastels",
            5: "pixel art style, retro gaming aesthetic, sharp pixels",
            6: "minimalist illustration, clean lines, simple colors",
            7: "watercolor painting style, soft blending, artistic",
            8: "storybook illustration, whimsical, detailed"
        }
    
    async def generate_image(self, 
                           user_input: str, 
                           game_mode: int, 
                           session_data: Dict) -> Tuple[bytes, Dict]:
        """
        메인 이미지 생성 함수
        
        Args:
            user_input: 사용자 입력 텍스트
            game_mode: 게임 모드 (0-8, 그림체 결정)
            session_data: 세션 데이터 (prev_prompt, summary, description 포함)
        
        Returns:
            Tuple[bytes, Dict]: (이미지 바이트 데이터, 업데이트된 세션 데이터)
        """
        
        # 1. GPT를 통한 프롬프트 생성
        print("🔹 [GPT] 스토리 요약 생성 중...")
        story_summary = self.gpt_generator.generate_story_summary(
            session_data.get("summary", ""), 
            user_input
        )
        
        print("🔹 [GPT] 장면 설명 생성 중...")
        description = self.gpt_generator.generate_description(
            session_data.get("description", ""),
            story_summary,
            user_input
        )
        
        print("🔹 [GPT] 이미지 프롬프트 생성 중...")
        image_prompt = self.gpt_generator.generate_image_prompt(description, user_input)
        
        # 2. 개체 탐지 및 레퍼런스 관리
        detected_entities = self.entity_manager.detect_entities_in_text(user_input)
        print(f"🔹 [개체 탐지] 발견된 개체: {detected_entities}")

        entity_references = session_data.get('entity_references', {})
        newly_referenced_entities = {} # 이번 턴에 레퍼런스가 생성/업데이트된 개체
        
        # 3. 그림체 스타일 가져오기
        art_style = self.art_styles.get(game_mode, "")

        # 4. 첫 등장 사물/장소에 대한 개별 레퍼런스 이미지 생성
        for entity_name in detected_entities:
            if entity_name not in entity_references:
                entity = self.entity_manager.get_entity(entity_name)
                # 캐릭터가 아니거나, 캐릭터지만 기본 이미지가 없는 경우
                if entity and (entity.entity_type != '인물' or not entity.image_path):
                    print(f"   - 첫 등장 (이미지 없음): '{entity.korean_name}'. 개별 레퍼런스 생성 중...")
                    temp_prompt = f"A single, clear, centered image of a {entity.name} in a {art_style}, on a plain white background."
                    try:
                        ref_img_bytes = self.gemini_generator.generate_text_to_image(temp_prompt, art_style)
                        entity_references[entity_name] = ref_img_bytes
                        newly_referenced_entities[entity_name] = ref_img_bytes
                        print(f"   - '{entity.korean_name}' 레퍼런스 이미지 생성 완료.")
                    except Exception as e:
                        print(f"   - '{entity.korean_name}' 레퍼런스 생성 실패: {e}")

        # 5. 최종 이미지 생성
        images_for_gemini = []
        entity_prompts = []
        
        if detected_entities:
            print("🔹 [Gemini] 최종 이미지 생성 (Image-to-Image 모드)...")
            for entity_name in detected_entities:
                entity = self.entity_manager.get_entity(entity_name)
                if not entity: continue

                if entity.prompt: entity_prompts.append(entity.prompt)

                if entity_name in entity_references:
                    # 재등장 또는 이번에 생성된 레퍼런스 사용
                    print(f"   - 레퍼런스 사용: '{entity.korean_name}'")
                    images_for_gemini.append(Image.open(io.BytesIO(entity_references[entity_name])))
                elif entity.image_path: # 캐릭터 첫 등장
                    print(f"   - 기본 레퍼런스 사용: '{entity.korean_name}' (캐릭터 첫 등장)")
                    with open(entity.image_path, "rb") as f: images_for_gemini.append(Image.open(f))
            
            image_bytes = self.gemini_generator.generate_image_to_image(images_for_gemini, image_prompt, entity_prompts, art_style)
        else:
            print("🔹 [Gemini] Text-to-Image 모드로 이미지 생성 중...")
            image_bytes = self.gemini_generator.generate_text_to_image(image_prompt, art_style)

        # 6. 첫 등장 캐릭터 레퍼런스 업데이트
        for entity_name in detected_entities:
            if entity_name not in session_data.get('entity_references', {}) and entity_name not in newly_referenced_entities:
                entity = self.entity_manager.get_entity(entity_name)
                if entity and entity.entity_type == '인물':
                    print(f"🔹 [레퍼런스 업데이트] 첫 등장 캐릭터 '{entity.korean_name}'의 레퍼런스를 최종 이미지로 업데이트합니다.")
                    entity_references[entity_name] = image_bytes

        # 7. 세션 데이터 업데이트
        updated_session_data = {
            "prev_prompt": image_prompt,
            "summary": story_summary,
            "description": description,
            "entity_references": entity_references
        }
        
        print("✅ [이미지 생성 완료]")
        return image_bytes, updated_session_data

# 사용 예시 및 테스트 함수
async def test_system():
    """시스템 테스트"""
    system = APIImageGenerationSystem()
    
    # 테스트 세션 데이터
    session_data = {
        "prev_prompt": "",
        "summary": "",
        "description": ""
    }
    
    # 테스트 1: 캐릭터 없는 경우
    print("=== 테스트 1: 캐릭터 없는 경우 ===")
    try:
        image_bytes, updated_data = await system.generate_image(
            "아름다운 숲속에 햇빛이 비치고 있다", 
            0,  # 애니메이션 스타일
            session_data
        )
        print(f"생성된 이미지 크기: {len(image_bytes)} bytes")
        session_data = updated_data
    except Exception as e:
        print(f"테스트 1 실패: {e}")
    
    # 테스트 2: 캐릭터 있는 경우
    print("=== 테스트 2: 캐릭터 있는 경우 ===")
    try:
        image_bytes, updated_data = await system.generate_image(
            "닌자가 숲속에서 수행을 하고 있다", 
            1,  # 3D 카툰 스타일
            session_data
        )
        print(f"생성된 이미지 크기: {len(image_bytes)} bytes")
        session_data = updated_data
    except Exception as e:
        print(f"테스트 2 실패: {e}")

if __name__ == "__main__":
    asyncio.run(test_system())
