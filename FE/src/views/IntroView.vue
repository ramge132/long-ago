<template>
  <div class="h-full grid grid-cols-2">
    <div class="flex flex-col items-center justify-center gap-y-10">
      <div class="relative">
        <div class="rounded-full border border-black w-44 overflow-hidden">
          <img :src="currentProfile" alt="프로필" />
        </div>
        <div
          class="absolute bottom-2 right-2 w-9 h-9 rounded-full bg-gray-200 flex justify-center items-center cursor-pointer"
          @click="refresh"
        >
          <img
            src="@/assets/icons/refresh.svg"
            alt="새로고침"
            class="w-[60%] h-[60%]"
          />
        </div>
      </div>
      <div class="flex text-xl flex-col">
        <label for="">닉네임</label>
        <input
          type="text"
          class="rounded-xl border border-neutral-300 bg-neutral-100/50 px-3"
          v-model="nickname"
        />
      </div>
      <div
        @click="start"
        class="cursor-pointer transition-all duration-300 hover:scale-110"
      >
        <img
          v-if="!route.query.roomID"
          :src="gameStart"
          alt="시작하기"
          class="h-10"
        />
        <img v-else :src="gameJoin" alt="참여하기" class="h-10" />
      </div>
    </div>
    <div
      class="rounded-xl border flex flex-col justify-center gap-y-7 p-5 bg-[#ffffff60] my-10 mr-10"
    >
      <div class="text-center">
        <h1 class="text-3xl basis-1 my">플레이 방법</h1>
      </div>
      <div
        class="border-dotted border-[5px] border-[#00000030] rounded-3xl h-[70%]"
      >
        <swiper
          class="h-[100%]"
          :modules="modules"
          :slides-per-view="1"
          :space-between="1"
          :centered-slides="true"
          navigation
          :loop="true"
          :autoplay="{
            delay: 5000,
            disableOnInteraction: false,
          }"
          :pagination="pagination"
        >
          <swiper-slide
            v-for="slide in ruleSlides"
            :key="slide.no"
            class="px-5 py-1 h-[100%]"
          >
            <div class="flex flex-col items-center h-[100%]">
              <div class="h-[50%]">
                <img
                  :src="slide.image"
                  alt="규칙 이미지"
                  class="h-full max-h-32"
                />
              </div>
              <div class="h-[50%] flex flex-col gap-y-5">
                <p class="self-center font-bold text-xl">{{ slide.title }}</p>
                <p v-html="slide.text" class="text-md"></p>
              </div>
            </div>
          </swiper-slide>
        </swiper>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { Swiper, SwiperSlide } from "swiper/vue";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import "swiper/css/scrollbar";
import { Autoplay, Navigation, Pagination } from "swiper/modules";
import {
  Profile1,
  Profile2,
  Profile3,
  Profile4,
  Profile5,
  Profile6,
  gameStart,
  gameJoin,
  rule1,
  rule2,
} from "@/assets";
import { useUserStore } from "@/stores/auth";

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();
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

const start = () => {
  userStore.setUserNickname(nickname);
  userStore.setUserProfile(currentProfile);
  sessionStorage.setItem("userNickname", nickname.value);
  if (route.query.roomID) {
    router.push(`/game/lobby?roomID=${route.query.roomID}`);
  } else {
    router.push("/game/lobby");
  }
};

onMounted(() => {
  const userData = JSON.parse(localStorage.getItem("userData"));
  if (userData && userData.nickname) {
    nickname.value = userData.nickname;
  } else {
    // 랜덤한 Guest_XXXXX 생성
    const randomGuest = `이야기꾼_${Math.floor(10000 + Math.random() * 90000)}`;
    nickname.value = randomGuest;

    // localStorage에 저장
    // const newUserData = { ...userData, nickname: randomGuest };
    // localStorage.setItem("userData", JSON.stringify(newUserData));
  }
});

const modules = ref([Navigation, Pagination, Autoplay]);

const ruleSlides = ref([
  {
    no: 1,
    image: rule1,
    title: "1. 게임 시작",
    text: `
    모든 플레이어는 게임이 시작할 때
    4점의 포인트와 4~6장의 이야기 카드를 가집니다. 
    이야기 카드는 사물이나 
    동작, 상태를 표현하고 있습니다.
    `,
  },
  {
    no: 2,
    image: rule2,
    title: "2. 게임 진행",
    text: `
    순서대로 돌아가며 카드 한 장을 소비해
    그 카드에 적힌 단어와 연관된 이야기를 작성합니다.
    게임의 가장 처음 시작하는 이야기는 "아주 먼 옛날" 로 이야기를 시작합니다.
    `,
  },
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
  background: #e5e091;
  border: 1px solid black;
}
.swiper-button-prev,
.swiper-button-next {
  color: black;
  scale: 0.5;
}
</style>
