<template>
  <div
    class="absolute w-full h-full bg-[#00000050] flex justify-center items-center"
  >
    <div class="w-2/3 h-5/6 bg-[#ffffffdd] rounded-xl flex flex-col items-center p-3 gap-3" :class="voteEnded ? 'bounce-reverse' : 'bounce'" @animationend="handleAnimationEnd">
      <div class="meter orange w-full h-14">
        <span class="w-full rounded-full" :class="countStarted ? 'decrease' : ''" @animationend="voteEnd"></span>
      </div>
      <p class="text-6xl font-katuri">이 이야기를 추가할까요?</p>
      <div class="border-2 border-black w-full rounded-md flex justify-center items-center h-32">
        <p>{{ prompt }}</p>
      </div>
      <div class="grid grid-cols-2 w-full h-full gap-4">
        <div class="border-4 border-black rounded-xl flex justify-center items-center cursor-pointer" @click= "selected = 'up'" :class="selected === 'up' ? 'border-green-400' : 'opacity-60'">
          <img :src="VoteUpLeftIcon" alt="따봉" class="w-3/5">
        </div>
        <div class="border-4 border-black rounded-xl flex justify-center items-center cursor-pointer" @click="selected = 'down'" :class="selected === 'down' ? 'border-green-400' : 'opacity-60'">
          <img :src="VoteDownRightIcon" alt="역따봉" class="w-3/5">
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { VoteUpLeftIcon, VoteDownRightIcon } from '@/assets';
import { ref } from 'vue';
import { useUserStore } from '@/stores/auth';
const userStore = useUserStore();
const selected = ref("up");
const countStarted = ref(false);
const voteEnded = ref(false);
const inVote = ref(false);
const emit = defineEmits(['voteEnd']);
const startCount = () => {
  countStarted.value = true;
};
const props = defineProps({
  prompt: {
    Type: String,
  },
})
const voteEnd = () => {
  setTimeout(() => {
    voteEnded.value = true;
  }, 500);
  emit('voteEnd', {
    sender: userStore.userData.userNickname,
    selected: selected.value
  });
};
const removeComponent = () => {
  inVote.value = false;
}
const handleAnimationEnd = (event) => {
  const animName = event.animationName;
  if (animName.includes("bounce-reverse")) {
    removeComponent();
  } 
  else if (animName.includes("bounce")) {
    startCount();
  }
};

</script>
<style scoped>
.meter {
  position: relative;
  background: #555;
  border-radius: 25px;
  padding: 10px;
}
.meter > span {
  display: block;
  height: 100%;
  box-shadow: inset 0 2px 9px rgba(255, 255, 255, 0.3),
    inset 0 -2px 6px rgba(0, 0, 0, 0.4);
  position: relative;
  overflow: hidden;
}
.meter > span:after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  background-image: linear-gradient(
    -45deg,
    rgba(255, 255, 255, 0.2) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0.2) 75%,
    transparent 75%,
    transparent
  );
  z-index: 1;
  background-size: 50px 50px;
  animation: move 2s linear infinite;
  overflow: hidden;
}
@keyframes move {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 50px 50px;
  }
}
.orange > span {
  background-image: linear-gradient(#f1a165, #f36d0a);
}

@keyframes decrease {
  from { width: 100%; }
  to { width: 0; }
}

@keyframes bounce {
  0% {
    scale: 0%;
  }
  80% {
    scale: 105%;
  }
  100% {
    scale: 100%;
  }
}

@keyframes bounce-reverse {
  0% {
    scale: 100%;
  }
  20% {
    scale: 105%;
  }
  100% {
    scale: 0%;
  }
}

.bounce {
  animation: bounce 0.5s;
}

.bounce-reverse {
  animation: bounce-reverse 0.5s;
}


.decrease {
  animation: decrease 10s linear forwards;
}
</style>
