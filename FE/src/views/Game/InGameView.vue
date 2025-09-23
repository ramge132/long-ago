<template>
  <div class="w-full h-full grid grid-cols-5 grid-rows-2 relative">
    <div class="h-full row-span-2 grid grid-rows-3 justify-start">
      <!-- <template v-for="(user, index) in props.participants" :key="user.id"> -->
      <template v-for="(order, index) in props.inGameOrder" :key="order">
        <div
          class="flex flex-col justify-center items-center relative ml-3"
          v-if="index < 3"
        >
          <div class="w-28 h-28 relative">
            <img :src="props.participants[order].image" class="absolute w-28 h-28 z-10" alt="프로필" />
            <div
              class="rounded-full w-24 h-24 absolute left-1/2 -translate-x-1/2 translate-y-3 z-0 scale-[115%]"
              :class="currTurn === index ? 'orb-glow-container' : ''"
              >
            </div>
          </div>
          <div
            class="absolute z-40 bg-[#ffffff] w-[120px] min-h-[30px] rounded-lg top-[20px] right-[-70px] after:absolute after:bottom-0 after:left-[10%] after:border-[15px] after:border-transparent after:border-b-0 after:border-l-0 after:mb-[-10px] after:border-t-[#ffffff] after:w-0 after:h-0 flex items-center justify-center px-3 py-1 hidden"
            :class="'speech-bubble' + index"
          >
            <p class="text-center text-sm leading-tight font-medium"></p>
          </div>
          <div
            class="absolute z-40 bg-[#ffffff] w-[80px] min-h-[60px] rounded-full bottom-[30px] right-[-20px] after:absolute after:top-0 after:left-[10%] after:border-[20px] after:border-transparent after:border-t-0 after:border-l-0 after:mt-[-10px] after:border-b-[#ffffff] after:w-0 after:h-0 flex justify-center items-center hidden"
            :class="'emoticon-bubble' + index"
          >
            <img src="" alt="" class="object-scale-down w-10 h-10" />
          </div>
          <div>{{ props.participants[order].name }}</div>
          <p></p>
          <div class="flex rounded-full bg-black p-1 text-white">
            <img :src="StarIcon" alt="별" class="w-4" />
            <div
              class=" w-5 h-5 text-center leading-[1.25rem] ml-1"

            >
              <!-- {{ 4 }} -->
              {{ props.participants[order].score }}
            </div>
          </div>
          <div class="absolute bottom-6 -right-5 font-bold text-2xl opacity-0" :class="'scoreChange' + index">
              <p></p>
          </div>
          <!-- 투표 (수정) -->
          <div class="absolute z-10 right-0 translate-x-28 top-1/2 -translate-y-1/2 flex justify-center items-center hidden scale-150" :class="'vote' + index">
            <img src="" alt="" class="w-48 h-27">
          </div>
        </div>
      </template>
      <template
        v-for="n in maxParticipants - props.participants.length"
        :key="n"
      >
        <div
          class="flex flex-col justify-center items-center ml-3"
          v-if="props.participants.length + n <= 3"
        >
          <div
            class="rounded-full overflow-hidden w-24 h-24 border-2 border-white"
          >
            <img :src="Profile.default_profile" alt="">
          </div>
          <div class="h-5"></div>
        </div>
      </template>
    </div>
    <div class="col-span-3 row-span-2 grid grid-rows-5">
      <InGameContent
        :bookContents="bookContents"
        :gameStarted="gameStarted"
        :isElected="isElected"
        :bookCover="bookCover"
        @narration-complete="onNarrationComplete"
      />
      <InGameControl
        ref="inGameControlRef"
        @broadcast-message="broadcastMessage"
        @next-turn="nextTurn"
        @card-reroll="cardReroll"
        @go-lobby="goLobby"
        :myTurn="myTurn"
        :currTurn="currTurn"
        :storyCards="storyCards"
        :endingCard="endingCard"
        :gameStarted="gameStarted"
        :isEndingMode="isEndingMode"
        :ISBN="ISBN"
        :participants="participants"
        :peerId="peerId"
        :gameId="gameId"
        @card-refreshed="$emit('card-refreshed', $event)"
        @send-exchange-request="$emit('send-exchange-request', $event)"
        @card-exchanged="$emit('card-exchanged', $event)"
        @reject-exchange="$emit('reject-exchange', $event)"
      />
    </div>
      <div class="h-full row-span-2 grid grid-rows-3 justify-end">
        <template v-for="(order, index) in props.inGameOrder" :key="order">
          <div
            class="flex flex-col justify-center items-center relative mr-3"
            v-if="index > 2"
          >
            <div class="w-28 h-28 relative">
              <img :src="props.participants[order].image" class="absolute w-28 h-28 z-10" alt="프로필" />
              <div
                class="rounded-full w-24 h-24 absolute left-1/2 -translate-x-1/2 translate-y-3 z-0 scale-[115%]"
                :class="currTurn === index ? 'orb-glow-container' : ''"
                >
              </div>
            </div>
            <div
              class="absolute z-40 bg-[#ffffff] w-[120px] min-h-[30px] rounded-lg top-[20px] left-[-70px] after:absolute after:bottom-0 after:right-[10%] after:border-[15px] after:border-transparent after:border-b-0 after:border-r-0 after:mb-[-10px] after:border-t-[#ffffff] after:w-0 after:h-0 flex items-center justify-center px-3 py-1 hidden"
              :class="'speech-bubble' + index"
            >
              <p class="text-center text-sm leading-tight font-medium"></p>
            </div>
            <div
              class="absolute z-40 bg-[#ffffff] w-[80px] min-h-[60px] rounded-full bottom-[30px] left-[-20px] after:absolute after:top-0 after:right-[10%] after:border-[20px] after:border-transparent after:border-t-0 after:border-r-0 after:mt-[-10px] after:border-b-[#ffffff] after:w-0 after:h-0 flex justify-center items-center hidden"
              :class="'emoticon-bubble' + index"
            >
              <img src="" alt="" class="object-scale-down w-10 h-10" />
            </div>
            <div>{{ props.participants[order].name }}</div>
            <p></p>
            <div class="flex rounded-full bg-black p-1 text-white">
              <img :src="StarIcon" alt="별" class="w-4" />
              <div
                class=" w-5 h-5 text-center leading-[1.25rem] ml-1"
              >
                <!-- {{ 4 }} -->
                {{ props.participants[order].score }}
              </div>
            </div>
            <div class="absolute bottom-6 -left-5 font-bold text-2xl opacity-0" :class="'scoreChange' + index">
              <p></p>
          </div>
          <!-- 투표 (수정) -->
          <div class="absolute z-10 left-0 -translate-x-28 top-1/2 -translate-y-1/2 flex justify-center items-center hidden scale-150" :class="'vote' + index">
            <img src="" alt="" class="w-48 h-27">
          </div>
          </div>
        </template>
        <template
          v-for="n in maxParticipants - props.participants.length"
          :key="n"
        >
          <div
            class="flex flex-col justify-center items-center mr-3"
            v-if="props.participants.length + n > 3"
          >
            <div
              class="rounded-full overflow-hidden w-24 h-24 border-2 border-white"
            >
              <img :src="Profile.default_profile" alt="">
            </div>
            <div class="h-5"></div>
          </div>
        </template>
      </div>
    <InGameProgress
      @next-turn="nextTurn"
      :roomConfigs="roomConfigs"
      :inProgress="inProgress"
      :percentage="percentage"
    />
    <InGameVote class="z-50" @vote-end="voteEnd" @vote-selected="onVoteSelected" :prompt="prompt" :usedCard="usedCard" :isPreview="isPreview" :key="`vote-${prompt}-${usedCard?.id || 'default'}`" v-if="prompt !== '' && isVoted === false"/>
    <!-- <Transition name="fade">
      <div
        v-if="modal.isOpen"
        @click="toggleModal"
        class="absolute bg-[#00000050] w-full h-full top-0 left-0 flex justify-center items-center"
      >
        <div
          @click.stop
          class="w-72 h-72 text-[#ffffff] font-makgeolli text-2xl rounded-md overflow-hidden flex flex-col"
        >

          <div
            class="flex-1 max-w-full bg-[#00000090] overflow-auto flex items-center justify-center"
          >

          </div>
        </div>
      </div>
    </Transition> -->
    <Transition name="fade">
      <InGameEnding v-show="props.isForceStopped" :isForceStopped="isForceStopped" :participants="participants" @winner-shown="onWinnerShown" />
    </Transition>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch, defineExpose } from "vue";
import { StarIcon, VoteUpLeftIcon, VoteUpRightIcon, VoteDownLeftIcon, VoteDownRightIcon, VoteUpLeftgif, VoteUpRightgif, VoteDownLeftgif, VoteDownRightgif } from "@/assets";
import Profile from "@/assets/images/profiles";
import {
  InGameControl,
  InGameContent,
  InGameProgress,
  InGameVote,
  InGameTrash,
  InGameEnding,
} from "@/components";

const maxParticipants = 6;
const chatTime = ref([
  [undefined, undefined],
  [undefined, undefined],
  [undefined, undefined],
  [undefined, undefined],
  [undefined, undefined],
  [undefined, undefined],
]);

// InGameControl 컴포넌트 참조
const inGameControlRef = ref(null);

const emit = defineEmits(["broadcastMessage", "gameExit", "nextTurn", "cardReroll", "voteEnd", "voteSelected", "goLobby", "winner-shown", "narration-complete", "card-refreshed", "send-exchange-request", "card-exchanged", "reject-exchange"]);

const broadcastMessage = (data) => {
  emit("broadcastMessage", data);
};

const nextTurn = (data) => {
  emit("nextTurn", data);
};

const cardReroll = () => {
  emit("cardReroll");
}
const voteEnd = (data) => {
  emit("voteEnd", data);
};

const onVoteSelected = (voteType) => {
  emit("voteSelected", voteType);
};
const goLobby = () => {
  emit("goLobby");
}

// 승자 표시 완료 후 나레이션 시작을 위한 이벤트
const onWinnerShown = () => {
  emit("winner-shown");
}

// 나레이션 완료 후 표지 표시
const onNarrationComplete = () => {
  emit("narration-complete");
}

const props = defineProps({
  roomConfigs: {
    type: Object,
  },
  connectedPeers: {
    type: Array,
  },
  receivedMessages: {
    type: Array,
  },
  participants: {
    type: Array,
  },
  inGameOrder: {
    type: Array,
  },
  currTurn: {
    type: Number,
  },
  inProgress: {
    type: Boolean,
  },
  myTurn: {
    type: Number,
  },
  bookContents: {
    type: Array,
  },
  storyCards:{
    type: Array,
  },
  endingCard:{
    type: Object,
  },
  prompt: {
    type: String,
  },
  votings: {
    type: Array,
  },
  percentage: {
    type: Number,
  },
  usedCard: {
    type: Object,
  },
  isForceStopped: {
    type: String,
  },
  gameStarted: {
    type: Boolean,
  },
  isEndingMode: {
    type: Boolean,
  },
  isElected: {
    type: Boolean,
  },
  isVoted: {
    type: Boolean,
  },
  bookCover: {
    type: Object,
  },
  ISBN: {
    type: String,
  },
  isPreview: {
    type: Boolean,
  },
  peerId: {
    type: String,
    default: ''
  },
  gameId: {
    type: String,
    default: ''
  }
});

watch(() => props.participants.map(participant => participant.score),
  (newScores, oldScores) => {
    newScores.forEach((newScore, index) => {
      if (newScore !== oldScores[index]) {
        props.inGameOrder.forEach((order, idx) => {
        if(order == index) {
        const select = document.querySelector(".scoreChange" + idx);
        if(newScore > oldScores[index]) {
          select.firstChild.textContent = "+" + (newScore - oldScores[index]);
          select.classList.add("plusScore");
          setTimeout(() => {
            select.classList.remove("plusScore");
          }, 2000);
        } else {
          select.firstChild.textContent = "-" + (oldScores[index] - newScore);
          select.classList.add("minusScore");
          setTimeout(() => {
            select.classList.remove("minusScore");
          }, 2000);
        }
      }
    });
      }
    });
    
});

watch(
  () => props.receivedMessages,
  async () => {
    const lastMessage = props.receivedMessages[props.receivedMessages.length - 1];
    if (!lastMessage || lastMessage.sender === '시스템') return;

    props.inGameOrder.forEach(async (order, index) => {
      if (props.participants[order].name === lastMessage.sender) {
        const select = ref();
        let type = 0;
        
        if (lastMessage.form === "emoticon") {
          select.value = document.querySelector(".emoticon-bubble" + index);
          type = 1;
          
          // 기존 타이머가 있다면 먼저 클리어
          if (chatTime.value[index][type]) {
            clearTimeout(chatTime.value[index][type]);
          }
          
          // 말풍선과 이모티콘을 완전히 동시에 표시
          const img = select.value.firstChild;
          
          // 이미지 src 설정과 동시에 말풍선 표시
          img.src = lastMessage.message;
          select.value.classList.remove("hidden");
          
          // 이미지 로딩 에러 방지
          img.onerror = () => {
            // 이모티콘 로드 실패 시 무시
          };
        } else {
          select.value = document.querySelector(".speech-bubble" + index);
          // 기존 텍스트 타이머가 있다면 먼저 클리어
          if (chatTime.value[index][type]) {
            clearTimeout(chatTime.value[index][type]);
          }
          select.value.firstChild.textContent = lastMessage.message;
          select.value.classList.remove("hidden");
        }
        
        // 새 타이머 설정 (이모티콘의 경우 이미 위에서 클리어됨)
        if (lastMessage.form !== "emoticon") {
          clearTimeout(chatTime.value[index][type]);
        }
        chatTime.value[index][type] = setTimeout(() => {
          select.value.classList.add("hidden");
        }, 5000);
      }
    });
  },
  { deep: true },
);

watch(
  () => props.votings.length,
  async () => {
    await nextTick();
    if(props.votings.length === props.participants.length) {
      props.votings.forEach((vote) => {
        props.inGameOrder.forEach((order, index) => {
          if (
            props.participants[order].name ==
            vote.sender
          ) {
            const select = ref();
            if (
              vote.selected ==
              "up"
            ) {
              select.value = document.querySelector(".vote" + index);
              if(index < 3) {
                select.value.firstChild.src = VoteUpLeftgif;
              } else {
                select.value.firstChild.src = VoteUpRightgif;
              }
            } else {
              select.value = document.querySelector(".vote" + index);
              if(index < 3) {
                select.value.firstChild.src = VoteDownLeftgif;
              } else {
                select.value.firstChild.src = VoteDownRightgif;
              }
            }
            select.value.classList.remove("hidden");
            setTimeout(() => {
              select.value.classList.add("hidden");
              select.value.firstChild.src = null;
            }, 3800);
          }
        });
      });
    }
  },
  { deep: true },
);

// 교환 신청 표시 함수
const showExchangeRequest = (exchangeRequestData) => {
  console.log("=== InGameView: showExchangeRequest 호출 ===");
  console.log("1. 받은 데이터:", exchangeRequestData);

  if (inGameControlRef.value && inGameControlRef.value.showExchangeRequest) {
    console.log("2. InGameControl의 showExchangeRequest 함수 호출");
    inGameControlRef.value.showExchangeRequest(exchangeRequestData);
  } else {
    console.log("2. ERROR: InGameControl ref나 showExchangeRequest 함수를 찾을 수 없음");
    console.log("   - inGameControlRef.value:", inGameControlRef.value);
    console.log("   - showExchangeRequest 함수:", inGameControlRef.value?.showExchangeRequest);
  }
};

// 외부에서 접근 가능하게 expose
defineExpose({
  showExchangeRequest,
  updateCounts: (newRefreshCount, newExchangeCount) => {
    console.log("=== InGameView updateCounts 중계 ===");
    console.log("inGameControlRef.value:", inGameControlRef.value);
    if (inGameControlRef.value && inGameControlRef.value.updateCounts) {
      console.log("InGameControl로 updateCounts 호출 중계");
      inGameControlRef.value.updateCounts(newRefreshCount, newExchangeCount);
    } else {
      console.error("❌ InGameControl ref 또는 updateCounts 메서드가 없습니다!");
    }
  }
});

onBeforeUnmount(() => {
  emit("gameExit");
});
</script>

<style scoped>
/* Orb glow effect container */
.orb-glow-container {
  position: relative;
  border-radius: 50%;
}

/* Orb backlight effect */
.orb-glow-container::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: -1;
  height: 100%;
  width: 100%;
  transform: translate(-50%, -50%) scale(0.95);
  filter: blur(10px);
  background: linear-gradient(270deg, #00bfff, #3b82f6, #06b6d4, #87ceeb);
  background-size: 150% 150%;
  border-radius: 50%;
  animation: orb-glow-animation-v3 8s linear infinite;
}

/* Orb glow animation v3 - centered and smaller movement */
@keyframes orb-glow-animation-v3 {
  0% {
    transform: translate(-50%, -50%) scale(0.95);
    background-position: 0% 50%;
    background-size: 150% 150%;
  }
  12.5% {
    transform: translate(-48%, -48%) scale(0.85);
    background-size: 120% 80%;
  }
  25% {
    transform: translate(-46%, -50%) scale(0.9);
    background-size: 130% 100%;
  }
  37.5% {
    transform: translate(-48%, -52%) scale(0.85);
    background-size: 120% 80%;
  }
  50% {
    transform: translate(-50%, -54%) scale(0.9);
    background-position: 100% 50%;
    background-size: 80% 80%;
  }
  62.5% {
    transform: translate(-52%, -52%) scale(0.85);
    background-size: 80% 120%;
  }
  75% {
    transform: translate(-54%, -50%) scale(0.9);
    background-size: 100% 130%;
  }
  87.5% {
    transform: translate(-52%, -48%) scale(0.85);
    background-size: 80% 120%;
  }
  100% {
    transform: translate(-50%, -50%) scale(0.95);
    background-position: 0% 50%;
    background-size: 150% 150%;
  }
}

.plusScore {
  color: rgb(0, 152, 0);
  animation: plus 2s ease-in-out forwards;
}

.minusScore {
  color: rgb(164, 1, 1);
  animation: minus 2s ease-in-out forwards;
}

@keyframes plus {
  0% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translateY(-100%);
  }
}

@keyframes minus {
  0% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translateY(100%);
  }
}

/* 이모티콘 이미지 렌더링 최적화 */
.emoticon-bubble0 img,
.emoticon-bubble1 img,
.emoticon-bubble2 img,
.emoticon-bubble3 img,
.emoticon-bubble4 img,
.emoticon-bubble5 img {
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
  transform: translateZ(0);
  backface-visibility: hidden;
  will-change: transform;
}
</style>
