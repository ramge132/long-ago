<template>
  <div
    class="absolute z-10 left-5 top-5 flex gap-x-3 items-center text-gray-800"
    :class="isInGame ? 'left-5 top-[-30px]' : 'left-5 top-5'"
  >
    <span class="font-semibold">SOUND</span>
    <span
      class="text-[10px]"
      :class="audioStore.audioData ? 'text-[#00000050]' : ''"
      >OFF</span
    >
    <label class="switch">
      <input
        type="checkbox"
        v-model="audioStore.audioData"
        @change="toggleAudio"
      />
      <div>
        <span></span>
      </div>
    </label>
    <span
      class="text-[10px]"
      :class="audioStore.audioData ? '' : 'text-[#00000050]'"
      >ON</span
    >

    <!-- 오디오 -->
    <audio ref="audioRef" :src="props.music" loop></audio>
  </div>
</template>

<script setup>
import { ref, defineProps, watch } from "vue";
import { useRoute } from "vue-router";
import { useAudioStore } from "@/stores/audio";

const audioStore = useAudioStore();
const route = useRoute();

// props로 음악 파일 경로를 받아옴
const props = defineProps({
  music: {
    type: String,
    required: true,
  },
});

// 오디오 상태 관리
const isInGame = ref(false);
const audioRef = ref(null);

// 음악 재생/정지 로직
const toggleAudio = () => {
  if (audioRef.value) {
    if (audioStore.audioData) {
      audioRef.value.play();
    } else {
      audioRef.value.pause();
    }
  }
};

watch(
  () => route.path,
  () => {
    if (route.path === "/game/play") {
      isInGame.value = true;
    } else {
      isInGame.value = false;
    }
  },
);
</script>
<style scoped>
.switch {
  --line: #505162;
  --dot: #f7f8ff;
  --circle: #9ea0be;
  --duration: 0.3s;
  --text: #9ea0be;
  cursor: pointer;
}
.switch input {
  display: none;
}
.switch input + div {
  position: relative;
}
.switch input + div:before,
.switch input + div:after {
  --s: 1;
  content: "";
  position: absolute;
  height: 4px;
  top: 10px;
  width: 24px;
  background: var(--line);
  transform: scaleX(var(--s));
  transition: transform var(--duration) ease;
}
.switch input + div:before {
  --s: 0;
  left: 0;
  transform-origin: 0 50%;
  border-radius: 2px 0 0 2px;
}
.switch input + div:after {
  left: 28px;
  transform-origin: 100% 50%;
  border-radius: 0 2px 2px 0;
}
.switch input + div span {
  padding-left: 56px;
  line-height: 24px;
  color: var(--text);
}
.switch input + div span:before {
  --x: 0;
  --b: var(--circle);
  --s: 4px;
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  box-shadow: inset 0 0 0 var(--s) var(--b);
  transform: translateX(var(--x));
  transition:
    box-shadow var(--duration) ease,
    transform var(--duration) ease;
}
.switch input + div span:not(:empty) {
  padding-left: 64px;
}
.switch input:checked + div:before {
  --s: 1;
}
.switch input:checked + div:after {
  --s: 0;
}
.switch input:checked + div span:before {
  --x: 28px;
  --s: 12px;
  --b: var(--dot);
}

html {
  box-sizing: border-box;
  -webkit-font-smoothing: antialiased;
}

* {
  box-sizing: inherit;
}
*:before,
*:after {
  box-sizing: inherit;
}

body {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  position: relative;
  background: #262730;
}
body .switch + .switch {
  margin-top: 32px;
}
body .dribbble {
  position: fixed;
  display: block;
  right: 20px;
  bottom: 20px;
}
body .dribbble img {
  display: block;
  height: 28px;
}
</style>
