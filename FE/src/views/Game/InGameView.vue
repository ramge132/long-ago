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
              :class="currTurn === index ? 'border-4 border-color' : ''"
              >
            </div>
          </div>
          <div
            class="absolute z-40 bg-[#ffffff] w-[120px] min-h-[30px] rounded-lg top-[20px] right-[-70px] after:absolute after:bottom-0 after:left-[10%] after:border-[15px] after:border-transparent after:border-b-0 after:border-l-0 after:mb-[-10px] after:border-t-[#ffffff] after:w-0 after:h-0 pl-3 hidden"
            :class="'speech-bubble' + index"
          >
            <p></p>
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
      />
      <InGameControl
        @broadcast-message="broadcastMessage"
        @next-turn="nextTurn"
        @card-reroll="cardReroll"
        @go-lobby="goLobby"
        :myTurn="myTurn"  
        :currTurn="currTurn"
        :storyCards="storyCards"
        :endingCard="endingCard"
        :gameStarted="gameStarted"
        :ISBN="ISBN"
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
                :class="currTurn === index ? 'border-4 border-color' : ''"
                >
              </div>
            </div>
            <div
              class="absolute z-40 bg-[#ffffff] w-[120px] min-h-[30px] rounded-lg top-[20px] left-[-70px] after:absolute after:bottom-0 after:right-[10%] after:border-[15px] after:border-transparent after:border-b-0 after:border-r-0 after:mb-[-10px] after:border-t-[#ffffff] after:w-0 after:h-0 pl-3 hidden"
              :class="'speech-bubble' + index"
            >
              <p></p>
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
    <InGameVote class="z-50" @vote-end="voteEnd" :prompt="prompt" :usedCard="usedCard" :isPreview="isPreview" v-if="prompt !== '' && isVoted === false"/>
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
      <InGameEnding v-show="props.isForceStopped" :isForceStopped="isForceStopped" :participants="participants" />
    </Transition>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from "vue";
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

const emit = defineEmits(["broadcastMessage", "gameExit", "nextTurn", "cardReroll", "voteEnd", "goLobby"]);

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
const goLobby = () => {
  emit("goLobby");
}

const props = defineProps({
  roomConfigs: {
    Type: Object,
  },
  connectedPeers: {
    Type: Array,
  },
  receivedMessages: {
    Type: Array,
  },
  participants: {
    Type: Array,
  },
  inGameOrder: {
    Type: Array,
  },
  currTurn: {
    Type: Number,
  },
  inProgress: {
    Type: Boolean,
  },
  myTurn: {
    Type: Number,
  },
  bookContents: {
    Type: Array,
  },
  storyCards:{
    Type: Array,
  },
  endingCard:{
    Type: Object,
  },
  prompt: {
    Type: String,
  },
  votings: {
    Type: Array,
  },
  percentage: {
    Type: Number,
  },
  usedCard: {
    Type: Object,
  },
  isForceStopped: {
    Type: String,
  },
  gameStarted: {
    Type: Boolean,
  },
  isElected: {
    Type: Boolean,
  },
  isVoted: {
    Type: Boolean,
  },
  bookCover: {
    Type: Object,
  },
  ISBN: {
    Type: String,
  },
  isPreview: {
    Type: Boolean,
  },
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
  () => {
    props.inGameOrder.forEach((order, index) => {
      if (
        props.receivedMessages[props.receivedMessages.length - 1].sender != '시스템' &&
        props.participants[order].name ==
        props.receivedMessages[props.receivedMessages.length - 1].sender
      ) {
        const select = ref();
        let type = 0;
        if (
          props.receivedMessages[props.receivedMessages.length - 1].form ==
          "emoticon"
        ) {
          select.value = document.querySelector(".emoticon-bubble" + index);
          type = 1;
          select.value.firstChild.src =
            props.receivedMessages[props.receivedMessages.length - 1].message;
        } else {
          select.value = document.querySelector(".speech-bubble" + index);
          select.value.firstChild.textContent =
            props.receivedMessages[props.receivedMessages.length - 1].message;
        }
        select.value.classList.remove("hidden");
        clearTimeout(chatTime.value[index][type]);
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

onBeforeUnmount(() => {
  emit("gameExit");
});
</script>

<style scoped>
.border-color {
  border-color: #72a0ff;
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
</style>
