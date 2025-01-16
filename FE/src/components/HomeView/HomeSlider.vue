<template>
  <div class="swiper-container">
    <swiper
      :modules="modules"
      :slides-per-view="3"
      space-between="30"
      :centered-slides="true"
      effect="coverflow"
      :coverflow-effect="{
        rotate: 50,
        stretch: 0,
        depth: 100,
        modifier: 1,
        slideShadows: false,
      }"
      :loop="true"
      :autoplay="{
        delay: 3500,
        disableOnInteraction: false,
      }"
      class="my-swiper"
    >
      <!-- 슬라이드 내용 (div 사용) -->
      <swiper-slide v-for="(slide, index) in slides" :key="index">
        <div
          class="flex justify-center items-center h-72 w-full bg-gray-300 rounded-lg text-2xl font-bold text-white shadow-lg"
          :style="{ backgroundColor: slide.color }"
        >
          {{ slide.text }}
        </div>
      </swiper-slide>
    </swiper>
  </div>
</template>

<script setup>
import { Swiper, SwiperSlide } from "swiper/vue";
import { Autoplay, EffectCoverflow } from "swiper/modules";
import "swiper/css"; // Swiper 기본 스타일
import "swiper/css/effect-coverflow"; // Coverflow 스타일

const modules = [Autoplay, EffectCoverflow];

// 슬라이드 데이터 정의
const slides = [
  { text: "Slide 1", color: "#FF6347" },
  { text: "Slide 2", color: "#3CB371" },
  { text: "Slide 3", color: "#1E90FF" },
  { text: "Slide 4", color: "#FFD700" },
];
</script>

<style scoped>
.swiper {
  perspective: 1000px; /* 3D 효과를 위한 원근감 설정 */
  padding-top: 50px;
  padding-bottom: 50px;
}

.swiper-slide {
  transition: transform 0.5s ease; /* 슬라이드 전환 효과 추가 */
}

.swiper-slide-active {
  transform: scale(1.1); /* 활성 슬라이드 확대 */
}
</style>
