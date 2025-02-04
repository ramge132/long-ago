<template>
  <div class="row-span-2 flex flex-col justify-between py-2">
    <div class="flex mb-3 grow">
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
    <div class="flex justify-center relative">
      <div
        class="rounded-full bg-[#AEE8FF] drop-shadow-md w-2/3 h-10 mx-1 flex px-3 items-center"
        v-for="(mode, index) in chatMode"
        :key="index"
        :class="index == currChatModeIdx ? '' : 'hidden'"
      >
        <div
          class="flex flex-nowrap flex-col justify-center items-center relative"
        >
          <p
            class="whitespace-nowrap absolute top-[-1.25rem]"
            v-text="mode.mark"
          ></p>
          <img :src="ChangeIcon" alt="채팅모드변경" class="h-3/5" />
        </div>
        <input
          type="text"
          class="pl-3 bg-transparent w-full h-full text-xl mx-2"
          v-model="message"
          @keyup.enter="mode.fucntion"
          :placeholder="mode.placeholder"
        />
        <button
          class="rounded-full border w-8 h-8 shrink-0 border-black p-1 flex justify-center items-center"
          @click="mode.fucntion"
        >
          <img
            :src="SendIcon"
            alt="보내기"
            class="object-scale-down w-3/4 h-3/4"
          />
        </button>
      </div>
      <div class="relative">
        <button
          class="bg-gray-400 rounded-full w-10 h-10 p-1 flex justify-center items-center drop-shadow-md mx-1 z-10 absolute"
          @click="toggleEmoticon = !toggleEmoticon"
        >
          <img :src="EmoticonIcon" alt="감정표현" class="object-scale-down" />
        </button>
        <button
          class="bg-gray-400 rounded-full w-10 h-10 p-1 flex justify-center items-center drop-shadow-md mx-1 absolute z-0 emoticon"
          v-for="(emoticon, index) in emoticons"
          :key="index"
          :class="toggleEmoticon ? 'emoticon' + index : ''"
          @click="sendEmoticon(emoticon.d_image)"
        >
          <img :src="emoticon.s_image" alt="이모티콘" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { RerollIcon, SendIcon, EmoticonIcon, ChangeIcon } from "@/assets";
import { useUserStore } from "@/stores/auth";
import emoji from "@/assets/images/emoticons";

const userStore = useUserStore();
const toggleEmoticon = ref(false);
const message = ref("");
const emoticons = ref([
  {
    d_image: emoji.d_laugh,
    s_image: emoji.s_laugh,
  },
  {
    d_image: emoji.d_wrath,
    s_image: emoji.s_wrath,
  },
  {
    d_image: emoji.d_confused,
    s_image: emoji.s_confused,
  },
]);

const emit = defineEmits(["broadcastMessage"]);

const sendChat = () => {
  if (message.value.trim()) {
    emit("broadcastMessage", {
      sender: userStore.userData.userNickname,
      message: message.value,
    });
    message.value = "";
  }
};
const sendprompt = () => {};
const sendEmoticon = (data) => {
  emit("broadcastMessage", {
    sender: userStore.userData.userNickname,
    message: data,
    form: "emoticon",
  });
  toggleEmoticon.value = false;
};

const chatMode = ref([
  {
    mark: "대화",
    fucntion: sendChat,
    placeholder: "채팅 입력",
  },
  {
    mark: "이야기",
    fucntion: sendprompt,
    placeholder: "다음 이어질 이야기를 작성해주세요",
  },
]);
const currChatModeIdx = ref(0);

window.addEventListener("keydown", (e) => {
  if (e.ctrlKey) changeMode();
});

const changeMode = () => {
  currChatModeIdx.value = (currChatModeIdx.value + 1) % chatMode.value.length;
};
</script>

<style scoped>
.reroll {
  background: linear-gradient(70deg, #fafcca 65%, #907800 35%);
}
.emoticon {
  transition: all 0.3s cubic-bezier(0.25, 1.65, 0.5, 1.15);
  opacity: 0;
}
.emoticon0 {
  transform: scale(1);
  transform: translate(-3rem, -3rem);
  opacity: 1;
}
.emoticon1 {
  transform: scale(1);
  transform: translate(0, -3rem);
  opacity: 1;
}
.emoticon2 {
  transform: scale(1);
  transform: translate(3rem, -3rem);
  opacity: 1;
}
</style>
