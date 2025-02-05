<template>
  <div
    class="row-span-3 w-full h-full flex items-center justify-center"
  >
    <div class="book absolute top-0">
      <div class="pages" ref="pagesRef">
        <div
          class="page cursor-pointer flex flex-col items-center justify-center text-gray-300 text-2xl"
          :class="{ flipped: isFlipped(0) }"
          @click="handlePageClick(0)"
        >
          Long Ago..
        </div>
        <template
          v-for="(content, index) in bookContent"
          :key="index"
        >
          <div
            class="page cursor-pointer flex flex-col items-center justify-center"
            :class="{ flipped: isFlipped(index * 2 + 1) }"
            @click="handlePageClick(index * 2 + 1)">
            {{ content.content }}
          </div>
          <div
            class="page cursor-pointer flex flex-col items-center justify-center"
            :class="{ flipped: isFlipped(index * 2 + 2) }"
            @click="handlePageClick(index * 2 + 2)">
            {{  content.image }}
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive, watch } from "vue";
import { useAudioStore } from "@/stores/audio";
import { TurningPage } from "@/assets";

const audioStore = useAudioStore();

const bookContent = ref([
  { content: "", image: null }  // 초기 상태
]);

const addBookContent = (newContent) => {
  // 마지막 요소 직전에 새 콘텐츠 추가
  const lastIndex = bookContent.value.length - 1;
  bookContent.value.splice(lastIndex, 0, {
    content: newContent.content || "",
    image: newContent.image || null
  });
  
  // 마지막 요소는 항상 빈 요소로 유지
  if (bookContent.value[bookContent.value.length - 1].content !== "" || 
      bookContent.value[bookContent.value.length - 1].image !== null) {
    bookContent.value.push({ content: "", image: null });
  }
};

// 페이지 삭제도 구현해야 함

// 사용 예시
// addBookContent({ content: "1번 글", image: "첫번째이미지" });
// addBookContent({ content: "2번 글", image: "두번째이미지" });

const pagesRef = ref(null);
const flippedPages = reactive(new Set());

const isFlipped = (pageIndex) => {
  return flippedPages.has(pageIndex);
};

const handlePageClick = (pageIndex) => {
  console.log(bookContent.value.length);
  if (pageIndex / 2 === bookContent.value.length){
    console.log('last page click event block');
    return
  }
  if (audioStore.audioData) {
    const turningEffect = new Audio(TurningPage);
    turningEffect.play();
  }
  if (pageIndex % 2 === 0) {
    // 오른쪽 페이지 클릭
    if (isFlipped(pageIndex)) {
      flippedPages.delete(pageIndex);
      flippedPages.delete(pageIndex - 1);
    } else {
      flippedPages.add(pageIndex);
      if (pageIndex + 1 < bookContent.value.length * 2 + 1) {
        flippedPages.add(pageIndex + 1);
      }
    }
  } else {
    // 왼쪽 페이지 클릭
    if (isFlipped(pageIndex)) {
      flippedPages.delete(pageIndex);
      if (pageIndex + 1 <= bookContent.value.length * 2 + 1) {
        flippedPages.delete(pageIndex - 1);
      }
    } else {
      flippedPages.add(pageIndex);
      flippedPages.add(pageIndex - 1);
    }
  }
};

watch(() => bookContent.value.length,
(afterSize, beforeSize) => {
  console.log(afterSize, beforeSize, 'size');
  console.log(bookContent.value.length);
  // 새로운 페이지가 추가됨
  if (afterSize > beforeSize) {
    for (let i of Array.from({length: afterSize - 1}, (_, index) => index * 2)) {
      console.log(i, 'clicked')
      // 오른쪽 페이지 클릭
      if (!isFlipped(i)) {
        flippedPages.add(i);
        flippedPages.add(i + 1);
        if (i + 1 <= bookContent.value.length * 2 + 1) {
          console.log('test');
        }
      }
    }
    flippedPages.add()
    // handlePageClick(index * 2 + 2)
  }
  // 투표를 통해 페이지가 버려짐
  else {

  }
  bookContent.value.length
});

onMounted(() => {
  const pageElements = pagesRef.value.children;
  for (let i = 0; i < pageElements.length; i++) {
    if (i % 2 === 0) {
      pageElements[i].style.zIndex = bookContent.value.length * 2 + 2 - i;
    }
  }

  var count = 1;

  handlePageClick(0);
  setInterval(() => {
      if (bookContent.value.length != 5) {
        console.log(bookContent.value.length);
        addBookContent({ content: `${count}번 글`, image: `${count}번째이미지` });
        count++;
        console.log(bookContent.value);
      }
    }, 5000);
});

// onUnmounted(() => {
//   clearInterval(intervalId);
// });
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
