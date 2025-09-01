<template>
  <div class="row-span-3 w-full h-full flex items-center justify-center">
    <div class="book absolute top-0">
      <div class="pages" ref="pagesRef">
        <div
          class="page cursor-pointer flex flex-col items-center justify-center text-4xl font-katuri relative"
          :class="{ flipped: isFlipped(0) }"
          @click="handlePageClick(0)"
          style="text-shadow: -2px 0px black, 0px 2px black, 2px 0px black, 0px -2px black;"
          :style="{ zIndex: calculateZIndex(0) }"
        >
        <!-- 표지 이미지 먼저 렌더링 (배경) -->
        <img :src="bookCover.imageUrl" alt="책 표지" v-if="bookCover.imageUrl && bookCover.imageUrl !== null && bookCover.imageUrl !== 'null'" class="absolute inset-0 w-full h-full object-cover" style="backface-visibility: hidden">
        <!-- 제목 텍스트 (전경, 이미지 위에 표시) -->
        <p v-html="bookCover.title ? bookCover.title : `아주 먼<br>옛날..<br>`" class="break-keep absolute top-1/3 -translate-y-1/2 font-title text-white text-5xl z-10" style="backface-visibility: hidden; text-shadow: 2px 2px 4px rgba(0,0,0,0.8)"></p>
        
        </div>
        <template
          v-for="(content, index) in bookContents"
          :key="index"
        >
          <div
            class="page cursor-pointer flex flex-col font-story text-4xl p-14 break-keep items-center justify-center"
            :class="{ flipped: isFlipped(index * 2 + 1) }"
            @click="handlePageClick(index * 2 + 1)"
            :style="{ zIndex: calculateZIndex(index * 2 + 1) }">
            {{ content.content }}
          </div>
          <div
            class="page cursor-pointer flex flex-col items-center justify-center"
            :class="{ flipped: isFlipped(index * 2 + 2) }"
            @click="handlePageClick(index * 2 + 2)"
            :style="{ zIndex: calculateZIndex(index * 2 + 2) }">
            <div class="ink-reveal-container" v-if="content.image && content.image !== 'null'">
              <div 
                v-if="!isAnimationComplete(index)" 
                class="mask-layer"
                :class="{ 'animating': isFlipped(index * 2 + 2) }"
                @animationend="onAnimationEnd(index)">
                <img :src="content.image" alt="이야기 이미지" class="story-image">
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
    
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch, defineProps } from "vue";
import { useAudioStore } from "@/stores/audio";
import { TurningPage } from "@/assets";
import { initVoices, speakText } from "@/functions/tts";
import { speakTextConcurrent, stopAllTTS } from "@/functions/cloudTts";

const audioStore = useAudioStore();
const pagesRef = ref(null);
const flippedPages = reactive(new Set());
const isClickLocked = ref(false);
const animationCompleted = reactive(new Set());

const props = defineProps({
  bookContents: {
    Type: Array,
  },
  gameStarted: {
    Type: Boolean,
  },
  isElected: {
    Type: Boolean,
  },
  bookCover: {
    Type: Object,
  },
  isReadingMode: {
    Type: Boolean,
    default: false
  }
})

// bookCover prop 모니터링
watch(() => props.bookCover, (newValue, oldValue) => {
  console.log("=== 🎨 InGameContent: bookCover prop 변경 감지 ===");
  console.log("이전 값:", oldValue);
  console.log("새 값:", newValue);
  
  if (newValue) {
    console.log("📚 bookCover.title:", newValue.title);
    console.log("🖼️ bookCover.imageUrl:", newValue.imageUrl);
    console.log("imageUrl 타입:", typeof newValue.imageUrl);
    console.log("imageUrl이 null인가?:", newValue.imageUrl === null);
    console.log("imageUrl이 'null' 문자열인가?:", newValue.imageUrl === 'null');
    console.log("imageUrl이 undefined인가?:", newValue.imageUrl === undefined);
    console.log("imageUrl이 빈 문자열인가?:", newValue.imageUrl === '');
    
    // URL 유효성 검사
    if (newValue.imageUrl && newValue.imageUrl !== 'null' && newValue.imageUrl !== null) {
      console.log("✅ imageUrl이 유효한 것으로 판단됨");
      console.log("URL 길이:", newValue.imageUrl.length);
      console.log("URL 시작 부분:", newValue.imageUrl.substring(0, 50));
      
      // 이미지 로드 테스트
      const testImg = new Image();
      testImg.onload = () => {
        console.log("✅ 이미지 로드 성공!");
      };
      testImg.onerror = (error) => {
        console.error("❌ 이미지 로드 실패:", error);
        console.error("실패한 URL:", newValue.imageUrl);
      };
      testImg.src = newValue.imageUrl;
    } else {
      console.log("⚠️ imageUrl이 유효하지 않음");
    }
  } else {
    console.log("⚠️ bookCover가 null 또는 undefined");
  }
}, { deep: true, immediate: true });
// const test = ref({
//   imageUrl: rule4,
//   title: "해리포터의 악행을 밝힙니다."
// })

const calculateZIndex = (pageIndex) => {
  const totalPages = props.bookContents.length * 2 + 1;
  
  // 홀수 페이지 인덱스가 높을수록 z-index가 커야함
  if (pageIndex % 2 === 1) {
    return pageIndex * 2;
  }
  // 짝수 페이지 인덱스가 낮을수록 z-index가 커야함
  else {
    return (totalPages - pageIndex) * 2;
  }
};

const updatePagesZIndex = () => {
  if (!pagesRef.value) return;
  
  const pageElements = pagesRef.value.children;
  for (let i = 0; i < pageElements.length; i++) {
    pageElements[i].style.zIndex = calculateZIndex(i);
  }
};

const isFlipped = (pageIndex) => {
  return flippedPages.has(pageIndex);
};

const isAnimationComplete = (index) => {
  return animationCompleted.has(index);
};

const onAnimationEnd = (index) => {
  animationCompleted.add(index);
};

const handlePageClick = (pageIndex) => {
  // 와다다 클릭하지 못하게 하기
  if (isClickLocked.value) {
    return;
  }
  if (pageIndex / 2 === props.bookContents.length) {
    return;
  }
  isClickLocked.value = true;

  
  if (audioStore.audioData) {
    const turningEffect = new Audio(TurningPage);
    turningEffect.play();
  }
  
  if (pageIndex % 2 === 0) {
    if (isFlipped(pageIndex)) {
      flippedPages.delete(pageIndex);
      flippedPages.delete(pageIndex - 1);
    } else {
      flippedPages.add(pageIndex);
      if (pageIndex + 1 < props.bookContents.length * 2 + 1) {
        flippedPages.add(pageIndex + 1);
      }
    }
  } else {
    if (isFlipped(pageIndex)) {
      flippedPages.delete(pageIndex);
      if (pageIndex + 1 <= props.bookContents.length * 2 + 1) {
        flippedPages.delete(pageIndex - 1);
      }
    } else {
      flippedPages.add(pageIndex);
      flippedPages.add(pageIndex - 1);
    }
  }
  
  setTimeout(() => {
    isClickLocked.value = false; // 1초 후 잠금 해제
  }, 1000);

  updatePagesZIndex();
};

watch(() => props.bookContents,
  () => {
  updatePagesZIndex();
},
{ deep: true });

watch(() => props.isElected,
(newValue) => {
  if (newValue) {
    for (let i of Array.from({length: props.bookContents.length}, (_, index) => index * 2)) {
      if (!isFlipped(i)) {
        flippedPages.add(i);
        flippedPages.add(i + 1);
      }
    }
  }
})

const emit = defineEmits(['narration-complete']);

// tts
const runBookSequence = async () => {
  // 동기적으로 initVoices() 실행 (만약 비동기라면 await 사용)
  await initVoices();
  
  // 표지 제목은 읽지 않고 바로 책 내용부터 시작
  // 책 내용을 순서대로 처리: 0,1 페이지, 그 다음 2,3 페이지, ...
  for (const [i, element] of props.bookContents.entries()) {
    // 첫 번째 페이지는 이미 열려있으므로 i > 0일 때만 페이지 넘김
    if (i > 0) {
      // 두 페이지씩 추가 (페이지 넘기는 효과)
      flippedPages.add(i * 2);
      flippedPages.add(i * 2 + 1);

      // 페이지 넘기는 효과음 재생
      if (audioStore.audioData) {
        const turningEffect = new Audio(TurningPage);
        turningEffect.play();
      }
    }

    // TTS를 순차적으로 재생 (한 페이지씩)
    await speakTextConcurrent(element.content);
  }
  
  // 모든 작업이 완료되면 표지로 되돌리기
  // 모든 페이지를 다시 닫아서 표지만 보이게 함
  flippedPages.clear();
  
  // 페이지 넘기는 효과음 재생 (표지로 돌아갈 때)
  if (audioStore.audioData) {
    const turningEffect = new Audio(TurningPage);
    turningEffect.play();
  }
  
  // 클릭 잠금 해제 및 나레이션 완료 신호 전송
  isClickLocked.value = false;
  emit('narration-complete');
}

watch(
  () => props.gameStarted,
  async (newValue) => {
    if (newValue === false) {
      isClickLocked.value = true;
      
      // 첫 페이지로 이동 (표지를 넘김)
      flippedPages.clear();
      flippedPages.add(0);
      flippedPages.add(1);
      
      // 페이지 넘기는 효과음 재생
      if (audioStore.audioData) {
        const turningEffect = new Audio(TurningPage);
        turningEffect.play();
      }
      
      // 페이지 넘김 애니메이션이 완료되기를 기다린 후 나레이션 시작
      setTimeout(async () => {
        if (audioStore.audioData) {
          await runBookSequence();
        } else {
          // 모든 작업이 완료되면 클릭 잠금 해제
          isClickLocked.value = false;
        }
      }, 1500); // 페이지 넘김 애니메이션 시간
    }
  }
);


onMounted(() => {
  updatePagesZIndex();
  
  // 읽기 모드가 아닐 때만 초기 페이지 클릭 (게임 중에는 페이지를 열어둠)
  if (!props.isReadingMode) {
    handlePageClick(0);
  }
  // 읽기 모드일 때는 표지만 보여줌 (flippedPages가 비어있으면 표지만 표시됨)
});
</script>

<style scoped>
.book {
  transition: opacity 0.4s 0.2s;
}
p {
  text-align: center;
}
.page {
  width: 30vw;
  height: 44vw;
  float: left;
  margin-bottom: 0.5em;
  background: left top no-repeat;
  background-size: cover;
}
.page:nth-child(even) {
  clear: both;
}
.book {
  perspective: 250vw;
}
.book .pages {
  width: 600px;
  height: 400px;
  position: relative;
  transform-style: preserve-3d;
  backface-visibility: hidden;
  border-radius: 4px;
}
.book .page {
  float: none;
  clear: none;
  margin: 0;
  position: absolute;
  top: 0;
  width: 300px;
  height: 400px;
  transform-origin: 0 0;
  transition: transform 1.4s;
  backface-visibility: hidden;
  transform-style: preserve-3d;
  user-select: none;
  /* background-color: white; 기본 페이지 색상 */
  background-image: url("/src/assets/images/bookPage.jpg");
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.1); /* 페이지 그림자 효과 */
}
.book .page:before {
  content: "";
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  transition: background 0.7s;
  z-index: -1;
}
.book .page:nth-child(odd) {
  transform: rotateY(0deg);
  right: 0;
  border-radius: 0 4px 4px 0;
}
/* .book .page:nth-child(odd):hover {
  transform: rotateY(-15deg);
}
.book .page:nth-child(odd):hover:before {
  background: rgba(0, 0, 0, 0.03);
} */
.book .page:nth-child(even) {
  transform: rotateY(180deg);
  transform-origin: 100% 0;
  left: 0;
  border-radius: 4px 0 0 4px;
}
.book .page:nth-child(even):before {
  background: rgba(0, 0, 0, 0.05); /* 뒷면 페이지 음영 */
}
.book .page.flipped:nth-child(odd) {
  transform: rotateY(-180deg);
}
.book .page.flipped:nth-child(odd):before {
  background: rgba(0, 0, 0, 0.05); /* 뒤집힌 페이지 음영 */
}
.book .page.flipped:nth-child(even) {
  transform: rotateY(0deg);
}
/* .book .page.flipped:nth-child(even):hover {
  transform: rotateY(15deg);
}
.book .page.flipped:nth-child(even):hover:before {
  background: rgba(0, 0, 0, 0.03);
} */

.book .page:nth-child(1) {
  /* background-color: #E5E091; */
  background-image: url("/src/assets/images/bookCover.svg");
}

/* 페이지 테두리 효과 */
.book .page {
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.page img {
  backface-visibility: hidden;
}

/* 잉크 번짐 reveal 효과 */
.ink-reveal-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

/* 스토리 이미지 - 아래 레이어 */
.story-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
}

/* 마스크 레이어 - 잉크 번짐 효과 (위 레이어) */
.mask-layer {
  /* background-image: url("/src/assets/images/bookPage.jpg"); */
  background-size: cover;
  background-position: center;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  pointer-events: none;
  /* 마스크 초기 상태 - 전체를 덮음 */
  -webkit-mask-image: url("/src/assets/ink_mask.png");
  mask-image: url("/src/assets/ink_mask.png");
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
  -webkit-mask-position: center;
  mask-position: center;
}

/* 페이지가 열려있을 때 애니메이션 클래스가 추가되면 마스크 애니메이션 시작 */
.mask-layer.animating {
  /* -webkit-animation: mask-play 2.5s steps(22) forwards; */
  /* animation: mask-play 2.5s steps(22) forwards; */
}

/* 페이지가 닫혀있을 때 마스크가 전체를 덮음 */
.page:not(.flipped) .mask-layer {
  -webkit-mask-position: 0% 0%;
  mask-position: 0% 0%;
  /* -webkit-animation: none; */
  /* animation: none; */
}


/* 기존 ink-effect 스타일 제거 */
.ink-effect {
    display: inline-block;
    position: relative;
    backface-visibility: hidden;
    overflow: visible;
    /* 잉크가 불규칙하게 번진 테두리 */
    clip-path: polygon(
      3% 2%, 15% 0%, 30% 3%, 45% 1%, 60% 2%, 75% 0%, 90% 3%, 98% 1%,
      99% 10%, 100% 25%, 98% 40%, 99% 55%, 100% 70%, 98% 85%, 99% 95%,
      95% 98%, 80% 100%, 65% 98%, 50% 99%, 35% 100%, 20% 98%, 5% 99%,
      1% 96%, 0% 80%, 2% 65%, 0% 50%, 1% 35%, 0% 20%, 2% 8%
    );
}

/* 잉크 번짐 배경 효과 */
.ink-effect:before {
    content: "";
    position: absolute;
    top: -15px;
    left: -15px;
    right: -15px;
    bottom: -15px;
    background: 
      radial-gradient(circle at 10% 20%, rgba(101, 67, 33, 0.4) 0%, transparent 25%),
      radial-gradient(circle at 85% 15%, rgba(139, 69, 19, 0.3) 0%, transparent 30%),
      radial-gradient(circle at 95% 85%, rgba(101, 67, 33, 0.35) 0%, transparent 25%),
      radial-gradient(circle at 15% 90%, rgba(139, 69, 19, 0.3) 0%, transparent 30%),
      radial-gradient(ellipse at 50% 5%, rgba(101, 67, 33, 0.25) 0%, transparent 40%),
      radial-gradient(ellipse at 50% 95%, rgba(139, 69, 19, 0.25) 0%, transparent 40%);
    filter: blur(3px);
    z-index: -1;
    animation: inkFlow 15s ease-in-out infinite;
    transform: rotate(0.5deg);
}

/* 추가 잉크 번짐 레이어 */
.ink-effect:after {
    content: "";
    position: absolute;
    top: -10px;
    left: -10px;
    right: -10px;
    bottom: -10px;
    background: 
      conic-gradient(from 45deg at 20% 30%, transparent, rgba(139, 69, 19, 0.1) 10%, transparent 20%),
      conic-gradient(from 135deg at 80% 70%, transparent, rgba(101, 67, 33, 0.1) 10%, transparent 20%),
      conic-gradient(from 225deg at 70% 20%, transparent, rgba(139, 69, 19, 0.08) 10%, transparent 20%),
      conic-gradient(from 315deg at 30% 80%, transparent, rgba(101, 67, 33, 0.08) 10%, transparent 20%);
    filter: blur(2px);
    mix-blend-mode: multiply;
    z-index: -1;
    animation: inkPulse 12s ease-in-out infinite reverse;
}

/* 이미지 자체에 적용되는 효과 */
.ink-effect img {
    width: 100%;
    height: 100%;
    display: block;
    /* 이미지 내부 그림자로 가장자리 어둡게 */
    box-shadow: 
      inset 0 0 30px rgba(101, 67, 33, 0.3),
      inset 0 0 60px rgba(139, 69, 19, 0.2),
      inset 0 0 90px rgba(101, 67, 33, 0.1);
    /* 이미지 자체도 약간 불규칙한 형태로 */
    filter: contrast(1.05) saturate(1.1);
}

/* 잉크 번짐 애니메이션 */
@keyframes inkFlow {
    0%, 100% {
        transform: rotate(0.5deg) scale(1);
        filter: blur(3px);
    }
    25% {
        transform: rotate(-0.3deg) scale(1.02);
        filter: blur(2.5px);
    }
    50% {
        transform: rotate(0.8deg) scale(1.01);
        filter: blur(3.5px);
    }
    75% {
        transform: rotate(-0.5deg) scale(1.03);
        filter: blur(2.8px);
    }
}

@keyframes inkPulse {
    0%, 100% {
        opacity: 0.7;
        transform: scale(1) rotate(0deg);
    }
    33% {
        opacity: 0.9;
        transform: scale(1.04) rotate(1deg);
    }
    66% {
        opacity: 0.8;
        transform: scale(1.02) rotate(-0.5deg);
    }
}

/* 호버 시 잉크 번짐 강조 */
.ink-effect:hover {
    clip-path: polygon(
      2% 3%, 14% 1%, 31% 2%, 44% 0%, 61% 3%, 74% 1%, 91% 2%, 97% 0%,
      100% 11%, 99% 26%, 100% 41%, 98% 56%, 99% 71%, 100% 86%, 98% 94%,
      96% 99%, 81% 98%, 66% 100%, 51% 98%, 36% 99%, 21% 100%, 6% 98%,
      0% 95%, 1% 81%, 0% 66%, 2% 51%, 0% 36%, 1% 21%, 0% 9%
    );
}

.ink-effect:hover:before {
    filter: blur(4px);
    transform: rotate(-0.8deg) scale(1.05);
}

.ink-effect:hover:after {
    filter: blur(3px);
    opacity: 0.9;
}

.ink-effect:hover img {
    filter: contrast(1.1) saturate(1.15);
    box-shadow: 
      inset 0 0 40px rgba(101, 67, 33, 0.35),
      inset 0 0 80px rgba(139, 69, 19, 0.25),
      inset 0 0 120px rgba(101, 67, 33, 0.15);
}
</style>
