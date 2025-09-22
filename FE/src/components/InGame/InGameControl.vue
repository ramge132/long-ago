<template>
  <div class="row-span-2 flex flex-col justify-between py-2 relative">
    <div v-if="gameStarted" class="flex justify-center items-center grow" style="transform: translateX(3px);">
      <!-- 스토리 카드 영역 -->
      <div class="flex justify-center items-end w-3/4 mr-3 h-48 -translate-y-8" :class="isEndingMode ? 'opacity-50' : ''">
          <transition-group name="list" tag="div" class="cardList flex justify-center items-end w-full h-full" :class="dynamicClass" @before-leave="setLeaveStyle" @after-leave="updateClass">
            <div
              v-for="(card) in storyCards"
              :key="card.id"
              class="handCard relative transition-all duration-300"
              :class="getCardHighlightClass(card.id)"
            >
              <img :src="CardImage.getStoryCardImage(card.id)" :alt="`스토리카드 ${card.keyword}`" class="w-36">
              <!-- 소프트 글로우 효과 -->
              <div
                v-if="highlightedCards.includes(card.id)"
                class="card-glow-effect absolute inset-0 pointer-events-none"
              ></div>
            </div>
          </transition-group>
      </div>
      <div class="flex justify-center items-end flex-1 h-48 -translate-y-8">
        <!-- 엔딩카드는 항상 표시 -->
        <div class="relative endingcard cursor-pointer" @click="sendEndingCard" ref="cardRef">
          <img :src="CardImage.getEndingCardImage(endingCard.id)" :alt="`엔딩카드 ${endingCard.id}`" class="w-36">
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
    <div class="absolute bottom-4 flex justify-center items-end gap-x-2 w-full z-[30] pointer-events-none">
      <div class="rounded-full bg-[#ffffffdb] drop-shadow-md h-10 flex flex-1 px-3 items-center pointer-events-auto"
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
      <div class="relative w-10 h-10 pointer-events-auto">
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
      <div v-if="gameStarted" class="relative w-10 h-10 pointer-events-auto">
        <!-- 결말 새로고침 버튼 (호버 확장형) -->
        <div
          class="refresh-button-container absolute bottom-0 w-10 bg-[#ffffffa0] rounded-full overflow-hidden cursor-pointer transition-all duration-300 ease-in-out"
          :class="'max-h-10 hover:max-h-24'"
          @click="cardReroll">
          <!-- 기본 상태 아이콘 버튼 (항상 표시) -->
          <button class="bg-[#ffffff] rounded-full w-10 h-10 flex justify-center items-center drop-shadow-md z-10 relative focus:outline-0">
            <img :src="RefreshIcon" alt="결말 새로고침" class="w-6" />
          </button>
          <!-- 확장 영역 (호버 시 표시) -->
          <div class="expanded-content flex flex-col items-center justify-center text-center text-[10px] text-gray-700 pt-1 pb-2">
            <p class="leading-tight">결말<br>새로고침</p>
            <p class="text-lg font-bold">{{ rerollCount }}</p>
          </div>
        </div>
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
import { ref, watch, nextTick, onMounted, computed } from "vue";
import { RefreshIcon, SendIcon, EmoticonIcon, ChangeIcon, TrashIcon, ReturnIcon, ShareIcon } from "@/assets";
import CardImage from "@/assets/cards"
import { useUserStore } from "@/stores/auth";
import emoji from "@/assets/images/emoticons";
import toast from "@/functions/toast";
import useCilpboard from "vue-clipboard3";

// 디바운스 함수
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

const userStore = useUserStore();
const { toClipboard } = useCilpboard();
const toggleEmoticon = ref(false);
const message = ref("");
const chatRefs = ref([]);
const cardRef = ref(null);
const rerollCount = ref(3);

// 실시간 카드 매칭을 위한 상태
const highlightedCards = ref([]);

// 카드 변형어 데이터 (init_db.sql 기반)
const cardVariants = {
  // 인물
  1: ['호랑이'],
  2: ['유령'],
  3: ['농부'],
  4: ['상인'],
  5: ['신'],
  6: ['외계인'],
  7: ['박사'],
  8: ['아이돌'],
  9: ['마법사'],
  10: ['마왕'],
  11: ['소녀', '소년'],
  12: ['부자'],
  13: ['탐정'],
  14: ['노인'],
  15: ['가난뱅이'],
  16: ['공주'],
  17: ['닌자'],

  // 사물
  18: ['핸드폰'],
  19: ['인형'],
  20: ['부적'],
  21: ['지도'],
  22: ['가면'],
  23: ['칼'],
  24: ['피리'],
  25: ['지팡이'],
  26: ['태양'],
  27: ['날개'],
  28: ['의자'],
  29: ['시계'],
  30: ['보석'],
  31: ['UFO', 'ufo', '유에포', '유에프오', '유애포', '유애프오', '유예포', '유예프오'],
  32: ['함정'],
  33: ['총'],
  34: ['타임머신'],

  // 장소
  35: ['바다'],
  36: ['다리'],
  37: ['묘지'],
  38: ['식당'],
  39: ['박물관'],
  40: ['비밀'],
  41: ['사막'],
  42: ['저택'],
  43: ['천국'],

  // 사건
  44: ['사망', '뒤졌', '뒤질', '뒤져'],
  45: ['배신'],
  46: ['계약'],
  47: ['폭발'],
  48: ['승리', '이김', '이긴', '이겨', '이겼', '이길'],
  49: ['패배', '짐', '진', '져', '졌', '질'],
  50: ['음모'],
  51: ['공연'],
  52: ['식사'],
  53: ['시간이 지남', '시간이'],
  54: ['떨어짐', '추락', '낙하', '하락', '무너짐', '넘어짐', '떨어'],
  55: ['모험'],
  56: ['희생'],
  57: ['실패'],
  58: ['유혹'],
  59: ['중단', '멈춤', '멈춰', '멈췄', '멈출'],
  60: ['의식'],
  61: ['고백'],
  62: ['짝사랑'],
  63: ['진화'],
  64: ['텔레파시'],
  65: ['노화'],
  66: ['멸망'],
  67: ['결투'],
  68: ['부활'],

  // 상태
  69: ['빛남', '빛난', '빛나', '빛났', '빛날', '빛내'],
  70: ['굶주림', '굶주린', '굶주려', '굶주리', '굶주렸', '굶주릴', '굶은', '굶음', '굶었', '굶을', '굶긴', '굶어', '굶겨', '배고픔', '배고픈', '배고프다'],
  71: ['착각'],
  72: ['순진함', '순진한', '순진하', '순진했', '순진할'],
  73: ['그리움', '그리운', '그리워', '그리웠', '그리울'],
  74: ['집착'],
  75: ['절망'],
  76: ['흥분'],
  77: ['실망'],
  78: ['귀찮음', '귀찮은', '귀찮아', '귀찮았', '귀찮을', '귀찮게'],
  79: ['자신만만함', '자신'],
  80: ['메스꺼움', '메스꺼운', '메스꺼워', '메스꺼웠', '메스꺼울'],
  81: ['들뜸', '들뜬', '들뜨', '들떴', '들뜰'],
  82: ['격분'],
  83: ['희열'],
  84: ['호기심'],
  85: ['지루함', '지루한', '지루하', '지루했', '지루할', '따분함', '무료함', '심심한', '심심하다', '무료하다'],
  86: ['간절함', '간절한', '간절하', '간절했', '간절할', '간절하다', '간절하게', '간절히 바라다'],
  87: ['잠재력'],
  88: ['자존심'],
  89: ['이쁨', '이쁜', '이쁘', '이쁠', '이뻤', '예쁜', '예쁘', '예뻤', '잘생긴', '잘생겨', '잘생겼', '잘생길', '잘생김', '이쁘다', '예쁘다', '잘생기다', '예뻐요', '이뻐요', '예쁨이 있다'],
  90: ['거대함', '거대한', '거대하', '거대했', '거대할']
};
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
  isEndingMode: {
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
  if (props.isEndingMode) {
    toast.errorToast("결말 모드에서는 이야기를 입력할 수 없습니다! 결말 카드를 사용하세요!");
    return;
  }
  if (props.myTurn !== props.currTurn) {
    toast.errorToast("자신의 턴에만 이야기를 제출할 수 있습니다!");
    return;
  }
  if (message.value.trim()) {
    // 엔딩카드 내용과 일치하는 경우만 결말로 처리
    const isEndingSubmit = message.value.trim() === props.endingCard.content.trim();

    emit("nextTurn", {
      prompt: message.value,
      isEnding: isEndingSubmit,
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

// 자유 결말 작성 함수 (새로 추가)
const sendFreeEnding = () => {
  if (props.gameStarted === false) {
    toast.errorToast("게임 진행중에만 결말을 제출할 수 있습니다!");
    return;
  }
  if (!props.isEndingMode) {
    toast.errorToast("결말 모드에서만 자유 결말을 작성할 수 있습니다!");
    return;
  }
  if (props.myTurn !== props.currTurn) {
    toast.errorToast("자신의 턴에만 결말을 제출할 수 있습니다!");
    return;
  }
  if (message.value.trim()) {
    emit("nextTurn", {
      prompt: message.value,
      isEnding: true,  // 결말카드와 동일하게 isEnding: true
      isFreeEnding: true,  // 자유 결말 구분용 플래그
    });

    message.value = "";
    chatRefs.value[currChatModeIdx.value].blur();
  }
};

const chatMode = computed(() => {
  const modes = [
    {
      mark: "대화",
      fucntion: sendChat,
      placeholder: "채팅 입력",
    }
  ];

  // 결말 모드에 따라 다른 모드 추가
  if (props.isEndingMode) {
    // 결말 모드: 자유 결말 작성 가능
    modes.push({
      mark: "결말",
      fucntion: sendFreeEnding,
      placeholder: "점수를 조금 얻지만 자유롭게 결말을 맺을 수 있습니다",
    });
  } else {
    // 일반 모드: 이야기 모드
    modes.push({
      mark: "이야기",
      fucntion: sendprompt,
      placeholder: "카드는 자동으로 인식됩니다 (한 장만 사용 가능)",
    });
  }

  return modes;
});
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
    // 카드 변경 후 호버 효과 재설정
    setupCardHoverEffects();
  });
};

watch(() => props.currTurn, (newVal) => {
  // 채팅바는 항상 표시하되, 내 턴일 때만 이야기 모드로 전환
  if(newVal === props.myTurn && chatMode.value.length > 1) {
    currChatModeIdx.value = 1; // 내 턴이면 이야기 모드 (있는 경우)
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


const setupCardHoverEffects = () => {
  nextTick(() => {
    const cards = document.querySelectorAll(".handCard");
    cards.forEach((el, index) => {
      // 기존 이벤트 리스너 제거 (중복 방지)
      el.removeEventListener("mouseenter", el._hoverEnter);
      el.removeEventListener("mouseleave", el._hoverLeave);

      const originalTransform = window.getComputedStyle(el).transform;

      el._hoverEnter = () => {
        cards.forEach((item, i) => item.style.zIndex = i); // 초기화
        el.style.zIndex = 50; // 채팅창(z-30)보다 높게 설정
        el.style.transform = `${originalTransform} translateY(-12px) rotateY(3deg)`;
        el.style.filter = "brightness(1.1) saturate(1.1)";
        el.style.boxShadow = "0 20px 40px rgba(0, 0, 0, 0.15), 0 8px 16px rgba(0, 0, 0, 0.1)";
      };

      el._hoverLeave = () => {
        el.style.zIndex = index; // 원래 z-index로 복원
        el.style.transform = originalTransform; // 원래 transform으로 복원
        el.style.filter = "";
        el.style.boxShadow = "";
      };

      el.addEventListener("mouseenter", el._hoverEnter);
      el.addEventListener("mouseleave", el._hoverLeave);
    });
  });
};

onMounted(() => {
  setupCardHoverEffects();
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

// 실시간 카드 매칭 함수
const analyzeInput = (inputText) => {
  if (!inputText || !props.storyCards) {
    highlightedCards.value = [];
    return;
  }

  const matchedCards = [];
  const cleanText = inputText.trim().toLowerCase();

  // 사용자가 소유한 카드들에 대해서만 검사
  props.storyCards.forEach(card => {
    const variants = cardVariants[card.id] || [];

    // 각 변형어가 입력 텍스트에 포함되어 있는지 확인 (단순 포함 검사)
    const isMatched = variants.some(variant => {
      const cleanVariant = variant.toLowerCase();

      // 단순히 키워드가 텍스트에 포함되어 있는지 확인
      return cleanText.includes(cleanVariant);
    });

    if (isMatched) {
      matchedCards.push(card.id);
    }
  });

  highlightedCards.value = matchedCards;
};

// 디바운스된 분석 함수 (더 빠른 반응을 위해 100ms로 설정)
const debouncedAnalyze = debounce(analyzeInput, 100);

// 카드 orb 효과 클래스 반환
const getCardHighlightClass = (cardId) => {
  return highlightedCards.value.includes(cardId) ? 'card-with-orb' : '';
};


// 채팅 입력 감지 (즉시 반응)
watch(() => message.value, (newValue) => {
  // 이야기 모드일 때만 실행 (턴 관계없이)
  if (currChatModeIdx.value === 1) {
    // 즉시 분석 (디바운싱 없이)
    analyzeInput(newValue);
  } else {
    highlightedCards.value = []; // 다른 경우에는 하이라이트 제거
  }
});
</script>

<style scoped>
.reroll {
  background: linear-gradient(70deg, #fafcca 65%, #907800 35%);
}

.emoticon {
  transition: all 0.3s ease-in-out;
}

/* 결말 새로고침 버튼 호버 효과 */
.refresh-button-container {
  transition: max-height 0.3s ease-in-out;
}

.refresh-button-container .expanded-content {
  opacity: 0;
  transform: translateY(-10px);
  transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
}

.refresh-button-container:hover .expanded-content {
  opacity: 1;
  transform: translateY(0);
}

.handCard {
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  transform-origin: center center;
}

/* 카드 뒤 사각형 Orb 효과 */
.card-with-orb {
  position: relative;
}

.card-with-orb::before {
  content: '';
  position: absolute;
  top: -8px;
  left: -8px;
  right: -8px;
  bottom: -8px;
  background: linear-gradient(-45deg, #fefefe, #f9f7f5, #fefefe, #f9f7f5);
  background-size: 400% 400%;
  border-radius: 16px;
  z-index: -1;
  animation: orb-fade-in 0.25s ease-out, gradient-shift 3s ease infinite;
  filter: blur(12px);
  opacity: 0.9;
  pointer-events: none;
}

.card-with-orb::after {
  content: '';
  position: absolute;
  top: -6px;
  left: -6px;
  right: -6px;
  bottom: -6px;
  background: linear-gradient(-45deg, #fefefe, #f9f7f5, #fefefe, #f9f7f5);
  background-size: 400% 400%;
  border-radius: 16px;
  z-index: -1;
  animation: orb-fade-in 0.3s ease-out, gradient-shift 3s ease infinite reverse;
  filter: blur(8px);
  opacity: 0.7;
  pointer-events: none;
}

/* 그라데이션 시프트 애니메이션 */
@keyframes gradient-shift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* orb 페이드인 애니메이션 */
@keyframes orb-fade-in {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  50% {
    opacity: 0.3;
    transform: scale(0.95);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.storycard {
  text-shadow: -1px 0px #9f876a, 0px 1px #9f876a, 1px 0px #9f876a, 0px -1px #9f876a;
}

.endingcard-text {
  text-shadow: -1px 0px #8a622a, 0px 1px #8a622a, 1px 0px #8a622a, 0px -1px #8a622a;
}

@keyframes swing {
  0% {
    transform: translateY(0px);
  }

  100% {
    transform: translateY(-2px);
  }
}

.endingcard {
  transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  transform-origin: center bottom;
}

.endingcard:hover {
  transform: translateY(-12px) scale(1.1) rotateY(5deg);
  transform-origin: center bottom;
  box-shadow:
    0 25px 50px rgba(0, 0, 0, 0.2),
    0 10px 20px rgba(0, 0, 0, 0.1);
  filter: brightness(1.1) saturate(1.1);
  z-index: 50;
}

.paper {
  padding: 2rem;
  position: relative;
  box-sizing: border-box;
}

.paper:before {
  background-image: radial-gradient(#C9B29C, #C9B29C);
  content: ' ';
}

/* 카드 뒤 사각형 Orb 효과 (프로필 이미지 스타일 기반) */
.card-with-orb {
  position: relative;
}

.card-with-orb::before {
  content: '';
  position: absolute;
  top: -8px;
  left: -8px;
  right: -8px;
  bottom: -8px;
  background: linear-gradient(-45deg, #fefefe, #f9f7f5, #fefefe, #f9f7f5);
  background-size: 400% 400%;
  border-radius: 16px;
  z-index: -1;
  animation: orb-fade-in 0.25s ease-out, gradient-shift 3s ease infinite;
  filter: blur(12px);
  opacity: 0.9;
  pointer-events: none;
}

.card-with-orb::after {
  content: '';
  position: absolute;
  top: -6px;
  left: -6px;
  right: -6px;
  bottom: -6px;
  background: linear-gradient(-45deg, #fefefe, #f9f7f5, #fefefe, #f9f7f5);
  background-size: 400% 400%;
  border-radius: 16px;
  z-index: -1;
  animation: orb-fade-in 0.3s ease-out, gradient-shift 3s ease infinite reverse;
  filter: blur(8px);
  opacity: 0.7;
  pointer-events: none;
}

/* 그라데이션 시프트 애니메이션 */
@keyframes gradient-shift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* 성능 최적화를 위한 미디어 쿼리 */
@media (prefers-reduced-motion: reduce) {
  .card-with-orb::before,
  .card-with-orb::after {
    animation: none;
    opacity: 0.5;
  }
}

.paper:before {
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

/* 카드 X축 위치는 기존과 동일 (나란히 배치) */
.card4 > :nth-child(1){
  transform: translateX(0);
}
.card4 > :nth-child(2){
  transform: translateX(0);
}
.card4 > :nth-child(3){
  transform: translateX(0);
}
.card4 > :nth-child(4){
  transform: translateX(0);
}

.card3 > :nth-child(1){
  transform: translateX(0);
}
.card3 > :nth-child(2){
  transform: translateX(0);
}
.card3 > :nth-child(3){
  transform: translateX(0);
}

.card2 > :nth-child(1){
  transform: translateX(0);
}
.card2 > :nth-child(2){
  transform: translateX(0);
}
</style>
