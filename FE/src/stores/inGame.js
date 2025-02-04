import { defineStore } from "pinia";

export const useGameStore = defineStore("gameData", {
    state: () => ({
        gameData: {
            currTurn: 0,
        },
    }), 
    actions: {
        nextTurn() {
            gameData.currTurn += 1;
        }
    },
});