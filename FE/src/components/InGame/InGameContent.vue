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
        <p v-html="bookCover.title ? bookCover.title : `아주 먼<br>옛날..<br>`" class="break-keep absolute -translate-y-150px font-title text-white" style="backface-visibility: hidden"></p>
        <img :src="bookCover.imageUrl" alt="" v-if="bookCover.imageUrl" class="w-full h-full object-fill">
        
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
            <div class="bg-effect scale-[85%] rounded-lg overflow-hidden" v-if="content.image">
              <img :src="content.image" alt="이야기 이미지" class="w-full h-full">
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

const audioStore = useAudioStore();
const pagesRef = ref(null);
const flippedPages = reactive(new Set());
const isClickLocked = ref(false);

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

  // 먼저 표지 제목을 읽어줌
  if (props.bookCover.title) {
    await speakText(props.bookCover.title);
  }

  // 책 내용을 순서대로 처리: 0,1 페이지, 그 다음 2,3 페이지, ...
  for (const [i, element] of props.bookContents.entries()) {
    // 두 페이지씩 추가 (페이지 넘기는 효과)
    flippedPages.add(i * 2);
    flippedPages.add(i * 2 + 1);

    // 페이지 넘기는 효과음 재생
    const turningEffect = new Audio(TurningPage);
    turningEffect.play();

    // tts 함수(speakText)가 음성 재생 완료 후 resolve하는 프로미스를 반환한다고 가정합니다.
    await speakText(element.content);
  }
  
  // 모든 작업이 완료되면 표지로 되돌리기
  // 모든 페이지를 다시 닫아서 표지만 보이게 함
  flippedPages.clear();
  
  // 클릭 잠금 해제 및 나레이션 완료 신호 전송
  isClickLocked.value = false;
  emit('narration-complete');
}

watch(
  () => props.gameStarted,
  async (newValue) => {
    if (newValue === false) {
      isClickLocked.value = true;
      
      // 즉시 표지로 이동 (페이지 닫기 애니메이션 없이)
      // flippedPages를 모두 클리어하여 표지만 보이게 함
      flippedPages.clear();
      
      // 즉시 나레이션 시작
      if (audioStore.audioData) {
        runBookSequence();
      } else {
        // 모든 작업이 완료되면 클릭 잠금 해제
        isClickLocked.value = false;
      }
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
  z-index: 2;
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

.bg-effect {
    display: inline-block;
    position: relative;
    backface-visibility: hidden;
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
      inset 0 0 30px #EEEEF0 /* 배경과 같은 색 */,
      inset 0 0 30px #EEEEF0,
      inset 0 0 30px #EEEEF0,
      inset 0 0 30px #EEEEF0;
}
</style>
