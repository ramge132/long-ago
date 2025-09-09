<template>
  <div class="col-span-1 flex flex-col gap-y-1 h-full">
    <!-- 접속한 사용자들 표시 -->
    <div
      v-for="(user, index) in props.participants"
      :key="user.id"
      class="participant-card relative flex items-center gap-x-3 rounded-md p-2 bg-gradient-to-r from-[#f3c86f]/20 via-[#d1b2c5]/20 to-[#9973b0]/20 border border-[#f3c86f]/30 backdrop-blur-sm hover:scale-102 transition-all duration-200"
    >
      <div class="relative flex w-10 h-10">
        <img :src="user.image" alt="프로필" />
        <span v-if="index === 0" class="absolute -top-4 -left-4 text-2xl z-10"
          >👑</span
        >
      </div>
      <div>
        {{ user.name }}
      </div>
    </div>

    <!-- 대기 중 슬롯 표시 -->
    <div
      v-for="n in maxParticipants - props.participants.length"
      :key="'waiting-' + n"
      class="waiting-slot flex items-center gap-x-3 rounded-md p-2 border-2 border-dashed border-[#adb7cf]/40 bg-[#52bebc]/10 backdrop-blur-sm"
    >
      <div class="rounded-full border border-white w-10 h-10 bg-gray-500"></div>
      <div class="flex">
        <div class="animate-bounce" style="animation-delay: 0.1s">대</div>
        <div class="animate-bounce" style="animation-delay: 0.2s">기</div>
        <div class="animate-bounce" style="animation-delay: 0.3s">중</div>
        <div class="animate-bounce" style="animation-delay: 0.4s">.</div>
        <div class="animate-bounce" style="animation-delay: 0.5s">.</div>
        <div class="animate-bounce" style="animation-delay: 0.6s">.</div>
      </div>
    </div>
    <div
      class="rounded-md border border-[#adb7cf]/40 bg-gradient-to-b from-[#52bebc]/10 to-transparent flex-1 max-h-28 overflow-y-scroll p-2 backdrop-blur-sm"
      ref="chatBox"
    >
      <p
        v-for="(msg, index) in props.receivedMessages"
        :key="index"
        class="text-sm"
      >
        <strong>{{ msg.sender }}:</strong> {{ msg.message }}
      </p>
    </div>
    <div
      class="flex items-center relative h-12 border border-[#f3c86f]/40 bg-white/5 backdrop-blur-sm rounded-lg overflow-hidden"
    >
      <input
        type="text"
        v-model="message"
        @keyup.enter="send"
        placeholder="메시지를 입력하세요"
        class="w-full h-full pl-4 pr-16 text-[0.8rem] bg-[#ffffff00] focus:outline-none focus:ring-2 focus:ring-[#f3c86f] focus:border-transparent placeholder-gray-600"
      />
      <button
        @click="send"
        class="absolute h-8 w-14 right-2 bg-black text-white rounded-lg transition-colors flex items-center justify-center font-medium text-sm hover:bg-gray-800"
      >
        전송
      </button>
    </div>
  </div>
</template>
<script setup>
import { ref, nextTick, watch, defineProps } from "vue";
import { useUserStore } from "@/stores/auth";

const userStore = useUserStore();
const message = ref("");
const chatBox = ref(null);
const maxParticipants = 6;
const props = defineProps({
  participants: {
    Type: Array,
  },
  connectedPeers: {
    Type: Array,
  },
  receivedMessages: {
    Type: Array,
  },
});

const emit = defineEmits(["broadcastMessage"]);

const scrollToBottom = async () => {
  await nextTick();
  if (chatBox.value) {
    chatBox.value.scrollTop = chatBox.value.scrollHeight;
  }
};

const send = () => {
  if (message.value.trim()) {
    emit("broadcastMessage", {
      sender: userStore.userData.userNickname,
      message: message.value,
    });
    message.value = "";
  }
  scrollToBottom();
};

watch(
  () => props.receivedMessages,
  () => {
    scrollToBottom();
  },
  { deep: true },
);
</script>
<style></style>
