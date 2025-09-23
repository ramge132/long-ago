<template>
  <div class="row-span-2 flex flex-col justify-between py-2 relative">
    <div v-if="gameStarted" class="flex justify-center items-center grow" style="transform: translateX(3px);">
      <!-- 스토리 카드 영역 -->
      <div class="flex justify-center items-end w-3/4 mr-3 h-48 -translate-y-8" :class="isEndingMode ? 'opacity-50' : ''">
          <transition-group name="wave" tag="div" class="cardList flex justify-center items-end w-full h-full" :class="dynamicClass" @before-leave="setLeaveStyle" @after-leave="updateClass">
            <div
              v-for="(card) in storyCards"
              :key="card.id"
              class="handCard relative transition-all duration-300 cursor-pointer group"
              :class="getCardHighlightClass(card.id)"
            >
              <img :src="CardImage.getStoryCardImage(card.id)" :alt="`스토리카드 ${card.keyword}`" class="w-36">

              <!-- 플로팅 액션 버튼들 (카드 상단 중앙 배치) -->
              <div class="absolute -top-4 left-1/2 transform -translate-x-1/2 flex gap-1 opacity-0 group-hover:opacity-100 transition-all duration-200">
                <!-- 새로고침 버튼 (호버 확장형) -->
                <div
                  class="refresh-button-container w-8 bg-[#ffffffa0] rounded-full overflow-hidden transition-all duration-300 ease-in-out max-h-8"
                  :class="[
                    refreshCount <= 0 ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:max-h-16'
                  ]"
                  @click.stop="refreshCount > 0 ? refreshCard(card) : null"
                >
                  <!-- 기본 상태 아이콘 버튼 (항상 표시) -->
                  <button class="bg-[#e6dece] rounded-full w-8 h-8 flex justify-center items-center drop-shadow-md z-10 relative focus:outline-0">
                    <svg class="w-4 h-4 text-[#d5c4ae]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                    </svg>
                  </button>
                  <!-- 확장 영역 (호버 시 표시) -->
                  <div class="expanded-content flex flex-col items-center justify-center text-center text-[9px] text-gray-700 pt-1 pb-1">
                    <p class="leading-tight">새로고침</p>
                    <p class="text-sm font-bold">{{ refreshCount }}</p>
                  </div>
                </div>

                <!-- 교환 버튼 (호버 확장형) -->
                <div
                  class="exchange-button-container w-8 bg-[#ffffffa0] rounded-full overflow-hidden transition-all duration-300 ease-in-out max-h-8"
                  :class="[
                    exchangeCount <= 0 ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:max-h-16'
                  ]"
                  @click.stop="exchangeCount > 0 ? openExchangeModal(card) : null"
                >
                  <!-- 기본 상태 아이콘 버튼 (항상 표시) -->
                  <button class="bg-[#e6dece] rounded-full w-8 h-8 flex justify-center items-center drop-shadow-md z-10 relative focus:outline-0">
                    <svg class="w-4 h-4 text-[#d5c4ae]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
                    </svg>
                  </button>
                  <!-- 확장 영역 (호버 시 표시) -->
                  <div class="expanded-content flex flex-col items-center justify-center text-center text-[9px] text-gray-700 pt-1 pb-1">
                    <p class="leading-tight">교환하기</p>
                    <p class="text-sm font-bold">{{ exchangeCount }}</p>
                  </div>
                </div>
              </div>

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
      <div class="rounded-full bg-[#ffffffdb] drop-shadow-md h-10 flex flex-1 px-3 items-center pointer-events-auto relative"
        v-for="(mode, index) in chatMode" :key="index"
        :class="[
          index == currChatModeIdx ? '' : 'hidden',
          (index !== 0 && props.myTurn === props.currTurn) ? 'chat-with-orb' : ''
        ]">
        <div class="flex flex-nowrap flex-col justify-center items-center relative cursor-pointer" @click="changeMode">
          <p class="whitespace-nowrap absolute top-[-1.25rem] font-semibold" style="text-shadow: 2px 0 4px #fff, -2px 0 4px #fff, 0 2px 4px #fff, 0 -2px 4px #fff, 1px 1px #fff, -1px -1px 4px #fff, 1px -1px 4px #fff, -1px 1px 4px #fff;" v-text="mode.mark" :class="index === 1 ? 'text-[#c3b6a5]' : ''"></p>
          <img :src="ChangeIcon" alt="채팅모드변경" class="h-3/5" />
        </div>
        <input type="text"
          :class="[
            'pl-3 bg-transparent w-full h-full text-2xl font-semibold mx-2 focus:outline-0',
            index !== 0 ? 'pr-12' : 'pr-0'
          ]"
          v-model="message"
          @keyup.enter="mode.fucntion"
          @input="handleMessageInput"
          :maxlength="index === 0 ? null : 40"
          :placeholder="mode.placeholder"
          :ref="(el) => (chatRefs[index] = el)" />
        <!-- 글자수 표시 (이야기/자유 결말 모드에서만) - 채팅창 내부 절대 위치 -->
        <div v-if="index !== 0" class="absolute right-12 top-1/2 transform -translate-y-1/2 text-xs text-gray-400 pointer-events-none">
          {{ message.length }}/40
        </div>
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

    <!-- 모달들 -->
    <!-- 플로팅 액션 버튼들은 카드 내부에 직접 렌더링됨 -->

    <UserSelectModal
      :show="showUserSelectModal"
      :selectedCard="selectedCard"
      :participants="participants"
      :myId="peerId"
      @close="closeUserSelectModal"
      @selectUser="handleUserSelect"
    />

    <ExchangeRequestModal
      :show="showExchangeRequestModal"
      :senderName="exchangeRequest.senderName"
      :senderCard="exchangeRequest.senderCard"
      :myCards="storyCards"
      :exchangeData="exchangeRequest"
      @close="closeExchangeRequestModal"
      @accept="handleAcceptExchange"
      @reject="handleRejectExchange"
    />
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onBeforeUnmount, computed } from "vue";
import { RefreshIcon, SendIcon, EmoticonIcon, ChangeIcon, TrashIcon, ReturnIcon, ShareIcon } from "@/assets";
import CardImage from "@/assets/cards"
import { useUserStore } from "@/stores/auth";
import emoji from "@/assets/images/emoticons";
import toast from "@/functions/toast";
import useCilpboard from "vue-clipboard3";
// StoryCardMenu는 플로팅 액션 버튼으로 교체됨
import UserSelectModal from "./UserSelectModal.vue";
import ExchangeRequestModal from "./ExchangeRequestModal.vue";
import { refreshStoryCard, exchangeStoryCard } from "@/apis/game";

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

// 카드 관련 모달 상태
const showCardMenu = ref(false);
const showUserSelectModal = ref(false);
const showExchangeRequestModal = ref(false);
const selectedCard = ref({ id: 0, keyword: '' });
const exchangeCount = ref(3);
const refreshCount = ref(3);

// 교환 요청 데이터
const exchangeRequest = ref({
  senderName: '',
  senderCard: { id: 0, keyword: '' },
  fromUserId: '',
  toUserId: '',
  fromCardId: 0
});

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
    type: Number,
  },
  currTurn: {
    type: Number,
  },
  storyCards: {
    type: Array,
  },
  endingCard: {
    type: Object,
  },
  gameStarted: {
    type: Boolean,
  },
  isEndingMode: {
    type: Boolean,
  },
  ISBN: {
    type: String,
  },
  participants: {
    type: Array,
    default: () => []
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

const dynamicClass = ref(`card${props.storyCards.length}`);

const emit = defineEmits([
  "broadcastMessage",
  "nextTurn",
  "cardReroll",
  "goLobby",
  "cardRefreshed",
  "sendExchangeRequest",
  "cardExchanged",
  "rejectExchange"
]);

// 메시지 입력 핸들러 - 40자 제한 (이야기/자유 결말 모드에서만)
const handleMessageInput = (event) => {
  const value = event.target.value;
  const currentIndex = currChatModeIdx.value;

  // 대화 모드(index 0)는 제한 없음, 이야기/자유 결말 모드는 40자 제한
  if (currentIndex !== 0 && value.length > 40) {
    message.value = value.slice(0, 40);
  } else {
    message.value = value;
  }
};

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
      usedCardIds: [...highlightedCards.value] // 사용된 카드 ID들 전달
    });

    message.value = "";
    chatRefs.value[currChatModeIdx.value].blur();

    // 이야기 제출 후 하이라이트 초기화
    highlightedCards.value = [];
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
      mark: "자유 결말",
      fucntion: sendFreeEnding,
      placeholder: "자유 결말은 카드보다 점수를 조금 얻습니다",
    });
  } else {
    // 일반 모드: 이야기 모드
    modes.push({
      mark: "이야기",
      fucntion: sendprompt,
      placeholder: "카드는 자동 인식됩니다 (한 장만 사용 가능)",
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
  // 모든 카드의 인라인 스타일 강제 초기화
  const cards = document.querySelectorAll(".handCard");
  cards.forEach((el) => {
    el.style.transform = "";
    el.style.filter = "";
    el.style.boxShadow = "";
    el.style.zIndex = "";
    el.style.transition = "";
    el.style.opacity = "";
  });

  nextTick(() => {
    // 클래스 업데이트
    dynamicClass.value = `card${props.storyCards.length}`;

    // DOM 업데이트 후 충분한 지연을 두고 호버 효과 재설정
    setTimeout(() => {
      setupCardHoverEffects();
    }, 100);
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
  // 이전 타이머가 있다면 취소
  if (setupCardHoverEffects._timeout) {
    clearTimeout(setupCardHoverEffects._timeout);
  }

  setupCardHoverEffects._timeout = setTimeout(() => {
    nextTick(() => {
      // 추가적인 프레임 지연으로 DOM 완전 업데이트 보장
      requestAnimationFrame(() => {
        const cards = document.querySelectorAll(".handCard");

        cards.forEach((el, index) => {
          // 기존 이벤트 리스너 제거 (중복 방지)
          el.removeEventListener("mouseenter", el._hoverEnter);
          el.removeEventListener("mouseleave", el._hoverLeave);

          // 강제로 인라인 스타일 초기화 (이전 애니메이션 잔여물 제거)
          el.style.transform = "";
          el.style.filter = "";
          el.style.boxShadow = "";
          el.style.zIndex = "";

          // 다음 프레임에서 원본 transform 계산 (CSS 적용 후)
          requestAnimationFrame(() => {
            const computedStyle = window.getComputedStyle(el);
            const originalTransform = computedStyle.transform;

            el._hoverEnter = () => {
              // 다른 카드들의 z-index 초기화
              cards.forEach((item, i) => {
                if (item !== el) {
                  item.style.zIndex = i;
                }
              });

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
      });
    });
  }, 50); // 50ms 디바운스
};

onMounted(() => {
  setupCardHoverEffects();

  // 교환 요청 전역 이벤트 리스너
  const handleExchangeRequest = (event) => {
    console.log("=== InGameControl: 전역 이벤트 수신 ===");
    console.log("1. 이벤트 수신:", event);
    console.log("2. event.detail:", event.detail);

    const data = event.detail;
    exchangeRequest.value = {
      senderName: data.senderName,
      senderCard: data.senderCard,
      fromUserId: data.fromUserId,
      toUserId: data.toUserId,
      fromCardId: data.fromCardId
    };
    console.log("3. exchangeRequest 설정:", exchangeRequest.value);

    showExchangeRequestModal.value = true;
    console.log("4. 모달 표시 설정:", showExchangeRequestModal.value);
    console.log("=== InGameControl: 전역 이벤트 처리 완료 ===");
  };

  window.addEventListener('showExchangeRequest', handleExchangeRequest);

  // 컴포넌트 언마운트 시 이벤트 리스너 제거
  onBeforeUnmount(() => {
    window.removeEventListener('showExchangeRequest', handleExchangeRequest);
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


// 플로팅 액션 버튼 함수들
const refreshCard = async (card) => {
  console.log("=== 카드 새로고침 버튼 클릭 ===");
  console.log("새로고침할 카드:", card);
  console.log("현재 새로고침 횟수:", refreshCount.value);
  console.log("gameId:", props.gameId);
  console.log("userId:", props.peerId);

  // 새로고침 횟수 체크
  if (refreshCount.value <= 0) {
    toast.errorToast("새로고침 횟수를 모두 사용했습니다.");
    return;
  }

  // GameView에서 새로고침 처리하도록 변경 (중복 방지 포함)
  emit("cardRefreshed", {
    oldCard: card,
    gameId: props.gameId,
    userId: props.peerId
  });

  console.log("cardRefreshed 이벤트 발송 완료");
};

const openExchangeModal = (card) => {
  selectedCard.value = card;
  showUserSelectModal.value = true;
};

// 기존 함수들 (호환성 유지)
const openCardMenu = (card) => {
  selectedCard.value = card;
  showCardMenu.value = true;
};

const closeCardMenu = () => {
  showCardMenu.value = false;
  selectedCard.value = { id: 0, keyword: '' };
};

const openUserSelectModal = () => {
  showCardMenu.value = false;
  showUserSelectModal.value = true;
};

const closeUserSelectModal = () => {
  showUserSelectModal.value = false;
};

const handleRefreshCard = async () => {
  console.log("=== 카드 메뉴에서 새로고침 클릭 ===");
  console.log("새로고침할 카드:", selectedCard.value);
  console.log("현재 새로고침 횟수:", refreshCount.value);

  // 새로고침 횟수 체크
  if (refreshCount.value <= 0) {
    toast.errorToast("새로고침 횟수를 모두 사용했습니다.");
    closeCardMenu();
    return;
  }

  // GameView에서 새로고침 처리하도록 변경 (중복 방지 포함)
  emit("cardRefreshed", {
    oldCard: selectedCard.value,
    gameId: props.gameId,
    userId: props.peerId
  });

  console.log("cardRefreshed 이벤트 발송 완료 (메뉴)");
  closeCardMenu();
};

// 교환 신청 진행 중인 카드들을 추적
const pendingExchangeCards = ref(new Set());

const handleUserSelect = (participant) => {
  console.log("=== InGameControl: 사용자 선택 처리 ===");
  console.log("1. 선택된 participant:", participant);
  console.log("2. 선택된 카드:", selectedCard.value);

  // 이미 교환 신청 중인 카드인지 확인
  if (pendingExchangeCards.value.has(selectedCard.value.id)) {
    toast.errorToast("이미 교환 신청 중인 카드입니다.");
    closeUserSelectModal();
    closeCardMenu();
    return;
  }

  // 교환 신청 중인 카드로 등록
  pendingExchangeCards.value.add(selectedCard.value.id);

  // P2P로 교환 신청 메시지 전송
  const requestData = {
    targetUserId: participant.id,
    cardId: selectedCard.value.id,
    card: selectedCard.value
  };
  console.log("3. emit할 데이터:", requestData);

  emit("sendExchangeRequest", requestData);
  console.log("4. sendExchangeRequest 이벤트 발송 완료");

  // 교환 신청 시 횟수 차감
  exchangeCount.value--;

  closeUserSelectModal();
  closeCardMenu();
  toast.successToast(`${participant.name}님에게 교환 신청을 보냈습니다.`);

  // 3초 후 pending 상태 해제 (타임아웃)
  setTimeout(() => {
    pendingExchangeCards.value.delete(selectedCard.value.id);
  }, 3000);

  console.log("=== InGameControl: 사용자 선택 처리 완료 ===");
};

// 교환 신청 수신 처리
const showExchangeRequest = (requestData) => {
  exchangeRequest.value = requestData;
  showExchangeRequestModal.value = true;
};

const closeExchangeRequestModal = () => {
  showExchangeRequestModal.value = false;
  exchangeRequest.value = {
    senderName: '',
    senderCard: { id: 0, keyword: '' },
    fromUserId: '',
    toUserId: '',
    fromCardId: 0
  };
};

const handleAcceptExchange = async (exchangeData) => {
  if (!exchangeData.toCardId) {
    toast.errorToast("교환할 카드를 선택하세요.");
    return;
  }

  // 선택한 내 카드 찾기
  const myCard = props.storyCards.find(card => card.id === exchangeData.toCardId);
  if (!myCard) {
    toast.errorToast("선택한 카드를 찾을 수 없습니다.");
    return;
  }

  // P2P로 교환 수락 메시지 전송
  emit("cardExchanged", {
    fromUserId: exchangeData.fromUserId,
    toUserId: exchangeData.toUserId,
    fromCardId: exchangeData.fromCardId,
    toCardId: exchangeData.toCardId,
    fromCard: exchangeData.senderCard,
    toCard: myCard,
    accepted: true
  });

  closeExchangeRequestModal();
  toast.successToast("교환 신청을 수락했습니다!");
};

const handleRejectExchange = (exchangeData) => {
  // P2P로 거절 메시지 전송
  emit("rejectExchange", exchangeData);
  closeExchangeRequestModal();
  toast.infoToast("교환 신청을 거절했습니다.");
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

// 교환 완료 시 pending 상태 해제
const clearPendingExchange = (cardId) => {
  pendingExchangeCards.value.delete(cardId);
};

// 카드 새로고침 성공 콜백
const onCardRefreshSuccess = () => {
  toast.successToast("카드가 새로고침되었습니다!");
  // refreshCount는 GameView에서 백엔드 응답값으로 업데이트됨
};

// 카드 새로고침 에러 콜백
const onCardRefreshError = (errorMessage) => {
  toast.errorToast(errorMessage);
};

// 외부에서 접근할 수 있는 함수들
defineExpose({
  showExchangeRequest,
  clearPendingExchange,
  onCardRefreshSuccess,
  onCardRefreshError,
  updateCounts: (newRefreshCount, newExchangeCount) => {
    if (newRefreshCount !== null && newRefreshCount !== undefined) {
      refreshCount.value = newRefreshCount;
    }
    if (newExchangeCount !== null && newExchangeCount !== undefined) {
      exchangeCount.value = newExchangeCount;
    }
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

/* 부드러운 웨이브 카드 교체 애니메이션 */
.wave-enter-active, .wave-leave-active {
  transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.wave-enter-from {
  opacity: 0;
  transform: translateY(30px) rotate(3deg) scale(0.96);
  filter: blur(2px);
}
.wave-leave-to {
  opacity: 0;
  transform: translateY(-30px) rotate(-3deg) scale(0.96);
  filter: blur(2px);
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
  .card-with-orb::after,
  .chat-with-orb::before,
  .chat-with-orb::after {
    animation: none;
    opacity: 0.5;
  }
}

/* 채팅창 orb 효과 - 카드 orb와 동일한 디자인 */
.chat-with-orb {
  position: relative;
}

.chat-with-orb::before {
  content: '';
  position: absolute;
  top: -7px;
  left: -7px;
  right: -7px;
  bottom: -7px;
  background: linear-gradient(-45deg, #fafafa, #f7f7f7, #fafafa, #f7f7f7);
  background-size: 400% 400%;
  border-radius: 24px; /* 채팅창에 맞게 더 둥글게 */
  z-index: -1;
  animation: orb-fade-in 0.25s ease-out, gradient-shift 3.5s ease infinite;
  filter: blur(12px);
  opacity: 0.7;
  pointer-events: none;
}

.chat-with-orb::after {
  content: '';
  position: absolute;
  top: -5px;
  left: -5px;
  right: -5px;
  bottom: -5px;
  background: linear-gradient(-45deg, #fafafa, #f7f7f7, #fafafa, #f7f7f7);
  background-size: 400% 400%;
  border-radius: 20px; /* 채팅창에 맞게 더 둥글게 */
  z-index: -1;
  animation: orb-fade-in 0.3s ease-out, gradient-shift 3.5s ease infinite reverse;
  filter: blur(8px);
  opacity: 0.5;
  pointer-events: none;
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
