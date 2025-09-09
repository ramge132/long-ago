<template>
  <div class="col-span-2">
    <!-- 방 설정 메뉴 표시 -->
    <form class="h-full">
      <div class="h-full w-full grid grid-rows-6">
        <div
          class="row-span-5 grid grid-cols-3 grid-rows-5 border drop-shadow-md rounded-xl bg-[#ffffffa3] p-5 font-extrabold"
          :class="configurable == false ? 'pointer-events-none' : ''"
        >
          <div class="col-span-3 flex flex-col items-center">
            <h3 class="text-lg font-bold bg-gradient-to-r from-slate-700 to-slate-900 bg-clip-text text-transparent mb-3">
              턴당 소요 시간
            </h3>
            <div class="w-2/3 flex justify-between mb-2">
              <template v-for="n in 11" :key="n">
                <span v-if="n % 2 != 0" class="text-xs font-medium text-slate-500 hover:text-slate-700 transition-colors duration-200">{{ n + 29 }}<span class="text-[10px] text-slate-400 ml-0.5">초</span></span>
              </template>
            </div>
            <div
              class="range-container drop-shadow-lg relative w-2/3 h-[24px] flex justify-center items-center"
            >
              <input
                type="range"
                :min="minTimeValue"
                :max="maxTimeValue"
                :step="stepTimeValue"
                class="range-slider rounded-xl appearance-none w-full bg-gradient-to-r from-gray-200 via-white to-gray-200 outline-none absolute h-[8px] shadow-inner"
                v-model="localRoomConfigs.currTurnTime"
              />
              <div
                class="ticks w-full h-[24px] pointer-events-none flex justify-between items-center p-[2px]"
              >
                <div
                  v-for="(tick, index) in ticks"
                  :key="index"
                  class="h-[6px] w-[6px] bg-gradient-to-b from-gray-300 to-gray-500 rounded-full relative z-20 shadow-sm"
                ></div>
              </div>
            </div>
          </div>
          <!-- <div class="absolute right-5 top-5 rounded-full border-4 border-[#E77DAF] flex justify-center items-center p-2 cursor-pointer" :class="isPreview ? 'bg-[#E77DAF]' : ''" @click="isPreview = !isPreview">
            <img :src="unicon" alt="" class="w-10 h-10">
          </div> -->
          <div class="col-span-3 row-span-3 flex flex-col items-center">
            <div class="grid grid-cols-3 gap-x-3 max-h-28 w-full overflow-y-scroll px-2 py-1 pb-1 pointer-events-auto">
              <template v-for="(modeGroup, idx) in chunkedModes" :key="group">
                <div class="flex justify-between w-full"  v-for="(mode, index) in modeGroup" :key="index" :class="idx === 0 ? '' : 'mt-2'">
                  <div class="flex flex-col items-center w-full modern-mode-card-container">
                    <div class="relative modern-card-wrapper group">
                      <label
                        class="relative block rounded-2xl overflow-hidden w-32 h-32 cursor-pointer transform transition-all duration-500 ease-out group-hover:scale-102 group-hover:shadow-lg group-hover:-translate-y-1"
                        :for="'mode' + mode.value"
                        :class="{
                          'ring-4 ring-opacity-60 modern-selected': localRoomConfigs.currMode === mode.value,
                        }"
                        @click="handleClick($event, mode.value)"
                        @mouseenter="startImageTransition(mode.value)"
                        @mouseleave="stopImageTransition(mode.value)"
                      >
                        <!-- Background Blur Overlay -->
                        <div class="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent z-10 group-hover:from-black/10 transition-all duration-300"></div>
                        
                        <!-- Images -->
                        <img
                          v-for="(image, imgIndex) in mode.images"
                          :key="imgIndex"
                          :src="image"
                          :alt="`${mode.text} 미리보기 ${imgIndex + 1}`"
                          class="absolute inset-0 w-full h-full object-cover transition-all duration-700 ease-out group-hover:scale-110"
                          :class="{
                            'opacity-100': mode.activeImageIndex === imgIndex,
                            'opacity-0': mode.activeImageIndex !== imgIndex,
                          }"
                        />
                        
                        <!-- Selection Checkmark -->
                        <div v-if="localRoomConfigs.currMode === mode.value" class="absolute top-3 right-3 z-20 modern-check-badge">
                          <div class="w-6 h-6 bg-gradient-to-r from-[#f78ca0] to-[#ef90b0] rounded-full flex items-center justify-center shadow-lg">
                            <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                            </svg>
                          </div>
                        </div>
                        
                        <!-- Hover Indicator -->
                        <div class="absolute inset-0 border-2 border-white/20 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-10"></div>
                      </label>
                      
                      <!-- Modern Mode Title -->
                      <div class="mt-2 text-center">
                        <h4 class="text-xs font-bold text-slate-700 group-hover:text-slate-900 transition-all duration-300 tracking-tight"
                            :class="{
                              'text-[#ef90b0] font-extrabold': localRoomConfigs.currMode === mode.value
                            }">
                          {{ mode.text }}
                        </h4>
                        <!-- Selection indicator dot -->
                        <div class="mt-1 flex justify-center">
                          <div class="w-1.5 h-1.5 rounded-full transition-all duration-300"
                               :class="localRoomConfigs.currMode === mode.value ? 'bg-[#ef90b0] shadow-lg shadow-[#ef90b0]/30' : 'bg-slate-300 group-hover:bg-slate-400'">
                          </div>
                        </div>
                      </div>
                    </div>
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
/* Modern Mode Card Styles */
.modern-card-wrapper {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.modern-selected {
  ring-color: rgb(239 144 176 / 0.6);
  box-shadow: 
    0 0 0 4px rgb(239 144 176 / 0.1),
    0 20px 40px -12px rgb(239 144 176 / 0.3),
    0 8px 25px -8px rgba(0, 0, 0, 0.1);
}

.modern-check-badge {
  animation: checkBounce 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes checkBounce {
  0% {
    transform: scale(0) rotate(-45deg);
    opacity: 0;
  }
  50% {
    transform: scale(1.2) rotate(-15deg);
  }
  100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}

.modern-mode-card-container:hover .modern-card-wrapper {
  transform: perspective(1000px) rotateX(-2deg);
}

/* Enhanced Image Hover Effects */
.modern-card-wrapper:hover label {
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.1);
}

/* Typography Enhancement */
.modern-card-wrapper h4 {
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  letter-spacing: -0.025em;
}

  .outline-color {
    outline: 4px solid;
    outline-color: transparent;
    position: relative;
    background: linear-gradient(white, white) padding-box,
                linear-gradient(45deg, #f78ca0, #ef90b0, #e797c1, #df9dd2) border-box;
    border: 4px solid transparent;
  }
  
  .outline-color::before {
    content: '';
    position: absolute;
    top: -4px;
    left: -4px;
    right: -4px;
    bottom: -4px;
    background: linear-gradient(45deg, #f78ca0, #ef90b0, #e797c1, #df9dd2);
    border-radius: inherit;
    z-index: -1;
    border-radius: 12px;
  }

  /* 모드 선택창의 스크롤바 스타일 - 그라데이션 제거 */
  .grid.grid-cols-3.gap-x-3.max-h-28.w-full.overflow-y-scroll::-webkit-scrollbar {
    width: 4px;
  }

  .grid.grid-cols-3.gap-x-3.max-h-28.w-full.overflow-y-scroll::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 2px;
  }

  .grid.grid-cols-3.gap-x-3.max-h-28.w-full.overflow-y-scroll::-webkit-scrollbar-thumb {
    background: #6b7280;
    border-radius: 2px;
  }

  .grid.grid-cols-3.gap-x-3.max-h-28.w-full.overflow-y-scroll::-webkit-scrollbar-thumb:hover {
    background: #4b5563;
  }

</style>
