<template>
  <div class="flex flex-1 justify-center">
    <div
      class="w-[50vh] h-[50vh] p-[30px] rounded-2xl bg-white flex flex-col justify-center items-center"
    >
      <img src="@/assets/images/ERE.GG.svg" class="grow w-[20vh]" />
      <div class="grow flex flex-col min-w-[100%] my-8">
        <label class="font-black text-xl mb-2 min-w-[100%]">스팀 ID</label>
        <input
          class="border rounded-xl p-[8px] min-w-[100%]"
          placeholder="ID 입력"
          type="text"
        />
      </div>
      <div class="grow min-w-[100%] text-center">
        <button
          class="p-[8px] rounded-xl text-sm bg-gray-600 text-white hover:bg-[#FF6666] hover:text-black"
          @click="nextInput"
        >
          계속하기
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";
const route = useRoute();
const router = useRouter();
const nextInput = () => {
  router.push(route.fullPath + "/nickname");
};
</script>

<style scope></style>
