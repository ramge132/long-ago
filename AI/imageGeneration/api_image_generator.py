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
class Character:
    name: str
    image_path: str
    prompt: str

class CharacterManager:
    def __init__(self):
        self.characters: Dict[str, Character] = {}
        self.load_characters()
    
    def load_characters(self):
        """캐릭터 이미지와 프롬프트 로드"""
        character_names = [
            "alien", "beggar", "boy", "detective", "doctor", 
            "farmer", "girl", "idol", "merchant", "ninja", 
            "oldman", "princess", "rich", "wizard"
        ]
        
        for name in character_names:
            image_path = os.path.join(CHARACTERS_DIR, f"{name}.png")
            txt_path = os.path.join(CHARACTERS_DIR, f"{name}.txt")
            
            if os.path.exists(image_path) and os.path.exists(txt_path):
                with open(txt_path, 'r', encoding='utf-8') as f:
                    prompt = f.read().strip()
                
                self.characters[name] = Character(
                    name=name,
                    image_path=image_path,
                    prompt=prompt
                )
    
    def get_character(self, name: str) -> Optional[Character]:
        """캐릭터 정보 가져오기"""
        return self.characters.get(name)
    
    def get_all_character_names(self) -> List[str]:
        """모든 캐릭터 이름 리스트 반환"""
        return list(self.characters.keys())
    
    def detect_characters_in_text(self, text: str) -> List[str]:
        """텍스트에서 언급된 캐릭터 탐지"""
        detected = []
        text_lower = text.lower()
        
        # 한국어-영어 매핑
        korean_mapping = {
            "닌자": "ninja", "공주": "princess", "의사": "doctor", 
            "농부": "farmer", "마법사": "wizard", "상인": "merchant",
            "소년": "boy", "소녀": "girl", "탐정": "detective",
            "거지": "beggar", "부자": "rich", "노인": "oldman",
            "아이돌": "idol", "외계인": "alien"
        }
        
        # 한국어 단어 탐지
        for korean, english in korean_mapping.items():
            if korean in text:
                detected.append(english)
        
        # 영어 단어 탐지
        for character_name in self.characters.keys():
            if character_name in text_lower:
                detected.append(character_name)
        
        return list(set(detected))  # 중복 제거

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
     * Relative Positioning:
       - This is CRITICAL for multiple characters. Indicate precisely how each subject is positioned relative to others (foreground, background, left/right, distance, etc.).
       - If the newest input changes the subject's location, update accordingly and remove outdated references.

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
        
        self.image_prompt = """
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
   - Preserve each subject's external appearance from the updated Description (e.g., clothing style, color, weapons).
   - Use the newest emotional expressions, actions, poses, and relative positions as given.
   - Ensure that multiple subjects do not merge; maintain their distinct positions via consistent references (e.g., "in the foreground," "to the left," "several paces away," etc.).
   - Highlight transitional motion effects (dust trails, shockwaves, etc.) and emphasize changes signaled by the latest input.

4. Constraints:
   - DO NOT repeat older or contradictory text from previous versions. 
   - Avoid bullet points or separate headings—only one cinematic paragraph.
   - If there's any mention in the updated Description about changes to a subject's state or location, reflect that precisely. 
   - The focus is on the current moment. Avoid rehashing prior events or extended backstory.

Goal:
- Deliver a powerful, immersive snapshot that shows exactly how the scene looks and feels after the latest changes, with correct subject positions, actions, and emotions.
"""
    
    def generate_story_summary(self, previous_summary: str, user_input: str) -> str:
        """스토리 요약 생성"""
        combined_input = f"Story_summary: {previous_summary}\nUser_Input: {user_input}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # GPT-5-nano가 아직 없으므로 gpt-4o-mini 사용
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
                model="gpt-4o-mini",
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
                model="gpt-4o-mini",
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
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """이미지를 base64로 인코딩"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def load_image_for_gemini(self, image_path: str):
        """Gemini용 이미지 로드"""
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        
        # PIL Image 객체로 변환
        image = Image.open(io.BytesIO(image_data))
        return image
    
    def generate_text_to_image(self, prompt: str, art_style: str = "") -> bytes:
        """텍스트에서 이미지 생성 (캐릭터 없는 경우)"""
        full_prompt = f"{prompt} {art_style}".strip()
        
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
    
    def generate_image_to_image(self, character_images: List[str], prompt: str, character_prompts: List[str], art_style: str = "") -> bytes:
        """이미지에서 이미지 생성 (캐릭터 있는 경우)"""
        try:
            # 캐릭터 이미지들을 로드
            images = []
            for img_path in character_images:
                if os.path.exists(img_path):
                    images.append(self.load_image_for_gemini(img_path))
            
            # 캐릭터 프롬프트들을 결합
            combined_character_prompt = " ".join(character_prompts)
            
            # 전체 프롬프트 구성
            full_prompt = f"Generate an image based on these reference images. {combined_character_prompt} {prompt} {art_style}".strip()
            
            # 이미지와 텍스트를 함께 전달
            content = [full_prompt] + images
            
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
        self.character_manager = CharacterManager()
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
        
        # 2. 캐릭터 탐지
        detected_characters = self.character_manager.detect_characters_in_text(user_input)
        print(f"🔹 [캐릭터 탐지] 발견된 캐릭터: {detected_characters}")
        
        # 3. 그림체 스타일 가져오기
        art_style = self.art_styles.get(game_mode, "")
        
        # 4. 이미지 생성
        if detected_characters:
            # 캐릭터가 있는 경우: image-to-image 모드
            print("🔹 [Gemini] Image-to-Image 모드로 이미지 생성 중...")
            character_images = []
            character_prompts = []
            
            for char_name in detected_characters:
                character = self.character_manager.get_character(char_name)
                if character:
                    character_images.append(character.image_path)
                    character_prompts.append(character.prompt)
            
            image_bytes = self.gemini_generator.generate_image_to_image(
                character_images, image_prompt, character_prompts, art_style
            )
        else:
            # 캐릭터가 없는 경우: text-to-image 모드
            print("🔹 [Gemini] Text-to-Image 모드로 이미지 생성 중...")
            image_bytes = self.gemini_generator.generate_text_to_image(
                image_prompt, art_style
            )
        
        # 5. 세션 데이터 업데이트
        updated_session_data = {
            "prev_prompt": image_prompt,
            "summary": story_summary,
            "description": description
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