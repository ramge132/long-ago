<template>
  <div class="w-[100%] h-[100%] flex justify-between">
    <div class="flex flex-col items-center justify-center w-[45%]">
      <div class="relative mb-5">
        <div
          class="rounded-full border border-black w-[120px] h-[120px] overflow-hidden"
        >
          <img :src="currentProfile" alt="프로필" />
        </div>
        <div
          class="absolute bottom-0 right-2 w-[25px] h-[25px] rounded-full bg-gray-200 flex justify-center items-center cursor-pointer"
          @click="refresh"
        >
          <img
            src="@/assets/icons/refresh.svg"
            alt="새로고침"  
            class="w-[60%] h-[60%]"
          />
        </div>
      </div>
      <div class="flex flex-col mb-10">
        <label for="">닉네임</label>
        <input
          type="text"
          class="rounded-xl border border-neutral-300 bg-neutral-100/50 px-3"
          v-model="nickname"
        />
      </div>
    </div>
    <div
      class="w-[50%] pb-5 pl-5 pr-5"
    >
      <div class="rounded-xl border  flex flex-col justify-between border-black p-5">
        <div class="text-center">
          <h1 class="text-2xl basis-1 my">플레이 방법</h1>
        </div>
        <div class="border border-dotted border-black rounded-3xl h-[60%]">
          <swiper class="h-[100%]"
          :modules="modules"
      :slides-per-view="1"
      :space-between="1"
      :centered-slides="true"
      navigation  
      :loop="true"
      :pagination="pagination"
      @swiper="onSwiper"
      @slideChange="onSlideChange"
    >
      <swiper-slide v-for="slide in ruleSlides" :key="slide.no" class="p-5 h-[100%]">
        <div class="flex flex-col items-center h-[100%]">
          <div class="h-[50%]">
            <img :src="slide.image" alt="규칙 이미지" class="h-[100%]">
          </div>
          <div class="h-[50%] flex flex-col">
            <p class="self-center font-bold text-xl">{{ slide.title }}</p>
            <p v-html="slide.text"></p>
          </div>
        </div>
      </swiper-slide>
      
    </swiper>
        </div>
        <div class="flex justify-center basis-1">
          <img :src="gameStart" alt="시작하기">
        </div>
        
      </div>
    </div>
  </div>
</template>
<script setup>
import Profile1 from "@/assets/images/profiles/profile1.svg";
import Profile2 from "@/assets/images/profiles/profile2.svg";
import Profile3 from "@/assets/images/profiles/profile3.svg";
import Profile4 from "@/assets/images/profiles/profile4.svg";
import Profile5 from "@/assets/images/profiles/profile5.svg";
import Profile6 from "@/assets/images/profiles/profile6.svg";
import gameStart from "@/assets/images/gameStart.svg";
import rule1 from "@/assets/images/rules/rule1.svg";
import rule2 from "@/assets/images/rules/rule2.svg";
import { ref, onMounted } from "vue";
import { Swiper, SwiperSlide } from "swiper/vue";
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import 'swiper/css/scrollbar';
import { Autoplay, Navigation, Pagination } from "swiper/modules";
const nickname = ref("닉네임");

const profiles = ref([
  Profile1,
  Profile2,
  Profile3,
  Profile4,
  Profile5,
  Profile6,
]);

const currentProfile = ref(Profile1);
const currentIndex = ref(0);

const refresh = () => {
  while (true) {
    const randomIndex = Math.floor(Math.random() * profiles.value.length);
    if (currentIndex.value != randomIndex) {
      currentIndex.value = randomIndex;
      currentProfile.value = profiles.value[currentIndex.value];
      break;
    }
  }
};  

onMounted(() => {
  nickname.value = JSON.parse(localStorage.getItem("userData")).nickname;
});

const modules = ref([Navigation, Pagination, Autoplay]);

const onSwiper = (swiper) => {
  console.log(swiper);
};
const onSlideChange = () => {
  console.log('slide change');
};

const ruleSlides = ref([
  {
    no: 1,
    image: rule1,
    title: '1. 게임 시작',
    text: `
    모든 플레이어는 게임이 시작할 때
    4점의 포인트와 4~6장의 이야기 카드를 가집니다. 
    이야기 카드는 사물이나 
    동작, 상태를 표현하고 있습니다.
    `  
  },
  {
    no: 2,
    image: rule2,
    title: '2. 게임 진행',
    text: `
    순서대로 돌아가며 카드 한 장을 소비해
    그 카드에 적힌 단어와 연관된 이야기를 작성합니다.
    게임의 가장 처음 시작하는 이야기는 "옛날 옛적에..." 로 이야기를 시작합니다.
    `
  }
]);


const pagination = {
  clickable: true,
};
</script>
<style>
.swiper-pagination-bullet {
  opacity: 1;
  width: 10px;
  height: 10px;
  position: relative;
}
.swiper-pagination-bullet-active {
  background: #0080FF;
}
.swiper-button-prev, .swiper-button-next {
  color: black;
}

</style>
