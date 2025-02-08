<template>
  <div
    class="w-4/5 max-w-6xl min-w-[1000px] h-16 flex justify-between items-center z-10 px-2"
  >
    <img :src="Logo" alt="logo" class="w-36 p-3" />
    <div
      v-if="isLoggedIn"
      class="p-3 font-semibold flex items-center gap-x-5 text-white text-sm"
    >
      <RouterLink
        to="#"
        class="transform transition-all duration-300 hover:scale-110 cursor-pointer"
        >베스트 셀러
      </RouterLink>
      <RouterLink
        to="#"
        class="transform transition-all duration-300 hover:scale-110 cursor-pointer"
        >내 서재
      </RouterLink>
      <div class="transform transition-all duration-300 hover:scale-110 cursor-pointer">
        로그아웃
      </div>
    </div>
    <div
      v-else
      class="p-3 font-semibold flex items-center gap-x-5 text-white text-sm"
    >
      <RouterLink
        to="#"
        class="transform transition-all duration-300 hover:scale-110 cursor-pointer"
        >베스트 셀러
      </RouterLink>
      <img
        class="h-6 transform transition-all duration-300 hover:scale-110 cursor-pointer"
        @click="toggleModal"
        :src="MyInfo"
        alt="로그인"
      />
    </div>
    <Transition name="fade">
      <div
        v-if="modal.isOpen"
        @click="toggleModal"
        class="absolute bg-[#00000050] w-full h-full top-0 left-0 flex justify-center items-center"
      >
        <div
          @click.stop
          class="w-72 h-72 text-[#ffffff] font-makgeolli text-2xl rounded-md overflow-hidden flex flex-col"
        >
          <!-- 상단 버튼 -->
          <div class="grid grid-cols-2 gap-x-1">
            <div
              @click="toggleSignIn('signin')"
              class="bg-[#00000090] flex justify-center items-center p-1 rounded-t-md cursor-pointer"
              :class="
                modal.status === 'signin'
                  ? 'text-[#E5E091]'
                  : 'text-xl bg-[#000000ff] scale-y-90'
              "
              style="height: 40px"
            >
              로그인
            </div>
            <div
              @click="toggleSignIn('signup')"
              class="bg-[#00000090] flex justify-center items-center p-1 rounded-t-md cursor-pointer"
              :class="
                modal.status === 'signup'
                  ? 'text-[#E5E091]'
                  : 'text-xl bg-[#000000ff] scale-y-90'
              "
              style="height: 40px"
            >
              회원가입
            </div>
          </div>

          <!-- 콘텐츠 영역 -->
          <div
            class="flex-1 max-w-full bg-[#00000090] overflow-auto flex items-center justify-center"
          >
            <SignIn v-if="modal.status === 'signin'" @sign-in="sign" />
            <SignUp v-else @register="sign" />
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>
<script setup>
import { ref } from "vue";
import { useUserStore } from "@/stores/auth";
import {
  MyInfo,
  Logo,
} from "@/assets";
import { SignIn, SignUp } from "@/components";

const userStore = useUserStore();
const isLoggedIn = ref(localStorage.getItem("userEmail") ? true : false);
const modal = ref({
  isOpen: false,
  status: "signin",
});

const toggleModal = () => {
  modal.value.isOpen = !modal.value.isOpen;
};

const toggleSignIn = (status) => {
  modal.value.status = status;
};

const sign = (userId) => {
  localStorage.setItem("userEmail", userId);
  isLoggedIn.value = true;
  userStore.setUserEmail(userId);
  modal.value.isOpen = false;
};
</script>
