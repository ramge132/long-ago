<template>
  <div>
    <div
      class="w-96 bg-[#f5f5f553] flex flex-col justify-center items-center relative rounded-3xl overflow-hidden"
    >
      <RouterLink to="/">
        <img :src="logo" alt="logo" class="w-64 p-3" />
      </RouterLink>
      <div class="mb-4">
        <transition name="fade" mode="out-in">
          <!-- <KeepAlive> -->
          <SignIn v-if="status == 'signin'" @register="moveRegister" />
          <SignUp v-else-if="status == 'signup'" @signin="moveSignIn" />
          <!-- </KeepAlive> -->
        </transition>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref } from "vue";
import { SignIn, SignUp } from "@/components";
import logo from "@/assets/logo.svg";

const status = ref("signin");

const moveRegister = () => {
  status.value = "signup";
};

const moveSignIn = () => {
  status.value = "signin";
};
</script>
<style>
/* Enter 애니메이션 (슬라이드 없이 나타남) */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease-in-out; /* opacity로 부드럽게 나타남 */
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0; /* 컴포넌트가 처음에는 안 보이게 설정 */
}
</style>
