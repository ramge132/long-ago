<template>
    <div class="col-span-3 row-span-1 bg-red-400 flex flex-col items-center justify-center">
      <link href="https://fonts.googleapis.com/css?family=Lovers+Quarrel" rel="stylesheet" />
      <div class="book">
        <div class="pages" ref="pagesRef">
          <div
            v-for="(content, index) in pageContents"
            :key="index"
            class="page"
            :class="{ 'flipped': isFlipped(index) }"
            @click="handlePageClick(index)"
          >
            <p>{{ content }}</p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, reactive } from 'vue';
  
  // 총 페이지 수와 각 페이지의 내용을 정의합니다.
  const totalPages = 32;
  const pageContents = Array.from({ length: totalPages }, (_, i) =>
    i === 0 ? 'Open Me, please!' : `Page ${i + 1}`
  );
  
  const pagesRef = ref(null);
  const flippedPages = reactive(new Set());
  
  const isFlipped = (pageIndex) => {
    return flippedPages.has(pageIndex);
  };
  
  const handlePageClick = (pageIndex) => {
    if (pageIndex % 2 === 0) {
      // 오른쪽 페이지 클릭
      if (isFlipped(pageIndex)) {
        flippedPages.delete(pageIndex);
        flippedPages.delete(pageIndex - 1);
      } else {
        flippedPages.add(pageIndex);
        if (pageIndex + 1 < totalPages) {
          flippedPages.add(pageIndex + 1);
        }
      }
    } else {
      // 왼쪽 페이지 클릭
      if (isFlipped(pageIndex)) {
        flippedPages.delete(pageIndex);
        if (pageIndex + 1 <= totalPages) {
          flippedPages.delete(pageIndex - 1);
        }
      } else {
        flippedPages.add(pageIndex);
        flippedPages.add(pageIndex - 1);
      }
    }
  };
  
  onMounted(() => {
    const pageElements = pagesRef.value.children;
    for (let i = 0; i < pageElements.length; i++) {
      if (i % 2 === 0) {
        pageElements[i].style.zIndex = totalPages - i;
      }
    }
  });
  </script>
  
  <style scoped>
  .book {
    transition: opacity 0.4s 0.2s;
  }
  p {
    margin-top: 8vw;
    text-align: center;
    font-size: 5vw;
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
    width: 380px;
    height: 250px;
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
    width: 190px;
    height: 250px;
    transform-origin: 0 0;
    transition: transform 1.4s;
    backface-visibility: hidden;
    transform-style: preserve-3d;
    cursor: pointer;
    user-select: none;
    background-color: white; /* 기본 페이지 색상 */
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.1); /* 페이지 그림자 효과 */
  }
  .book .page:before {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    transition: background 0.7s;
    z-index: 2;
  }
  .book .page:nth-child(odd) {
    pointer-events: all;
    transform: rotateY(0deg);
    right: 0;
    border-radius: 0 4px 4px 0;
    background-color: white;
    /* 오른쪽 페이지 그라데이션 */
    background-image: linear-gradient(to right, 
      rgba(0,0,0,0.05) 0%, 
      rgba(0,0,0,0) 10%
    );
  }
  .book .page:nth-child(odd):hover {
    transform: rotateY(-15deg);
  }
  .book .page:nth-child(odd):hover:before {
    background: rgba(0, 0, 0, 0.03);
  }
  .book .page:nth-child(even) {
    pointer-events: none;
    transform: rotateY(180deg);
    transform-origin: 100% 0;
    left: 0;
    border-radius: 4px 0 0 4px;
    background-color: white;
    /* 왼쪽 페이지 그라데이션 */
    background-image: linear-gradient(to left, 
      rgba(0,0,0,0.05) 0%, 
      rgba(0,0,0,0) 10%
    );
  }
  .book .page:nth-child(even):before {
    background: rgba(0, 0, 0, 0.05); /* 뒷면 페이지 음영 */
  }
  .book .page.flipped:nth-child(odd) {
    pointer-events: none;
    transform: rotateY(-180deg);
  }
  .book .page.flipped:nth-child(odd):before {
    background: rgba(0, 0, 0, 0.05); /* 뒤집힌 페이지 음영 */
  }
  .book .page.flipped:nth-child(even) {
    pointer-events: all;
    transform: rotateY(0deg);
  }
  .book .page.flipped:nth-child(even):hover {
    transform: rotateY(15deg);
  }
  .book .page.flipped:nth-child(even):hover:before {
    background: rgba(0, 0, 0, 0.03);
  }
  
  /* 페이지 테두리 효과 */
  .book .page {
    border: 1px solid rgba(0, 0, 0, 0.1);
  }
  </style>