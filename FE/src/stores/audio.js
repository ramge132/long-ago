import { defineStore } from "pinia";

export const useAudioStore = defineStore("audioData", {
  state: () => ({
    audioVolume: 1,
    audioData: true,  // 기본 사운드 켜짐
    audioPlay: true,
  }),
  actions: {
    // toggleAudio() {
    //     this.audioData = !this.audioData;
    // }
  },
});
