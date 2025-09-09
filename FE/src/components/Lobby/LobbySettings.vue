<template>
  <div class="col-span-2">
    <!-- 방 설정 메뉴 표시 -->
    <form class="h-full">
      <div class="h-full w-full grid grid-rows-6">
        <div
          class="row-span-5 grid grid-cols-3 grid-rows-5 border drop-shadow-md rounded-xl bg-[#ffffffa3] p-5 font-extrabold"
          :class="configurable == false ? 'pointer-events-none' : ''"
        >
          <div class="col-span-3 flex flex-col items-center space-y-6 py-4">
            <!-- 헤더와 현재 값 -->
            <div class="flex flex-col items-center space-y-3">
              <label class="text-lg font-semibold text-gray-700">턴당 소요 시간</label>
              <div class="modern-timer-display bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-6 py-3 rounded-2xl font-bold text-2xl shadow-lg">
                {{ localRoomConfigs.currTurnTime }}초
              </div>
            </div>

            <!-- 모던 슬라이더 컨테이너 -->
            <div class="w-4/5 max-w-md">
              <!-- 값 라벨 -->
              <div class="flex justify-between text-xs text-gray-500 mb-4 px-1">
                <span class="transform -translate-x-1">30초</span>
                <span>35초</span>
                <span class="transform translate-x-1">40초</span>
              </div>
              
              <!-- 슬라이더 -->
              <div class="modern-slider-container relative h-8 flex items-center">
                <!-- 트랙 배경 -->
                <div class="slider-track-bg absolute w-full h-2 bg-gradient-to-r from-gray-200 to-gray-300 rounded-full shadow-inner"></div>
                
                <!-- 진행도 트랙 -->
                <div 
                  class="slider-track-progress absolute h-2 bg-gradient-to-r from-blue-400 via-indigo-500 to-purple-600 rounded-full shadow-md transition-all duration-300 ease-out"
                  :style="{ width: sliderProgress + '%' }"
                ></div>
                
                <!-- 실제 input -->
                <input
                  type="range"
                  :min="minTimeValue"
                  :max="maxTimeValue"
                  :step="stepTimeValue"
                  class="modern-range-input w-full h-2 bg-transparent appearance-none cursor-pointer relative z-10"
                  v-model="localRoomConfigs.currTurnTime"
                />
                
                <!-- 인터랙티브 틱 마크 -->
                <div class="absolute w-full flex justify-between pointer-events-none z-5">
                  <div
                    v-for="(position, index) in tickPositions"
                    :key="index"
                    class="tick-mark w-4 h-4 bg-white border-2 border-gray-300 rounded-full shadow-sm transition-all duration-200"
                    :class="{
                      'border-blue-500 bg-blue-100 scale-125': isTickActive(index),
                      'border-gray-300 bg-white': !isTickActive(index)
                    }"
                    :style="{ left: position + '%', transform: 'translateX(-50%)' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
          <!-- <div class="absolute right-5 top-5 rounded-full border-4 border-[#E77DAF] flex justify-center items-center p-2 cursor-pointer" :class="isPreview ? 'bg-[#E77DAF]' : ''" @click="isPreview = !isPreview">
            <img :src="unicon" alt="" class="w-10 h-10">
          </div> -->
          <div class="col-span-3 row-span-4 flex flex-col items-center">
            <label class="block mt-4">게임 모드</label>
            <div class="grid grid-cols-3 gap-x-8 max-h-64 w-full overflow-y-scroll p-5 pointer-events-auto">
              <template v-for="(modeGroup, idx) in chunkedModes" :key="group">
                <div class="flex justify-between w-full"  v-for="(mode, index) in modeGroup" :key="index" :class="idx === 0 ? '' : 'mt-7'">
                  <div class="flex flex-col items-center w-full">
                    <p class="mb-2">{{ mode.text }}</p>
<label
                      class="relative rounded-lg overflow-hidden w-40 h-40 cursor-pointer transform transition-transform duration-300 hover:scale-105 hover:shadow-xl"
                      :for="'mode' + mode.value"
                      :class="{
                        'outline outline-4 outline-color': localRoomConfigs.currMode === mode.value,
                      }"
                      @click="handleClick($event, mode.value)"
                      @mouseover="startImageTransition(mode.value)"
                      @mouseleave="stopImageTransition(mode.value)"
                    >
                      <img
                        v-for="(image, imgIndex) in mode.images"
                        :key="imgIndex"
                        :src="image"
                        :alt="`Mode ${mode.value} Image ${imgIndex + 1}`"
                        class="absolute inset-0 w-full h-full object-cover transition-opacity duration-500 ease-in-out"
                        :class="{
                          'opacity-100': mode.activeImageIndex === imgIndex,
                          'opacity-0': mode.activeImageIndex !== imgIndex,
                        }"
                      />
                    </label>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
        <div class="grid grid-cols-2">
          <div class="flex justify-center items-center">
            <button
              type="button"
              class="duration-300 ease-in-out w-40 h-10 rounded-lg bg-black text-white flex items-center justify-center hover:bg-gray-800 hover:scale-105 font-medium"
              @click="copy"
            >
              <div class="flex gap-x-4">
                <img
                  :src="InviteIcon"
                  alt="초대 아이콘"
                  class="w-4"
                />
                <span>초대하기</span>
              </div>
            </button>
          </div>
          <div class="flex justify-center items-center">
            <button
              type="button"
              class="duration-300 ease-in-out w-40 h-10 rounded-lg bg-black text-white flex items-center justify-center hover:bg-gray-800 hover:scale-105 font-medium"
              @click="gameStart"
            >
              <div class="flex gap-x-4">
                <img :src="StartIcon" alt="시작 아이콘" class="w-4" />
                <span>시작하기</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>
<script setup>
import { ref, computed, watch, defineProps, defineEmits, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import useCilpboard from "vue-clipboard3";
import toast from "@/functions/toast";
import { InviteIcon, StartIcon } from "@/assets";
import modeImages from "@/assets/images/modes";
import unicon from "@/assets/icons/favicon_4.svg";
const router = useRouter();
const { toClipboard } = useCilpboard();
const minTimeValue = ref(30);
const maxTimeValue = ref(40);
const stepTimeValue = ref(2);
const localRoomConfigs = ref({
  currTurnTime: 30,
  currMode: 0,
});
const isPreview = ref(false);

const emit = defineEmits(["roomConfiguration", "gameStart"]);

const props = defineProps({
  configurable: {
    type: Boolean,
    required: true,
    default: false,
  },
  participants: {
    type: Array,
  },
  roomConfigs: {
    type: Object,
  },
  gameStarted: {
    Type: Boolean,
    default: false,
  },
  InviteLink: {
    Type: String,
  },
  peerId: {
    Type: String,
  },
});

const ticks = computed(() => {
  const steps = (maxTimeValue.value - minTimeValue.value) / stepTimeValue.value;
  const positions = [];
  for (let i = 0; i <= steps; i++) {
    positions.push((i / steps) * 100); // 위치를 백분율로 계산
  }
  return positions;
});

const sliderProgress = computed(() => {
  const current = localRoomConfigs.value.currTurnTime;
  const min = minTimeValue.value;
  const max = maxTimeValue.value;
  return ((current - min) / (max - min)) * 100;
});

const tickPositions = computed(() => {
  const steps = (maxTimeValue.value - minTimeValue.value) / stepTimeValue.value;
  const positions = [];
  for (let i = 0; i <= steps; i++) {
    positions.push((i / steps) * 100);
  }
  return positions;
});

const isTickActive = (index) => {
  const currentValue = localRoomConfigs.value.currTurnTime;
  const minValue = minTimeValue.value;
  const step = stepTimeValue.value;
  const currentStep = (currentValue - minValue) / step;
  return index <= currentStep;
};

// // 플레이어 카드 개수
// const cardCount = ref([4, 5, 6]);

// 게임 모드
const modes = ref([
  {
    text: "기본 모드",
    value: 0,
    images: modeImages.Mode0,
    activeImageIndex: 0,
    intervalId: null,
  },
  {
    text: "3D 모드",
    value: 1,
    images: modeImages.Mode1,
    activeImageIndex: 0,
    intervalId: null,
  },
  {
    text: "코믹북 모드",
    value: 2,
    images: modeImages.Mode2,
    activeImageIndex: 0,
    intervalId: null,
  },
  {
    text: "클레이 모드",
    value: 3,
    images: modeImages.Mode3,
    activeImageIndex: 0,
    intervalId: null,
  },
  {
    text: "유치원 모드",
    value: 4,
    images: modeImages.Mode4,
    activeImageIndex: 0,
    intervalId: null,
  },
  {
    text: "픽셀 모드",
    value: 5,
    images: modeImages.Mode5,
    activeImageIndex: 0,
    intervalId: null,
  },
  {
    text: "PS1 모드",
    value: 6,
    images: modeImages.Mode6,
    activeImageIndex: 0,
    intervalId: null,
  },
  {
    text: "동화책 모드",
    value: 7,
    images: modeImages.Mode7,
    activeImageIndex: 0,
    intervalId: null,
  },
  {
    text: "일러스트 모드",
    value: 8,
    images: modeImages.Mode8,
    activeImageIndex: 0,
    intervalId: null,
  },
]);

const startImageTransition = (modeValue) => {
  const mode = modes.value.find((m) => m.value === modeValue);
  if (mode && !mode.intervalId) {
    // Start with the next image immediately
    mode.activeImageIndex = 1;
    mode.intervalId = setInterval(() => {
      mode.activeImageIndex = (mode.activeImageIndex + 1) % mode.images.length;
    }, 1000);
  }
};

const stopImageTransition = (modeValue) => {
  const mode = modes.value.find((m) => m.value === modeValue);
  if (mode && mode.intervalId) {
    clearInterval(mode.intervalId);
    mode.intervalId = null;
    mode.activeImageIndex = 0;
  }
};

const copy = async () => {
  try {
    await toClipboard(props.InviteLink);
    toast.successToast("클립보드에 복사되었습니다.");
  } catch (error) {
    toast.errorToast("복사 실패");
  }
};

const gameStart = () => {
  if (props.participants[0].id !== props.peerId) {
    toast.errorToast("방장만 게임 시작할 수 있습니다.");
  } else if (props.participants.length < 2) {
    toast.warningToast("혼자서는 진행할 수 없습니다.");
  } else {
    let playerOrder;
    if(isPreview.value) {
      playerOrder = Array.from({length: props.participants.length},(_, i) => i);
    } else {
      playerOrder = Array(props.participants.length)
        .fill()
        .map((value, index) => index)
        .sort(() => Math.random() - 0.5);
    }
    emit("gameStart", {
      gameStarted: true,
      order: playerOrder,
      isPreview: isPreview.value,
    });
  }
};

const chunkedModes = computed(() => {
  const result = [];
  for (let i = 0; i < modes.value.length; i += 3) {
    result.push(modes.value.slice(i, i + 3)) // 3개씩 잘라서 새로운 배열에 추가
  }
  return result;
});

const handleClick = (event, data) => {
  if(props.configurable) {
    // Stop any running animations on other modes
    modes.value.forEach(mode => {
      if (mode.value !== data) {
        stopImageTransition(mode.value);
      }
    });
    localRoomConfigs.value.currMode = data;
  } else {
    event.preventDefault();
  }
}

onUnmounted(() => {
  modes.value.forEach(mode => {
    stopImageTransition(mode.value);
  });
});

watch(
  () => props.roomConfigs,
  () => {
    localRoomConfigs.value = props.roomConfigs;
  },
  { deep: true },
);

watch(
  () => localRoomConfigs.value,
  () => {
    if (props.configurable) {
      emit("roomConfiguration", localRoomConfigs.value);
    }
  },
  { deep: true },
);
</script>
<style>
  .outline-color {
    outline: 4px solid;
    outline-color: transparent;
    position: relative;
    background: linear-gradient(white, white) padding-box,
                linear-gradient(45deg, #f3c86f, #d1b2c5, #9973b0, #de7caf, #e28cb8, #cba8cd, #adb7cf, #52bebc) border-box;
    border: 4px solid transparent;
  }
  
  .outline-color::before {
    content: '';
    position: absolute;
    top: -4px;
    left: -4px;
    right: -4px;
    bottom: -4px;
    background: linear-gradient(45deg, #f3c86f, #d1b2c5, #9973b0, #de7caf, #e28cb8, #cba8cd, #adb7cf, #52bebc);
    border-radius: inherit;
    z-index: -1;
    border-radius: 12px;
  }

  /* 모드 선택창의 스크롤바 스타일 - 그라데이션 제거 */
  .grid.grid-cols-3.gap-x-8.max-h-64.w-full.overflow-y-scroll::-webkit-scrollbar {
    width: 8px;
  }

  .grid.grid-cols-3.gap-x-8.max-h-64.w-full.overflow-y-scroll::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 4px;
  }

  .grid.grid-cols-3.gap-x-8.max-h-64.w-full.overflow-y-scroll::-webkit-scrollbar-thumb {
    background: #6b7280;
    border-radius: 4px;
  }

  .grid.grid-cols-3.gap-x-8.max-h-64.w-full.overflow-y-scroll::-webkit-scrollbar-thumb:hover {
    background: #4b5563;
  }

  /* 최신 모던 슬라이더 스타일 */
  .modern-range-input {
    -webkit-appearance: none;
    appearance: none;
    background: transparent;
    outline: none;
  }

  .modern-range-input::-webkit-slider-track {
    -webkit-appearance: none;
    background: transparent;
    height: 8px;
    border-radius: 4px;
  }

  .modern-range-input::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6, #6366f1, #8b5cf6);
    border: 3px solid white;
    cursor: pointer;
    box-shadow: 
      0 4px 12px rgba(59, 130, 246, 0.4),
      0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    z-index: 20;
  }

  .modern-range-input::-webkit-slider-thumb:hover {
    transform: scale(1.1);
    box-shadow: 
      0 6px 20px rgba(59, 130, 246, 0.5),
      0 4px 8px rgba(0, 0, 0, 0.15);
    background: linear-gradient(135deg, #2563eb, #4f46e5, #7c3aed);
  }

  .modern-range-input::-webkit-slider-thumb:active {
    transform: scale(1.05);
    box-shadow: 
      0 2px 8px rgba(59, 130, 246, 0.6),
      0 1px 4px rgba(0, 0, 0, 0.2);
  }

  /* Firefox 스타일 */
  .modern-range-input::-moz-range-track {
    background: transparent;
    height: 8px;
    border-radius: 4px;
    border: none;
  }

  .modern-range-input::-moz-range-thumb {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6, #6366f1, #8b5cf6);
    border: 3px solid white;
    cursor: pointer;
    box-shadow: 
      0 4px 12px rgba(59, 130, 246, 0.4),
      0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .modern-range-input::-moz-range-thumb:hover {
    transform: scale(1.1);
    background: linear-gradient(135deg, #2563eb, #4f46e5, #7c3aed);
  }

  /* 애니메이션 효과 */
  .modern-slider-container:hover .slider-track-progress {
    box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.2);
  }

  .tick-mark {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .modern-timer-display {
    animation: pulse-subtle 2s ease-in-out infinite;
  }

  @keyframes pulse-subtle {
    0%, 100% {
      box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
    }
    50% {
      box-shadow: 0 6px 25px rgba(59, 130, 246, 0.4);
    }
  }
</style>
