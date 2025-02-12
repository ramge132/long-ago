<template>
  <div class="row-span-2 flex flex-col justify-between py-2 relative">
    <div class="flex justify-center items-center grow">
      <div class="flex flex-col justify-center items-center w-3/4 mr-3">
        <div class="flex justify-between w-full">
          <div
            v-for="(card, index) in storyCards"
            :key="index"
            class="relative"
          >
            <img :src="CardImage.storyCardBack" alt="스토리카드" class="w-28">
            <div class="storycard w-full h-full p-2 flex items-center justify-center absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 font-katuri text-[#eadfcd] text-3xl">{{ card.keyword }}</div>
          </div>
        </div>
      </div>
      <div class="flex flex-col flex-1 justify-center items-center">
        <div
          class="relative endingcard cursor-pointer"
          @click="sendEndingCard"
        >
          <img :src="CardImage.endingCardBack" alt="엔딩카드" class="w-28">
          <div class="endingcard-text w-full h-full p-3 flex items-center justify-center absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 font-katuri text-[#fee09e] text-xl">{{ endingCard.content }}</div>
        </div>
      </div>
    </div>
    <div class="absolute bottom-4 flex justify-center items-end gap-x-2 w-full">
      <div
        class="rounded-full bg-[#ffffffdb] drop-shadow-md h-10 flex flex-1 px-3 items-center"
        v-for="(mode, index) in chatMode"
        :key="index"
        :class="index == currChatModeIdx ? '' : 'hidden'"
      >
        <div
          class="flex flex-nowrap flex-col justify-center items-center relative"
          @click="changeMode"
        >
          <p
            class="whitespace-nowrap absolute top-[-1.25rem]"
            v-text="mode.mark"
          ></p>
          <img :src="ChangeIcon" alt="채팅모드변경" class="h-3/5" />
        </div>
        <input
          type="text"
          class="pl-3 bg-transparent w-full h-full text-2xl font-semibold mx-2"
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
      <div class="relative w-10 h-10">
        <button
          class="bg-[#ffffff] rounded-full w-10 h-10 flex justify-center items-center drop-shadow-md z-10 absolute bottom-0" 
          @click="toggleEmoticon = !toggleEmoticon"
        >
          <img :src="EmoticonIcon" alt="감정표현" class="w-6" />
        </button>
        <div class="rounded-full w-10 bg-[#ffffffa0] absolute bottom-2 overflow-hidden emoticon" :class="toggleEmoticon ? 'max-h-[520px]' : 'max-h-0'">
          <button
          class="rounded-full w-10 h-10 p-1 flex justify-center items-center drop-shadow-md z-0"
          v-for="(emoticon, index) in emoticons"
          :key="index"
          @click="sendEmoticon(emoticon.d_image)"
          >
          <img :src="emoticon.s_image" alt="이모티콘" />
        </button>
        <div class="w-8 h-8">
        </div>
        </div>
      </div>
      <div
        class="w-10 h-24 bg-[#ffffffdb] rounded-full flex flex-col items-center justify-center text-center text-[10px] cursor-pointer"
        @click="cardReroll"
      >
        <img :src="RefreshIcon" alt="" class="w-6">
        <p>결말<br>새로고침</p>
        <p class="text-xl">{{ rerollCount }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { RefreshIcon, SendIcon, EmoticonIcon, ChangeIcon } from "@/assets";
import CardImage from "@/assets/cards"
import { useUserStore } from "@/stores/auth";
import emoji from "@/assets/images/emoticons";
import toast from "@/functions/toast";

const userStore = useUserStore();
const toggleEmoticon = ref(false);
const message = ref("");
const rerollCount = ref(3);
const emoticons = ref(
  [
    "laugh",
    "wrath",
    "confused",
    "asleep", 
    "crossed",
    "fear",
    "expressionless",
    "loving",
    "sad",
    "sunglasses",
    "tongue",
    "wink",
  ].map((type) => ({
    d_image: emoji[`d_${type}`],
    s_image: emoji[`s_${type}`],
  }))
);

const props = defineProps({
  myTurn: {
    Type: Number,
  },
  currTurn: {
    Type: Number,
  },
  storyCards: {
    Type: Array,
  },
  endingCard: {
    Type: Object,
  },
});

const emit = defineEmits(["broadcastMessage", "nextTurn", "cardReroll"]);

const sendChat = () => {
  if (message.value.trim()) {
    emit("broadcastMessage", {
      sender: userStore.userData.userNickname,
      message: message.value,
    });
    message.value = "";
  }
};
const sendprompt = () => {
  if (props.myTurn !== props.currTurn) {
    toast.errorToast("자신의 턴에만 이야기를 제출할 수 있습니다!");
  } else if(message.value.trim()) {
    emit("nextTurn", {
      prompt: message.value
    });
    message.value = "";
  }
};
const sendEmoticon = (data) => {
  emit("broadcastMessage", {
    sender: userStore.userData.userNickname,
    message: data,
    form: "emoticon",
  });
  toggleEmoticon.value = false;
};
const sendEndingCard = () => {
  if (props.myTurn !== props.currTurn) {
    toast.errorToast("자신의 턴에만 결말카드를 제출할 수 있습니다!");
  } else {
    emit("nextTurn", {
      prompt: props.endingCard.content,
      isEnding: true,
    });
  }
}

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

const cardReroll = () => {
  if (rerollCount.value) {
    emit("cardReroll");
    rerollCount.value--;
  } else {
    toast.errorToast("모두 사용했습니다!");
  }
};
</script>

<style scoped>
.reroll {
  background: linear-gradient(70deg, #fafcca 65%, #907800 35%);
}
.emoticon {
  transition: all 0.3s ease-in-out;
}
.storycard {
  text-shadow: -1px 0px #9f876a, 0px 1px #9f876a, 1px 0px #9f876a, 0px -1px #9f876a;
}
.endingcard-text {
  text-shadow: -1px 0px #8a622a, 0px 1px #8a622a, 1px 0px #8a622a, 0px -1px #8a622a;
}

@keyframes swing {
  0% { transform: rotate(-2deg); }
  100% { transform: rotate(2deg); }
}

.endingcard {
  transition: transform 0.2s ease-in-out;
  transform-origin: bottom center;
}

.endingcard:hover {
  animation: swing 0.5s ease-in-out infinite alternate;
}
</style>
