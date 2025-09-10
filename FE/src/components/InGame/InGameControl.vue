<template>
  <div class="row-span-2 flex flex-col justify-between py-2 relative">
    <div v-if="gameStarted" class="flex justify-center items-center grow">
      <div class="flex flex-col justify-center items-center w-3/4 mr-3">
          <transition-group name="list" tag="div" class="cardList flex justify-center w-full" :class="dynamicClass" @before-leave="setLeaveStyle" @after-leave="updateClass"> 
            <div v-for="(card) in storyCards" :key="card.id" class="handCard relative">
              <img :src="CardImage.storyCardBack" alt="스토리카드" class="w-28">
              <div
                class="storycard w-full h-full p-2 flex items-center justify-center absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 font-katuri text-[#eadfcd] text-3xl leading-tight text-center">
                <div v-html="formatCardText(card.keyword)"></div>
              </div>
            </div>
          </transition-group>
      </div>
      <div class="flex flex-col flex-1 justify-center items-center">
        <div class="relative endingcard cursor-pointer" @click="sendEndingCard" ref="cardRef">
          <img :src="CardImage.endingCardBack" alt="엔딩카드" class="w-28">
          <div
            class="endingcard-text w-full h-full p-3 flex items-center justify-center absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 font-katuri text-[#fee09e]" ref="contentRef">
            {{ endingCard.content }}</div>
        </div>
      </div>
    </div>
    <div v-else class="flex justify-center items-center gap-x-4 my-auto">
      <div
        @click="emit('goLobby')"
        class="bg-gray-50 hover:bg-gray-200 p-4 rounded-2xl font-omp flex items-center gap-x-3 cursor-pointer"
      >
        로비로 돌아가기
        <img :src="ReturnIcon" alt="" class="w-4">
      </div>
      <div
        v-if="ISBN != ''"
        @click="copy"
        class="bg-gray-50 hover:bg-gray-200 p-4 rounded-full cursor-pointer"
      >
        <img :src="ShareIcon" alt="" class="w-4">
      </div>
    </div>
    <div class="absolute bottom-4 flex justify-center items-end gap-x-2 w-full z-[30]">
      <div class="rounded-full bg-[#ffffffdb] drop-shadow-md h-10 flex flex-1 px-3 items-center"
        v-for="(mode, index) in chatMode" :key="index" :class="index == currChatModeIdx ? '' : 'hidden'">
        <div class="flex flex-nowrap flex-col justify-center items-center relative cursor-pointer" @click="changeMode">
          <p class="whitespace-nowrap absolute top-[-1.25rem] font-semibold" style="text-shadow: 2px 0 4px #fff, -2px 0 4px #fff, 0 2px 4px #fff, 0 -2px 4px #fff, 1px 1px #fff, -1px -1px 4px #fff, 1px -1px 4px #fff, -1px 1px 4px #fff;" v-text="mode.mark" :class="index === 1 ? 'text-[#c3b6a5]' : ''"></p>
          <img :src="ChangeIcon" alt="채팅모드변경" class="h-3/5" />
        </div>
        <input type="text" class="pl-3 bg-transparent w-full h-full text-2xl font-semibold mx-2 focus:outline-0" v-model="message"
          @keyup.enter="mode.fucntion" :placeholder="mode.placeholder" :ref="(el) => (chatRefs[index] = el)" />
        <button class="rounded-full w-8 h-8 shrink-0 p-1 flex justify-center items-center focus:outline-0"
          @click="mode.fucntion">
          <img :src="SendIcon" alt="보내기" class="object-scale-down w-3/4 h-3/4" />
        </button>
      </div>
      <div class="relative w-10 h-10">
        <button
          class="bg-[#ffffff] hover:bg-gray-200 rounded-full w-10 h-10 flex justify-center items-center drop-shadow-md z-10 absolute bottom-0 focus:outline-0"
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
        v-if="gameStarted"
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
import { RefreshIcon, SendIcon, EmoticonIcon, ChangeIcon, TrashIcon, ReturnIcon, ShareIcon } from "@/assets";
import CardImage from "@/assets/cards"
import { useUserStore } from "@/stores/auth";
import emoji from "@/assets/images/emoticons";
import toast from "@/functions/toast";
import useCilpboard from "vue-clipboard3";

const userStore = useUserStore();
const { toClipboard } = useCilpboard();
const toggleEmoticon = ref(false);
const message = ref("");
const chatRefs = ref([]);
const cardRef = ref(null);
const contentRef = ref(null);
const contentSizes = ref([
  "xl", "lg", "sm", "xs"
]);
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
  gameStarted: {
    Type: Boolean,
  },
  ISBN: {
    Type: String,
  },
});

const dynamicClass = ref(`card${props.storyCards.length}`);

const emit = defineEmits(["broadcastMessage", "nextTurn", "cardReroll", "goLobby"]);

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
  if (props.gameStarted === false) {
    toast.errorToast("게임 진행중에만 이야기를 제출할 수 있습니다!");
    return;
  }
  if (props.myTurn !== props.currTurn) {
    toast.errorToast("자신의 턴에만 이야기를 제출할 수 있습니다!");
    return;
  }
  if (message.value.trim()) {
    // 제출된 내용이 엔딩카드 내용과 일치하는지 확인
    const isEndingSubmit = message.value.trim() === props.endingCard.content.trim();
    
    emit("nextTurn", {
      prompt: message.value,
      isEnding: isEndingSubmit, // 확인된 값을 전달
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
    console.log("🎯 [DEBUG] sendEndingCard 호출됨");
    console.log("🎯 [DEBUG] 엔딩카드 내용:", props.endingCard.content);
    console.log("🎯 [DEBUG] isEnding 값:", true);
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
    placeholder: "한 카드만 사용할 수 있습니다",
  },
]);
const currChatModeIdx = ref(0);

window.addEventListener("keydown", (e) => {
  if (e.key === "Tab"){
    changeMode();
    e.preventDefault();
  }
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

watch(() => props.currTurn, (newVal) => {
  if(newVal === props.myTurn) {
    currChatModeIdx.value = 1; // 내 턴이면 이야기 모드
  } else {
    currChatModeIdx.value = 0; // 내 턴이 아니면 대화 모드
  }
}, {immediate: true});

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

watch(() => props.endingCard, async () => {
  await nextTick();
  if(contentRef.value && cardRef.value) {
    let index = 0;
    contentRef.value.classList.add("text-" + contentSizes.value[index]);
    while(contentRef.value.scrollHeight > cardRef.value.clientHeight && index < contentSizes.value.length - 1) {
      contentRef.value.classList.remove("text-" + contentSizes.value[index++]);
      contentRef.value.classList.add("text-" + contentSizes.value[index]);
    }
  }
}, {deep: true, immediate: true});

onMounted(() => {
  nextTick(() => {
    document.querySelectorAll(".handCard").forEach((el, index, arr) => {
    let computedStyle;
    let transform;
    el.addEventListener("mouseenter", () => {
      arr.forEach((item, i) => item.style.zIndex = i); // 초기화
      el.style.zIndex = arr.length; // hover된 요소를 가장 위로
      computedStyle = window.getComputedStyle(el);
      transform = computedStyle.transform;
      el.style.setProperty("scale", "120%"); // CSS 변수 설정
    });
    el.addEventListener("mouseleave", () => {
    el.style.zIndex = index; // 원래 z-index로 복원
    el.style.setProperty("scale", "100%"); // CSS 변수 원래 값으로 복원
  });
  });
  });
});

onkeydown = (e) => {
  // 입력창이 이미 포커스되어 있지 않고, 일반 문자 키인 경우에만
  if (!e.target.matches('input, textarea, [contenteditable]') && 
      e.key.length === 1 && 
      !e.ctrlKey && !e.altKey && !e.metaKey) {
    const chatInput = chatRefs.value[currChatModeIdx.value];
    if (chatInput) {
      chatInput.focus();
    }
  }
};

const formatCardText = (text) => {
  if (!text || text.length <= 3) {
    return text;
  }
  
  // 4글자 이상인 경우 더 균등하게 분할
  if (text.length === 4) {
    return text.substring(0, 2) + '<br>' + text.substring(2);
  } else if (text.length === 5) {
    return text.substring(0, 2) + '<br>' + text.substring(2);
  } else if (text.length === 6) {
    return text.substring(0, 3) + '<br>' + text.substring(3);
  } else {
    // 7글자 이상인 경우 중간 지점에서 분할
    const midPoint = Math.ceil(text.length / 2);
    return text.substring(0, midPoint) + '<br>' + text.substring(midPoint);
  }
};

const copy = async () => {
  try {
    await toClipboard(import.meta.env.VITE_MAIN_API_SERVER_URL + "?ISBN=" + props.ISBN);
    toast.successToast("클립보드에 복사되었습니다.");
  } catch (error) {
    toast.errorToast("복사 실패");
  }
};
</script>

<style scoped>
.reroll {
  background: linear-gradient(70deg, #fafcca 65%, #907800 35%);
}

.emoticon {
  transition: all 0.3s ease-in-out;
}

.handCard {
  transform: var(--original-transform, none) scale(var(--hover-scale, 100%));
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
