import { defineStore } from "pinia";

export const useAudioStore = defineStore("audioData", {
  state: () => ({
    audioVolume: 1,
    audioData: false,
    audioPlay: false,
  }),
  actions: {
    // toggleAudio() {
    //     this.audioData = !this.audioData;
    // }
  },
});
