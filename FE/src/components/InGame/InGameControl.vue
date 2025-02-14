<template>
  <div class="row-span-2 flex flex-col justify-between py-2 relative">
    <div class="flex justify-center items-center grow">
      <div class="flex flex-col justify-center items-center w-3/4 mr-3">
          <transition-group name="list" tag="div" class="cardList flex justify-center w-full" :class="dynamicClass" @before-leave="setLeaveStyle" @after-leave="updateClass"> 
            <div v-for="(card) in storyCards" :key="card.id" class="handCard relative">
              <img :src="CardImage.storyCardBack" alt="스토리카드" class="w-28">
              <div
                class="storycard w-full h-full p-2 flex items-center justify-center absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 font-katuri text-[#eadfcd] text-3xl">
                {{ card.keyword }}</div>
            </div>
          </transition-group>
      </div>
      <div class="flex flex-col flex-1 justify-center items-center">
        <div class="relative endingcard cursor-pointer" @click="sendEndingCard">
          <img :src="CardImage.endingCardBack" alt="엔딩카드" class="w-28">
          <div
            class="endingcard-text w-full h-full p-3 flex items-center justify-center absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 font-katuri text-[#fee09e] text-xl">
            {{ endingCard.content }}</div>
        </div>
      </div>
    </div>
    <div class="absolute bottom-4 flex justify-center items-end gap-x-2 w-full z-[30]">
      <div class="rounded-full bg-[#ffffffdb] drop-shadow-md h-10 flex flex-1 px-3 items-center"
        v-for="(mode, index) in chatMode" :key="index" :class="index == currChatModeIdx ? '' : 'hidden'">
        <div class="flex flex-nowrap flex-col justify-center items-center relative cursor-pointer" @click="changeMode">
          <p class="whitespace-nowrap absolute top-[-1.25rem]" v-text="mode.mark"></p>
          <img :src="ChangeIcon" alt="채팅모드변경" class="h-3/5" />
        </div>
        <input type="text" class="pl-3 bg-transparent w-full h-full text-2xl font-semibold mx-2" v-model="message"
          @keyup.enter="mode.fucntion" :placeholder="mode.placeholder" :ref="(el) => (chatRefs[index] = el)" />
        <button class="rounded-full w-8 h-8 shrink-0 p-1 flex justify-center items-center"
          @click="mode.fucntion">
          <img :src="SendIcon" alt="보내기" class="object-scale-down w-3/4 h-3/4" />
        </button>
      </div>
      <div class="relative w-10 h-10">
        <button
          class="bg-[#ffffff] hover:bg-gray-200 rounded-full w-10 h-10 flex justify-center items-center drop-shadow-md z-10 absolute bottom-0"
          @click="toggleEmoticon = !toggleEmoticon">
          <img :src="EmoticonIcon" alt="감정표현" class="w-6" />
        </button>
        <div class="rounded-full w-10 bg-[#ffffffa0] absolute bottom-2 overflow-hidden emoticon"
          :class="toggleEmoticon ? 'max-h-[520px]' : 'max-h-0'">
          <button class="rounded-full w-10 h-10 p-1 flex justify-center items-center drop-shadow-md z-0"
            v-for="(emoticon, index) in emoticons" :key="index" @click="sendEmoticon(emoticon.d_image)">
            <img :src="emoticon.s_image" alt="이모티콘" />
          </button>
          <div class="w-8 h-8">
          </div>
        </div>
        <!-- <button
            class="bg-[#ffffff] rounded-full w-10 h-10 flex justify-center items-center drop-shadow-md z-10 absolute bottom-[137%]"
            @click="openTrashcan">
            <img :src="TrashIcon" alt="쓰레기통" class="w-6" />
          </button> -->
      </div>
      <div
        class="w-10 h-24 bg-[#ffffffdb] hover:bg-gray-100 rounded-full flex flex-col items-center justify-center text-center text-[10px] cursor-pointer"
        @click="cardReroll">
        <img :src="RefreshIcon" alt="" class="w-6">
        <p>결말<br>새로고침</p>
        <p class="text-xl">{{ rerollCount }}</p>
      </div>

      <!-- <div class="paper z-50 flex justify-center items-center">
        <div class="bg-effect rounded-lg overflow-hidden w-4/5 h-4/5">
          <img :src="testImage" alt="테스트이미지">
        </div>
      </div>

      <svg>
        <defs>
          <filter id="crumple-effect">
            <feTurbulence type="fractalNoise" baseFrequency="0.01" numOctaves="20" result="turbulence" />
            <feDisplacementMap in2="turbulence" in="SourceGraphic" scale="50" />
          </filter>
        </defs>
      </svg> -->

    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from "vue";
import { RefreshIcon, SendIcon, EmoticonIcon, ChangeIcon, TrashIcon } from "@/assets";
import CardImage from "@/assets/cards"
import { useUserStore } from "@/stores/auth";
import emoji from "@/assets/images/emoticons";
import toast from "@/functions/toast";
import testImage from "@/assets/test.png";

const userStore = useUserStore();
const toggleEmoticon = ref(false);
const message = ref("");
const chatRefs = ref([]);
const rerollCount = ref(3);
const emoticons = ref(
  [
    "laugh",
    "wrath",
    "confused",
    "asleep",
    "crossed",
    "fear",
    "expressionless",
    "loving",
    "sad",
    "sunglasses",
    "tongue",
    "wink",
  ].map((type) => ({
    d_image: emoji[`d_${type}`],
    s_image: emoji[`s_${type}`],
  }))
);

const props = defineProps({
  myTurn: {
    Type: Number,
  },
  currTurn: {
    Type: Number,
  },
  storyCards: {
    Type: Array,
  },
  endingCard: {
    Type: Object,
  },
});

const dynamicClass = ref(`card${props.storyCards.length}`);

const emit = defineEmits(["broadcastMessage", "nextTurn", "cardReroll"]);

const sendChat = () => {
  if (message.value.trim()) {
    emit("broadcastMessage", {
      sender: userStore.userData.userNickname,
      message: message.value,
    });
    message.value = "";
  }
};
const sendprompt = () => {
  if (props.myTurn !== props.currTurn) {
    toast.errorToast("자신의 턴에만 이야기를 제출할 수 있습니다!");
  } else if (message.value.trim()) {
    emit("nextTurn", {
      prompt: message.value
    });
    message.value = "";
    chatRefs.value[currChatModeIdx.value].blur();
  }
};
const sendEmoticon = (data) => {
  emit("broadcastMessage", {
    sender: userStore.userData.userNickname,
    message: data,
    form: "emoticon",
  });
  toggleEmoticon.value = false;
};
const sendEndingCard = () => {
  if (props.myTurn !== props.currTurn) {
    toast.errorToast("자신의 턴에만 결말카드를 제출할 수 있습니다!");
  } else {
    emit("nextTurn", {
      prompt: props.endingCard.content,
      isEnding: true,
    });
  }
}

const chatMode = ref([
  {
    mark: "대화",
    fucntion: sendChat,
    placeholder: "채팅 입력",
  },
  {
    mark: "이야기",
    fucntion: sendprompt,
    placeholder: "다음 이어질 이야기를 작성해주세요",
  },
]);
const currChatModeIdx = ref(0);

window.addEventListener("keydown", (e) => {
  if (e.ctrlKey) changeMode();
});

const changeMode = () => {
  currChatModeIdx.value = (currChatModeIdx.value + 1) % chatMode.value.length;
};

const cardReroll = () => {
  if (rerollCount.value) {
    emit("cardReroll");
    rerollCount.value--;
  } else {
    toast.errorToast("모두 사용했습니다!");
  }
};

const setLeaveStyle = (el) => {
  const computedStyle = window.getComputedStyle(el);
  const transform = computedStyle.transform; // 현재 transform 값을 가져옴
  el.style.transition = "all 1s ease";
  el.style.transform = `${transform} translateY(-50px)`; // 원래 transform 유지 + 추가 애니메이션
  el.style.opacity = "0";
};

// transition 끝난 후 class 업데이트
const updateClass = () => {
  nextTick(() => {
    dynamicClass.value = `card${props.storyCards.length}`;
  });
};

watch(currChatModeIdx, async (newIndex, oldIndex) => {
  // 기존 input blur()
  if (chatRefs.value[oldIndex]) {
    chatRefs.value[oldIndex].blur();
  }

  // DOM 업데이트 후 focus() 실행
  await nextTick(); // display: none → block 변경 후 실행 보장
  if (chatRefs.value[newIndex]) {
    chatRefs.value[newIndex].focus();
  }
});

onMounted(() => {
  nextTick(() => {
    document.querySelectorAll(".handCard").forEach((el, index, arr) => {
    el.addEventListener("mouseenter", () => {
      arr.forEach((item, i) => item.style.zIndex = i); // 초기화
      el.style.zIndex = arr.length; // hover된 요소를 가장 위로
    });
    el.addEventListener("mouseleave", () => {
    el.style.zIndex = index; // 원래 z-index로 복원
  });
  });

  });
});
</script>

<style scoped>
.reroll {
  background: linear-gradient(70deg, #fafcca 65%, #907800 35%);
}

.emoticon {
  transition: all 0.3s ease-in-out;
}

.storycard {
  text-shadow: -1px 0px #9f876a, 0px 1px #9f876a, 1px 0px #9f876a, 0px -1px #9f876a;
}

.endingcard-text {
  text-shadow: -1px 0px #8a622a, 0px 1px #8a622a, 1px 0px #8a622a, 0px -1px #8a622a;
}

@keyframes swing {
  0% {
    transform: rotate(-2deg);
  }

  100% {
    transform: rotate(2deg);
  }
}

.endingcard {
  transition: transform 0.2s ease-in-out;
  transform-origin: bottom center;
}

.endingcard:hover {
  animation: swing 0.5s ease-in-out infinite alternate;
}

.paper {
  padding: 2rem;
  position: relative;
  box-sizing: border-box;
}

.paper:before {
  background-image: radial-gradient(#C9B29C, #C9B29C);
  content: ' ';
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  z-index: -1;
  display: block;
  filter: url("#crumple-effect") drop-shadow(0 2px 2px rgba(0, 0, 0, 0.1));
}

.bg-effect {
  display: inline-block;
  position: relative;
}

.bg-effect:after {
  position: absolute;
  display: block;
  content: "";
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  box-shadow:
    inset 0 0 30px #C9B29C
    /* 배경과 같은 색 */
    ,
    inset 0 0 30px #C9B29C,
    inset 0 0 30px #C9B29C,
    inset 0 0 30px #C9B29C;
}

.card4 > :nth-child(1){
  transform: rotate(-10deg) translateY(13px);
}

.card4 > :nth-child(2){
  transform: rotate(-3deg) translateX(-10px);
}
.card4 > :nth-child(3){
  transform: rotate(3deg) translateX(-20px);
}
.card4 > :nth-child(4){
  transform: rotate(10deg) translateX(-30px) translateY(15px);
}

.card3 > :nth-child(1){
  transform: rotate(-3deg) translateY(3px) translateX(10px);
}
.card3 > :nth-child(2){
  transform: rotate(0);
}
.card3 > :nth-child(3){
  transform: rotate(3deg) translateY(3px) translateX(-10px);
}

.card2 > :nth-child(1){
  transform: rotate(-2deg);
}
.card2 > :nth-child(2){
  transform: rotate(2deg) translateX(-10px);
}

</style>
