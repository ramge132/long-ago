import { defineStore } from "pinia";

export const useAudioStore = defineStore("audioData", {
  state: () => ({
    audioVolume: 0.5,  // 기본값 50%
    audioData: true,  // 기본 사운드 켜짐
    audioPlay: true,
  }),
  actions: {
    // toggleAudio() {
    //     this.audioData = !this.audioData;
    // }
  },
});
