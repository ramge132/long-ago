<template>
  <div class="row-span-3 w-full h-full flex items-center justify-center">
    <div class="book absolute top-0">
      <div class="pages" ref="pagesRef">
        <div
          class="page cursor-pointer flex flex-col items-center justify-center text-gray-300 text-2xl"
          :class="{ flipped: isFlipped(0) }"
          @click="handlePageClick(0)"
          :style="{ zIndex: calculateZIndex(0) }"
        >
          Long Ago..
        </div>
        <template
          v-for="(content, index) in bookContents"
          :key="index"
        >
          <div
            class="page cursor-pointer flex flex-col items-center justify-center"
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
            {{ content.image }}
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

const audioStore = useAudioStore();
const pagesRef = ref(null);
const flippedPages = reactive(new Set());

const props = defineProps({
  bookContents: {
    Type: Array,
  }
})

const calculateZIndex = (pageIndex) => {
  const totalPages = props.bookContents.length * 2 + 1;
  
  if (pageIndex % 2 === 1) {
    return pageIndex * 2;
  }
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
  if (pageIndex / 2 === props.bookContents.length) {
    return;
  }
  
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
  
  updatePagesZIndex();
};

watch(() => props.bookContents.length,
(afterSize, beforeSize) => {
  if (afterSize > beforeSize) {
    for (let i of Array.from({length: afterSize - 1}, (_, index) => index * 2)) {
      if (!isFlipped(i)) {
        flippedPages.add(i);
        flippedPages.add(i + 1);
      }
    }
  }
  updatePagesZIndex();
});

onMounted(() => {
  updatePagesZIndex();
  handlePageClick(0);
});
</script>

<style scoped>
.book {
  transition: opacity 0.4s 0.2s;
}
p {
  text-align: center;
  color: #000000;
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
  background-image: url("/src/assets/images/bookPage.svg");
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
</style>
