<template>
  <div class="absolute w-full h-full rounded-lg bg-gradient-to-br from-black/20 via-black/15 to-black/20 flex justify-center">
    
    <!-- 메인 투표 패널 -->
    <div class="w-1/2 max-w-2xl h-2/3 bg-gradient-to-br from-white/95 to-white/85 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 flex flex-col items-center p-6 gap-4 z-20 relative overflow-hidden" 
         :class="voteEnded ? 'bounce-reverse' : 'bounce'" 
         @animationend="handleAnimationEnd">
      
      <!-- 배경 장식 요소 -->
      <div class="absolute -top-4 -right-4 w-32 h-32 bg-gradient-to-br from-orange-200/20 to-amber-300/10 rounded-full blur-xl"></div>
      <div class="absolute -bottom-8 -left-8 w-40 h-40 bg-gradient-to-tr from-blue-200/15 to-purple-300/10 rounded-full blur-2xl"></div>
      
      <!-- 모던한 프로그레스 바 -->
      <div class="modern-progress-container w-full h-6 mb-4">
        <div class="modern-progress-bar h-full rounded-full overflow-hidden bg-gradient-to-r from-gray-300 via-gray-200 to-gray-300 shadow-inner border-2 border-gray-300">
          <div class="modern-progress-fill h-full bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-500 shadow-lg relative" 
               :class="countStarted ? 'animate-decrease' : 'w-full'" 
               :style="{ animationDuration: duration + 's' }" 
               @animationend="voteEnd">
            <div class="progress-shine absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent skew-x-12 animate-shine"></div>
          </div>
        </div>
      </div>
      
      <!-- 질문 텍스트 -->
      <div class="text-center relative z-10">
        <h2 class="text-2xl lg:text-3xl font-katuri bg-gradient-to-r from-gray-800 via-gray-700 to-gray-800 bg-clip-text text-transparent drop-shadow-sm mb-2 leading-tight px-4">
          {{ usedCard.isEnding ? '이 이야기로 끝맺을까요?' : '이 이야기를 추가할까요?' }}
        </h2>
        <div class="w-16 h-1 bg-gradient-to-r from-orange-300 to-amber-400 rounded-full mx-auto"></div>
      </div>
      
      <!-- 프롬프트 박스 -->
      <div class="w-full bg-gradient-to-br from-gray-50 to-white border border-gray-200/50 rounded-2xl p-4 shadow-inner backdrop-blur-sm relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-r from-blue-50/20 via-transparent to-purple-50/20 rounded-2xl"></div>
        <p class="text-lg lg:text-xl text-gray-700 font-medium leading-relaxed text-center relative z-10 break-words">{{ prompt }}</p>
      </div>
      
      <!-- 모던한 투표 버튼들 -->
      <div class="grid grid-cols-2 w-full h-full gap-6 mt-2">
        <!-- 찬성 버튼 -->
        <div class="vote-button vote-up relative group cursor-pointer" 
             @click="selectVote('up')" 
             :class="selected === 'up' ? 'selected' : ''">
          <div class="vote-button-inner bg-gradient-to-br from-emerald-400 to-green-500 hover:from-emerald-300 hover:to-green-400 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 active:scale-95 border border-white/30 overflow-hidden h-full flex justify-center items-center relative">
            <!-- 반짝이는 효과 -->
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 transform -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
            <!-- 아이콘 -->
            <div class="relative z-10 flex flex-col items-center gap-2">
              <img :src="VoteUpLeftIcon" alt="찬성" class="w-16 h-16 drop-shadow-lg filter brightness-110">
              <span class="text-white font-katuri text-lg font-bold drop-shadow-sm">찬성</span>
            </div>
            <!-- 선택된 효과 -->
            <div class="absolute inset-0 border-4 border-white rounded-2xl transition-opacity duration-300" :class="selected === 'up' ? 'opacity-100' : 'opacity-0'"></div>
          </div>
        </div>
        
        <!-- 반대 버튼 -->
        <div class="vote-button vote-down relative group cursor-pointer" 
             @click="selectVote('down')" 
             :class="selected === 'down' ? 'selected' : ''">
          <div class="vote-button-inner bg-gradient-to-br from-rose-400 to-red-500 hover:from-rose-300 hover:to-red-400 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 active:scale-95 border border-white/30 overflow-hidden h-full flex justify-center items-center relative">
            <!-- 반짝이는 효과 -->
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 transform -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
            <!-- 아이콘 -->
            <div class="relative z-10 flex flex-col items-center gap-2">
              <img :src="VoteDownRightIcon" alt="반대" class="w-16 h-16 drop-shadow-lg filter brightness-110">
              <span class="text-white font-katuri text-lg font-bold drop-shadow-sm">반대</span>
            </div>
            <!-- 선택된 효과 -->
            <div class="absolute inset-0 border-4 border-white rounded-2xl transition-opacity duration-300" :class="selected === 'down' ? 'opacity-100' : 'opacity-0'"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 사용한 카드 패널 -->
    <div class="bg-gradient-to-br from-white/90 to-white/75 backdrop-blur-xl rounded-2xl shadow-xl border border-white/30 flex flex-col translate-y-1/2 items-center p-6 ml-4 transition-all duration-1000 ease-in-out relative overflow-hidden min-h-[280px]" 
         :class="showCard ? '' : '-translate-x-[120%] opacity-0 z-0'"
         :style="{ height: cardPanelHeight + 'px' }">
      
      <!-- 카드 패널 배경 장식 -->
      <div class="absolute -top-2 -right-2 w-16 h-16 bg-gradient-to-br from-amber-200/30 to-orange-300/20 rounded-full blur-lg"></div>
      
      <div class="relative z-10">
        <p class="font-omp text-lg font-semibold text-gray-700 mb-3 text-center">사용한 카드</p>
        <div class="relative transform hover:scale-105 transition-transform duration-300" ref="cardRef">
          <img :src="usedCard.isEnding ? CardImage.endingCardBack : CardImage.storyCardBack" 
               alt="스토리카드" 
               class="w-32 drop-shadow-lg">
          <!-- 카드 글로우 효과 -->
          <div class="absolute inset-0 bg-gradient-to-br from-amber-400/20 to-orange-500/10 rounded-lg blur-sm -z-10"></div>
          <div class="absolute inset-0 p-2 flex items-center justify-center font-katuri font-bold text-center leading-tight overflow-visible" 
               :class="usedCard.isEnding ? 'endingcard text-[#fee09e]' : 'storycard text-[#eadfcd]'" 
               ref="contentRef"
               :style="{ fontSize: currentFontSize + 'px' }">
            {{ props.usedCard.keyword }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { VoteUpLeftIcon, VoteDownRightIcon } from '@/assets';
import CardImage from "@/assets/cards";
import { ref, onMounted, nextTick, watch } from 'vue';
import { useUserStore } from '@/stores/auth';
const userStore = useUserStore();
const selected = ref("up");
const countStarted = ref(false);
const voteEnded = ref(false);
const showCard = ref(false);
const cardRef = ref(null);
const contentRef = ref(null);
const contentSizes = ref([24, 20, 18, 16, 14, 12]); // px 단위로 변경
const duration = ref(10);
const cardPanelHeight = ref(280);
const currentFontSize = ref(24);
const emit = defineEmits(['voteEnd']);
const startCount = () => {
  countStarted.value = true;
};

const selectVote = async (voteType) => {
  console.log('🗳️ selectVote 호출됨:', voteType);
  selected.value = voteType;
  console.log('🗳️ selected.value 설정됨:', selected.value);
  
  // 서버에 투표 버튼 클릭 로그 전송
  try {
    await fetch('/api/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'VOTE_BUTTON_CLICK',
        user: userStore.userData.userNickname,
        selected: voteType,
        timestamp: new Date().toISOString()
      })
    });
  } catch (error) {
    // 로그 전송 실패해도 게임은 계속 진행
  }
};
const props = defineProps({
  prompt: {
    Type: String,
  },
  usedCard: {
    Type: Object,
  },
  isPreview: {
    Type: Boolean,
  },
})
const voteEnd = () => {
  showCard.value = false;
  setTimeout(() => {
    voteEnded.value = true;
  }, 500);
};
const removeComponent = async () => {
  console.log('🗳️ removeComponent 호출됨, selected.value:', selected.value);
  
  // 서버에 투표 종료 로그 전송
  try {
    await fetch('/api/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'VOTE_END',
        user: userStore.userData.userNickname,
        finalSelected: selected.value,
        timestamp: new Date().toISOString()
      })
    });
  } catch (error) {
    // 로그 전송 실패해도 게임은 계속 진행
  }
  
  const voteData = {
    sender: userStore.userData.userNickname,
    selected: selected.value
  };
  console.log('🗳️ emit할 voteEnd 데이터:', voteData);
  emit('voteEnd', voteData);
}
const handleAnimationEnd = (event) => {
  const animName = event.animationName;
  if (animName.includes("bounce-reverse")) {
    removeComponent();
  } 
  else if (animName.includes("bounce")) {
    startCount();
    showCard.value = true;
  }
};

const adjustCardSize = async () => {
  await nextTick();
  if(contentRef.value && cardRef.value) {
    let index = 0;
    currentFontSize.value = contentSizes.value[index];
    
    // 텍스트 크기를 줄여가며 카드 안에 맞도록 조정
    while(contentRef.value.scrollHeight > cardRef.value.clientHeight && index < contentSizes.value.length - 1) {
      index++;
      currentFontSize.value = contentSizes.value[index];
      await nextTick(); // DOM 업데이트 대기
    }
    
    // 가장 작은 폰트로도 텍스트가 넘치면 카드 패널 높이를 늘림
    if(contentRef.value.scrollHeight > cardRef.value.clientHeight) {
      const overflow = contentRef.value.scrollHeight - cardRef.value.clientHeight;
      cardPanelHeight.value = 280 + overflow + 60; // 기본 높이 + 오버플로우 + 여유 공간
    } else {
      cardPanelHeight.value = 280; // 기본 높이로 리셋
    }
  }
};

// 카드 내용 변경 시 크기 재조정
watch(() => props.usedCard.keyword, async () => {
  await adjustCardSize();
}, { deep: true });

onMounted(async () => {
  await adjustCardSize();
  // 미리보기 모드와 상관없이 항상 10초로 통일
  duration.value = 10;
});

</script>
<style scoped>
/* 모던한 프로그레스 바 애니메이션 */
@keyframes animate-decrease {
  from { width: 100%; }
  to { width: 0; }
}

.animate-decrease {
  animation: animate-decrease linear forwards;
}

/* 반짝이는 효과 애니메이션 */
@keyframes animate-shine {
  0% { transform: translateX(-100%) skewX(12deg); }
  100% { transform: translateX(200%) skewX(12deg); }
}

.animate-shine {
  animation: animate-shine 2s infinite;
}

/* 부드러운 바운스 애니메이션 (개선된 버전) */
@keyframes bounce {
  0% {
    transform: scale(0) rotate(-12deg);
    opacity: 0;
  }
  50% {
    transform: scale(1.05) rotate(3deg);
    opacity: 0.9;
  }
  80% {
    transform: scale(0.98) rotate(-1deg);
    opacity: 1;
  }
  100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}

@keyframes bounce-reverse {
  0% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
  20% {
    transform: scale(1.05) rotate(-3deg);
    opacity: 0.9;
  }
  100% {
    transform: scale(0) rotate(12deg);
    opacity: 0;
  }
}

.bounce {
  animation: bounce 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.bounce-reverse {
  animation: bounce-reverse 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

/* 투표 버튼 호버 효과 */
.vote-button:not(.selected) {
  opacity: 0.85;
}

.vote-button.selected {
  opacity: 1;
}

.vote-button:not(.selected):hover {
  opacity: 1;
}

/* 투표 버튼 선택 시 펄스 효과 */
.vote-button.selected .vote-button-inner::before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: inherit;
  background: linear-gradient(45deg, rgba(255,255,255,0.8), rgba(255,255,255,0.2), rgba(255,255,255,0.8));
  z-index: -1;
  animation: pulse-border 2s infinite;
}

@keyframes pulse-border {
  0%, 100% { opacity: 0.7; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.02); }
}

/* 카드 텍스트 그림자 효과 - 핸드 카드와 동일 */
.storycard {
  text-shadow: -1px 0px #9f876a, 0px 1px #9f876a, 1px 0px #9f876a, 0px -1px #9f876a;
}

.endingcard {
  text-shadow: -1px 0px #8a622a, 0px 1px #8a622a, 1px 0px #8a622a, 0px -1px #8a622a;
}

/* 프로그레스 바 컨테이너 */
.modern-progress-container {
  position: relative;
}

.modern-progress-bar {
  position: relative;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.modern-progress-fill {
  position: relative;
  transition: width 0.3s ease;
}

/* 글래스모피즘 효과를 위한 추가 스타일 */
.backdrop-blur-xl {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

/* 반응형 디자인 */
@media (max-width: 1024px) {
  .text-2xl.lg\:text-3xl {
    font-size: 1.5rem;
  }
  
  .vote-button .w-16 {
    width: 3rem;
    height: 3rem;
  }
  
  .text-lg.lg\:text-xl {
    font-size: 1rem;
  }
}

@media (max-width: 768px) {
  .text-2xl.lg\:text-3xl {
    font-size: 1.25rem;
    line-height: 1.3;
  }
}

/* 접근성을 위한 포커스 스타일 */
.vote-button:focus-within {
  outline: 2px solid rgba(59, 130, 246, 0.5);
  outline-offset: 2px;
}

/* 터치 디바이스를 위한 탭 하이라이트 제거 */
.vote-button {
  -webkit-tap-highlight-color: transparent;
}
</style>