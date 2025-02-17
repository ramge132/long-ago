<template>
  <div class="col-span-2">
    <!-- 방 설정 메뉴 표시 -->
    <form class="h-full">
      <div class="h-full w-full grid grid-rows-4">
        <div
          class="row-span-3 grid grid-cols-3 grid-rows-3   border drop-shadow-md rounded-xl bg-[#ffffffa3] p-5"
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
          <div class="col-span-3 row-span-2 flex flex-col items-center">
            <label class="mb-2 block">게임 모드</label>
            <div class="grid grid-cols-2 gap-x-3 h-2/3">
              <label
                class="border-2 border-black rounded-xl flex flex-col justify-between p-3"
                v-for="(mode, index) in modes"
                :key="index"
                :for="'mode' + index"
                :class="
                  localRoomConfigs.currMode === mode.value
                    ? 'shadow-lg scale-105'
                    : ''
                "
              >
                <img :src="mode.icon" alt="모드 아이콘" />
                <p class="text-xs" v-html="mode.text"></p>
                <input
                  type="radio"
                  :id="'mode' + index"
                  name="mode"
                  :value="mode.value"
                  v-model="localRoomConfigs.currMode"
                  class="self-center appearance-none border border-black rounded-xl w-5 h-5 checked:bg-white checked:border-[#EB978B] checked:border-4"
                  :checked="index === 0"
                />
              </label>
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
import { Mode1, Mode2, InviteIcon, StartIcon } from "@/assets";

const router = useRouter();
const { toClipboard } = useCilpboard();
const minTimeValue = ref(30);
const maxTimeValue = ref(40);
const stepTimeValue = ref(2);
const localRoomConfigs = ref({
  currTurnTime: 30,
  currMode: 1,
});

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
    icon: Mode1,
    text: "기본 모드",
    value: 1,
  },
  {
    icon: Mode2,
    text: "클레이 모드",
    value: 2,
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
<style></style>
