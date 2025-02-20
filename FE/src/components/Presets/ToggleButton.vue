<template>
  <div
    class="absolute z-10 left-5 top-5 flex flex-col gap-y-1 text-gray-800"
    :class="isInGame ? 'left-5 top-[-50px]' : 'left-5 top-5'"
  >
  <div class="flex items-center gap-x-3">

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
    <audio ref="audioRef" :src="route.path === '/game/rank' ? RankingMusic : LobbyMusic" loop></audio>
  </div>
    <div v-show="audioStore.audioData" class="flex items-center gap-x-3">
      <span class="font-semibold text-sm">VOLUME</span>
      <input type="range" min="0" max="1" v-model="audioStore.audioVolume" step="0.01">
      <span
      class="text-[10px]"
      >{{ Math.round(audioStore.audioVolume * 100) }}</span
    >
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useAudioStore } from "@/stores/audio";
import { LobbyMusic, RankingMusic } from "@/assets";

const audioStore = useAudioStore();
const route = useRoute();

// 오디오 상태 관리
const isInGame = ref(false);
const audioRef = ref(null);

// 음악 재생/정지 로직
const toggleAudio = () => {
  if (audioRef.value) {
    if (audioStore.audioData) {
      audioStore.audioPlay = true;
      audioRef.value.play();
    } else {
      audioStore.audioPlay = false;
      audioRef.value.pause(); 
    }
  }
};

watch(() => audioStore.audioVolume, () => {
  audioRef.value.volume = audioStore.audioVolume;
});

watch(() => audioStore.audioPlay,  () => {
  if (audioStore.audioPlay) {
    audioRef.value.play();
  } else {
    audioRef.value.pause();
  }
})

watch(
  () => route.path,
  () => {
    if (route.path === "/game/play" || route.path === "/game/rank") {
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

/* input[type="range"] {
  appearance: none;
  width: 100%;
  padding: 2px;
  box-shadow: inset 4px 6px 10px -4px rgba(0, 0, 0, 0.3),
    0 1px 1px -1px rgba(255, 255, 255, 0.3);
  background: #9ea0be;
  overflow: hidden;
  outline: none;
  border: 1px solid rgba(0, 0, 0, 0.7);
  border-radius: 20px;
}

input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 10px;
  height: 10px;
  background: #d1d8ff;
  position: relative;
  z-index: 3;
  box-shadow: inset 4px 6px 10px -4px #d1d8ffbd,
    0 1px 1px -1px #d1d8ff97;
    border-radius: 50%
}

input[type="range"]::-moz-range-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  background: #333;
  position: relative;
  z-index: 3;
  box-shadow: inset 4px 6px 10px -4px rgba(0, 0, 0, 0.3),
    0 1px 1px -1px rgba(255, 255, 255, 0.3);
    border-radius: 50%
}

input[type="range"]::-webkit-slider-thumb:hover {
  cursor: pointer;
}

input[type="range"]::-moz-range-thumb:hover {
  cursor: pointer;
} */
input[type="range"]{
  -webkit-appearance:none;
  width:85px;
  height:4px;
  border-radius: 2px;
  background: #505162;
  background-position:center;
  background-repeat:no-repeat;
}

input[type="range"]::-webkit-slider-thumb{
  -webkit-appearance:none;
  width:15px;
  height:15px;
  border-radius: 100%;
  background: #f7f8ff;
  position:relative;
  border: 3px solid #f7f8ff;
  z-index:3;
  cursor: pointer;
}
</style>
