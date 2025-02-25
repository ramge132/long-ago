<template>
    <div v-if="isVisible" class="notice-banner absolute z-20 bg-white">
      <div class="notice-content flex flex-col items-center gap-y-4 text-xl">
        <div class="font-bold text-3xl">공지사항</div>
        <p><strong>아주 먼 옛날</strong>에 대한 많은 관심에 깊이 감사드립니다.</p>
        <p>
            현재 서비스 이용자가 급증함에 따라 <strong>이미지 생성 속도</strong>가
            크게 저하될 것으로 예상됩니다.
        </p>
        <p class="text-center">
            이는 GPU 서버 자원이 제한된 환경💸에서 운영되기 때문이며,<br>
            보다 원활한 서비스 제공을 위해 <strong>최적화 작업을 지속적으로 진행하고 있습니다.</strong>
        </p>

        <h4>이용에 불편을 드려 죄송하며, 너그러운 양해 부탁드립니다.</h4>

        <p>감사합니다!😘</p>
      </div>
      <button class="close-btn" @click="isVisible = false">닫기 ✖</button>
    </div>
  </template>
  
  <script setup>
  import { ref } from "vue";
  
  const isVisible = ref(true); // 공지 표시 여부
  </script>
  
  <style scoped>
  .notice-banner {
    background-color: #ffeeba;
    color: #856404;
    border: 1px solid #ffeeba;
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 16px;
    cursor: pointer;
  }
  </style>
  