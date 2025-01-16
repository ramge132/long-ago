<template>
  <div class="flex flex-col justify-center items-center space-y-10">
    <img :src="Logo" alt="옛날 옛적에..." />
    <div @click="start" class="font-bold text-3xl cursor-pointer animate-shake">
      시작하기! ➜
    </div>
    <!-- <HomeHeader />
    <HomeSlider />
    <HomeChampTable /> -->
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import Logo from "@/assets/logo.svg";

const router = useRouter();

const start = () => {
  router.push("/init");
};
</script>
