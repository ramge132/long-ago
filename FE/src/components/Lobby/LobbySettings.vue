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
            <label>턴당 소요 시간(초)</label>
            <div class="w-2/3 flex justify-between">
              <template v-for="n in 11" :key="n">
                <p v-if="n % 2 != 0">{{ n + 29 }}</p>
              </template>
            </div>
            <div
              class="range-container drop-shadow-md relative w-2/3 h-[20px] flex justify-center items-center"
            >
              <input
                type="range"
                :min="minTimeValue"
                :max="maxTimeValue"
                :step="stepTimeValue"
                class="range-slider rounded-xl appearance-none w-full bg-white outline-none absolute"
                v-model="localRoomConfigs.currTurnTime"
              />
              <div
                class="ticks w-full h-[20px] pointer-events-none flex justify-between items-center p-[2px]"
              >
                <div
                  v-for="(tick, index) in ticks"
                  :key="index"
                  class="h-[8px] w-[8px] bg-[#6d6d6d] rounded-lg relative z-20"
                ></div>
              </div>
            </div>
          </div>
          <div class="col-span-3 row-span-4 flex flex-col items-center">
            <label class="block mt-4">게임 모드</label>
            <div class="grid grid-cols-3 gap-x-8 max-h-64 w-full overflow-y-scroll p-5 pointer-events-auto">
              <template v-for="(modeGroup, idx) in chunkedModes" :key="group">
                <div class="flex justify-between w-full"  v-for="(mode, index) in modeGroup" :key="index" :class="idx === 0 ? '' : 'mt-7'">
                  <div class="flex flex-col items-center w-full">
                    <p class="mb-2">{{ mode.text }}</p>
                    <label class="rounded-lg overflow-hidden" :for="'mode' + index" :class="localRoomConfigs.currMode === mode.value ? 'outline outline-4 outline-color' : ''" @click="handleClick($event, mode.value)" @mouseover="mode.ishovered = true" @mouseleave="mode.ishovered = false">
                      <img :src="localRoomConfigs.currMode === mode.value || mode.ishovered ? modeViews[mode.value].modePreview : modeViews[mode.value].modeImage" alt="">
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
              class="duration-300 ease-in-out border-2 w-40 h-10 rounded-lg border-black bg-black text-white flex items-center justify-center hover:shadow-md hover:scale-105"
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
              class="duration-300 ease-in-out border-2 w-40 h-10 rounded-lg border-black bg-black text-white flex items-center justify-center hover:shadow-md hover:scale-105"
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
import { ref, computed, watch, defineProps, defineEmits } from "vue";
import { useRouter } from "vue-router";
import useCilpboard from "vue-clipboard3";
import toast from "@/functions/toast";
import { InviteIcon, StartIcon } from "@/assets";
import mode from "@/assets/images/modes";

const router = useRouter();
const { toClipboard } = useCilpboard();
const minTimeValue = ref(30);
const maxTimeValue = ref(40);
const stepTimeValue = ref(2);
const localRoomConfigs = ref({
  currTurnTime: 30,
  currMode: 0,
});
const modeViews = ref(
  [
  "Mode0",
  "Mode1",
  "Mode2",
  "Mode3",
  "Mode4",
  "Mode5",
  "Mode6",
  "Mode7",
  "Mode8",
  ].map((type) => ({
    modeImage: mode[`${type}`],
    modePreview: mode[`${type}_preview`],
  }))
);

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
    ishovered: false,
  },
  {
    
    text: "3D 모드",
    value: 1,
    ishovered: false,
  },
  {
    text: "코믹북 모드",
    value: 2,
    ishovered: false,
  },
  {
    
    text: "클레이 모드",
    value: 3,
    ishovered: false,
  },
  {
    text: "어린이 모드",
    value: 4,
    ishovered: false,
  },
  {
    
    text: "픽셀 모드",
    value: 5,
    ishovered: false,
  },
  {
    text: "PS1 모드",
    value: 6,
    ishovered: false,
  },
  {
    
    text: "동화책 모드",
    value: 7,
    ishovered: false,
  },
  {
    
    text: "일러스트 모드",
    value: 8,
    ishovered: false,
  },
]);

const copy = async () => {
  try {
    await toClipboard(props.InviteLink);
    toast.successToast("클립보드에 복사되었습니다.");
  } catch (error) {
    toast.errorToast("복사 실패");
    console.log(error);
  }
};

const gameStart = () => {
  if (props.participants[0].id !== props.peerId) {
    toast.errorToast("방장만 게임 시작할 수 있습니다.");
  } else if (props.participants.length < 2) {
    toast.warningToast("혼자서는 진행할 수 없습니다.");
  } else {
    emit("gameStart", {
      gameStarted: true,
      order: Array(props.participants.length)
        .fill()
        .map((value, index) => index)
        .sort(() => Math.random() - 0.5),
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
    localRoomConfigs.value.currMode = data;
  } else {
    event.preventDefault();
  }
}

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
    outline-color: #72a0ff;
  }
</style>
