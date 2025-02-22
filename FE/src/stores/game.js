import { defineStore } from "pinia";

export const useGameStore = defineStore("gameData", {
  state: () => ({
    gameData: {
      bossId: "",
    },
  }),
  actions: {
    setBossId(data) {
      this.gameData.bossId = data;
    },
    getBossId() {
      return this.gameData.bossId;
    },
    clearGameData() {
      this.gameData.bossId = "";
    }
  },
});
