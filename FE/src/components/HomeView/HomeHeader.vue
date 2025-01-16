<template>
  <div class="flex flex-col items-center relative my-8 mb-14">
    <img :src="logo" alt="ere.gg" class="w-96" />
    <div
      class="flex absolute bottom-[-50px] rounded-full px-6 p-2 bg-white items-center"
    >
      <div>
        <div class="text-[12px] font-semibold">검색</div>
        <input
          type="text"
          placeholder="플레이어 ID를 입력하세요."
          class="w-[35rem] h-8 text-base appearance-none border-none outline-none focus:ring-0 focus:outline-none bg-transparent"
        />
      </div>
      <button>
        <img :src="magnify" />
      </button>
    </div>
  </div>
</template>
<script setup>
import logo from "@/assets/logo.svg";
import magnify from "@/assets/icons/magnify.svg";
</script>
