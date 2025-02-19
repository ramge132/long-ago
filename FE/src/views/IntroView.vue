<template>
  <div class="h-full grid grid-cols-2">
    <div class="flex flex-col items-center justify-center gap-y-6">
      <div class="flex items-center relative">
        <img :src="currentProfile" alt="프로필" class="w-52 h-52" />
        <div
          class="absolute bottom-3 right-3 w-10 h-10 rounded-full bg-gray-200 transition-all duration-200 hover:bg-gray-300 hover:scale-105 flex justify-center items-center cursor-pointer"
          @click="refresh"
        >
          <img
            src="@/assets/icons/refresh.svg"
            alt="새로고침"
            class="w-[60%] h-[60%]"
          />
        </div>
      </div>
      <div class="flex text-xl flex-col w-80">
        <input
          type="text"
          class="w-full h-12 font-medium rounded-xl border border-[#00000090] bg-neutral-100/50 px-3"
          v-model="nickname"
          @keydown.enter="start"
        />
      </div>
      <div
        class="w-80 h-16 font-semibold text-2xl rounded-xl bg-black text-white cursor-pointer flex justify-center items-center startBtn"
      >
        <div
          @click="start"
          class="w-full h-full flex justify-center items-center gap-x-2 hover:scale-110 transition-transform"
        >
          <img :src="StartIcon" alt="시작하기 아이콘" class="h-5 w-5">
          <span>
            {{ !gameStore.getBossId() ? "시작하기" : "참여하기" }}
          </span>
        </div>
      </div>
    </div>
    <div
      class="rounded-xl border flex flex-col justify-center p-5 bg-[#ffffffbb] my-10 mr-10"
    >
      <div class="text-center">
        <h1 class="text-xl font-medium basis-1 my">게임 플레이 방법</h1>
      </div>
      <div
        class="h-full"
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
            class="px-5 py-1 h-full"
          >
            <div class="flex flex-col items-center h-full">
              <div class="h-1/6">
                <p class="self-center font-bold text-2xl">{{ slide.title }}</p>
              </div>
              <div class="h-3/5 flex justify-center items-center">
                <img
                  :src="slide.image"
                  alt="규칙 이미지"
                  class="h-4/5 max-w-[90%]"
                />
              </div>
              <div class="flex-1 flex justify-center items-center">
                <p v-html="slide.text" class="text-lg text-center font-semibold"></p>
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
import { StartIcon, rule1, rule2, rule3, rule4, rule5 } from "@/assets";
import Profile from "@/assets/images/profiles";
import { useUserStore } from "@/stores/auth";
import { useGameStore } from "@/stores/game";

const userStore = useUserStore();
const gameStore = useGameStore();
const router = useRouter();
const route = useRoute();
const nickname = ref("닉네임");

const profiles = ref([
  Profile.cat_1,
  Profile.cat_2,
  Profile.cat_4,
  Profile.cat_5,
  Profile.cat_6,
  Profile.dog_1,
  Profile.dog_2,
  Profile.dog_3,
  Profile.dog_4,
  Profile.dog_5,
  Profile.dog_6,
  Profile.cattle_1,
  Profile.cattle_2,
  Profile.cattle_3,
  Profile.cattle_4,
  Profile.cow_1,
  Profile.chicken_1,
  Profile.dragon_1,
  Profile.dragon_2,
  Profile.dragon_3,
  Profile.dragon_4,
  Profile.horse_1,
  Profile.monkey_1,
  Profile.monkey_2,
  Profile.pig_1,
  Profile.pig_2,
  Profile.pig_4,
  Profile.rabbit_1,
  Profile.rabbit_2,
  Profile.rabbit_3,
  Profile.rabbit_4,
  Profile.rat_1,
  Profile.rat_2,
  Profile.rat_3,
  Profile.rat_4,
  Profile.rat_5,
  Profile.sheep_1,
  Profile.sheep_2,
  Profile.sheep_3,
  Profile.tiger_1,
  Profile.tiger_2,
]);

const currentProfile = ref(Profile.cat_1);
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

  router.push("/game/lobby");
};

onMounted(() => {
  currentProfile.value = profiles.value[Math.floor(Math.random() * profiles.value.length)];
  const userData = JSON.parse(localStorage.getItem("userData"));
  if (userData && userData.nickname) {
    nickname.value = userData.nickname;
  } else {
    // 랜덤한 Guest_XXXXX 생성
    const randomGuest = `이야기꾼_${Math.floor(10000 + Math.random() * 90000)}`;
    nickname.value = randomGuest;
  }

  if (route.query.roomID) {
    gameStore.setBossId(route.query.roomID);
    // 쿼리 파라미터 제거
    router.replace({ path: route.path, query: {} });
  }
});

const modules = ref([Navigation, Pagination, Autoplay]);

const ruleSlides = ref([
  {
    no: 1,
    image: rule1,
    title: "시작준비",
    text: `
    이야기 카드 4장,<br>결말 카드 1장을 갖고 시작합니다
    `,
  },
  {
    no: 2,
    image: rule2,
    title: "이야기 펼치기",
    text: `
    차례대로 이야기 카드를 꺼내서<br>다 같이 스토리를 만들어봐요
    `,
  },
  {
    no: 3,
    image: rule3,
    title: "투표하기",
    text: `
    이야기를 들은 사람들은<br>찬성 또는 반대를 눌러 전개를 결정해요
    `,
  },
  {
    no: 4,
    image: rule4,
    title: "결말맺기",
    text: `
    긴장감이 충분해지면<br>결말 카드를 사용해 이야기를 마무리하세요
    `,
  },
  {
    no: 5,
    image: rule5,
    title: "결과",
    text: `
    게임이 끝났을 때 점수가 가장 높은 사람이 우승!<br>
    아무도 결말을 못 맺으면 전원 탈락!
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
  width: 7px;
  height: 7px;
  position: relative;
  background: #00000030;
}
.swiper-pagination-bullet-active {
  background: black;
}
.swiper-button-prev,
.swiper-button-next {
  color: black;
  font-weight: 900;
  scale: 0.5;
}
.startBtn:hover {
  background: linear-gradient(60deg, rgba(232,193,147,1) 0%, rgba(193,164,204,1) 20%, rgba(221,124,175,1) 60%, rgba(191,176,209,1) 90%, #9FBACC 100%);
  background-size: 300% 100%;
  animation: gradient 1.5s ease-in-out infinite alternate;
}
@keyframes gradient {
  0% {
    background-position: 0%;
  }
  100% {
    background-position: 100%;
  }
}
</style>
