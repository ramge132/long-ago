<template>
  <div class="w-full h-full grid grid-cols-5 grid-rows-2">
    <div class="h-full row-span-2 grid grid-rows-3">
      <template v-for="(user, index) in props.participants" :key="user.id">
        <div
          class="flex flex-col justify-center items-center relative"
          v-if="index % 2 == 0"
        >
          <div
            class="rounded-full overflow-hidden w-24 h-24 border border-black"
          >
            <img :src="user.image" alt="프로필" />
          </div>
          <div
            class="absolute bg-[#aee8ff] w-[120px] min-h-[30px] rounded-lg top-[20px] right-[-70px] after:absolute after:bottom-0 after:left-[10%] after:border-[15px] after:border-transparent after:border-b-0 after:border-l-0 after:mb-[-10px] after:border-t-[#aee8ff] after:w-0 after:h-0 pl-3 hidden"
            :class="'speech-bubble' + index"
          >
            <p></p>
          </div>
          <div
            class="absolute bg-[#aee8ff] w-[80px] min-h-[60px] rounded-full bottom-[30px] right-[-20px] after:absolute after:top-0 after:left-[10%] after:border-[20px] after:border-transparent after:border-t-0 after:border-l-0 after:mt-[-10px] after:border-b-[#aee8ff] after:w-0 after:h-0 flex justify-center items-center text-3xl hidden"
            :class="'emoticon-bubble' + index"
          >
            <p></p>
          </div>
          <div>{{ user.name }}</div>
          <p></p>
          <div class="flex">
            <img :src="HeartIcon" alt="하트" />
            <div
              class="rounded-full bg-gray-400 w-5 h-5 text-center leading-[1.25rem] ml-1"
            >
              {{ 4 }}
            </div>
          </div>
        </div>
      </template>
      <template
        v-for="n in maxParticipants - props.participants.length"
        :key="n"
      >
        <div
          class="flex flex-col justify-center items-center"
          v-if="n % 2 == 0"
        >
          <div
            class="rounded-full bg-gray-500 w-24 h-24 border border-black"
          ></div>
          <div>비어 있음</div>
          <div class="h-5"></div>
        </div>
      </template>
    </div>
    <div class="col-span-3 row-span-2 grid grid-rows-2">
      <InGameContent />
      <InGameControl @broadcast-message="broadcastMessage" />
    </div>
    <div class="h-full row-span-2 grid grid-rows-3">
      <template v-for="(user, index) in props.participants" :key="user.id">
        <div
          class="flex flex-col justify-center items-center relative"
          v-if="index % 2 != 0"
        >
          <div
            class="rounded-full overflow-hidden w-24 h-24 border border-black"
          >
            <img :src="user.image" alt="프로필" />
          </div>
          <div
            class="absolute bg-[#aee8ff] w-[120px] h-[30px] rounded-lg top-[20px] left-[-70px] after:absolute after:bottom-0 after:right-[10%] after:border-[15px] after:border-transparent after:border-b-0 after:border-r-0 after:mb-[-10px] after:border-t-[#aee8ff] after:w-0 after:h-0 pl-3 hidden"
            :class="'speech-bubble' + index"
          >
            <p></p>
          </div>
          <div
            class="absolute bg-[#aee8ff] w-[80px] min-h-[60px] rounded-full bottom-[30px] left-[-20px] after:absolute after:top-0 after:right-[10%] after:border-[20px] after:border-transparent after:border-t-0 after:border-r-0 after:mt-[-10px] after:border-b-[#aee8ff] after:w-0 after:h-0 flex justify-center items-center text-3xl hidden"
            :class="'emoticon-bubble' + index"
          >
            <p></p>
          </div>
          <div>{{ user.name }}</div>
          <p></p>
          <div class="flex">
            <img :src="HeartIcon" alt="하트" />
            <div
              class="rounded-full bg-gray-400 w-5 h-5 text-center leading-[1.25rem] ml-1"
            >
              {{ 4 }}
            </div>
          </div>
        </div>
      </template>
      <template
        v-for="n in maxParticipants - props.participants.length"
        :key="n"
      >
        <div
          class="flex flex-col justify-center items-center"
          v-if="n % 2 != 0"
        >
          <div
            class="rounded-full bg-gray-500 w-24 h-24 border border-black"
          ></div>
          <div>비어 있음</div>
          <div class="h-5"></div>
        </div>
      </template>
    </div>
    <InGameProgress />
  </div>
</template>

<script setup>
import { onBeforeMount, ref, watch } from "vue";
import { HeartIcon } from "@/assets";
import { InGameControl, InGameContent, InGameProgress } from "@/components";

const maxParticipants = 6;
const chatTime = ref([
  [undefined, undefined],
  [undefined, undefined],
  [undefined, undefined],
  [undefined, undefined],
  [undefined, undefined],
  [undefined, undefined],
]);

const emit = defineEmits(["broadcastMessage", "gameExit"]);

const broadcastMessage = (data) => {
  emit("broadcastMessage", data);
};

const props = defineProps({
  roomConfigs: {
    Type: Object,
  },
  connectedPeers: {
    Type: Array,
  },
  receivedMessages: {
    Type: Array,
  },
  participants: {
    Type: Array,
  },
});

watch(
  () => props.receivedMessages,
  () => {
    for (const index in props.participants) {
      if (
        props.participants[index].name ==
        props.receivedMessages[props.receivedMessages.length - 1].sender
      ) {
        const select = ref();
        let type = 0;
        if (
          props.receivedMessages[props.receivedMessages.length - 1].form ==
          "emoticon"
        ) {
          select.value = document.querySelector(".emoticon-bubble" + index);
          type = 1;
        } else select.value = document.querySelector(".speech-bubble" + index);
        console.log(props.receivedMessages[props.receivedMessages.length - 1]);
        select.value.firstChild.textContent =
          props.receivedMessages[props.receivedMessages.length - 1].message;
        select.value.classList.remove("hidden");
        clearTimeout(chatTime.value[index][type]);
        chatTime.value[index][type] = setTimeout(() => {
          select.value.classList.add("hidden");
        }, 2000);
        break;
      }
    }
  },
  { deep: true },
);

onBeforeMount(() => {
  emit("gameExit");
});
</script>

<style scoped></style>
