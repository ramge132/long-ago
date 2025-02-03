<template>
  <div class="row-span-2 flex flex-col justify-between py-2">
    <div
      class="rounded-md bg-gray-300 flex flex-col p-3 w-4/5 self-center mb-3"
    >
      <label>다음 이야기</label>
      <input
        class="rounded-xl pl-3 border-2 border-black"
        type="text"
        placeholder="다음 이어질 이야기를 작성해주세요."
      />
    </div>
    <div class="flex mb-3">
      <div class="flex flex-col justify-center items-center w-[50%] mr-3">
        <p v-html="`<사용 가능 카드>`"></p>
        <div class="flex justify-between w-full">
          <div
            v-for="n in 4"
            :key="n"
            class="bg-gray-400 w-[4rem] h-[7.5rem] mx-1"
          ></div>
        </div>
      </div>
      <div class="flex flex-col justify-center items-center w-[20%]">
        <p v-html="`<결말 카드>`"></p>
        <div class="bg-gray-400 w-[4rem] h-[7.5rem]"></div>
      </div>
      <div class="flex items-center justify-center min-w-[30%]">
        <div class="rounded-xl reroll flex p-3 w-full justify-between">
          <div class="text-xs">
            <p>결말 카드 바꾸기</p>
            <div class="flex items-center justify-between">
              <span>남은 횟수 :</span>
              <strong class="text-xl">3</strong>
            </div>
          </div>
          <img
            :src="RerollIcon"
            alt="리롤"
            class="justify-self-end self-center w-6 h-6"
          />
        </div>
      </div>
    </div>
    <div class="flex justify-center">
      <input
        type="text"
        class="rounded-full bg-[#AEE8FF] drop-shadow-md w-2/3 mx-1 pl-3"
        v-model="message"
        @keyup.enter="send"
      />
      <button
        class="bg-gray-400 rounded-full w-10 h-10 p-1 flex justify-center items-center drop-shadow-md mx-1"
        @click="send"
      >
        <img :src="SendIcon" alt="보내기" class="object-scale-down" />
      </button>
      <button
        class="bg-gray-400 rounded-full w-10 h-10 p-1 flex justify-center items-center drop-shadow-md mx-1"
      >
        <img :src="EmoticonIcon" alt="감정표현" class="object-scale-down" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { RerollIcon, SendIcon, EmoticonIcon } from "@/assets";
import { useUserStore } from "@/stores/auth";

const userStore = useUserStore();

const message = ref("");

const emit = defineEmits(["broadcastMessage"]);

const send = () => {
  if (message.value.trim()) {
    emit("broadcastMessage", {
      sender: userStore.userData.userNickname,
      message: message.value,
    });
    message.value = "";
  }
};
</script>

<style scoped>
.reroll {
  background: linear-gradient(70deg, #fafcca 65%, #907800 35%);
}
</style>
