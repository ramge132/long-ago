import { defineStore } from "pinia";
import { useRoute } from "vue-router";

const route = useRoute();

export const useGameStore = defineStore("gameInfo", {
  state: () => ({
    GameData: {
      bossId: ""
    },
  }),
  actions: {
    setBossId(data) {
        this.bossId = data;
    }
  },
});
