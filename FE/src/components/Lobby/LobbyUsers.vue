<template>
  <div class="col-span-1 flex flex-col gap-y-1 h-full">
    <!-- 접속한 사용자들 표시 -->
    <div
      v-for="(user, index) in props.participants"
      :key="user.id"
      class="flex items-center gap-x-3 rounded-md p-1 border-2 border-[#00000050]"
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
      class="flex items-center gap-x-3 rounded-md p-1 border-2 border-[#00000050]"
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
      class="rounded-md border-2 border-[#00000050] flex-1 max-h-28 overflow-y-scroll"
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
      class="flex items-center relative h-12 border-2 border-[#00000050] rounded-lg overflow-hidden"
    >
      <input
        type="text"
        v-model="message"
        @keyup.enter="send"
        placeholder="메시지를 입력하세요"
        class="w-full h-full pl-4 pr-16 text-[0.8rem] bg-[#ffffff00] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-600"
      />
      <button
        @click="send"
        class="absolute h-8 w-14 right-2 px-4 py-2 bg-black text-center text-[0.8rem] text-white rounded-lg transition-colors"
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
