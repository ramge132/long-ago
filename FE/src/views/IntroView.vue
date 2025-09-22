<template>
  <div class="h-full grid grid-cols-2 relative">
    
    <!-- SEO 콘텐츠 (화면에 보이지 않지만 검색엔진용) -->
    <div class="sr-only seo-content">
      <h1>아주먼옛날 - Long Ago | AI 협동 스토리텔링 웹게임</h1>
      <p>아주먼옛날은 AI가 그려주는 실시간 협동 스토리텔링 게임입니다. 친구들과 함께 창의적인 이야기를 만들고 AI가 실시간으로 삽화를 그려줍니다.</p>
      
      <h2>게임 특징</h2>
      <ul>
        <li>AI 실시간 이미지 생성 - 당신의 이야기를 즉시 그림으로 변환</li>
        <li>최대 6명 동시 플레이 - 친구들과 함께 즐기는 멀티플레이어 게임</li>
        <li>실시간 협동 스토리텔링 - 턴 방식으로 이야기를 함께 만들어가기</li>
        <li>완성된 동화책 저장 - 만든 이야기를 영구 보관하고 공유</li>
        <li>9가지 그림 스타일 - 다양한 아트 스타일로 이야기 표현</li>
        <li>투표 시스템 - 민주적인 방식으로 이야기 품질 관리</li>
      </ul>

      <h2>인기 검색어</h2>
      <p>아주먼옛날, 아주 먼 옛날, long ago, AI게임, 웹게임, 멀티게임, 그리기 게임, 책 게임, 스토리텔링 게임, 실시간 게임, 협동 게임, 온라인 게임, AI 그림, 창작 게임, 무료 게임, 브라우저 게임, 친구와 게임, 동화 만들기, 이야기 게임, 멀티플레이어 게임, AI 이미지 생성</p>

      <h2>게임 방법</h2>
      <ol>
        <li>닉네임을 입력하고 게임을 시작하세요</li>
        <li>친구들을 초대하거나 혼자서도 플레이 가능합니다</li>
        <li>턴 방식으로 한 문장씩 이야기를 작성합니다</li>
        <li>AI가 실시간으로 당신의 이야기를 그림으로 그려줍니다</li>
        <li>다른 플레이어들과 투표를 통해 이야기를 선택합니다</li>
        <li>완성된 이야기는 아름다운 동화책으로 저장됩니다</li>
      </ol>

      <h2>자주 묻는 질문</h2>
      <h3>아주먼옛날은 무료인가요?</h3>
      <p>네, 아주먼옛날은 완전 무료 게임입니다. 회원가입 없이도 바로 플레이할 수 있습니다.</p>
      
      <h3>몇 명이서 함께 플레이할 수 있나요?</h3>
      <p>최소 1명부터 최대 6명까지 동시에 플레이할 수 있습니다. 혼자서도, 친구들과도 재미있게 즐길 수 있습니다.</p>

      <h3>어떤 기기에서 플레이할 수 있나요?</h3>
      <p>웹 브라우저만 있으면 PC, 태블릿, 스마트폰 등 어떤 기기에서도 플레이 가능합니다. 별도 앱 설치가 필요 없습니다.</p>

      <h3>AI는 어떤 그림을 그려주나요?</h3>
      <p>AI는 당신이 작성한 이야기를 분석해서 그에 맞는 삽화를 실시간으로 생성합니다. 9가지 다양한 아트 스타일 중에서 선택할 수 있습니다.</p>
    </div>
    <!-- 초기 ink.gif 로딩 오버레이 -->
    <Transition name="fade">
      <div v-if="introLoading" class="absolute inset-0 bg-white flex justify-center items-center z-10">
        <img src="@/assets/ink.gif" alt="Loading..." style="width: 300px; height: auto;"/>
      </div>
    </Transition>

    <div class="flex flex-col items-center justify-center gap-y-6">
      <div class="flex items-center relative">
        <img :src="currentProfile" alt="프로필" class="w-52 h-52" style="transition: none;" />
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
          @click="startWithAudio"
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
import { ref, onMounted, nextTick } from "vue";
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
import { useAudioStore } from "@/stores/audio";

const userStore = useUserStore();
const gameStore = useGameStore();
const audioStore = useAudioStore();
const router = useRouter();
const route = useRoute();
const nickname = ref("닉네임");
const introLoading = ref(true); // 인트로 화면 자체 로딩 상태

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
  // 랜덤한 프로필 선택 (현재 프로필과 다른 것 선택)
  let randomIndex;
  do {
    randomIndex = Math.floor(Math.random() * profiles.value.length);
  } while (randomIndex === currentIndex.value && profiles.value.length > 1);
  
  currentIndex.value = randomIndex;
  currentProfile.value = profiles.value[randomIndex];
};

const start = () => {
  userStore.setUserNickname(nickname);
  userStore.setUserProfile(currentProfile);
  sessionStorage.setItem("userNickname", nickname.value);

  router.push("/game/lobby");
};

// 사용자 상호작용으로 오디오 활성화
const startWithAudio = async () => {
  try {
    // AudioContext 생성 및 활성화 시도
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    if (audioContext.state === 'suspended') {
      await audioContext.resume();
    }
    
    // 오디오 설정 활성화
    audioStore.audioData = true;
    
  } catch (error) {
  }
  
  start();
};

// 이미지 프리로딩 함수
const preloadImages = () => {
  return Promise.all(profiles.value.map(profileSrc => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.src = profileSrc;
      img.onload = resolve;
      img.onerror = reject;
    });
  }));
};

onMounted(async () => {
  // 이미지 프리로딩
  try {
    await preloadImages();
  } catch (error) {
    // 이미지 프리로딩 실패 시 무시
  } finally {
    // 모든 처리가 끝난 후 로딩 화면 제거
    nextTick(() => {
      introLoading.value = false;
    });
  }
  
  const randomIndex = Math.floor(Math.random() * profiles.value.length);
  currentIndex.value = randomIndex;
  currentProfile.value = profiles.value[randomIndex];
  
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
